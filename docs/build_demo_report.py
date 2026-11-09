"""Build the formatted project and demo guide as docs/demo_report.docx."""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


OUTPUT_PATH = Path(__file__).with_name("demo_report.docx")
TEAL = "167C72"
INK = "203B36"
PALE_GREEN = "EAF3EE"
PALE_CORAL = "FFF2EC"
WHITE = "FFFFFF"


def _shade_cell(cell, fill: str) -> None:
    properties = cell._tc.get_or_add_tcPr()
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), fill)
    properties.append(shading)


def _format_cell(cell, *, bold: bool = False, color: str = INK) -> None:
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    for paragraph in cell.paragraphs:
        for run in paragraph.runs:
            run.bold = bold
            run.font.name = "Aptos"
            run.font.size = Pt(9)
            run.font.color.rgb = RGBColor.from_string(color)


def _add_table(document: Document, headers: list[str], rows: list[list[str]]) -> None:
    table = document.add_table(rows=1, cols=len(headers))
    table.style = "Light Shading Accent 1"
    for index, header in enumerate(headers):
        cell = table.rows[0].cells[index]
        cell.text = header
        _shade_cell(cell, TEAL)
        _format_cell(cell, bold=True, color=WHITE)
    for row_index, values in enumerate(rows):
        cells = table.add_row().cells
        for index, value in enumerate(values):
            cells[index].text = value
            _format_cell(cells[index])
            if row_index % 2 == 0:
                _shade_cell(cells[index], PALE_GREEN)
    document.add_paragraph()


def _bullet(document: Document, text: str) -> None:
    document.add_paragraph(text, style="List Bullet")


def _numbered(document: Document, text: str) -> None:
    document.add_paragraph(text, style="List Number")


def _qa(document: Document, question: str, answer: str) -> None:
    paragraph = document.add_paragraph()
    run = paragraph.add_run(question)
    run.bold = True
    run.font.color.rgb = RGBColor.from_string(TEAL)
    document.add_paragraph(answer)


