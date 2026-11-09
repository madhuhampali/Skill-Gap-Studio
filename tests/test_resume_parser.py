from io import BytesIO

from docx import Document
from pypdf import PdfReader

from src.resume_parser import extract_resume_text, infer_resume_skills
from src.report import create_pdf_report


def _minimal_pdf(text: str) -> bytes:
    stream = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode("ascii")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    output = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, body in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{index} 0 obj\n".encode("ascii") + body + b"\nendobj\n")
    xref_offset = len(output)
    output.extend(f"xref\n0 {len(offsets)}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.extend(
        f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("ascii")
    )
    return bytes(output)


def test_txt_resume_extracts_skills_with_evidence_and_suggested_levels():
    resume = b"Developed Python services and SQL reports. Advanced experience with React."

    extracted = extract_resume_text("resume.txt", resume)
    result = infer_resume_skills(extracted)

    assert result["skill_levels"] == {"python": 3, "sql": 3, "react": 4}
    assert all(item["evidence"] for item in result["evidence"])


def test_docx_resume_extracts_paragraphs_and_tables():
    buffer = BytesIO()
    document = Document()
    document.add_paragraph("Built Python data pipelines.")
    table = document.add_table(rows=1, cols=1)
    table.cell(0, 0).text = "SQL and Tableau"
    document.save(buffer)

    extracted = extract_resume_text("resume.docx", buffer.getvalue())
    result = infer_resume_skills(extracted)

    assert "Built Python data pipelines." in extracted
    assert {"python", "sql", "tableau"}.issubset(result["skill_levels"])


def test_pdf_resume_extracts_selectable_text():
    extracted = extract_resume_text(
        "resume.pdf", _minimal_pdf("Built REST API services with FastAPI and Docker.")
    )
    result = infer_resume_skills(extracted)

    assert "FastAPI" in extracted
    assert {"rest_api", "fastapi", "docker"}.issubset(result["skill_levels"])


def test_unsupported_or_empty_resume_is_rejected():
    try:
        extract_resume_text("resume.rtf", b"some text")
    except ValueError as error:
        assert "PDF, DOCX, or TXT" in str(error)
    else:
        raise AssertionError("Expected an unsupported-format error")

    try:
        extract_resume_text("empty.txt", b" \n ")
    except ValueError as error:
        assert "No selectable text" in str(error)
    else:
        raise AssertionError("Expected an empty-text error")


def test_pdf_report_is_readable_when_generated():
    report = create_pdf_report("Resume skill gap", ["Suggested skill: Python", "Level 2 to level 4"])
    text = " ".join(page.extract_text() or "" for page in PdfReader(BytesIO(report)).pages)

    assert "Resume skill gap" in text
    assert "Suggested skill: Python" in text
