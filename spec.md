# spec.md — executable spec · Incident Messenger (P3) · skeleton v0

> Session 3 skeleton, completed in Session 4. What Claude Code (or Cursor) reads to build the prototype.
> Same content as `03_product_brief.md`, with nothing left vague: inputs, outputs, edge cases, fallbacks, done.

## problem
During a platform incident at Telemetra (DevOps / observability SaaS, 5,000 accounts), support receives ~1,500 tickets, 70 % asking "is it down?", and the first public update arrives ~40 minutes after the first ticket. The agent attaches incoming tickets to the right incident, drafts the status update for the incident commander (IC), and answers the cluster with IC-approved facts only. It never states an unapproved cause, ETA, scope of impact or data loss, and never mentions another customer.

## user_workflow
```
- trigger  : error_rate event | incident_declared event | ticket spike (≥ N similar tickets in 10 min)
             -> cluster {incident_id, component, region, opened_at}                         (L4, rule)
- attach   : ticket + open clusters -> {incident_id | none, confidence}                     (L4 if confidence ≥ 0.80, else L1 → human queue)
- category : ticket text -> status | impact | cause_credit | unrelated, confidence           (L4 for routing only)
- draft    : alerts + incident channel (never tickets) -> status_update draft                (L2 — IC approves or edits)
- approve  : IC -> approved_facts {component, region, symptom, workaround, next_update_at}   (person)
- reply    : approved_facts + recipient account region + status link -> templated reply     (L2 first message of the cluster, L4 follow-ups)
- check    : reply -> pass | block(reason)                                                  (rule, runs on every outgoing text)
- hand_over: category in {impact, cause_credit} or unrelated or low confidence -> human queue with a summary (L1)
- resolve  : IC marks resolved -> resolution notice draft (L2) -> sent to cluster (L4)
```

## io_contracts
```
ticket         : {id, account_id, account_region, text, created_at, language}
cluster        : {incident_id, component, region, opened_at, status: open|resolved}
attach_result  : {ticket_id, incident_id | null, confidence: 0..1, category, decision: auto_reply|human_queue}
approved_facts : {incident_id, version, text, component, regions[], approved_by, approved_at}
reply          : {ticket_id, text, facts_version, status_link, disclosure: true, policy: pass|block, reason}
```

## edge_cases
- two incidents open at the same time → attach to the one whose component/region matches; if both match within 0.10 confidence → human queue, never merge
- ticket from an account whose region is not affected → no incident reply; human queue with "region not affected" note
- unrelated urgent ticket during an incident (security report, billing lockout, other bug) → never attached; top of the human queue
- no approved facts yet → no reply; the auto-acknowledge rule sends the status link only
- ticket asks ETA, root cause, data loss or SLA credits → human queue (person only), agent attaches a summary
- language not English → human queue (WON'T: multilingual)
- personal data or secrets in the ticket (API key, hostname) → redacted before any model call
- ticket mentions another customer → reply never repeats it

## fallbacks
- attach confidence below 0.80 → human queue, with the candidate incident and the score
- policy block → no sending; show the reason to the IC / support engineer
- IC has not approved within 10 min → remind the IC; never publish on time-out
- agent paused or down → auto-acknowledge rule (status link + "we are investigating")

## done_criteria
- ≥ 63 % of "is it down?" status tickets in the eval-set correctly attached AND reply judged sendable as is by two graders
- zero unapproved cause / ETA / impact / data-loss statements, zero other-customer mentions, zero merged incidents
- attach precision ≥ 90 % (H1 in 01_problem_statement.md)

## out_of_scope
Proactive messages to accounts that have not written · "is my data affected?" answers · root cause, ETA, SLA credits, compensation · multilingual replies · publishing without the IC · LLM-written customer replies · customers' own outages.

## eval_set
`evals/eval_set_v0.csv` — 20 invented cases now, 200 replayed incident tickets by Session 5. Split by incident, never tuned on.
