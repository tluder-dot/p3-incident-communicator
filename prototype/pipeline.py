"""Runs the four steps on one input, in the order of spec.md user_workflow. Used by evals.py, app.py and rollback_drill.py.
Three input types: ticket (route -> rule -> reply -> check) · incident_channel (draft the status update for the IC) ·
approval_event (the IC approves a new facts version -> update notification to the cluster)."""
import os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
import router, attach, route_rule, draft, policy, switch

SENT = {"auto_reply", "rule_ack", "update_cluster"}


def allowed(at):
    """The allowlist for customer replies: the template sentences + every facts version approved by time `at`."""
    facts = [f["text"] for i in draft.INCIDENTS.values() for f in i["facts"] if draft._min(f["approved_at"]) <= draft._min(at)]
    return draft.template_sentences() + facts


def run_one(row, cluster_state=None, position=None):
    """row: {input_type, received_at_utc, input, account_region, plan, language}. cluster_state: {incident: True} once the
    cluster's first message was approved (shared across calls). Returns one dict with every intermediate result."""
    state = {} if cluster_state is None else cluster_state
    position = position or switch.get()
    kind = str(row.get("input_type") or "ticket").strip()
    at, text = str(row["received_at_utc"]).strip(), policy.redact(str(row["input"]))
    o = dict(input_type=kind, category="", cat_conf=None, incident="", attach_conf=None, decision="", reason="", text="",
             facts_version=None, policy="pass", policy_reason="", trust="", sendable=False, notify_csm=False, switch=position)

    if kind == "incident_channel":
        att = attach.score(text, row.get("account_region", ""), at)
        best = next((c for c in att["candidates"] if c["confidence"] > 0), None)
        o.update(category="status_update_draft", incident=best["incident_id"] if best else "",
                 attach_conf=best["confidence"] if best else 0.0)
        if not best:
            o.update(decision="human_queue", reason="no open incident matches the channel")
            return o
        o["text"], drafter = draft.status_update(text, best["incident_id"])
        o["policy"], o["policy_reason"] = policy.check(o["text"], kind="status_update")
        o.update(decision="draft_for_IC", reason=f"{drafter} drafter, inputs = alert + incident channel only",
                 trust="L2 — the IC approves or edits; nothing is published before")
        return o

    if kind == "approval_event":
        m = re.search(r"(INC-\d+)\s+facts\s+v(\d+)", text)
        if not m:
            o.update(decision="human_queue", reason="approval event without an incident and a version")
            return o
        o["text"], o["facts_version"] = draft.reply(m.group(1), at, version=m.group(2))
        o.update(category="status", incident=m.group(1), decision="update_cluster",
                 reason="new facts approved: update notification to every ticket of the cluster, human-queue tickets skipped",
                 trust="L4 — same content as the approved update")
    else:
        o["category"], o["cat_conf"] = router.predict(text)
        o["cat_conf"] = round(o["cat_conf"], 2)
        att = attach.score(text, row.get("account_region", ""), at)
        facts = draft.latest_facts(att["incident_id"], at) if att["incident_id"] else None
        decision, reason, inc = route_rule.decide(o["category"], att, {"text": text, "language": row.get("language", "en")}, facts is not None)
        o.update(decision=decision, reason=reason, incident=inc or "", attach_conf=att["confidence"])
        if decision == "auto_reply":
            o["text"], o["facts_version"] = draft.reply(inc, at)
            first = not state.get(inc)
            state[inc] = True
            o["trust"] = "L2 — first message of the cluster: the IC approves it once" if first else "L4 — follow-up on approved facts"
            o["notify_csm"] = str(row.get("plan", "")).strip() == "enterprise"
        elif decision == "rule_ack":
            o.update(text=draft.ack(), trust="rule — auto-acknowledge, status link only")
        else:
            o["trust"] = "person — the agent attaches a summary" if decision.startswith("human") else ""

    o["policy"], o["policy_reason"] = policy.check(o["text"], kind="reply", allowed=allowed(at))
    if o["policy"] == "block":
        o.update(decision="human_queue", reason=f"policy block: {o['policy_reason']}")

    if position == "OFF" and kind == "ticket":
        o.update(decision="rule_ack", text=draft.ack(), reason="switch OFF: humans only, the auto-acknowledge rule answers",
                 trust="rule", facts_version=None)
    elif position == "OFF":
        o.update(decision="paused", text="", reason="switch OFF: nothing is drafted or sent")
    o["sendable"] = o["decision"] in SENT and o["policy"] == "pass" and position != "SUGGEST_ONLY"
    if position == "SUGGEST_ONLY" and o["decision"] in SENT:
        o["trust"] = "L1 — switch on SUGGEST_ONLY: shown to a person, never sent"
    return o
