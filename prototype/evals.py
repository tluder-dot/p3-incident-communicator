"""spec.md done_criteria on the eval-set. Never tune while looking at these rows — a row looked at while changing the code is demo data.
Run: python prototype/evals.py [evals/eval_set_v0.csv]   ->  prints the numbers and writes evals/outputs_<set>.csv (the graders' input)."""
import os, re, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(__file__))
import pandas as pd
import attach, pipeline, policy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CRITERION = 0.63          # 03_product_brief.md §7 = 90 % answerable × 70 % deflection (02_sizing.xlsx base case)
PRECISION_FLOOR = 0.90    # H1 in 01_problem_statement.md


def norm_attach(s):
    s = str(s).strip()
    if s.lower().startswith("both"):
        return "none"
    m = re.match(r"(INC-\d+)", s)
    return m.group(1) if m else "none"


def norm_action(s):
    s = str(s)
    for key, label in (("TOP", "human_queue_top"), ("human_queue_top", "human_queue_top"), ("auto-acknowledge", "rule_ack"),
                       ("rule_ack", "rule_ack"), ("draft status update", "draft_for_IC"), ("draft_for_IC", "draft_for_IC"),
                       ("update notification", "update_cluster"), ("update_cluster", "update_cluster"), ("auto_reply", "auto_reply"),
                       ("person only", "human_queue"), ("human_queue", "human_queue")):
        if key in s:
            return label
    return "?"


def expected_facts(s):
    m = re.search(r"(INC-\d+) facts v(\d+)", str(s))
    return (m.group(1), int(m.group(2))) if m else (None, None)


def violations(text, must_not):
    """Literal terms of the must_not column ('quoted' or single words like Kafka) + other customers' names + secrets, found in a sent text."""
    if not text:
        return []
    terms = re.findall(r"'([^']+)'", str(must_not))
    terms += [w for w in re.split(r"\s*·\s*|\s+or\s+", str(must_not)) if re.fullmatch(r"[A-Za-z][\w-]*", w.strip()) and w.strip().lower() not in {"any", "none"}]
    found = [t for t in terms if t and re.search(r"(?<!\w)" + re.escape(t.strip()) + r"(?!\w)", text, re.I)]
    found += [n for n in policy.CUSTOMER_NAMES if re.search(r"\b" + re.escape(n) + r"\b", text, re.I)]
    if policy.SECRET.search(text):
        found.append("a secret")
    return sorted(set(found))


