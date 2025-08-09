import io, requests, uuid
from fastapi import APIRouter, HTTPException
from typing import List
from ..models.request_models import RunRequest, RunResponse
from ..services.embeddings import Encoder, FaissWrapper
from ..services.parser import parse_query
from ..services.logic_eval import evaluate
from ..services.json_formatter import format_answer
from ..core.config import settings
from ..services import clause_matching

router = APIRouter()

# Initialize encoder and index (singleton for process)
_encoder = Encoder(model_name=settings.EMBED_MODEL)
_DIM = _encoder.model.get_sentence_embedding_dimension()
_faiss = FaissWrapper(dim=_DIM, path=settings.FAISS_INDEX_PATH)

# In-memory map for chunk id -> text/meta
CHUNK_STORE = {}  # key: chunk_id, value: {"text":..., "doc_id":..., "meta": {...}}


def simple_chunk_text(text: str, max_words: int = 250, overlap: int = 50) -> List[str]:
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = words[i:i+max_words]
        chunks.append(" ".join(chunk))
        i += max_words - overlap
    return chunks

@router.post("/api/v1/hackrx/run", response_model=RunResponse)
def hackrx_run(payload: RunRequest):
    # download the document url
    try:
        resp = requests.get(str(payload.documents), timeout=20)
        resp.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not fetch document: {e}")

    # Save bytes and try PDF first
    raw_bytes = resp.content

    # Minimal PDF extraction using pdfplumber
    text_pages = []
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(raw_bytes)) as pdf:
            for page in pdf.pages:
                txt = page.extract_text() or ""
                text_pages.append(txt)
    except Exception:
        # If not PDF or pdfplumber fails, treat whole as text
        text_pages = [raw_bytes.decode(errors='ignore')]

    # Build chunks and index them
    all_chunks = []  # list of (chunk_id, text)
    for pno, page_text in enumerate(text_pages):
        chunks = simple_chunk_text(page_text, max_words=settings.MAX_CHUNK_TOKENS, overlap=settings.CHUNK_OVERLAP_TOKENS)
        for i, c in enumerate(chunks):
            chunk_id = f"doc::page{pno}::chunk{i}::{str(uuid.uuid4())[:8]}"
            CHUNK_STORE[chunk_id] = {"text": c, "doc_id": "doc1", "page": pno, "chunk_no": i}
            all_chunks.append((chunk_id, c))

    if not all_chunks:
        raise HTTPException(status_code=400, detail="No text extracted from document.")

    # Embed chunks in batches to avoid memory blow up
    texts = [c for _, c in all_chunks]
    ids = [cid for cid, _ in all_chunks]
    embeddings = _encoder.embed(texts)
    metas = [{"text": t, "doc_id": "doc1", "page": idx // 1000, "chunk_no": idx} for idx, t in enumerate(texts)]
    _faiss.add(embeddings, ids, metas)
    _faiss.save()

    results = []
    for q in payload.questions:
        parsed = parse_query(q)
        q_emb = _encoder.embed([q])
        hits = _faiss.search(q_emb, top_k=settings.TOP_K)
        # Convert hits to list of dicts with fetched text
        retrieved = []
        for hid, score in hits:
            meta = CHUNK_STORE.get(hid) or _faiss.id_to_meta.get(hid) or {"text": ""}
            retrieved.append({"id": hid, "text": meta.get("text",""), "score": score})

        # Evaluate
        raw_answer = evaluate(q, parsed, retrieved)
        # If deterministic engine produced no 'answer', create a short answer from top clause
        if raw_answer.get("answer","") == "":
            top = retrieved[0] if retrieved else None
            if top:
                raw_answer["answer"] = f"Based on clause {top['id']}: {top['text'][:300]}..."
        # Ensure supporting clauses include clause_id key
        for sc in raw_answer.get("supporting_clauses", []):
            if "clause_id" not in sc:
                sc["clause_id"] = sc.get("id", "")

        formatted = format_answer(raw_answer)
        results.append(formatted)

    return {"answers": results}
