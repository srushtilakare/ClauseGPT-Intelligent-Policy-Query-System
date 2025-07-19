from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os
import tempfile
import re
import google.generativeai as genai
import os
import json
# Set your Gemini API Key (you can load from env instead)
GOOGLE_API_KEY = "AIzaSyCLj1ReK7kW5rpDamsiBA5_VsQHH2_1e_k"
genai.configure(api_key=GOOGLE_API_KEY)

# Load Gemini Pro model
gemini_model = genai.GenerativeModel("models/gemini-1.5-flash")


app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model and FAISS index
model = SentenceTransformer('all-MiniLM-L6-v2')
dimension = 384  # embedding size
index = faiss.IndexFlatL2(dimension)
clause_metadata = []  # Store clauses and their info


@app.get("/")
def read_root():
    return {"message": "FastAPI backend is running!"}


@app.post("/analyze")
async def analyze_pdf(file: UploadFile = File(...)):
    try:
        # Save the uploaded PDF temporarily
        suffix = os.path.splitext(file.filename)[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # Extract text from PDF
        reader = PdfReader(tmp_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        os.remove(tmp_path)

        # --- Phase 1: Rule-Based Clause Matching ---
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

        # --- Phase 2: Semantic Embedding ---
        # 1. Split text into potential clauses
        possible_clauses = re.split(r'\n+|\. ', text)  # Split on line breaks or periods

        embedded_clauses = []
        for clause in possible_clauses:
            cleaned = clause.strip()
            if cleaned and len(cleaned) > 20:  # Filter short/noisy lines
                embedded_clauses.append(cleaned)

        # 2. Embed and add to FAISS
        embeddings = model.encode(embedded_clauses)
        index.add(np.array(embeddings))  # Store in FAISS
        clause_metadata.extend(embedded_clauses)  # Store corresponding text

        return {
            "matched_clauses": matched_clauses,
            "embedded_clause_count": len(embedded_clauses)
        }

    except Exception as e:
        return {"error": str(e)}
from pydantic import BaseModel

# Define input schema for search
class SearchRequest(BaseModel):
    query: str
    top_k: int = 5  # Default top 5 matches

@app.post("/search")
async def search_clauses(request: SearchRequest):
    try:
        if index.ntotal == 0:
            return {"error": "No data available for search. Please analyze a PDF first."}

        query_embedding = model.encode([request.query])
        distances, indices = index.search(np.array(query_embedding), request.top_k)

        results = []
        for i in indices[0]:
            if i < len(clause_metadata):  # Safety check
                results.append(clause_metadata[i])

        return {
            "query": request.query,
            "results": results
        }

    except Exception as e:
        return {"error": str(e)}
    
class QueryParseRequest(BaseModel):
    user_input: str

@app.post("/parse_query")
async def parse_query_with_gemini(request: QueryParseRequest):
    try:
        prompt = f"""
You are an intelligent assistant that extracts structured health insurance data from user queries.
Input: "{request.user_input}"

Return a JSON object with:
- age (integer)
- gender (Male/Female/Other)
- treatment (string)
- duration (string, e.g., "3-month policy")

Example:
Input: "46M, knee surgery, 3-month policy"
Output:
{{
  "age": 46,
  "gender": "Male",
  "treatment": "knee surgery",
  "duration": "3-month policy"
}}
"""

        # Generate from Gemini
        response = gemini_model.generate_content(prompt)
        response_text = response.text.strip()

        # ✅ Sanitize the response (remove ```json ... ```)
        json_string = re.sub(r"```json|```", "", response_text).strip()

        # ✅ Convert to Python dictionary
        structured_data = json.loads(json_string)

        return {"structured_info": structured_data}

    except Exception as e:
        return {"error": str(e)}