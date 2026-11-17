# 06_07 — Experiments & operation · Team 8 · Incident Messenger (P3)

> Five sections = the five moves of Sessions 6 + 7. Every number traces to `02_sizing.xlsx` (cell named), `05_metrics.md`, `evals/report_v0.md`, the course calculator `evals/sample_size.xlsx` or the drill log `evals/rollback_tests.csv`; the few operating thresholds we set ourselves (1 minute, 10 minutes, under 2 minutes) follow from the ≤ 10-minute promise of `05_metrics.md` §4; every owner is a role of our proposal; every threshold has a clock.
> **When this protocol runs:** our memo says NO-GO at today's volume. This is the test we would run if the 12-month ticket log shows the ~2× incident volume that reopens the decision (`02_investment_memo.md` §2) — and only once spec v2 is built (M1–M4, the held-out lines, red row A05) and the floors read 0 on `evals/eval_set_v1.csv`, with at least 2 of 3 IC drafts publishable.

## §1 Prove the effect — hypothesis, unit, design

**Hypotheses** (one per business metric of `05_metrics.md` §4):

1. If we let the agent answer "is it down?" tickets with IC-approved facts in the first pilot region, then the share of those tickets closed without a person and not reopened within 48 h moves from **0 %** (today every one is answered by a person) to **at least 70 % of the answerable ones** (02_sizing, Inputs D22) by the fifth incident — without the wrong-reply rate of any segment leaving its **6 %** band (Inputs C26), and without the tickets it does not answer waiting longer for a person.
2. If the agent drafts the first status update and answers the cluster as soon as the IC approves, then the median minutes from the first ticket to the first customer-facing update move from **40** (`01_problem_statement.md`) to **≤ 10** by the fifth incident — without a single unapproved statement published.
3. If the agent answers incident tickets in the pilot region, then the yearly churn of the accounts that went through an incident stays at **8 % ± 0.5 point** (Inputs G67) at month 12 — the claim we would be wrong about if one bad reply costs more trust than many fast ones earn.

**Unit of randomisation: the region, incident by incident** — not the ticket. Inside one incident every ticket shares the same approved update, the same status page and the same first message the IC approves once: answering half of a cluster would leak the treatment to the other half (customers read the same page, the IC works the whole incident differently). A region is a cluster of accounts that our incidents already separate (`incidents.json`: EU, US).

**Design: shadow mode, then a stepped wedge by region.** Shadow mode first — replays of past incidents and the next live ones: the agent drafts, nothing is sent, we compare with what people sent (the report_v0 number, on real traffic). Then the agent goes live **one region at a time, in a random order**: each incident has a treated region and a not-yet-treated one, so the not-yet-live region is the control (before / after with a control).
**What it cannot see:** with about 5 incidents a quarter (Inputs G39) only large effects show; incident types differ between regions (an EU ingestion outage is not a US alerting delay); the IC's enthusiasm in the first weeks (novelty); and the public status page, which both regions read.

## §2 Decide before — duration and decision rule

**Smallest improvement that still justifies the agent:** the base case itself — 70 % of the answerable status tickets closed without a person (Inputs D22, i.e. 63 % of all status tickets) and a first update in ≤ 10 minutes. Below it the base case's +€1.8k a year (Decision D17) turns negative; the cheap alternative (auto-acknowledge rule + comms-lead role, `01` §7) would be enough.
**Slowest guardrail → how long we run:** the 48-hour reopen window closes fast, so incidents set the clock, not tickets: reading 5 incidents per region at about 5 incidents a quarter (Inputs G39) takes **two quarters**. Churn (12 months) is read later, outside the test, as a counter-metric.

| Input | Value | Source |
|---|---|---|
| Baseline p₀ — status tickets closed without a person, not reopened in 48 h | 0 % (every one answered by a person today) | `05_metrics.md` §1, level 4 |
| Smallest rise worth acting on | +63 points (70 % of the 90 % answerable) | 02_sizing, Inputs D18 × D22 |
| Two risks accepted (false win · missed win) | 1 in 20 · 1 in 5 | preset in the calculator |
| **Units per group** | about 9 tickets — but tickets inside one incident are not independent, so the real unit is the incident: **5 incidents per region arm** | `evals/sample_size.xlsx` |
| Volume per week | about 577 incident tickets (2,500 a month, Inputs D6) — in bursts, about 5 incidents a quarter (Inputs G39) | 02_sizing |
| **Duration actually run** | **two quarters** (5 incidents per arm); churn read at month 12 | slowest read: the incidents |

