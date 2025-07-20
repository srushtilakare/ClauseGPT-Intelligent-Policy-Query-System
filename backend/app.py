from fastapi import FastAPI, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List
import pymupdf  # Correct import for PyMuPDF
import pymupdf as fitz  # ✅ Alias it to use as `fitz`
import os
import shutil
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can limit this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Sample clause keywords
clause_keywords = [
    "termination", "confidentiality", "governing law", "payment terms", 
    "liability", "intellectual property", "warranty", "dispute resolution"
]

@app.get("/")
def read_root():
    return {"message": "FastAPI backend is running!"}

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_location, "wb") as f:
        shutil.copyfileobj(file.file, f)

    text = extract_text_from_pdf(file_location)
    matched_clauses = extract_clauses(text)

    return JSONResponse(content={"clauses": matched_clauses})

@app.post("/parse_query")
async def parse_query(request: Request):
    try:
        body = await request.json()
        query = body.get("query")
        if not query:
            return JSONResponse(content={"response": "No query received"}, status_code=400)

        # Simulated Gemini-style response (replace with actual logic)
        return JSONResponse(content={"response": f"🤖 Gemini says: The answer to your query '{query}' is under construction."})

    except Exception as e:
        return JSONResponse(content={"response": f"Error: {str(e)}"}, status_code=500)

def extract_text_from_pdf(path):
    text = ""
    with fitz.open(path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_clauses(text):
    matched = []
    for clause in clause_keywords:
        if clause.lower() in text.lower():
            matched.append(clause)
    return matched

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
