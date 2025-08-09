import os
import numpy as np
from typing import List, Tuple, Dict
from tqdm import tqdm
from ..core.config import settings

# Encoder
try:
    from sentence_transformers import SentenceTransformer
except Exception as e:
    raise RuntimeError("Please install sentence-transformers. See requirements.txt") from e

class Encoder:
    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.EMBED_MODEL
        self.model = SentenceTransformer(self.model_name)

    def embed(self, texts: List[str]) -> np.ndarray:
        # returns numpy array (N, D)
        if not texts:
            return np.empty((0, self.model.get_sentence_embedding_dimension()), dtype=np.float32)
        return self.model.encode(texts, show_progress_bar=False, convert_to_numpy=True, normalize_embeddings=True)

# FAISS Index wrapper with fallback
class FaissWrapper:
    def __init__(self, dim: int = None, path: str = None):
        self.path = path or settings.FAISS_INDEX_PATH
        self.dim = dim
        self._use_faiss = True
        self.index = None
        self.id_to_meta = {}  # id -> {"text":..., "doc_id":...}
        try:
            import faiss
            self.faiss = faiss
        except Exception:
            self._use_faiss = False
            self.faiss = None

        if self._use_faiss and dim:
            # IndexFlatIP expects normalized vectors for inner product ~= cosine
            self.index = self.faiss.IndexFlatIP(dim)

        # In-memory fallback
        self._vectors = []  # list of np arrays (not normalized necessarily)
        self._ids = []

    def add(self, vectors: np.ndarray, meta_ids: List[str], metas: List[dict]):
        """
        vectors: np.ndarray shape (N, D) already normalized
        meta_ids: list of string IDs
        metas: list of meta dicts (text, doc_id, page, chunk_no etc.)
        """
        n, d = vectors.shape
        if self._use_faiss and self.index is not None:
            # ensure dims match
            if d != self.index.d:
                # rebuild? For demo, we will not support mismatch
                raise ValueError("Dimension mismatch for FAISS index.")
            self.index.add(np.ascontiguousarray(vectors.astype('float32')))
            for mid, m in zip(meta_ids, metas):
                self._ids.append(mid)
                self.id_to_meta[mid] = m
        else:
            # fallback simply stores arrays and metadata
            for i in range(n):
                self._vectors.append(vectors[i])
            self._ids.extend(meta_ids)
            for mid, m in zip(meta_ids, metas):
                self.id_to_meta[mid] = m

    def search(self, query_vector: np.ndarray, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        query_vector: shape (1, D) normalized
        returns list of (meta_id, score)
        """
        if self._use_faiss and self.index is not None:
            D, I = self.index.search(np.ascontiguousarray(query_vector.astype('float32')), top_k)
            results = []
            for idx_score, idx_id in zip(D[0], I[0]):
                if idx_id == -1:
                    continue
                meta_id = self._ids[idx_id]
                results.append((meta_id, float(idx_score)))
            return results
        else:
            # brute force cosine similarity via dot (vectors and query already normalized)
            if len(self._vectors) == 0:
                return []
            vs = np.vstack(self._vectors).astype(np.float32)
            scores = np.dot(vs, query_vector[0].astype(np.float32))
            ranked_idx = np.argsort(-scores)[:top_k]
            return [(self._ids[i], float(scores[i])) for i in ranked_idx]

    def save(self):
        # minimal save: metadata and vectors (not a full faiss persistence)
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        try:
            if self._use_faiss and self.index is not None:
                self.faiss.write_index(self.index, self.path)
            # save metadata
            import json
            meta_path = self.path + ".meta.json"
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(self.id_to_meta, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def load_meta(self):
        import json
        meta_path = self.path + ".meta.json"
        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                self.id_to_meta = json.load(f)
                self._ids = list(self.id_to_meta.keys())
