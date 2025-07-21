from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import fitz  # PyMuPDF
from werkzeug.utils import secure_filename
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Gemini API setup
genai.configure(api_key="YOUR_GEMINI_API_KEY")  # Replace with your Gemini key
model = genai.GenerativeModel("gemini-pro")

# Define common legal clauses
CLAUSES = [
    "termination", "confidentiality", "governing law", "liability",
    "intellectual property", "payment", "indemnification", "dispute resolution"
]

def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text.lower()

def detect_clauses(text):
    found = []
    for clause in CLAUSES:
        if clause in text:
            found.append(clause)
    return found

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    extracted_text = extract_text_from_pdf(filepath)
    clauses = detect_clauses(extracted_text)

    return jsonify({"clauses": clauses, "text": extracted_text})

@app.route("/ask", methods=["POST"])
def ask_gemini():
    data = request.get_json()
    question = data.get("question")
    context = data.get("context")

    if not question or not context:
        return jsonify({"error": "Missing question or context"}), 400

    prompt = f"Context:\n{context}\n\nQuestion:\n{question}"
    try:
        response = model.generate_content(prompt)
        return jsonify({"answer": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    return "ClauseGPT API is running!"

if __name__ == "__main__":
    app.run(debug=True)
