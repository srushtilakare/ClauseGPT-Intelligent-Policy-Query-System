import fitz  # PyMuPDF

def extract_clauses_from_pdf(file_bytes):
    doc = fitz.open("pdf", file_bytes)
    text = ""
    for page in doc:
        text += page.get_text()

    # Naive clause matcher (can be improved)
    clauses = ["termination", "confidentiality", "governing law", "payment terms", "liability", "intellectual property"]
    extracted = {}
    for clause in clauses:
        if clause in text.lower():
            start = text.lower().find(clause)
            snippet = text[start:start+300]
            extracted[clause] = snippet
    return extracted
