"""Streamlit demo surface — the IC console (prototype v1). Run from the repo root: streamlit run prototype/app.py
Demo rows come from data/demo_inputs.csv, never from the eval-set. Nothing is sent: buttons only show a toast."""
import html, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import pandas as pd
import streamlit as st
import attach, draft, pipeline, policy, switch

HERE = os.path.dirname(__file__)
st.set_page_config(page_title="Incident Messenger — IC console v1", layout="wide")

st.sidebar.title("Incident Messenger")
page = st.sidebar.radio("Prototype v1", ["IC console", "Eval"])
position = st.sidebar.radio("⏻ Switch", switch.POSITIONS, index=switch.POSITIONS.index(switch.get()),
                            help="ON: as designed · SUGGEST_ONLY: drafts shown, nothing sendable (L1) · OFF: humans only, auto-acknowledge rule")
if position != switch.get():
    switch.set_position(position, who="IC console", reason="set from the sidebar")
    st.sidebar.success(f"Switch set to {position}")
st.sidebar.caption("Streamlit = demo surface. One file, one session, no auth. Fake data only.")


def highlight(text):
    """Blocked words in red inside the draft (brief v2: the IC hesitated on a greyed-out Approve button)."""
    out, last = [], 0
    for s, e, why in policy.blocked_spans(text):
        if s < last:
            continue
        out += [html.escape(text[last:s]), f"<mark style='background:#f8c4c4' title='{html.escape(why)}'>{html.escape(text[s:e])}</mark>"]
        last = e
    return "".join(out + [html.escape(text[last:])])


if page == "IC console":
    demo = pd.read_csv(os.path.join(HERE, "data", "demo_inputs.csv"), dtype=str).fillna("")
    scenario = st.radio("Scenario", ["Morning · INC-01 + INC-02", "Evening · INC-03 + INC-04"], horizontal=True)
    rows = demo[demo["received_at_utc"] < "12:00"] if scenario.startswith("Morning") else demo[demo["received_at_utc"] >= "12:00"]
    now = rows["received_at_utc"].max()
    st.title("IC console")
    rail = st.columns(len(attach.open_incidents(now)) or 1)
    for col, inc in zip(rail, attach.open_incidents(now)):
        facts = draft.latest_facts(inc["id"], now)
        col.metric(f"{inc['id']} · {inc['component']}", " + ".join(inc["regions"]),
                   f"facts v{facts['version']} approved {facts['approved_at']}" if facts else "no approved facts yet", delta_color="off")
    state, results = {}, []
    for _, r in rows.sort_values("received_at_utc").iterrows():
        o = pipeline.run_one(r.to_dict(), state, position=switch.get())
        att = attach.score(r["input"], r["account_region"], r["received_at_utc"]) if r["input_type"] == "ticket" else None
        o["mismatch"] = bool(att and att["incident_id"] and not next(c for c in att["candidates"] if c["incident_id"] == att["incident_id"])["hits"])
        results.append((r, o))
    cluster, person, drafts = st.tabs(["Cluster — auto-handled", "Needs a person", "Status update draft"])
    with cluster:
        sent = [(r, o) for r, o in results if o["decision"] in pipeline.SENT]
        st.caption(f"{len(sent)} tickets · first message of each cluster: L2 (you approve once) · follow-ups: L4 on approved facts")
        for r, o in sent:
            flag = " · ⚠ words do not match the incident component" if o["mismatch"] else ""
            with st.expander(f"{r['id']} · {r['account_region']} · {r['plan']} · {o['incident']} ({o['attach_conf']}) → {o['decision']}{flag}"):
                st.write(r["input"])
                st.caption(f"routed {o['category']} ({o['cat_conf']}) · {o['trust']} · policy {o['policy']}")
                st.text(o["text"])
                if st.button("Not this incident", key=f"no-{r['id']}"):
                    st.toast(f"{r['id']} moved to the human queue")
        if sent:
            st.subheader("First reply of the cluster")
            st.write(f"Recipients: {len(sent)} tickets — 3 samples above, full list on demand.")
            st.button("✅ Approve the first reply", type="primary", disabled=switch.get() != "ON", on_click=lambda: st.toast("Approved — nothing is really sent in v1"))
    with person:
        queue = sorted([(r, o) for r, o in results if o["decision"].startswith("human")], key=lambda x: x[1]["decision"] != "human_queue_top")
        for r, o in queue:
            st.markdown(f"**{'🔴 TOP · ' if o['decision'] == 'human_queue_top' else ''}{r['id']} · {r['account_region']} · {r['plan']}** — {o['reason']}")
            st.caption(r["input"])
    with drafts:
        for r, o in results:
            if o["decision"] != "draft_for_IC":
                continue
            st.caption(f"{r['id']} · {o['incident']} · {o['reason']} · {o['trust']}")
            edited = st.text_area("Draft — edit before approving; the guardrail re-checks every edit", o["text"], key=f"ed-{r['id']}")
            status, why = policy.check(edited, kind="status_update")
            st.markdown(highlight(edited), unsafe_allow_html=True)
            if status == "block":
                st.error(f"Blocked: {why} — edit the highlighted words before approving.")
            st.button("✅ Approve and publish", key=f"ap-{r['id']}", type="primary",
                      disabled=status == "block" or switch.get() != "ON", on_click=lambda: st.toast("Approved — nothing is really published in v1"))
            with st.expander("Incident channel (input)"):
                st.write(r["input"])
else:
    st.title("Eval — evals/")
    import evals
    files = sorted(f for f in os.listdir(os.path.join(evals.ROOT, "evals")) if f.startswith("eval_set_") and f.endswith(".csv"))
    choice = st.selectbox("Eval-set (frozen — never tune while looking at it)", files)
    out, m = evals.run(os.path.join(evals.ROOT, "evals", choice), quiet=True)
    c = st.columns(4)
    c[0].metric("Sendable (proxy)", f"{m['sendable_proxy']}/{m['status_tickets']}", f"criterion {evals.CRITERION:.0%}", delta_color="off")
    c[1].metric("Attach precision", f"{m['attach_precision']:.2f}", "floor 0.90", delta_color="off")
    c[2].metric("Sent on human-only", m["sent_on_human_only"], "must be 0", delta_color="off")
    c[3].metric("Merged incidents", m["merged_incidents"], "must be 0", delta_color="off")
    st.dataframe(out.drop(columns=["output", "input"]), use_container_width=True, hide_index=True)
