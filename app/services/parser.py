import os, json, re
from typing import Dict, Any, List
from ..core.config import settings

OPENAI_AVAILABLE = bool(settings.OPENAI_API_KEY)

if OPENAI_AVAILABLE:
    import openai
    openai.api_key = settings.OPENAI_API_KEY

def _local_parse(query: str) -> Dict[str, Any]:
    """
    Very light-weight parser to extract:
      - intent: 'coverage' | 'definition' | 'waiting_period' | 'limit' | 'other'
      - keywords: tokens like 'knee', 'maternity', 'waiting period'
    """
    q = query.lower()
    intent = "other"
    if any(x in q for x in ["cover", "covered", "coverage", "indemnif", "pay for", "provides for"]):
        intent = "coverage"
    elif "define" in q or "what is" in q:
        intent = "definition"
    elif "waiting period" in q or "waiting" in q:
        intent = "waiting_period"
    elif any(x in q for x in ["sub-limit", "limit", "cap", "capped", "maximum", "per day", "%"]):
        intent = "limit"

    # keywords: simple nouns
    keywords = re.findall(r"\b([a-z]{3,20})\b", q)
    # reduce common stopwords (very basic)
    stop = {"what","is","the","a","an","for","this","does","policy","cover","and","or","of","in","to","be","are"}
    keywords = [k for k in keywords if k not in stop]
    return {"intent": intent, "keywords": keywords, "raw": query}

def parse_query(query: str) -> Dict[str, Any]:
    """
    If OPENAI available, call GPT-4 to return structured parse; else use local.
    """
    if not OPENAI_AVAILABLE:
        return _local_parse(query)

    # When OpenAI available: ask for JSON parse with function like output
    prompt = f"""
You are a parser. Given a user question about policy coverage, return JSON only with:
{{"intent": "...", "entities": ["knee", "surgery"], "raw": "..."}}
User question: {query}
"""
    resp = openai.ChatCompletion.create(
        model=settings.OPENAI_MODEL,
        messages=[{"role":"system","content":"You are a policy Q&A parser that returns JSON only."},
                  {"role":"user","content":prompt}],
        max_tokens=200,
        temperature=0.0
    )
    txt = resp["choices"][0]["message"]["content"]
    try:
        return json.loads(txt)
    except Exception:
        # fallback
        return _local_parse(query)
