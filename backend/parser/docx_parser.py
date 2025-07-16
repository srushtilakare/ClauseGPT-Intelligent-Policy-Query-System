from docx import Document

def extract_text_from_docx(filepath):
    doc = Document(filepath)
    text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    return text
