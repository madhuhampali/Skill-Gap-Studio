"""Create downloadable PDF reports for explainable skill-gap analysis."""

from __future__ import annotations

from collections.abc import Iterable
import textwrap


def _escape_pdf_text(value: str) -> str:
    ascii_text = value.encode("latin-1", "replace").decode("latin-1")
    return ascii_text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _fallback_pdf(title: str, lines: list[str]) -> bytes:
    """Build a basic Helvetica PDF when fpdf2's optional native stack is blocked."""
    wrapped = [line for value in [title, *lines] for line in (textwrap.wrap(value, width=88) or [""])]
    pages = [wrapped[index : index + 48] for index in range(0, len(wrapped), 48)] or [[]]
    objects: dict[int, bytes] = {
        1: b"<< /Type /Catalog /Pages 2 0 R >>",
        3: b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    }
    page_ids: list[int] = []
    for page_index, page_lines in enumerate(pages):
        page_id = 4 + page_index * 2
        content_id = page_id + 1
        page_ids.append(page_id)
        commands = ["BT", "/F1 16 Tf", "50 790 Td", f"({_escape_pdf_text(page_lines[0] if page_lines else title)}) Tj", "/F1 10 Tf", "0 -28 Td", "14 TL"]
        start = 1 if page_lines else 0
        commands.extend(f"({_escape_pdf_text(line)}) Tj T*" for line in page_lines[start:])
        commands.append("ET")
        stream = "\n".join(commands).encode("latin-1")
        objects[page_id] = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 842] "
            f"/Resources << /Font << /F1 3 0 R >> >> /Contents {content_id} 0 R >>"
        ).encode("ascii")
        objects[content_id] = f"<< /Length {len(stream)} >>\nstream\n".encode("ascii") + stream + b"\nendstream"
    objects[2] = (
        f"<< /Type /Pages /Kids [{' '.join(f'{page_id} 0 R' for page_id in page_ids)}] "
        f"/Count {len(page_ids)} >>"
    ).encode("ascii")

    output = bytearray(b"%PDF-1.4\n")
    offsets = [0] * (max(objects) + 1)
    for object_id in sorted(objects):
        offsets[object_id] = len(output)
        output.extend(f"{object_id} 0 obj\n".encode("ascii") + objects[object_id] + b"\nendobj\n")
    xref_offset = len(output)
    output.extend(f"xref\n0 {len(offsets)}\n0000000000 65535 f \n".encode("ascii"))
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.extend(
        f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("ascii")
    )
    return bytes(output)


def create_pdf_report(title: str, lines: Iterable[str]) -> bytes:
    """Render a compact ASCII-safe report and return its PDF bytes."""
    report_lines = list(lines)
    try:
        from fpdf import FPDF
    except (ImportError, OSError):
        return _fallback_pdf(title, report_lines)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(0, 10, title.encode("latin-1", "replace").decode("latin-1"))
    pdf.ln(3)
    pdf.set_font("Helvetica", size=10)
    for line in report_lines:
        safe_line = str(line).encode("latin-1", "replace").decode("latin-1")
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(0, 6, safe_line)
    output = pdf.output()
    return bytes(output)
