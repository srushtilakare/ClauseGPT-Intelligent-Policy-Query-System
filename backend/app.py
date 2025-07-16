### 📁 File: backend/app.py

import sys
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import json

# Add parser folder to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'parser')))

from pdf_parser import extract_text_from_pdf
from docx_parser import extract_text_from_docx

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def split_into_clauses(text):
    lines = text.split('\n')
    clauses = []
    for i, line in enumerate(lines):
        line = line.strip()
        if line and len(line) > 20:
            clauses.append({
                "clause_id": f"C{i+1}",
                "text": line
            })
    return clauses

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    if file.filename.endswith('.pdf'):
        raw_text = extract_text_from_pdf(filepath)
    elif file.filename.endswith('.docx'):
        raw_text = extract_text_from_docx(filepath)
    else:
        return jsonify({"error": "Unsupported file format"}), 400

    clauses = split_into_clauses(raw_text)

    with open("extracted_clauses.json", "w") as f:
        json.dump(clauses, f, indent=2)

    return jsonify(clauses)

if __name__ == '__main__':
    app.run(debug=True)


### 📁 File: backend/parser/__init__.py

# leave this file empty, it just tells Python this folder is a package


### 📁 File: backend/parser/pdf_parser.py

import fitz  # PyMuPDF

def extract_text_from_pdf(filepath):
    doc = fitz.open(filepath)
    text = "\n".join([page.get_text() for page in doc])
    return text


### 📁 File: backend/parser/docx_parser.py

from docx import Document

def extract_text_from_docx(filepath):
    doc = Document(filepath)
    text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    return text
