from docx import Document

def extract_docx_text(path: str):
    doc = Document(path)
    parts = []
    for i, p in enumerate(doc.paragraphs, start=1):
        t = p.text.strip()
        if t:
            parts.append({'idx': i, 'text': t})
    return parts