"""Streamlit interface for explainable role matching and skill pathways."""

from __future__ import annotations

import json
import csv
from io import StringIO
from pathlib import Path
import sys

import plotly.graph_objects as go
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.matching import analyze_student
from src.recommend import recommend_learning_pathway
from src.report import create_pdf_report
from src.resume_parser import extract_resume_text, infer_resume_skills
from src.skills_catalog import ROLE_BY_ID, ROLES, SKILL_BY_ID


DATA_PATH = PROJECT_ROOT / "data" / "students.csv"

st.set_page_config(page_title="Skill Gap Studio", layout="wide")

st.html(
        """
        <style>
            :root {
                --skill-ink: #203b36;
                --skill-teal: #167c72;
                --skill-coral: #e78262;
                --skill-line: #d3e4da;
                --skill-paper: rgba(255, 255, 255, 0.82);
            }

            .stApp {
                background:
                    radial-gradient(ellipse at 92% 4%, rgba(231, 130, 98, 0.10), transparent 25%),
                    linear-gradient(130deg, #f5faf7 0%, #f2f8f6 52%, #fff8f2 100%);
                color: var(--skill-ink);
            }

            [data-testid="stHeader"] {
                background: rgba(245, 250, 247, 0.72);
            }

            [data-testid="stSidebar"] {
                background: linear-gradient(165deg, #e5f1ea 0%, #f1f7f3 72%, #fdf7f0 100%);
                border-right: 1px solid var(--skill-line);
            }

            [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
                color: #35564f;
            }

            h1, h2, h3 {
                color: var(--skill-ink);
            }

            h1 {
                font-weight: 600;
            }

            [data-testid="stMetric"] {
                background: var(--skill-paper);
                border: 1px solid var(--skill-line);
                border-radius: 6px;
                padding: 0.9rem 1rem;
                box-shadow: 0 5px 18px rgba(32, 59, 54, 0.045);
            }

            [data-testid="stMetricLabel"] p {
                color: #54736a;
            }

            [data-testid="stMetricValue"] {
                color: var(--skill-teal);
            }

            [data-testid="stFileUploader"] section {
                background: rgba(255, 255, 255, 0.72);
                border: 1px dashed #91b9a7;
                border-radius: 6px;
            }

            [data-testid="stExpander"],
            [data-testid="stVerticalBlockBorderWrapper"] {
                border-color: var(--skill-line);
                border-radius: 6px;
            }

            .stButton > button,
            .stDownloadButton > button,
            [data-testid="stFormSubmitButton"] > button {
                border-radius: 6px;
                border-color: #b7d1c4;
                transition: transform 120ms ease, box-shadow 120ms ease, background 120ms ease;
            }

            .stButton > button:hover,
            .stDownloadButton > button:hover {
                border-color: var(--skill-coral);
                color: #8d4936;
                box-shadow: 0 4px 12px rgba(32, 59, 54, 0.08);
                transform: translateY(-1px);
            }

            button[kind="primary"] {
                background: var(--skill-teal);
                border-color: var(--skill-teal);
            }

            button[kind="primary"]:hover {
                background: #116a61;
                border-color: #116a61;
                color: white;
            }

            [data-testid="stMarkdownContainer"] table {
                border-collapse: collapse;
                width: 100%;
            }

            [data-testid="stMarkdownContainer"] th {
                background: #eaf3ee;
                color: #203b36;
            }

            [data-testid="stAlert"] {
                border-radius: 6px;
            }
        </style>
        """
)


@st.cache_data(ttl="15m")
def load_profiles(path: str) -> list[dict[str, str]]:
    """Load generated profiles from CSV for use by the dashboard."""
    with Path(path).open("r", encoding="utf-8-sig", newline="") as source:
        return list(csv.DictReader(source))


def _required_and_prerequisite_ids(role_id: str) -> list[str]:
    """Collect direct role skills and their full prerequisite closure."""
    visited: set[str] = set()

    def visit(skill_id: str) -> None:
        if skill_id in visited:
            return
        visited.add(skill_id)
        for prerequisite in SKILL_BY_ID[skill_id]["prerequisites"]:
            visit(prerequisite)

    for item in ROLE_BY_ID[role_id]["required_skills"]:
        visit(item["skill_id"])
    return sorted(visited, key=lambda skill_id: SKILL_BY_ID[skill_id]["name"].casefold())


def _skill_levels(profile: dict[str, str]) -> dict[str, int]:
    return {key: int(value) for key, value in json.loads(profile["skill_levels"]).items()}


