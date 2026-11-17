"""Step 2 — the routing rule (rung 1), spec.md user_workflow + edge_cases. Decides what happens to a ticket; nothing here is learned.
Order matters: the cheapest safe exit first. Below THRESHOLD, or anything a person must answer, goes to the human queue."""
import re

THRESHOLD = 0.80
PERSON_ONLY = {"impact", "cause_credit"}
SECURITY = re.compile(r"\b(security|breach|leak(ed)?|api key|secret|token|password|credentials?|vulnerab\w*|exposed|revoke)\b", re.I)
ETA = re.compile(r"\b(eta|when will (it|this|you|the)|how long (will|until|before)|time to (fix|resolution))\b", re.I)
DATA_LOSS = re.compile(r"\b(lose|lost|losing|loss of)\b.{0,40}\b(data|metrics|logs|events|points)\b|\bdata loss\b|\bbackfill", re.I)
MONEY_OR_CAUSE = re.compile(r"\b(sla|credits?|refund|compensation|contract|penalt\w*|root cause|what caused|why did|post-?mortem|rca)\b", re.I)


def decide(category, attach, ticket, facts_available):
    """Return (decision, reason, attached_incident). Decisions: auto_reply · rule_ack · human_queue · human_queue_top."""
    text, inc = ticket["text"], attach["incident_id"]
    if SECURITY.search(text):
        return "human_queue_top", "security or secret in the ticket: never attached, top of the queue", None
    if str(ticket.get("language", "en")).strip().lower() != "en":
        return "human_queue", "not English (multilingual replies are a WON'T)", inc
    if category == "unrelated":
        return "human_queue", "not about the incident: never attached, never closed with the cluster", None
    if attach["ambiguous"]:
        ids = " and ".join(c["incident_id"] for c in attach["candidates"][:2])
        return "human_queue", f"matches two open incidents ({ids}): never merged", None
    if inc is None:
        return "human_queue", "region not affected" if attach["region_not_affected"] else "no open incident matches", None
    if attach["resolved"]:
        return "human_queue_top", f"{inc} already resolved: possible reopen or recurrence, alert the support lead", inc
    if category in PERSON_ONLY or ETA.search(text) or DATA_LOSS.search(text) or MONEY_OR_CAUSE.search(text):
        return "human_queue", "person only: impact, cause, ETA, data loss or credits (agent attaches a summary)", inc
    if attach["confidence"] < THRESHOLD:
        return "human_queue", f"attach confidence {attach['confidence']:.2f} below {THRESHOLD} (candidate {inc})", None
    if not facts_available:
        return "rule_ack", "no approved facts yet: the auto-acknowledge rule sends the status link only", inc
    return "auto_reply", "status question, attached, approved facts available", inc