def build_report() -> Path:
    """Create the report using the project's verified architecture and metrics."""
    document = Document()
    section = document.sections[0]
    section.top_margin = Inches(0.65)
    section.bottom_margin = Inches(0.65)
    section.left_margin = Inches(0.8)
    section.right_margin = Inches(0.8)

    normal = document.styles["Normal"]
    normal.font.name = "Aptos"
    normal.font.size = Pt(10)
    normal.font.color.rgb = RGBColor.from_string(INK)
    for style_name, size in (("Title", 28), ("Heading 1", 19), ("Heading 2", 14), ("Heading 3", 11)):
        style = document.styles[style_name]
        style.font.name = "Aptos Display"
        style.font.size = Pt(size)
        style.font.color.rgb = RGBColor.from_string(TEAL if style_name != "Title" else INK)

    header = section.header.paragraphs[0]
    header.text = "SKILL GAP STUDIO  |  PROJECT DEMO GUIDE"
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    for run in header.runs:
        run.font.size = Pt(8)
        run.font.color.rgb = RGBColor.from_string(TEAL)

    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer_run = footer.add_run("Synthetic-data learning tool  |  ")
    footer_run.font.size = Pt(8)
    footer_run.font.color.rgb = RGBColor.from_string(TEAL)
    page_field = OxmlElement("w:fldSimple")
    page_field.set(qn("w:instr"), "PAGE")
    footer._p.append(page_field)

    title = document.add_paragraph(style="Title")
    title.add_run("AI-Based Student Skill Gap Analysis System")
    subtitle = document.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.LEFT
    subtitle_run = subtitle.add_run("Detailed project report and presentation guide")
    subtitle_run.font.size = Pt(14)
    subtitle_run.font.color.rgb = RGBColor.from_string("B85E48")
    document.add_paragraph(
        "A role-focused learning planner that compares assessed skills with job requirements, explains the gaps, and suggests a prerequisite-aware learning pathway."
    )

    document.add_heading("1. Executive summary", level=1)
    document.add_paragraph(
        "Skill Gap Studio helps a learner understand how their current skill levels compare with a selected example job role. It identifies missing and below-target skills, calculates a transparent weighted coverage score, and creates an ordered learning pathway with reasons and resource suggestions."
    )
    document.add_paragraph(
        "The score is not a probability of employment, job success, or personal potential. Recommendations are learning prompts for the user to review. The project uses only generated synthetic profiles for its sample dataset and evaluation."
    )
    _add_table(
        document,
        ["Project fact", "Current implementation"],
        [
            ["Catalog", "75 skills across 10 example job roles"],
            ["Synthetic profiles", "500 profiles, deterministic seed 42 by default"],
            ["Skill scale", "Integer levels from 0 to 5"],
            ["Role requirement", "Importance weight 1 to 5 and required level 1 to 5"],
            ["Inputs", "Synthetic profile, manual levels, or PDF/DOCX/TXT resume"],
            ["Interfaces", "Streamlit dashboard and FastAPI JSON API"],
        ],
    )

    document.add_heading("2. Problem and goals", level=1)
    document.add_paragraph(
        "A learner may have a target role in mind but not know which specific skills to work on first. A simple list of missing skills can be hard to act on when some skills depend on others or matter more to the role."
    )
    for item in [
        "Compare a 0-5 skill assessment with the selected role's catalog requirements.",
        "Show the score calculation and distinguish missing skills from partially developed skills.",
        "Prioritize learning using role importance and gap size, while respecting prerequisites.",
        "Make resume-derived skill suggestions reviewable and editable by the learner.",
        "Keep example data synthetic and avoid saving uploaded resume files.",
    ]:
        _bullet(document, item)

    document.add_heading("3. Architecture and data flow", level=1)
    for item in [
        "Catalog: src/skills_catalog.py defines skills, categories, role requirements, prerequisites, and learning-resource descriptions.",
        "Data generation: src/generate_data.py creates 500 reproducible synthetic profiles and writes CSV/JSON files under data/.",
        "Input: the dashboard accepts a synthetic profile, manual levels, or an uploaded resume. Resume text is extracted in memory and never written to disk by the app.",
        "Matching: src/matching.py normalizes skills, calculates weighted role coverage, and computes TF-IDF cosine-similarity signals.",
        "Recommendations: src/recommend.py orders weak/missing skills and inserts required foundations before dependent skills.",
        "Presentation: app/dashboard.py displays match results, charts, evidence, pathway reasons, and PDF/CSV downloads.",
        "API: api/main.py exposes the catalog and analysis operations as validated HTTP endpoints.",
        "Evaluation: src/evaluate.py compares role-ranking methods on generated profiles and writes docs/evaluation_results.md.",
    ]:
        _numbered(document, item)

    document.add_heading("4. Synthetic data and catalog", level=1)
    document.add_paragraph(
        "The catalog contains 75 skills spanning areas such as programming, data, cloud, security, frontend, backend, mobile, and quality assurance. Ten sample roles specify required skill IDs, importance weights, and target levels. Skill entries may also specify prerequisite IDs and learning-resource descriptions."
    )
    document.add_paragraph(
        "The generator cycles evenly through the 10 target roles, so the 500-profile default contains 50 synthetic profiles per target role. It generates skill levels with a seeded NumPy random generator. Levels for skills required by a profile's assigned role are sampled around that role's target; other skills are sampled around a lower baseline. Free-text summaries mention several stronger required skills, without stating the assigned role name."
    )
    document.add_paragraph(
        "The fixed seed supports repeatable demos and tests. These generated distributions and assigned roles are design assumptions, not observations about students or labor-market requirements."
    )

    document.add_heading("5. Resume processing", level=1)
    document.add_paragraph(
        "src/resume_parser.py accepts PDF, DOCX, and TXT byte content. The dashboard limits files to 5 MB. PDF pages must contain selectable text; scanned images are not OCR-processed. DOCX paragraphs and table cells are read. Extracted text is capped at 50,000 characters for inference."
    )
    document.add_paragraph(
        "The parser searches the text for catalog skill names and selected aliases such as 'sklearn' for Scikit-learn and 'k8s' for Kubernetes. For each recognized skill it displays the nearby sentence as evidence. Wording heuristics suggest an initial level: proficiency words suggest level 4, action verbs suggest level 3, learning/coursework language suggests level 1, and an unqualified mention suggests level 2."
    )
    document.add_paragraph(
        "These levels are deliberately editable. The parser does not verify claims, assess actual proficiency, or establish that a skill was used in a professional context. Users should review each suggestion before analysis."
    )

    document.add_heading("6. Matching methods", level=1)
    document.add_heading("6.1 Weighted skill coverage", level=2)
    document.add_paragraph(
        "For each required skill i, let w_i be role importance, s_i the learner level, and r_i the required level. Coverage is capped at the requirement so extra levels do not over-credit one skill."
    )
    formula = document.add_paragraph()
    formula.alignment = WD_ALIGN_PARAGRAPH.CENTER
    formula_run = formula.add_run("Match (%) = 100 * sum(w_i * min(s_i / r_i, 1)) / sum(w_i)")
    formula_run.bold = True
    formula_run.font.size = Pt(11)
    formula_run.font.color.rgb = RGBColor.from_string(TEAL)
    document.add_paragraph(
        "A level of 0 is classified as missing; a positive level below the role requirement is weak; a level at or above the requirement is matched. The output also includes the role's total importance weight and per-skill details."
    )
    document.add_heading("6.2 TF-IDF and role ranking", level=2)
    document.add_paragraph(
        "TF-IDF converts text into weighted token vectors, and cosine similarity compares their direction. The code creates vectors for catalog skills and role descriptions, then compares them to the learner's summary and assessed skill names. For a selected-role analysis, text similarity is displayed separately and does not change the weighted match percentage."
    )
    document.add_paragraph(
        "For role ranking, baseline uses weighted coverage, TF-IDF uses text similarity, and hybrid combines them as 0.70 * baseline + 0.30 * TF-IDF. TF-IDF is a lexical baseline; matching words does not guarantee matching meaning or transferable competence."
    )

    document.add_heading("7. Explainable learning pathway", level=1)
    document.add_paragraph(
        "The pathway begins with direct role requirements that are below their target. A deficient skill's prerequisites may be added when the learner has them below level 2. Added foundations target level 2 and inherit the dependent role skill's importance. A topological ordering places prerequisite candidates before their dependents; among currently available candidates, priority is importance weight multiplied by gap size."
    )
    _add_table(
        document,
        ["Recommendation type", "Example explanation"],
        [
            ["Direct role gap", "Required for Data Analyst (weight 5); you are at level 1, need level 4."],
            ["Prerequisite", "Foundation for Scikit-learn, which is required for ML Engineer; learn this foundation first."],
        ],
    )
    document.add_paragraph(
        "Every pathway item includes the current level, target level, gap size, importance, prerequisite list, status, reason, and a short learning-resource description."
    )

    document.add_heading("8. Application interfaces", level=1)
    document.add_heading("Streamlit dashboard", level=2)
    for item in [
        "Upload resume: extract catalog skills, show evidence, edit suggested levels, and analyze.",
        "Synthetic student: select one of the generated demo profiles and analyze it for a role.",
        "Enter skill levels: manually rate role skills and prerequisites from 0 to 5.",
        "Results: weighted match, separate text similarity, radar chart, gap bar chart, reason panel, and ordered pathway.",
        "Exports: PDF analysis report and CSV learning pathway.",
    ]:
        _bullet(document, item)
    document.add_heading("FastAPI service", level=2)
    _add_table(
        document,
        ["Route", "Purpose"],
        [
            ["GET /roles", "List roles and their requirements."],
            ["GET /skills", "List skills, categories, prerequisites, and resources."],
            ["POST /analyze", "Accept skill levels and a target role; return score, gaps, and pathway."],
            ["POST /recommend-roles", "Return baseline, TF-IDF, and hybrid role rankings."],
        ],
    )
    document.add_paragraph(
        "API requests are JSON skill-level assessments; file uploads are currently handled by the Streamlit dashboard rather than an API upload endpoint. Pydantic validates skill values and role names."
    )

    document.add_heading("9. Evaluation results", level=1)
    document.add_paragraph("The generated report evaluates all 500 profiles:")
    _add_table(
        document,
        ["Method", "Top-1 accuracy", "Top-3 accuracy"],
        [
            ["Baseline", "0.910", "0.990"],
            ["TF-IDF", "0.530", "0.914"],
            ["Hybrid", "0.926", "0.996"],
        ],
    )
    document.add_paragraph(
        "The hybrid scored slightly above the baseline for this synthetic dataset. These values are not estimates of real-world job fit: the profiles and target roles come from the same constructed catalog assumptions."
    )
    document.add_paragraph(
        "The missing-skill precision and recall are both 1.000 because evaluation defines truth as a required skill at level 0 and the detector uses the same level-0 rule. This checks implementation consistency, not independent predictive accuracy. Meaningful external validation would need independently labeled profiles and reviewed job requirements."
    )

    document.add_heading("10. Tests and quality checks", level=1)
    document.add_paragraph(
        "The test suite covers deterministic synthetic generation, weighted score boundaries, missing-versus-weak classification, prerequisite ordering, API endpoints and invalid inputs, resume extraction from TXT/DOCX/PDF, empty/unsupported files, and readable PDF output. The last recorded full suite run had 15 passing tests."
    )

    document.add_heading("11. Limitations and responsible use", level=1)
    for item in [
        "The profiles and target-role labels are synthetic and do not describe real learners.",
        "The 75-skill, 10-role catalog is small and cannot represent all industries, regions, seniority levels, or employer requirements.",
        "Role weights, target levels, prerequisites, and resume level suggestions are simplified assumptions.",
        "TF-IDF recognizes lexical overlap and does not interpret context, proficiency, or transferable skills deeply.",
        "Scanned PDFs are unsupported without OCR. Resume levels are suggestions and must be reviewed.",
        "The weighted percentage is not a probability, credential, diagnosis, hiring prediction, or automated decision.",
        "The evaluation's synthetic labels and rule-based gap metrics are not independent validation.",
    ]:
        _bullet(document, item)

    document.add_heading("12. Demo walkthrough", level=1)
    talk_track = document.add_paragraph()
    talk_track.paragraph_format.left_indent = Inches(0.25)
    talk_track.paragraph_format.right_indent = Inches(0.25)
    talk_track_run = talk_track.add_run(
        '"Skill Gap Studio compares a learner\'s skills with a selected role profile. It explains the weighted score, identifies specific gaps, and orders learning suggestions around prerequisites. Resume-derived levels are suggestions for the learner to review, not verified qualifications."'
    )
    talk_track_run.italic = True
    talk_track_run.font.color.rgb = RGBColor.from_string(TEAL)
    for item in [
        "Use a redacted resume or a synthetic profile; avoid projecting personal contact details.",
        "Select a target role and show the resume skill evidence.",
        "Edit one suggested skill level to demonstrate user control.",
        "Run the analysis and explain weighted match versus text similarity.",
        "Choose one missing skill and one weak skill and show how the pathway orders prerequisites.",
        "Download the CSV or PDF report. Optionally show the FastAPI docs at /docs.",
    ]:
        _numbered(document, item)

    document.add_heading("13. Demo questions and answers", level=1)
    _qa(
        document,
        "Is the score a chance of being hired?",
        "No. It is weighted coverage of the selected role's catalog requirements. It is not a probability or hiring prediction.",
    )
    _qa(
        document,
        "Does the system use AI?",
        "It uses TF-IDF and cosine similarity for text matching, plus deterministic weighted scoring and prerequisite rules. It does not use a large language model or a trained employment prediction model.",
    )
    _qa(
        document,
        "Can resume proficiency levels be trusted automatically?",
        "No. They are wording-based initial suggestions with evidence snippets. The learner can edit them, and should do so before analysis.",
    )
    _qa(
        document,
        "Why use synthetic profiles?",
        "They provide repeatable examples and known target-role labels without using real student data. Their results are illustrative only.",
    )
    _qa(
        document,
        "Why is missing-skill precision and recall perfect?",
        "The evaluation's definition of a missing skill and the detector use the same level-0 rule. This is a consistency check, not an independent model evaluation.",
    )
    _qa(
        document,
        "What would be needed before real-world use?",
        "A broader, reviewed role catalog; validated proficiency assessments; privacy and security review; human oversight; and independent evaluation with consented, representative data.",
    )

    document.add_heading("14. Run commands", level=1)
    document.add_paragraph("Run from the project root in PowerShell:")
    commands = [
        "python -m venv .venv",
        ".\\.venv\\Scripts\\Activate.ps1",
        "python -m pip install -r requirements.txt",
        "python -m src.generate_data",
        "python -m src.evaluate",
        "python -m uvicorn api.main:app --host 127.0.0.1 --port 8000",
        "streamlit run app/dashboard.py",
        "python -m pytest",
    ]
    for command in commands:
        paragraph = document.add_paragraph()
        paragraph.paragraph_format.left_indent = Inches(0.2)
        run = paragraph.add_run(command)
        run.font.name = "Consolas"
        run.font.size = Pt(9)

    document.add_paragraph(
        "Keep the API and dashboard running in separate terminals. The API docs are available at http://127.0.0.1:8000/docs."
    )
    document.core_properties.title = "AI-Based Student Skill Gap Analysis System - Demo Report"
    document.core_properties.subject = "Project architecture, algorithms, evaluation, limitations, and demo preparation"
    document.core_properties.author = "Skill Gap Studio"
    document.save(OUTPUT_PATH)
    return OUTPUT_PATH


if __name__ == "__main__":
    print(f"Created {build_report()}")