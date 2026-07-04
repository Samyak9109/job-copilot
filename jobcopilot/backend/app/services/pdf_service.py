"""Resume/document text extraction. PDF via pdfplumber, DOCX via python-docx."""
import io

from fastapi import HTTPException


def extract_document_text(file_bytes: bytes, filename: str) -> str:
    """Dispatch by extension. Supports .pdf and .docx."""
    name = (filename or "").lower()
    if name.endswith(".docx"):
        return extract_docx_text(file_bytes)
    return extract_pdf_text(file_bytes)


def extract_docx_text(file_bytes: bytes) -> str:
    try:
        import docx  # python-docx
    except ImportError as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail="DOCX parser not installed (pip install python-docx)") from exc
    try:
        document = docx.Document(io.BytesIO(file_bytes))
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Could not read DOCX file") from exc
    text = "\n".join(p.text for p in document.paragraphs if p.text.strip()).strip()
    if not text:
        raise HTTPException(status_code=422, detail="No extractable text found in DOCX")
    return text


def extract_pdf_text(file_bytes: bytes) -> str:
    try:
        import pdfplumber
    except ImportError as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail="PDF parser not installed") from exc

    text_parts: list[str] = []
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                if page_text.strip():
                    text_parts.append(page_text)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Could not read PDF file") from exc

    text = "\n\n".join(text_parts).strip()
    if not text:
        raise HTTPException(status_code=422, detail="No extractable text found in PDF (is it a scan?)")
    return text
