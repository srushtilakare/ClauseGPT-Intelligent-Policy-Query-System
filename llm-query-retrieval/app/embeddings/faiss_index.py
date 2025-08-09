import faiss
import numpy as np
import os
import json
from typing import List, Tuple

class FaissIndex:
    def __init__(self, dim: int, path: str = './data/faiss.index'):
        self.dim = dim
        self.path = path
        self.index = faiss.IndexFlatIP(dim)  # inner product on L2-normalized vectors
        self.meta = []  # list of metadata dicts: {'id':..., 'text':..., ...}

    def add(self, vectors: np.ndarray, metas: list):
        # vectors shape: (N, dim)
        if vectors.ndim == 1:
            vectors = vectors.reshape(1, -1)
        faiss.normalize_L2(vectors)
        self.index.add(vectors)
        self.meta.extend(metas)

    def search(self, query_vectors: np.ndarray, top_k: int = 5) -> list:
        if query_vectors.ndim == 1:
            query_vectors = query_vectors.reshape(1, -1)
        faiss.normalize_L2(query_vectors)
        D, I = self.index.search(query_vectors, top_k)
        results = []
        for row_idx in range(I.shape[0]):
            row = []
            for col, idx in enumerate(I[row_idx]):
                if idx == -1:
                    continue
                row.append({'meta': self.meta[idx], 'score': float(D[row_idx, col])})
            results.append(row)
        return results

    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        faiss.write_index(self.index, self.path)
        meta_path = self.path + '.meta.json'
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(self.meta, f, ensure_ascii=False, indent=2)

    def load(self):
        if os.path.exists(self.path):
            self.index = faiss.read_index(self.path)
            meta_path = self.path + '.meta.json'
            if os.path.exists(meta_path):
                with open(meta_path, 'r', encoding='utf-8') as f:
                    self.meta = json.load(f)