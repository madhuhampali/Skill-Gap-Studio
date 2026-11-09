"""Extract resume text and suggest editable skill levels without saving uploads."""

from __future__ import annotations

import re
from io import BytesIO
from pathlib import Path

from docx import Document
from pypdf import PdfReader

from src.skills_catalog import SKILLS


MAX_RESUME_BYTES = 5 * 1024 * 1024
MAX_EXTRACTED_CHARACTERS = 50_000

SKILL_ALIASES = {
    "excel": ("excel", "microsoft excel", "google sheets"),
    "power_bi": ("power bi", "powerbi"),
    "postgresql": ("postgresql", "postgres"),
    "mongodb": ("mongodb", "mongo db"),
    "scikit_learn": ("scikit-learn", "scikit learn", "sklearn"),
    "ci_cd": ("ci/cd", "continuous integration", "continuous delivery"),
    "data_visualization": ("data visualization", "data visualisation", "dashboarding"),
    "data_structures": ("data structures", "algorithms"),
    "oop": ("object-oriented programming", "object oriented programming", "oop"),
    "aws": ("aws", "amazon web services"),
    "gcp": ("gcp", "google cloud platform"),
    "azure": ("azure", "microsoft azure"),
    "rest_api": ("rest api", "restful api", "restful services"),
    "api_basics": ("api integration", "integrated apis", "api integrations"),
    "javascript": ("javascript", "js"),
    "typescript": ("typescript", "ts"),
    "nodejs": ("node.js", "nodejs"),
    "kubernetes": ("kubernetes", "k8s"),
    "nlp": ("natural language processing", "nlp"),
    "deep_learning": ("deep learning", "neural networks"),
    "ux_design": ("ux design", "user experience design"),
    "accessibility": ("web accessibility", "accessibility", "wcag"),
    "r": ("r programming", "r language", "rstudio"),
}


_LEVEL_SIGNALS = (
    (4, re.compile(r"\b(expert|advanced|proficient|senior|lead|architected|owned)\b", re.I)),
    (3, re.compile(r"\b(built|developed|implemented|designed|maintained|deployed|automated|analyzed|analysed|created|delivered|used|worked with)\b", re.I)),
    (1, re.compile(r"\b(beginner|basic|familiar|learning|coursework|training|studied|introductory)\b", re.I)),
)


def extract_resume_text(filename: str, content: bytes) -> str:
    """Extract text from a PDF, DOCX, or TXT byte payload in memory."""
    extension = Path(filename).suffix.casefold()
    if len(content) > MAX_RESUME_BYTES:
        raise ValueError("Resume exceeds the 5 MB upload limit")
    if extension == ".txt":
        raw_text = content.decode("utf-8-sig", errors="replace")
    elif extension == ".pdf":
        reader = PdfReader(BytesIO(content))
        if reader.is_encrypted:
            raise ValueError("Encrypted PDFs are not supported; upload an unlocked PDF")
        raw_text = "\n".join(page.extract_text() or "" for page in reader.pages)
    elif extension == ".docx":
        document = Document(BytesIO(content))
        paragraph_text = [paragraph.text for paragraph in document.paragraphs]
        table_text = [cell.text for table in document.tables for row in table.rows for cell in row.cells]
        raw_text = "\n".join(paragraph_text + table_text)
    else:
        raise ValueError("Upload a PDF, DOCX, or TXT resume")

    cleaned = re.sub(r"[ \t]+", " ", raw_text)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    if not cleaned:
        raise ValueError("No selectable text was found in this file")
    return cleaned[:MAX_EXTRACTED_CHARACTERS]


def _contains_alias(text: str, alias: str) -> re.Match[str] | None:
    pattern = rf"(?<!\w){re.escape(alias)}(?!\w)"
    return re.search(pattern, text, flags=re.IGNORECASE)


def _evidence_sentence(text: str, start: int, end: int) -> str:
    """Return the sentence-like span surrounding one skill mention."""
    sentence_start = max(text.rfind(".", 0, start), text.rfind("!", 0, start), text.rfind("?", 0, start), text.rfind("\n", 0, start)) + 1
    endings = [position for character in ".!?\n" if (position := text.find(character, end)) >= 0]
    sentence_end = min(endings) if endings else len(text)
    return text[sentence_start:sentence_end].strip()


def _suggest_level(evidence: str) -> tuple[int, str]:
    """Use nearby resume wording for a conservative, reviewable starting level."""
    for level, pattern in _LEVEL_SIGNALS:
        if pattern.search(evidence):
            return level, f"Suggested level {level} from wording in: {evidence}"
    return 2, f"Skill is mentioned; suggested level 2 for your review: {evidence}"


def infer_resume_skills(text: str) -> dict[str, object]:
    """Return skill mentions, suggested levels, and evidence snippets for review."""
    levels: dict[str, int] = {}
    evidence_rows: list[dict[str, object]] = []
    for skill in SKILLS:
        skill_id = skill["skill_id"]
        aliases = SKILL_ALIASES.get(skill_id, (skill["name"],))
        if skill_id not in SKILL_ALIASES:
            aliases = (skill["name"],)
        mention = next((match for alias in aliases if (match := _contains_alias(text, alias))), None)
        if mention is None:
            continue
        evidence = _evidence_sentence(text, mention.start(), mention.end())
        level, reason = _suggest_level(evidence)
        levels[skill_id] = level
        evidence_rows.append(
            {
                "skill_id": skill_id,
                "skill_name": skill["name"],
                "suggested_level": level,
                "evidence": evidence,
                "reason": reason,
            }
        )
    return {"skill_levels": levels, "evidence": evidence_rows}
