"""Deterministic discount verification. All eligibility rules are enforced here in Python."""
import math
import re
from dataclasses import dataclass, field
from datetime import date

from policies import CATEGORIES, POLICY_BY_CODE
from retriever import TfidfRetriever

MAX_PRICE = 1_000_000
_retriever = TfidfRetriever()


@dataclass
class Result:
    status: str                      # ELIGIBLE | INELIGIBLE | REFUSED | INVALID_INPUT
    price: float | None = None
    discount: float = 0.0
    final_price: float | None = None
    reasons: list[str] = field(default_factory=list)   # rule outcomes (executed checks)
    warnings: list[str] = field(default_factory=list)
    evidence: list[dict] = field(default_factory=list)  # retrieved docs
    cited_ids: list[str] = field(default_factory=list)
    calculation: list[str] = field(default_factory=list)  # executed calc steps
    explanation: str = ""                                 # template text, NOT LLM output


def parse_claim(claim: str) -> dict | None:
    """Extract a claimed discount: {'type': 'percent'|'flat', 'value': float} or None."""
    if not claim:
        return None
    m = re.search(r"(\d+(?:\.\d+)?)\s*%", claim)
    if m:
        return {"type": "percent", "value": float(m.group(1))}
    m = re.search(r"(\d+(?:\.\d+)?)\s*(?:sar|riyals?|ريال)\s*(?:off|discount)?|(?:save|off)\s*(\d+(?:\.\d+)?)", claim, re.I)
    if m:
        return {"type": "flat", "value": float(m.group(1) or m.group(2))}
    return None


def _invalid(msg: str) -> Result:
    r = Result(status="INVALID_INPUT", reasons=[msg])
    r.explanation = f"Input rejected: {msg}"
    return r


def verify(price, category: str, coupon: str, claim: str = "", today: date | None = None) -> Result:
    today = today or date.today()

    # ---- 1. input validation
    try:
        price = float(price)
    except (TypeError, ValueError):
        return _invalid("Price must be a number.")
    if not math.isfinite(price) or price <= 0:
        return _invalid("Price must be a positive finite number.")
    if price > MAX_PRICE:
        return _invalid(f"Price exceeds the supported maximum of {MAX_PRICE:,} SAR.")
    if category not in CATEGORIES:
        return _invalid(f"Unsupported category '{category}'. Supported: {', '.join(CATEGORIES)}.")
    coupon = (coupon or "").strip().upper()
    if coupon and not re.fullmatch(r"[A-Z0-9]{3,20}", coupon):
        return _invalid("Coupon code must be 3-20 letters/digits only.")
    claim = (claim or "").strip()
    if len(claim) > 300:
        return _invalid("Promotional claim is too long (max 300 characters).")

    res = Result(status="REFUSED", price=round(price, 2), final_price=round(price, 2))

    # ---- 2. retrieval (evidence)
    res.evidence = _retriever.search(f"{coupon} {category} {claim}")

    claimed = parse_claim(claim)
    if claim and not claimed:
        res.warnings.append("The claim contains no recognizable discount amount; it was not compared.")

    # ---- 3. policy lookup (never invent a policy)
    if not coupon:
        res.reasons.append("No coupon code supplied; no policy can be applied.")
        res.explanation = "Refused: no coupon code was provided, so no discount is assumed."
        res.cited_ids = [e["id"] for e in res.evidence]
        return res
    pol = POLICY_BY_CODE.get(coupon)
    if pol is None:
        res.reasons.append(f"Coupon '{coupon}' matches no known policy (unsupported code).")
        res.warnings.append("Unknown coupon: no policy evidence exists, so no discount is granted.")
        res.explanation = (f"Refused: coupon '{coupon}' is not in the policy database. "
                           "No eligibility is assumed and no policy is invented.")
        res.cited_ids = [e["id"] for e in res.evidence]
        return res
    if not any(e["id"] == pol["id"] for e in res.evidence):  # always show the governing policy
        res.evidence.insert(0, {"id": pol["id"], "title": pol["title"],
                                "source_text": pol["source_text"], "score": 0.0})
    res.cited_ids = [pol["id"]]

    # ---- 4. eligibility rules
    fails = []
    if today > pol["expires"]:
        fails.append(f"Policy expired on {pol['expires']}.")
    if category in pol["excluded_categories"]:
        fails.append(f"Category '{category}' is excluded.")
    if pol["allowed_categories"] and category not in pol["allowed_categories"]:
        fails.append(f"Only valid for: {', '.join(pol['allowed_categories'])}.")
    if price < pol["min_spend"]:
        fails.append(f"Price {price:.2f} is below the minimum spend of {pol['min_spend']} SAR.")

    if fails:
        res.status = "INELIGIBLE"
        res.reasons = fails
        res.calculation = ["Eligibility failed -> discount = 0.00 SAR"]
        discount = 0.0
    else:
        res.status = "ELIGIBLE"
        res.reasons = ["All conditions satisfied (date, category, minimum spend)."]
        if pol["discount_type"] == "percent":
            raw = price * pol["value"] / 100
            discount = min(raw, pol["cap"])
            res.calculation = [f"{price:.2f} x {pol['value']}% = {raw:.2f}",
                               f"Cap {pol['cap']} SAR -> discount = min({raw:.2f}, {pol['cap']}) = {discount:.2f}"]
        elif pol["discount_type"] == "flat":
            discount = min(float(pol["value"]), price)
            res.calculation = [f"Flat discount {pol['value']} SAR -> {discount:.2f}"]
        else:
            discount = 0.0
            res.calculation = ["Free-shipping coupon: product price unchanged (discount = 0.00)"]
    discount = round(discount, 2)
    res.discount = discount
    res.final_price = round(price - discount, 2)
    res.calculation.append(f"Final price = {price:.2f} - {discount:.2f} = {res.final_price:.2f} SAR")

    # ---- 5. claim conflict check
    if claimed:
        claimed_amt = price * claimed["value"] / 100 if claimed["type"] == "percent" else claimed["value"]
        if claimed_amt > discount + 0.01:
            res.warnings.append(
                f"MISLEADING CLAIM: advertised discount ≈ {claimed_amt:.2f} SAR but policy "
                f"{pol['id']} yields {discount:.2f} SAR.")

    # ---- 6. template explanation (not an LLM)
    verdict = "eligible" if res.status == "ELIGIBLE" else "NOT eligible"
    res.explanation = (f"Coupon {coupon} is {verdict} for a {price:.2f} SAR {category} item. "
                       f"{' '.join(res.reasons)} Actual discount: {discount:.2f} SAR; "
                       f"final price: {res.final_price:.2f} SAR. Source: {pol['id']}.")
    return res
