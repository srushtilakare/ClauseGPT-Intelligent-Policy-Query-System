import re
from typing import List, Dict, Any

def simple_clause_extract(clause_text: str) -> Dict[str, Any]:
    """
    Try to find patterns like:
      - X months/years (waiting period)
      - % (discounts)
      - number of deliveries, limits (2 deliveries)
      - money amounts (INR 10000, Rs. 10000, 10000)
    """
    text = clause_text
    out = {}
    # months / years
    m = re.search(r'(\d{1,3})\s*(month|months|year|years)', text, re.I)
    if m:
        out['duration_value'] = int(m.group(1))
        out['duration_unit'] = m.group(2).lower()

    # percentages
    p = re.search(r'(\d{1,3})\s*%','%')
    # careful: simple attempt below
    p2 = re.search(r'(\d{1,3})\s*%', text)
    if p2:
        out['percentage'] = int(p2.group(1))

    # small numbers like 'two deliveries' or '2 deliveries'
    n = re.search(r'(\d{1,3})\s*(delivery|deliveries|deliverys)', text, re.I)
    if n:
        out['deliveries'] = int(n.group(1))

    # money amounts (basic)
    money = re.findall(r'(?:rs\.?|inr)?\s*[\u20B9]?\s?([\d,]+)', text, re.I)
    if money:
        out['amounts'] = money

    return out

def clause_contains_keywords(clause_text: str, keywords: List[str]) -> bool:
    q = clause_text.lower()
    return any(k.lower() in q for k in keywords)
