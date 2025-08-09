import json
from typing import List, Dict, Any
from ..core.config import settings
from .clause_matching import simple_clause_extract, clause_contains_keywords

OPENAI_AVAILABLE = bool(settings.OPENAI_API_KEY)
if OPENAI_AVAILABLE:
    import openai
    openai.api_key = settings.OPENAI_API_KEY

def deterministic_decision(question: str, parsed: Dict[str, Any], retrieved: List[Dict[str,Any]]):
    """
    A cheap deterministic decision:
      - If top clause contains keyword & has reasonable score -> covered
      - If clause explicitly denies (words 'not covered', 'exclusion') -> not_covered
      - Else conditional/unknown
    """
    keywords = parsed.get("keywords") or parsed.get("entities") or []
    top = retrieved[0] if retrieved else None
    decision = "unknown"
    conditions = []
    supporting = []
    rationale_lines = []

    for r in retrieved:
        txt = r.get("text","").lower()
        cid = r.get("id")
        sc = r.get("score", 0.0)
        supporting.append({"clause_id": cid, "text": r.get("text",""), "score": sc})
        if "not covered" in txt or "exclusion" in txt or "shall not be" in txt or "is excluded" in txt:
            decision = "not_covered"
            rationale_lines.append(f"Found exclusion language in clause {cid}")
            break

    if decision != "not_covered":
        # Check if any retrieved clause contains keywords and is positive
        for r in retrieved:
            txt = r.get("text","")
            if clause_contains_keywords(txt, keywords):
                decision = "covered"
                rationale_lines.append(f"Keyword match found in clause {r.get('id')}")
                # extract structured conditions if any:
                cond = simple_clause_extract(txt)
                if cond:
                    conditions.append({**cond, "clause_id": r.get("id")})
                break

    if decision == "unknown":
        decision = "conditional" if retrieved else "unknown"
        rationale_lines.append("No conclusive clause found; marking conditional/unknown.")

    return {
        "question": question,
        "answer": "",  # filled by LLM or deterministically
        "decision": decision,
        "conditions": conditions,
        "supporting_clauses": supporting,
        "rationale": " ; ".join(rationale_lines)
    }

def call_openai_decision(question: str, parsed: Dict[str,Any], retrieved: List[Dict[str,Any]]):
    """
    Call GPT-4 to produce final structured JSON (only if OPENAI available).
    We'll keep prompt minimal and pass top-k retrieved clauses.
    """
    if not OPENAI_AVAILABLE:
        return deterministic_decision(question, parsed, retrieved)

    prompt = (
        "You are an assistant that must return JSON only. Given a user question about an insurance policy, "
        "and the retrieved supporting clauses (list of id, text, score), return a JSON with keys: "
        "question, answer (one-line), decision (covered|not_covered|conditional|unknown), "
        "conditions (list of {'type', 'value','clause_id'}), supporting_clauses (list of clause objects), "
        "rationale (short explanation). Don't add extra keys.\n\n"
        f"User question: {question}\n\nRetrieved clauses:\n"
    )
    for r in retrieved:
        prompt += f"- ID: {r.get('id')}\n{r.get('text')}\nScore: {r.get('score')}\n\n"

    resp = openai.ChatCompletion.create(
        model=settings.OPENAI_MODEL,
        messages=[{"role":"system","content":"Return JSON only."},
                  {"role":"user","content":prompt}],
        temperature=0.0,
        max_tokens=400
    )
    txt = resp["choices"][0]["message"]["content"]
    try:
        parsed = json.loads(txt)
        return parsed
    except Exception:
        # fallback
        return deterministic_decision(question, parsed, retrieved)

def evaluate(question: str, parsed: Dict[str,Any], retrieved: List[Dict[str,Any]]):
    """
    Top-level entry used by endpoint.
    """
    if OPENAI_AVAILABLE:
        return call_openai_decision(question, parsed, retrieved)
    else:
        return deterministic_decision(question, parsed, retrieved)
