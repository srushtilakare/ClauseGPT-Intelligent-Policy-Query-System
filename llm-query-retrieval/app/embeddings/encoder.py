from sentence_transformers import SentenceTransformer
import numpy as np
from ..core.config import settings

class Encoder:
    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.EMBED_MODEL
        print('Loading encoder model:', self.model_name)
        self.model = SentenceTransformer(self.model_name)

    def embed(self, texts: list) -> np.ndarray:
        if not isinstance(texts, list):
            texts = [texts]
        embs = self.model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        return embs