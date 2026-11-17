"""Step 4 — the guardrail checker (rung 1: rules). Runs on every outgoing text; a blocked text is shown with its reason and never sent.
Customer replies: every sentence must be a template sentence or an IC-approved fact (allowlist). Status-update drafts: no cause,
no ETA, no data-loss claim, no internal percentage. Everything: no other customer's name, no secret. The model is not trusted with this."""
import csv, os, re

ACCOUNTS = os.path.join(os.path.dirname(__file__), "data", "accounts.csv")
with open(ACCOUNTS, encoding="utf-8") as f:
    CUSTOMER_NAMES = [r["name"] for r in csv.DictReader(f)]

SECRET = re.compile(r"\b(?:tm|sk|pk|ghp|xox[bp])_[A-Za-z0-9_\-]{6,}\b|\bAKIA[0-9A-Z]{16}\b")
RULES = [
    (r"\b(caused by|due to|because|root cause|the cause is|deploy\w*|roll(ed|ing)?[ -]?back|release|migration|config(uration)? change"
     r"|kafka|database|cache|dns|certificate|disk|bug|upgrade|patch)\b", "states a cause"),
    (r"\b(eta|fixed (in|by|within|soon)|resolved (in|by|within|soon)|back to normal (in|by|within)|should be (fixed|ok|okay|back|resolved|done)"
     r"|within \d+ ?(min|mins|minutes|h|hours?)|in (about |around )?\d+ ?(min|mins|minutes|h|hours?))\b", "gives an ETA"),
    (r"\b(no data (was |is |will be |has been )?lost|data (is|was|are) (safe|lost|intact)|data loss|backfill\w*|will be recovered"
     r"|nothing (was|is) lost)\b", "makes a data-loss statement"),
    (r"\d+(\.\d+)?\s?%", "quotes an internal number"),
]


def redact(text):
    """Remove secrets customers paste into tickets — before any model call (spec.md edge case)."""
    return SECRET.sub("[REDACTED]", text)


def _sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text) if s.strip()]


def check(text, kind="reply", allowed=None, recipient=None):
    """Return ('pass', '') or ('block', reason). kind: reply (to a customer) · status_update (draft for the IC)."""
    if not text:
        return "pass", ""
    if SECRET.search(text):
        return "block", "contains a secret"
    for name in CUSTOMER_NAMES:
        if name != recipient and re.search(r"\b" + re.escape(name) + r"\b", text, re.I):
            return "block", f"names another customer ({name})"
    if kind == "reply":
        allowed_set = {s for a in (allowed or []) for s in _sentences(a)}
        for s in _sentences(text):
            if s not in allowed_set:
                return "block", f"sentence not in the approved facts: \"{s[:60]}\""
        return "pass", ""
    for pat, reason in RULES:
        m = re.search(pat, text, re.I)
        if m:
            return "block", f"{reason} (\"{m.group(0)}\")"
    return "pass", ""


def blocked_spans(text):
    """(start, end, reason) of every blocked word — the IC console highlights them inside the draft (brief v2, usability test)."""
    spans = [(m.start(), m.end(), reason) for pat, reason in RULES for m in re.finditer(pat, text, re.I)]
    spans += [(m.start(), m.end(), "names another customer") for n in CUSTOMER_NAMES for m in re.finditer(r"\b" + re.escape(n) + r"\b", text, re.I)]
    return sorted(spans)
