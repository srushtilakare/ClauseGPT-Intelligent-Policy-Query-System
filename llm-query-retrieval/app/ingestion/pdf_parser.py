import pdfplumber
from typing import List

def extract_pdf_text_bytes(b: bytes):
    import io
    out = []
    with pdfplumber.open(io.BytesIO(b)) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            out.append({'page': i, 'text': text})
    return out

def extract_pdf_text(path: str):
    out = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            out.append({'page': i, 'text': text})
    return out