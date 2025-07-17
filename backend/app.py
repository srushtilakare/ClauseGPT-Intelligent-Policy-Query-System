from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PyPDF2 import PdfReader
import os
import tempfile

app = FastAPI()

# Allow CORS from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Update this if frontend is hosted elsewhere
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "FastAPI backend is running!"}

@app.post("/analyze")
async def analyze_pdf(file: UploadFile = File(...)):
    try:
        # Save the uploaded file temporarily
        suffix = os.path.splitext(file.filename)[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # Extract text from PDF
        reader = PdfReader(tmp_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""

        os.remove(tmp_path)  # Clean up temp file

        # Clause keyword matching
        clause_keywords = {
            "Termination": ["terminate", "termination", "cancel the agreement"],
            "Confidentiality": ["confidential", "non-disclosure", "privacy"],
            "Governing Law": ["jurisdiction", "governing law", "court of"],
            "Payment Terms": ["invoice", "payment due", "fee structure"],
            "Liability": ["liability", "indemnify", "responsible for"],
            "Intellectual Property": ["IP", "intellectual property", "copyright", "patent"]
        }

        matched_clauses = []
        for clause, keywords in clause_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    matched_clauses.append(clause)
                    break

        return {"clauses": matched_clauses}

    except Exception as e:
        return {"error": str(e)}
