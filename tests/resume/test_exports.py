from io import BytesIO

import fitz
from docx import Document

from hireme_ai.resume.docx_renderer import render_docx
from hireme_ai.resume.pdf_renderer import render_pdf
from hireme_ai.schemas.candidate import CandidateProfile
from hireme_ai.schemas.resume import GeneratedResumeBullet


def test_pdf_selectable_text() -> None:
    data = render_pdf(
        CandidateProfile(name="Demo"),
        [GeneratedResumeBullet(text="Applied Python.", source_fact_ids=["F1"])],
    )
    doc = fitz.open(stream=data, filetype="pdf")
    assert "Applied Python" in "".join(page.get_text() for page in doc)


def test_docx_generated() -> None:
    data = render_docx(
        CandidateProfile(name="Demo"),
        [GeneratedResumeBullet(text="Applied Python.", source_fact_ids=["F1"])],
    )
    doc = Document(BytesIO(data))
    assert any("Applied Python" in p.text for p in doc.paragraphs)