def _show_markdown_table(title: str, headers: list[str], rows: list[list[object]]) -> None:
    """Render a small table without requiring pandas or Arrow serialization."""
    def cell_text(value: object) -> str:
        return str(value).replace("|", "\\|").replace("\r", " ").replace("\n", " ")

    lines = [
        "| " + " | ".join(cell_text(header) for header in headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(cell_text(value) for value in row) + " |" for row in rows)
    st.markdown(f"**{title}**\n\n" + "\n".join(lines))


def _resume_flow(role_id: str) -> None:
    uploaded_file = st.file_uploader(
        "Upload your resume",
        type=["pdf", "docx", "txt"],
        max_upload_size=5,
        help="PDF, DOCX, or TXT; maximum 5 MB. Files are processed in memory and not saved.",
    )
    if uploaded_file is None:
        st.info("Upload a resume to suggest skills and build a role-specific learning pathway.")
        return

    try:
        resume_text = extract_resume_text(uploaded_file.name, uploaded_file.getvalue())
        inference = infer_resume_skills(resume_text)
    except ValueError as error:
        st.error(str(error), title="Resume could not be analyzed")
        return

    evidence = inference["evidence"]
    if not evidence:
        st.warning("No catalog skills were recognized. Try a text-based resume or enter levels manually.")
        return

    st.caption("Suggested levels are inferred from wording, not verified credentials. Review and edit every level before analysis. Resume contents are not written to disk.")
    _show_markdown_table(
        "Resume skill evidence",
        ["Skill", "Suggested level", "Evidence"],
        [[row["skill_name"], row["suggested_level"], row["evidence"]] for row in evidence],
    )
    with st.form("resume_skill_review"):
        st.subheader("Review skill levels")
        columns = st.columns(3)
        reviewed_levels: dict[str, int] = {}
        for index, row in enumerate(evidence):
            skill_id = str(row["skill_id"])
            reviewed_levels[skill_id] = columns[index % len(columns)].number_input(
                str(row["skill_name"]),
                min_value=0,
                max_value=5,
                value=int(row["suggested_level"]),
                step=1,
                key=f"resume-level-{role_id}-{skill_id}",
                help="Edit this suggested level before comparing it with role requirements.",
            )
        submitted = st.form_submit_button("Find my skill gaps", type="primary")
    if submitted:
        _render_results(reviewed_levels, role_id, resume_text)


def _radar_chart(levels: dict[str, int], role_id: str) -> go.Figure:
    role = ROLE_BY_ID[role_id]
    requirements = role["required_skills"]
    names = [SKILL_BY_ID[item["skill_id"]]["name"] for item in requirements]
    current = [levels.get(item["skill_id"], 0) for item in requirements]
    target = [item["required_level"] for item in requirements]
    figure = go.Figure()
    figure.add_trace(go.Scatterpolar(r=current, theta=names, fill="toself", name="Current level"))
    figure.add_trace(go.Scatterpolar(r=target, theta=names, fill="toself", name="Role requirement"))
    figure.update_layout(
        title="Current skills and role requirements",
        polar={"radialaxis": {"visible": True, "range": [0, 5], "dtick": 1}},
        showlegend=True,
        margin={"t": 55, "b": 25, "l": 35, "r": 35},
    )
    return figure


def _gap_chart(result: dict[str, object]) -> go.Figure:
    gaps = result["missing_skills"] + result["weak_skills"]
    figure = go.Figure()
    if gaps:
        ordered = sorted(gaps, key=lambda item: (item["importance_weight"], item["gap_size"], item["name"]))
        figure.add_trace(
            go.Bar(
                x=[item["gap_size"] for item in ordered],
                y=[item["name"] for item in ordered],
                orientation="h",
                marker={
                    "color": [item["importance_weight"] for item in ordered],
                    "colorscale": "Teal",
                    "showscale": True,
                    "colorbar": {"title": "Role weight"},
                },
                hovertemplate="%{y}<br>Levels to required: %{x}<extra></extra>",
            )
        )
        title = "Levels below requirement"
    else:
        title = "No role skill gaps"
    figure.update_layout(
        title=title,
        xaxis_title="Levels to required",
        yaxis_title="Skill",
        yaxis={"categoryorder": "total ascending"},
        margin={"t": 55, "b": 25, "l": 20, "r": 20},
    )
    return figure


def _render_results(levels: dict[str, int], role_id: str, summary: str) -> None:
    result = analyze_student(levels, role_id, summary)
    pathway = recommend_learning_pathway(levels, role_id)
    st.session_state["last_analysis"] = {"result": result, "pathway": pathway, "role_id": role_id}

    st.title(f"{result['role_name']} skill-gap analysis")
    metric_column, explanation_column = st.columns([1, 2])
    metric_column.metric("Weighted match", f"{result['match_percentage']:.1f}%")
    metric_column.metric("Text similarity", f"{result['tfidf_similarity']:.1f}%")
    explanation_column.info(result["score_explanation"], title="Why this score?")

    chart_columns = st.columns(2)
    chart_columns[0].plotly_chart(
        _radar_chart(levels, role_id),
        alt="Radar comparison of the selected student's skill levels and role requirements",
    )
    chart_columns[1].plotly_chart(
        _gap_chart(result),
        alt="Skill gaps ordered by level difference and role importance",
    )

    st.subheader("Learning pathway")
    if not pathway:
        st.success("Every catalog skill for this role meets its current required level.")
    else:
        for item in pathway:
            with st.container(border=True):
                st.markdown(f"**{item['step']}. {item['skill_name']}** · {item['status']} · level {item['current_level']} → {item['target_level']}")
                st.write(item["reason"])
                st.caption(item["learning_resource"])

    with st.expander("Matched skills and role gaps"):
        _show_markdown_table(
            "Matched at or above the role requirement",
            ["Skill", "Current level", "Required level", "Importance"],
            [[item["name"], item["current_level"], item["required_level"], item["importance_weight"]] for item in result["matched_skills"]],
        )
        gaps = result["missing_skills"] + result["weak_skills"]
        _show_markdown_table(
            "Missing and below requirement",
            ["Skill", "Current level", "Required level", "Gap", "Importance"],
            [[item["name"], item["current_level"], item["required_level"], item["gap_size"], item["importance_weight"]] for item in gaps],
        )

    report_lines = [
        f"Role: {result['role_name']}",
        f"Weighted skill match: {result['match_percentage']:.1f}%",
        f"TF-IDF text similarity (separate signal): {result['tfidf_similarity']:.1f}%",
        "Why this score: " + result["score_explanation"],
        "",
        "Learning pathway:",
        *[f"{item['step']}. {item['skill_name']} (level {item['current_level']} to {item['target_level']}) - {item['reason']} Resource: {item['learning_resource']}" for item in pathway],
        "",
        "This analysis is a learning-planning aid, not a measure of a person's potential or employment suitability.",
    ]
    downloads = st.columns(2)
    downloads[0].download_button(
        "Download report (PDF)",
        create_pdf_report("Skill gap analysis", report_lines),
        "skill_gap_analysis.pdf",
        "application/pdf",
    )
    csv_fields = ["step", "skill_id", "skill_name", "current_level", "target_level", "reason", "learning_resource"]
    csv_buffer = StringIO()
    writer = csv.DictWriter(csv_buffer, fieldnames=csv_fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(pathway)
    downloads[1].download_button(
        "Download pathway (CSV)",
        csv_buffer.getvalue().encode("utf-8"),
        "learning_pathway.csv",
        "text/csv",
    )


def main() -> None:
    st.title("Skill Gap Studio")
    st.caption("Compare assessed skills with a role profile, then build a reasoned learning sequence.")
    source = st.sidebar.radio("Profile source", ["Upload resume", "Synthetic student", "Enter skill levels"])
    role_options = {role["name"]: role["role_id"] for role in ROLES}
    selected_role_name = st.sidebar.selectbox("Target role", list(role_options))
    role_id = role_options[selected_role_name]

    if source == "Upload resume":
        _resume_flow(role_id)
    elif source == "Synthetic student":
        if not DATA_PATH.exists():
            st.error("Synthetic profiles are not generated yet.", icon=":material/error:")
            st.code("python -m src.generate_data")
            st.stop()
        profiles = load_profiles(str(DATA_PATH))
        profile_ids = [profile["student_id"] for profile in profiles]
        profile_id = st.sidebar.selectbox("Student profile", profile_ids)
        profile = next(profile for profile in profiles if profile["student_id"] == profile_id)
        levels = _skill_levels(profile)
        summary = st.text_area("Skills summary", value=profile["skills_summary"], max_chars=3000)
        st.caption(f"Using generated synthetic profile {profile_id}; profile data is not persisted by the app.")
        if st.button("Analyze profile", type="primary"):
            _render_results(levels, role_id, summary)
        elif "last_analysis" in st.session_state:
            previous = st.session_state["last_analysis"]
            _render_results(levels, role_id, summary)
    else:
        skill_ids = _required_and_prerequisite_ids(role_id)
        with st.form("manual_skill_assessment"):
            st.write("Rate each selected role skill from 0 (not yet assessed) to 5 (strong working proficiency).")
            columns = st.columns(3)
            levels: dict[str, int] = {}
            for index, skill_id in enumerate(skill_ids):
                skill = SKILL_BY_ID[skill_id]
                levels[skill_id] = columns[index % len(columns)].number_input(
                    skill["name"], min_value=0, max_value=5, value=0, step=1, key=f"manual-{role_id}-{skill_id}"
                )
            summary = st.text_area("Skills summary", max_chars=3000)
            submitted = st.form_submit_button("Analyze custom profile", type="primary")
        if submitted:
            _render_results(levels, role_id, summary)
        elif "last_analysis" in st.session_state:
            previous = st.session_state["last_analysis"]
            if previous["role_id"] == role_id:
                _render_results(levels, role_id, summary)


if __name__ == "__main__":
    main()
