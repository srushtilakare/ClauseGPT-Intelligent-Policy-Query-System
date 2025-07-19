from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json
import os

# Load model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load clauses
def load_clauses(json_path="data/clause_store.json"):
    with open(json_path, "r") as f:
        data = json.load(f)
    return data["clauses"]  # assuming stored as { "clauses": [...] }

# Embed & store
def create_faiss_index(clauses):
    embeddings = model.encode(clauses)
    dim = embeddings.shape[1]
    
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))
    
    return index, embeddings, clauses

# Search
def semantic_search(index, query, clauses, top_k=5):
    query_vec = model.encode([query])
    distances, indices = index.search(np.array(query_vec), top_k)
    return [clauses[i] for i in indices[0]]
