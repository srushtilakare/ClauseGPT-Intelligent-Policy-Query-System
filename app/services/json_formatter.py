from ..models.request_models import AnswerResponse, Clause, Condition
from typing import Dict, Any, List

def format_answer(raw: Dict[str,Any]) -> AnswerResponse:
    # Raw keys: question, answer, decision, conditions, supporting_clauses, rationale
    supporting = []
    for c in raw.get("supporting_clauses", []):
        supporting.append(Clause(clause_id=c.get("clause_id", c.get("clause_id", c.get("id",""))),
                                 text=c.get("text",""),
                                 score=float(c.get("score",0.0))))
    conditions = []
    for c in raw.get("conditions", []):
        conditions.append(Condition(type=c.get("type","unknown"),
                                    value=c.get("value"),
                                    clause_id=c.get("clause_id")))
    return AnswerResponse(
        question=raw.get("question",""),
        answer=raw.get("answer",""),
        decision=raw.get("decision","unknown"),
        conditions=conditions,
        supporting_clauses=supporting,
        rationale=raw.get("rationale","")
    )
