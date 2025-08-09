from ..embeddings.encoder import Encoder
from ..embeddings.faiss_index import FaissIndex
from ..preprocessing.chunker import sentence_chunker
from ..core.config import settings
import uuid

class Retriever:
    def __init__(self, encoder: Encoder, index: FaissIndex):
        self.encoder = encoder
        self.index = index

    def add_document(self, doc_id: str, text: str, metadata: dict = None):
        chunks = sentence_chunker(text)
        if not chunks:
            return []
        embs = self.encoder.embed(chunks)
        metas = []
        for i, c in enumerate(chunks):
            mid = f"{doc_id}::chunk::{i}::" + uuid.uuid4().hex[:8]
            meta = {
                'id': mid,
                'doc_id': doc_id,
                'chunk_index': i,
                'text': c,
                'metadata': metadata or {}
            }
            metas.append(meta)
        self.index.add(embs, metas)
        return metas

    def query(self, q: str, top_k: int = None):
        top_k = top_k or settings.TOP_K
        qv = self.encoder.embed([q])
        hits = self.index.search(qv, top_k)
        # hits is list-of-list per query
        return hits[0]  # single query