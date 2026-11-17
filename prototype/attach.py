"""Step 1b — attach a ticket to an open incident (rung 1: rules on three signals — time window, account region, component words).
The brief planned pretrained embeddings (rung 3); we start one rung lower and climb only if the eval-set says the rules fail.
Two incidents within MARGIN of each other -> ambiguous: never merged, a person decides (spec.md edge case)."""
import json, os, re

DATA = os.path.join(os.path.dirname(__file__), "data", "incidents.json")
WINDOW_BEFORE = 15     # minutes: customers often write just before the incident is opened
AFTER_RESOLVED = 60    # minutes: a ticket shortly after resolution still matches (possible reopen)
MARGIN = 0.10
INCIDENTS = None


def load(path=DATA):
    global INCIDENTS
    with open(path, encoding="utf-8") as f:
        INCIDENTS = json.load(f)["incidents"]
    return INCIDENTS


def minutes(hhmm):
    h, m = hhmm.strip().split(":")
    return int(h) * 60 + int(m)


def regions_of(account_region):
    """'EU + US' -> {'EU', 'US'}."""
    return {r.strip() for r in re.split(r"[+,/]", str(account_region)) if r.strip() in {"EU", "US"}}


def keyword_hits(text, keywords):
    t = text.lower()
    return sorted(k for k in keywords if re.search(r"(?<![a-z0-9])" + re.escape(k) + r"(?![a-z0-9])", t))


def open_incidents(received_at):
    if INCIDENTS is None:
        load()
    t = minutes(received_at)
    return [i for i in INCIDENTS
            if minutes(i["opened_at"]) - WINDOW_BEFORE <= t
            and (i["resolved_at"] is None or t <= minutes(i["resolved_at"]) + AFTER_RESOLVED)]


def score(text, account_region, received_at):
    """Return {incident_id | None, confidence, ambiguous, region_not_affected, resolved, candidates}."""
    regions = regions_of(account_region)
    cands = []
    for inc in open_incidents(received_at):
        hits = keyword_hits(text, inc["keywords"])
        resolved = inc["resolved_at"] is not None and minutes(received_at) > minutes(inc["resolved_at"])
        cands.append({"incident_id": inc["id"], "region_ok": bool(regions & set(inc["regions"])),
                      "hits": hits, "resolved": resolved})
    any_hits = any(c["hits"] for c in cands)
    n_region_ok = sum(c["region_ok"] for c in cands)
    for c in cands:
        if not c["region_ok"]:
            c["confidence"] = 0.0                                  # the account cannot be affected
        elif c["hits"]:
            c["confidence"] = round(0.85 + 0.12 * min(1, len(c["hits"]) / 2), 2)   # region + component words
        elif not any_hits:
            c["confidence"] = 0.82 if n_region_ok == 1 else 0.60   # vague ticket: enough only if one incident fits
        else:
            c["confidence"] = 0.40                                 # the symptom points to another incident
    cands.sort(key=lambda c: c["confidence"], reverse=True)
    best = cands[0] if cands and cands[0]["confidence"] > 0 else None
    second = cands[1] if len(cands) > 1 else None
    ambiguous = bool(best and second and second["confidence"] > 0.5 and best["confidence"] - second["confidence"] < MARGIN)
    region_not_affected = best is None and any(c["hits"] and not c["region_ok"] for c in cands)
    return {"incident_id": best["incident_id"] if best and not ambiguous else None,
            "confidence": best["confidence"] if best else 0.0,
            "ambiguous": ambiguous, "region_not_affected": region_not_affected,
            "resolved": bool(best and best["resolved"]), "candidates": cands}
