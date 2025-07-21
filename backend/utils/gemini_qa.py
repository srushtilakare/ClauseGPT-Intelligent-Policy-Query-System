import google.generativeai as genai
import os

GOOGLE_API_KEY = "AIzaSyAIjNVZqSy_quccahpOg0VVbkpZmWrSAoM"
genai.configure(api_key=GOOGLE_API_KEY)

def ask_gemini(query, context):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(f"Context:\n{context}\n\nUser Query:\n{query}")
    return response.text.strip()
