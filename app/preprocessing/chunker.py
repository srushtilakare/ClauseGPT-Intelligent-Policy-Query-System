import nltk
nltk.download('punkt', quiet=True)
from nltk.tokenize import sent_tokenize
from ..core.config import settings


def sentence_chunker(text: str, max_words: int = None, overlap: int = None):
    """Chunk by sentences, targetting max_words per chunk with overlap in words."""
    if not text:
        return []
    max_words = max_words or settings.MAX_CHUNK_WORDS
    overlap = overlap or settings.CHUNK_OVERLAP
    sents = sent_tokenize(text)
    chunks = []
    cur = []
    cur_words = 0
    for s in sents:
        w = len(s.split())
        if cur_words + w > max_words and cur:
            chunks.append(' '.join(cur).strip())
            # start new chunk with overlap
            overlap_words = []
            if overlap and overlap < cur_words:
                # take last `overlap` words
                last = ' '.join(cur).split()[-overlap:]
                overlap_words = last
            cur = overlap_words + [s]
            cur_words = len(' '.join(cur).split())
        else:
            cur.append(s)
            cur_words += w
    if cur:
        chunks.append(' '.join(cur).strip())
    return chunks