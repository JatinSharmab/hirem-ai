from io import BytesIO

from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas

from hireme_ai.schemas.candidate import CandidateProfile
from hireme_ai.schemas.resume import GeneratedResumeBullet


def render_pdf(candidate: CandidateProfile, bullets: list[GeneratedResumeBullet]) -> bytes:
    output = BytesIO()
    pdf = canvas.Canvas(output, pagesize=LETTER)
    width, height = LETTER
    y = height - 50
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, y, candidate.name)
    y -= 30
    pdf.setFont("Helvetica", 10)
    for bullet in bullets:
        for line in _wrap("• " + bullet.text, 95):
            pdf.drawString(50, y, line)
            y -= 14
            if y < 50:
                pdf.showPage()
                y = height - 50
                pdf.setFont("Helvetica", 10)
        y -= 4
    pdf.save()
    return output.getvalue()


def _wrap(text: str, width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        if len(current) + len(word) + 1 > width:
            lines.append(current)
            current = word
        else:
            current = f"{current} {word}".strip()
    if current:
        lines.append(current)
    return lines
