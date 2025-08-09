from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Any

class RunRequest(BaseModel):
    documents: HttpUrl
    questions: List[str]

class Clause(BaseModel):
    clause_id: str
    text: str
    score: float

class Condition(BaseModel):
    type: str
    value: Any
    clause_id: Optional[str] = None

class AnswerResponse(BaseModel):
    question: str
    answer: str
    decision: str  # covered | not_covered | conditional | unknown
    conditions: List[Condition]
    supporting_clauses: List[Clause]
    rationale: str

class RunResponse(BaseModel):
    answers: List[AnswerResponse]
