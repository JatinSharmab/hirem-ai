from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import pymupdf
from docx import Document

from hireme_ai.core.exceptions import ValidationError


def parse_resume_bytes(filename: str, content: bytes, max_upload_mb: int = 5) -> str:
    if len(content) > max_upload_mb * 1024 * 1024:
        raise ValidationError("Resume exceeds upload size limit")
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        if not content.startswith(b"%PDF"):
            raise ValidationError("File extension is PDF but signature is invalid")
        try:
            with pymupdf.open(stream=content, filetype="pdf") as doc:
                if doc.needs_pass:
                    raise ValidationError("Encrypted PDFs are not supported")
                if len(doc) > 50:
                    raise ValidationError("Resume must contain at most 50 pages")
                parts = []
                total = 0
                for page in doc:
                    part = page.get_text()
                    total += len(part)
                    if total > 30000:
                        raise ValidationError("Resume exceeds 30,000 text characters")
                    parts.append(part)
                text = "\n".join(parts)
        except ValidationError:
            raise
        except Exception as exc:
            raise ValidationError("Malformed or unreadable PDF") from exc
    elif suffix == ".docx":
        try:
            with ZipFile(BytesIO(content)) as archive:
                entries = archive.infolist()
                if len(entries) > 500 or sum(x.file_size for x in entries) > 20 * 1024 * 1024:
                    raise ValidationError("DOCX archive exceeds decompression limits")
                if any(x.flag_bits & 1 for x in entries):
                    raise ValidationError("Encrypted DOCX files are not supported")
            docx = Document(BytesIO(content))
            text = "\n".join(p.text for p in docx.paragraphs)
        except ValidationError:
            raise
        except Exception as exc:
            raise ValidationError("Malformed or unreadable DOCX") from exc
    else:
        raise ValidationError("Only PDF and DOCX resumes are supported")
    if len(text) > 30000:
        raise ValidationError("Resume exceeds 30,000 text characters")
    if not text.strip():
        raise ValidationError("Resume contains no extractable text")
    return text.strip()
