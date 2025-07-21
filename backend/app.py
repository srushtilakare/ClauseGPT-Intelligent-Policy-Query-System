# backend/app.py

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import fitz  # PyMuPDF
import google.generativeai as genai

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable not set")

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

clauses_text = ""

@app.route('/upload', methods=['POST'])
def upload_pdf():
    global clauses_text

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    text = ""
    with fitz.open(path) as doc:
        for page in doc:
            text += page.get_text()

    clauses_text = text
    return jsonify({'message': 'File uploaded and processed successfully'}), 200

@app.route('/ask', methods=['POST'])
def ask_question():
    global clauses_text

    data = request.get_json()
    question = data.get('question')

    if not clauses_text:
        return jsonify({'error': 'No clauses extracted yet'}), 400

    response = model.generate_content(f"Given this contract:\n\n{clauses_text}\n\nAnswer the following:\n{question}")
    return jsonify({'answer': response.text.strip()}), 200

if __name__ == '__main__':
    app.run(debug=True)
