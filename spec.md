# spec.md — executable spec · Incident Messenger (P3) · v2

> Session 3 skeleton (v0), turned into v2 after the first prototype run (Session 4, `evals/report_v0.md`). What Claude Code (or Cursor) reads to build the prototype.
> Same content as `03_product_brief.md`, with nothing left vague: inputs, outputs, edge cases, fallbacks, done.
> **[v2]** = changed since the skeleton because of what we built · **[v2 · miss M#]** = a line written because the eval found a miss (`evals/report_v0.md` §2). A miss that is not in the spec comes back.

## problem
During a platform incident at Telemetra (DevOps / observability SaaS, 5,000 accounts), support receives ~1,500 tickets, 70 % asking "is it down?", and the first public update arrives ~40 minutes after the first ticket. The agent attaches incoming tickets to the right incident, drafts the status update for the incident commander (IC), and answers the cluster with IC-approved facts only. It never states an unapproved cause, ETA, scope of impact or data loss, and never mentions another customer.

## user_workflow
```
- trigger  : error_rate event | incident_declared event | ticket spike (≥ N similar tickets in 10 min)
             -> cluster {incident_id, component, regions, opened_at, keywords}                  (L4, rule)
- category : ticket text -> status | impact | cause_credit | unrelated, confidence           (L4 for routing only)
             [v2] TF-IDF on words + characters, logistic regression, 240 synthetic training tickets (prototype/router.py)
- attach   : ticket + open clusters -> {incident_id | none, confidence, candidates}         (L4 if confidence ≥ 0.80, else L1 → human queue)
             [v2] rung 1, not embeddings: open window = opened_at − 15 min … resolved_at + 60 min; region must match;
             confidence 0.85 + 0.12 × min(1, component words / 2); a vague ticket 0.82 if it is the only incident in the
             region, 0.60 if two; 0.40 if its symptom points to another incident (prototype/attach.py)
- route    : category + attach + ticket -> auto_reply | rule_ack | human_queue | human_queue_top   (rule, prototype/route_rule.py)
             [v2] order: security/secret → top · not English → human · unrelated → human · two incidents → human ·
             none / region not affected → human · incident resolved → top · person-only topic → human ·
             confidence < 0.80 → human · no approved facts → rule_ack · else auto_reply
- draft    : alerts + incident channel (never tickets) -> status_update draft                (L2 — IC approves or edits)
             [v2] the LLM reads the alert line and the IC's own lines only; without an API key the mock drafter keeps the same contract
             [v2 · miss M1] the draft turns the IC's impact note into what customers may see, in a full sentence ("Dashboards of EU
             accounts may show missing or delayed data."), never pastes the note ("Impact: EU ingestion, dashboards delayed."), and takes
             "since" only from an explicit time — the time of the IC's message is not when recovery started. The mock drafter cannot do
             this (0 of 3 drafts publishable, report_v0): the LLM drafter, or a "what customers may see" sentence per component in
             incidents.json, is needed before a pilot (P3-12, P3-13, P3-24)
- approve  : IC -> approved_facts {component, regions, text, next_update_at, version}       (person)
- reply    : approved_facts + recipient account region + status link -> templated reply     (L2 first message of the cluster, L4 follow-ups)
             [v2] template text fixed in prototype/draft.py; the facts version in force at the ticket's minute, word for word
- check    : reply -> pass | block(reason)                                                  (rule, runs on every outgoing text)
             [v2] customer reply: every sentence must be a template sentence or an approved fact (allowlist);
             IC draft: no cause, ETA, data-loss claim, internal percentage; everything: no other customer's name, no secret
- hand_over: category in {impact, cause_credit} or unrelated or low confidence -> human queue with a summary (L1)
- resolve  : IC marks resolved -> resolution notice draft (L2) -> sent to cluster (L4)
- switch   : [v2] ON · SUGGEST_ONLY (drafts shown, nothing sendable — L1) · OFF (humans only, auto-acknowledge rule)
             — one click, owner Head of Support (prototype/switch.py, tested with prototype/rollback_drill.py)
             [v2 · not built] a per-segment position (region, plan), so the harm threshold can stop one segment without the others
```

## io_contracts
```
ticket         : {id, account_id, account_region, plan, text, created_at, language}
cluster        : {incident_id, component, regions[], opened_at, keywords[], status: open|resolved}
attach_result  : {ticket_id, incident_id | null, confidence: 0..1, ambiguous, region_not_affected, resolved, candidates[]}   [v2]
route_result   : {decision: auto_reply|rule_ack|human_queue|human_queue_top, reason, attached_incident}                 [v2]
approved_facts : {incident_id, version, text, component, regions[], approved_by, approved_at}
reply          : {ticket_id, text, facts_version, status_link, disclosure: true, policy: pass|block, reason, trust, sendable}  [v2]
switch         : {position: ON|SUGGEST_ONLY|OFF, set_by, reason, at}                                                    [v2]
```

## edge_cases
- two incidents open at the same time → attach to the one whose component/region matches; if both match within 0.10 confidence → human queue, never merge
- ticket from an account whose region is not affected → no incident reply; human queue with "region not affected" note
- **[v2 · miss M3]** a word is evidence of a component only when it describes a symptom: "status page", "page" in "your status page", "dashboard" in a link are not symptoms. If the ticket's symptom words match an incident **outside** the account's region better than the incident inside it, or the in-region incident's approved facts say that component "is not affected", do **not** attach → human queue "region not affected" (P3-08: a US dashboard gap got the US alerting facts because of the words "status page")
- **[v2 · miss M2]** a question about other customers or the extent of the incident ("is X down too?", "how many customers are affected?", "is it everyone in the EU?") asks for the **scope of impact**, which only the IC may state → **person only**, by a rule in step 2, not left to the router (P3-34 got an automatic reply; P3-17 reached a person only because the router guessed "impact"). Both graders overruled the first label of these two cases; they were re-labelled on 17 November 2026
- **[v2 · red row A05]** a ticket that names a component no open incident covers ("traces"), or a time outside the incident window ("yesterday"), is not a vague ticket: never attach it through the only-incident-in-the-region rule → human queue (`evals/adversarial_v0.csv`: a question about yesterday's traces got today's ingestion facts)
- **[v2 · held-out v1]** the "only incident in the region" rule attaches a vague ticket only if the router says status with confidence ≥ 0.5 and the ticket names no component of another product: a CPU chart or a broken export button is not a vague outage question (P3-53, P3-54 — same family as A05, false clustering)
- **[v2 · held-out v1]** data-impact questions are person only whatever their words: "still being stored", "gaps", "thin data", "did we lose" — add them to the rule and 20 such tickets to the router's training data (P3-75 got an automatic reply); the data-impact check runs before the "resolved → top" rule (P3-85, a data question after the resolution, went to the top of the queue as a reopen)
- **[v2 · held-out v1]** component words match their plurals and suffixes ("429s"); an incident resolved less than 60 minutes ago is a candidate only for an explicit symptom match (a reopen), never for a vague ticket (P3-56 was not answered, P3-77 lost its top priority)
- **[v2 · held-out v1]** "breach" alone is not a security word: an "SLA breach" is a credit question (P3-76 went to the top of the queue as a security case)
- **[v2 · open decision]** a ticket that arrives before the incident is opened: the label says a person checks it (P3-79), the prototype sends the auto-acknowledgement because of its 15-minute window. The Head of Support decides; until then the label holds
- unrelated urgent ticket during an incident (security report, billing lockout, other bug) → never attached; top of the human queue
- no approved facts yet → no reply; the auto-acknowledge rule sends the status link only
- ticket asks ETA, root cause, data loss or SLA credits → human queue (person only), agent attaches a summary; **[v2]** a mixed question ("is it down, and when will it be fixed?") counts as person only
- **[v2]** ticket matching an incident resolved less than 60 minutes ago → top of the human queue (possible reopen or recurrence), alert the support lead
- language not English → human queue (WON'T: multilingual)
- personal data or secrets in the ticket (API key, hostname) → redacted before any model call
- ticket mentions another customer → reply never repeats it
- **[v2 · miss M4]** approved facts whose "Next update by HH:MM" time has passed are not sent unchanged: the agent reminds the IC at that time and answers with the auto-acknowledgement until a new version is approved (P3-21: at 19:38 the reply still promised an update by 19:30)

## fallbacks
- attach confidence below 0.80 → human queue, with the candidate incident and the score
- policy block → no sending; show the reason to the IC / support engineer; **[v2]** for the IC's draft the blocked words are highlighted and Approve is disabled until they are edited
- IC has not approved within 10 min → remind the IC; never publish on time-out
- agent paused or down → auto-acknowledge rule (status link + "we are investigating"); **[v2]** SUGGEST_ONLY keeps drafts visible but nothing is sendable
- **[v2]** LLM API down or no key → mock status-update drafter, same inputs and contract; customer replies never use a model

## done_criteria
- ≥ 63 % of "is it down?" status tickets in the eval-set correctly attached AND reply judged sendable as is by two graders
- **[v2 · miss M5 — the criterion itself]** report the criterion two ways: on all status tickets of the eval-set (the set oversamples status tickets that must go to a person: only 16 of the 33 in v0 should get an automatic reply, so the stratified ceiling is 48 %), and on the status tickets that should get an automatic reply, re-weighted to the 90 % answerable share of `02_sizing.xlsx`
- zero unapproved cause / ETA / impact / data-loss statements, zero other-customer mentions, zero merged incidents, **[v2]** zero replies sent on a ticket that must go to a person (a floor, not a target: one miss blocks the release)
- attach precision ≥ 90 % (H1 in 01_problem_statement.md)

## out_of_scope
Proactive messages to accounts that have not written · "is my data affected?" answers · root cause, ETA, SLA credits, compensation · multilingual replies · publishing without the IC · LLM-written customer replies · customers' own outages · **[v2]** cause speculation copied from the incident channel (from the user research, brief v2).

## eval_set
`evals/eval_set_v0.csv` — 50 cases (Assignment 4); `evals/eval_set_v1.csv` — 100 cases (Assignment 5). Inputs synthetic and label-free when generated; labels by hand before the run. Split by incident, never by ticket; never tuned on. Grading guideline: `evals/judge_rubric.md`.