**Pre-registered segments:** region (EU · US · EU + US) · plan (self-serve · enterprise) · language (English · other) · single vs overlapping incidents (`05_metrics.md` §3).

**Decision rule, written on 17 November 2026, before the first unit:**
- **Ship** (switch the next region on) if, over ≥ 5 incidents in the live region: ≥ 70 % of the answerable status tickets closed without a person and not reopened in 48 h, median first update ≤ 10 min, attach precision ≥ 0.90 on the weekly sample, and zero floor misses.
- **Iterate** if deflection is between 50 % (the pessimistic case, Inputs C22) and 70 %, or the first update between 10 and 20 minutes (half of today's 40), with every floor intact: one more cycle on the misses (spec lines), same protocol.
- **Kill** — back to the auto-acknowledge rule and the comms-lead runbook — if deflection stays below 50 % or the first update above 20 minutes after two cycles, or attach precision falls below 0.90 twice.
- **Stop early only on the harm threshold of `governance.md`:** a wrong-reply rate above 6 % in a segment during an incident, or one unapproved statement or other-customer mention sent. Never on a good number.

## §3 Watch the four layers — monitoring and drift

| Layer | Metric (from `05_metrics.md`) | Threshold that pages someone | Clock | Owner | Tool — startup | Tool — large company |
|---|---|---|---|---|---|---|
| Infrastructure | time from IC approval to reply sent · errors of the ticketing, status-page and incident-tool APIs | a reply not sent 1 minute after approval (the ≤ 10-minute promise needs it) · any API failing for 10 minutes → switch to OFF | real time | on-call engineer (VP Engineering's team) | Cloud Run metrics · Sentry · Grafana Cloud | Cloud Monitoring → Datadog |
| Model quality | attach precision and sendable share on the weekly 5 % human sample vs the judge | precision < 0.90 (H1 floor) · human–judge agreement below the rate measured in `evals/README.md` | after every incident + weekly | support lead | Langfuse (EU cloud) | LangSmith or Langfuse self-hosted |
| Product & guardrails | replies sent on person-only tickets · unapproved statements · other-customer mentions · wrong-reply rate by segment · time to first human answer | any floor miss → page the IC at once · wrong-reply rate > 6 % in a segment (harm threshold) | during the incident, then daily | IC on duty → Head of Support | SQL table + Metabase | warehouse + Power BI |
| Business | tickets per incident · minutes to first update · cost of incident tickets · churn of incident-hit accounts | first update > 10 min on two incidents in a row · churn above 8.5 % | per incident · monthly · yearly | Head of Support + CFO | weekly query + shared sheet | finance BI dashboard |
| Paging | — | — | — | — | Slack webhook to the incident channel | PagerDuty (already the on-call tool) |

**Where our FastAPI runs:** today the four steps run inside the Streamlit console on our laptop (`prototype/app.py` — the demo surface). For a pilot: the same four steps behind a FastAPI service (`/reply`, `/draft`, `/health`) on **Google Cloud Run in europe-west1** — EU processing as `governance.md` promises, pay per request, the same Docker image from staging to production, rollback = the previous image. Secrets in the cloud secret store and `.env` locally, never in Git.

**Release path and gates:** **dev** (every commit: `python prototype/evals.py` — the floors must read 0 on the frozen set) → **staging** (every change of a rule, template, prompt, model version or the incident → component map: `eval_set_v1` + the judge; shadow mode on the next real incident; the rollback drill run by the people who press the switch) → **production region by region** (the stepped wedge of §1), each step gated by the decision rule of §2.

**First drift expected: knowledge drift** — component names, regions and products change (the freshness answer of the Session 3 audit). A new component or region that is not in an incident's signature makes tickets go unattached or, worse, attach by a stray word (the P3-08 miss, `spec.md` M3). **Signal:** the share of incident tickets with "no open incident matches" doubles from one incident to the next, and the attach-confidence histogram moves left. **What we re-run:** the frozen `evals/eval_set_v1.csv` on every change of the incident → component map, a template, a rule or the model version.

## §4 Contain the incident — trace, classes, rollback

**Trace — one OpenTelemetry trace per ticket, one span per step of `04_architecture.md`:** `request` (ticket id · received at · segment: region, plan, language · versions: rules, template, facts version, model) → `classify` (category · confidence) → `attach` (candidates · scores · matched words · decision) → `route` (decision · reason) → `draft` (template id and facts version; for IC drafts: tokens · latency) → `guardrail` (pass / block · reason) → `human_decision` (IC approved / edited · "Not this incident" · reply "human") → `send` (channel · time). Stored in Langfuse, EU region.

**Our one-page dashboard — five panels:** stat tiles with thresholds (floor misses today, attach precision on the sample, minutes to first update — am I paged?) · line over the incident (tickets per minute: auto-answered vs human queue — is the queue still growing?) · histogram of attach confidence, this incident vs the last (drift) · bars by segment (wrong-reply rate and time to first human answer, EU vs US, self-serve vs enterprise — Simpson and fairness) · worst-cases table ("Not this incident" clicks, reopens, blocks — what to fix on Monday). Built as one Streamlit tab next to the IC console.

| Class | Example on our agent | Action |
|---|---|---|
| Caught | the guardrail blocks "probably the Kafka deploy" in the IC's draft; a support engineer clicks "Not this incident" before the follow-up goes out | count it; weekly review; a spec line if it repeats |
| Sent wrong | a customer gets the v1 facts after v2 was approved; a reply goes to an account whose region was not affected (P3-08) | correcting follow-up with the right facts, apology; a spec line (M3); counted in the wrong-reply rate |
| Harmful (above the harm threshold) | an unapproved cause or "no data was lost" is sent; another customer is named; a security report is auto-closed with the cluster | switch to SUGGEST_ONLY now (OFF if it repeats) · incident report · the DPO the same day if a customer was named |
| Outage | the ticketing API is down; the pipeline crashes during an incident | automatic fallback: OFF → the auto-acknowledge rule answers, people handle the queue |

**Rollback plan**

| Field | Ours |
|---|---|
| 1 · Trigger | any harmful-class incident · wrong-reply rate > 6 % in a segment · attach precision < 0.90 on a live incident's sample · an API down for 10 minutes |
| 2 · Who decides (day / night) | by day the IC on duty or the support lead on duty; at night the on-call support lead — who informs the Head of Support (the owner) the same morning |
| 3 · The action | first SUGGEST_ONLY (drafts still shown, nothing sendable — L1); OFF if the harm repeats (humans only, the auto-acknowledge rule answers); redeploy the previous image if a release caused it |
| 4 · Time to execute | one click in the IC console, under 2 minutes — the drill takes 0.13 s of machine time |
| 5 · What people see | support: "automatic replies paused — the cluster is in your queue"; the IC: drafts still shown; customers: the auto-acknowledge reply with the status-page link; the status page is unchanged |
| 6 · Last tested | 17 November 2026 (16:47 UTC, by Till Lüder, all three positions passed) — on the prototype, our laptop being our staging; `evals/rollback_tests.csv`. Next test: before every release and every quarter |

## §5 Own the system — the five owners

| Decision | Owner (role) | Written where |
|---|---|---|
| Run an experiment on real customers | the **Head of Support** signs the protocol; the **VP Engineering** co-signs (it changes the IC's job); the **DPO** reads it before the first unit | this file §1–§2 · `governance.md` |
| Read the weekly numbers and act | the **Head of Support**, with the support lead — every Monday and after every incident | §3 |
| Press the switch (day / night) | the **IC on duty** or the **support lead on duty** by day; the **on-call support lead** at night | §4 · `governance.md` |
| Approve a release (rule, template, prompt, model, incident map) | the **Head of Support** with the **VP Engineering**, with the eval-set and judge re-run attached | `evals/README.md` |
| Keep the trace; answer a customer or a regulator | **engineering** (VP Engineering) keeps the trace; **Legal and the DPO** answer | `governance.md` |