def run(path=os.path.join(ROOT, "evals", "eval_set_v0.csv"), quiet=False):
    df = pd.read_csv(path, dtype=str).fillna("")
    order = sorted(range(len(df)), key=lambda i: (attach.minutes(df.loc[i, "received_at_utc"]), i))
    state, rows = {}, {}
    for i in order:                              # in time order: the first reply of each cluster is the L2 one
        r = df.loc[i]
        o = pipeline.run_one(r.to_dict(), state, position="ON")
        e_att, e_act, e_cat = norm_attach(r["expected_attach"]), norm_action(r["expected_action"]), r["expected_category"].strip()
        e_inc, e_ver = expected_facts(r["expected_output"])
        p_att = o["incident"] if o["decision"] in pipeline.SENT | {"draft_for_IC"} or o["incident"] else "none"
        is_ticket = r["input_type"].strip() == "ticket"
        sent = o["sendable"]
        facts_ok = (e_inc is None) or (o["incident"] == e_inc and o["facts_version"] == e_ver)
        bad = violations(o["text"], r["must_not"]) if sent or o["decision"] == "draft_for_IC" else []
        rows[i] = dict(
            case_id=r["case_id"], input_type=r["input_type"], received=r["received_at_utc"], segment=r["segment"],
            case_type=r["case_type"], expected_category=e_cat, routed=o["category"], cat_conf=o["cat_conf"],
            expected_attach=e_att, attached=p_att or "none", attach_conf=o["attach_conf"],
            expected_action=e_act, decision=o["decision"], expected_hand_over="yes" if r["hand_over"].strip().lower().startswith("yes") else "no",
            facts_version=o["facts_version"], policy=o["policy"], policy_reason=o["policy_reason"], violations="; ".join(bad),
            attach_ok=(e_att == (p_att or "none")), action_ok=(e_act == o["decision"]), facts_ok=facts_ok,
            category_ok=(e_cat == o["category"]) if is_ticket else None,
            proxy_sendable=bool(e_cat == "status" and is_ticket and e_act == "auto_reply" and o["decision"] == "auto_reply"
                                and e_att == o["incident"] and facts_ok and o["policy"] == "pass" and not bad),
            reason=o["reason"], trust=o["trust"], output=o["text"], input=r["input"])
    out = pd.DataFrame([rows[i] for i in range(len(df))])
    tickets = out[out["input_type"].str.strip() == "ticket"]
    status = tickets[tickets["expected_category"] == "status"]
    human_only = out[out["expected_action"].isin(["human_queue", "human_queue_top"])]
    agent_attached = tickets[tickets["decision"] == "auto_reply"]
    merged = out[(out["case_type"].str.contains("overlap")) & (out["decision"] == "auto_reply")]
    sent_out = out[out["decision"].isin(pipeline.SENT) | (out["decision"] == "draft_for_IC")]
    m = {
        "cases": len(out), "status_tickets": len(status),
        "sendable_proxy": int(status["proxy_sendable"].sum()),
        "status_expected_auto": int((status["expected_action"] == "auto_reply").sum()),
        "category_accuracy": tickets["category_ok"].mean(),
        "attach_accuracy": tickets["attach_ok"].mean(),
        "attach_precision": agent_attached["attach_ok"].mean() if len(agent_attached) else float("nan"),
        "attach_recall": (status[status["expected_attach"] != "none"]["attached"] == status[status["expected_attach"] != "none"]["expected_attach"]).mean(),
        "action_accuracy": out["action_ok"].mean(),
        "hand_over_accuracy": (out["expected_hand_over"] == out["decision"].map(lambda d: "yes" if d.startswith("human") or d == "draft_for_IC" else "no")).mean(),
        "sent_on_human_only": int(human_only["decision"].isin(pipeline.SENT).sum()),
        "merged_incidents": len(merged), "policy_blocks": int((out["policy"] == "block").sum()),
        "guardrail_violations_sent": int((sent_out["violations"] != "").sum()),
    }
    if not quiet:
        cols = ["case_id", "case_type", "expected_attach", "attached", "attach_conf", "expected_action", "decision", "routed", "policy", "proxy_sendable"]
        print(out[cols].to_string(index=False))
        p = m["sendable_proxy"] / max(1, m["status_tickets"])
        print(f"\ncases                        {m['cases']}  ({m['status_tickets']} status tickets, {m['status_expected_auto']} of them expected to get an automatic reply)")
        print(f"sendable as is (proxy)       {m['sendable_proxy']}/{m['status_tickets']} status tickets = {p:.0%}   (criterion {CRITERION:.0%}; the human-graded number is in evals/report_v0.md)")
        print(f"category accuracy            {m['category_accuracy']:.2f}")
        print(f"attach accuracy              {m['attach_accuracy']:.2f}   precision {m['attach_precision']:.2f} (H1 floor {PRECISION_FLOOR:.2f})   recall {m['attach_recall']:.2f}")
        print(f"action accuracy              {m['action_accuracy']:.2f}   hand-over accuracy {m['hand_over_accuracy']:.2f}")
        print(f"sent on human-only tickets   {m['sent_on_human_only']}   (must be 0)")
        print(f"merged incidents             {m['merged_incidents']}   (must be 0)")
        print(f"guardrail violations, sent   {m['guardrail_violations_sent']}   (must be 0)")
        print(f"policy blocks                {m['policy_blocks']}")
        misses = out[(~out["action_ok"]) | (~out["attach_ok"]) | (out["violations"] != "") | ((out["expected_category"] == "status") & (out["input_type"] == "ticket") & (out["expected_action"] == "auto_reply") & (~out["proxy_sendable"]))]
        print("\nmisses by case type:")
        for ct, n in Counter(misses["case_type"]).most_common():
            print(f"  {n} × {ct}  ({', '.join(misses[misses['case_type'] == ct]['case_id'])})")
        floor_ok = m["sent_on_human_only"] == 0 and m["merged_incidents"] == 0 and m["guardrail_violations_sent"] == 0
        print(f"\nverdict: {'PASS' if p >= CRITERION and floor_ok else 'FAIL — do not fix the code on these rows; turn each miss into a line of spec.md'}")
    name = os.path.splitext(os.path.basename(path))[0].replace("eval_set_", "")
    out.to_csv(os.path.join(ROOT, "evals", f"outputs_{name}.csv"), index=False)
    return out, m


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "evals", "eval_set_v0.csv"))
