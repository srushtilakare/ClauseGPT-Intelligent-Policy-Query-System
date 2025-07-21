import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("google_api_key"))
model = genai.GenerativeModel("gemini-pro")

def ask_gemini(clause_text, question):
    try:
        prompt = f"""You are a legal assistant. Analyze the following clause from a contract and answer the user's question.

Clause:
\"\"\"
{clause_text}
\"\"\"

Question: {question}
"""
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("Gemini Error:", e)
        return "❌ Gemini API error. Try again."
