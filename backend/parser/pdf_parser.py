import fitz  # PyMuPDF

def extract_text_from_pdf(filepath):
    doc = fitz.open(filepath)
    text = "\n".join([page.get_text() for page in doc])
    return text
