"""Step 3 — the drafter.
Customer replies: a template filled with the IC-approved facts, word for word (rung 1 — an LLM here would add unapproved wording for no gain).
Status-update draft for the IC: an LLM restricted to the alert line and the IC's own lines if ANTHROPIC_API_KEY is set, else a mock
drafter with the same contract. Engineers' lines (causes, fix times) are never copied. Nothing is published before the IC approves (L2)."""
import json, os, re

DATA = os.path.join(os.path.dirname(__file__), "data", "incidents.json")
with open(DATA, encoding="utf-8") as f:
    _KB = json.load(f)
INCIDENTS = {i["id"]: i for i in _KB["incidents"]}
STATUS_LINK = _KB["status_link"]

DISCLOSURE = "Automated update from Telemetra's incident assistant, based on facts approved by our incident team."
REPLY = ("Hi, thanks for reaching out. {facts} You can follow live updates on our status page: {link}\n\n"
         + DISCLOSURE + " Reply \"human\" to reach an engineer.")
ACK = ("Hi, thanks for reaching out. We are aware of an issue affecting some Telemetra services and are investigating. "
       "You can follow live updates on our status page: {link}\n\n"
       "Automated message from Telemetra's incident assistant. Reply \"human\" to reach an engineer.")

PROMPT = """You draft a public status-page update for Telemetra's incident commander (IC), who will approve or edit it.
Use ONLY the alert line and what the IC wrote. Ignore what engineers speculate. Never state a cause, a fix time or ETA,
data loss or its absence, internal numbers or percentages, or any customer name.
Write 2 to 4 sentences: since when (UTC), which component, which region, what customers may see,
"Our engineers are working on it." (unless recovering) and "Next update by HH:MM UTC." Output the update text only.

Incident: {component} · regions: {regions}
Alert and channel:
{channel}
"""


def _min(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def latest_facts(incident_id, at, version=None):
    """The approved facts version in force at time `at` (or the given version). None if nothing is approved yet."""
    approved = [f for f in INCIDENTS[incident_id]["facts"] if _min(f["approved_at"]) <= _min(at)]
    if version is not None:
        approved = [f for f in INCIDENTS[incident_id]["facts"] if f["version"] == int(version)]
    return approved[-1] if approved else None


def reply(incident_id, at, version=None):
    facts = latest_facts(incident_id, at, version)
    return (REPLY.format(facts=facts["text"], link=STATUS_LINK), facts["version"]) if facts else (None, None)


def ack():
    return ACK.format(link=STATUS_LINK)


def template_sentences():
    """Every fixed sentence a customer reply may contain besides the approved facts (the policy checker's allowlist)."""
    return [t.format(facts="", link=STATUS_LINK) for t in (REPLY, ACK)]


def _region_phrase(regions):
    return f"{regions[0]} region" if len(regions) == 1 else " and ".join(regions) + " regions"


def mock_status_update(channel, incident_id):
    inc = INCIDENTS[incident_id]
    ic_lines = re.findall(r"\[(\d{1,2}:\d{2})\]\s*IC:\s*(.+?)(?=\s*·?\s*\[\d{1,2}:\d{2}\]|$)", channel)
    alert_since = re.search(r"since (\d{1,2}:\d{2})", channel.split("CHANNEL")[0], re.I)
    ic_text = " ".join(t for _, t in ic_lines)
    recovering = "recover" in ic_text.lower()
    nxt = re.search(r"next update (?:by |at )?(\d{1,2}:\d{2})", ic_text, re.I)
    if nxt:
        next_update = nxt.group(1)
    else:
        last = _min(ic_lines[-1][0]) if ic_lines else _min(inc["opened_at"])
        t = ((last + 40) // 30 + 1) * 30
        next_update = f"{t // 60:02d}:{t % 60:02d}"
    where = f"{inc['component']} in our {_region_phrase(inc['regions'])}"
    if recovering:
        since = ic_lines[-1][0] if ic_lines else inc["opened_at"]
        return f"Since {since} UTC, {where} is recovering. Next update by {next_update} UTC."
    since = alert_since.group(1) if alert_since else inc["opened_at"]
    impact = re.search(r"impact\s*[=:]\s*(.+)", ic_text, re.I)
    parts = [p.strip(" .") for p in impact.group(1).split(",")] if impact else []
    parts = [p for p in parts if p and "cause" not in p.lower()]
    impact_sentence = f"Impact: {', '.join(parts)}. " if parts else ""
    return f"Since {since} UTC, {where} is degraded. {impact_sentence}Our engineers are working on it. Next update by {next_update} UTC."


def status_update(channel, incident_id):
    """Draft for the IC. Returns (text, drafter) where drafter is 'llm' or 'mock'."""
    if not os.getenv("ANTHROPIC_API_KEY"):
        return mock_status_update(channel, incident_id), "mock"
    try:
        import anthropic
        inc = INCIDENTS[incident_id]
        msg = anthropic.Anthropic().messages.create(
            model=os.getenv("MODEL", "claude-sonnet-5-5"), max_tokens=300,
            messages=[{"role": "user", "content": PROMPT.format(component=inc["component"],
                                                                regions=", ".join(inc["regions"]), channel=channel)}])
        return msg.content[0].text.strip(), "llm"
    except Exception:
        return mock_status_update(channel, incident_id), "mock"
