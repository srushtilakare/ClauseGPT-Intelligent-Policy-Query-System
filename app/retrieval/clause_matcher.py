import re
from typing import List

KEYWORDS = ['cover', 'covered', 'coverage', 'benefit', 'exclusion', 'waiting', 'maternity', 'surgery', 'knee', 'donor']


def keyword_score(text: str, question: str) -> float:
    # simple heuristic: keyword overlap
    t = text.lower()
    q = question.lower()
    score = 0.0
    for w in KEYWORDS:
        if w in t and w in q:
            score += 0.3
        elif w in t:
            score += 0.05
    # numeric matches: years/months/percent
    m = re.findall(r"(\d+\s*(?:years|year|months|month|%)?)", text.lower())
    if m:
        score += 0.2
    return min(score, 1.0)


def match_clauses(hits: List[dict], question: str):
    """Return hits augmented with heuristic matching score."""
    out = []
    for h in hits:
        meta = h['meta']
        base = h['score']
        text = meta.get('text', '')
        kscore = keyword_score(text, question)
        combined = max(base, kscore)
        out.append({
            'id': meta.get('id'),
            'doc_id': meta.get('doc_id'),
            'chunk_index': meta.get('chunk_index'),
            'text': text,
            'score': combined
        })
    # sort by score
    out = sorted(out, key=lambda x: x['score'], reverse=True)
    return out