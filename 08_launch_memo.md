# Launch memo — Incident Messenger (P3) — 26 November 2026

> One page. Team 8. Every number is in `02_sizing.xlsx` (cell named), `evals/` or `06_07_experiments_operations.md`.

## 1 · Decision
**No-go for customers this year — conditional go when two things are true:** the 12-month ticket log shows about twice today's incident volume (the flip point of `02_investment_memo.md`), **and** spec v2 is built with zero floor misses on `evals/eval_set_v1.csv`. **What we launch instead, from 1 December 2026:** the cheap alternative — a comms-lead role in the incident runbook and the auto-acknowledge rule — and the next-best project, the in-product incident banner. The next decision is read on **14 January 2027** by the **Head of Support** and the **CFO**, with the ticket log in hand.

**Budget we ask for:** now, about **€10k a year** for the banner (02_sizing, Inputs G60) and **nothing for the agent**. Once the conditions hold: about **€80k a year**, the fixed costs of 02_sizing (Decision D14) — integration €23k amortised, evaluation €15k, supervision €17.5k (0.25 of a support lead), monitoring and on-call €15k, re-evaluation €9k.

## 2 · Evidence
- **Eval v0 (50 cases, labelled before the run, two graders on 30, judge validated — agreement 100 % between the graders, 77 % → 100 % for the judge after one fix):** **15 of the 16 answerable status tickets got a reply both graders would send unchanged — 94 %, 84 % re-weighted to real traffic** — against the criterion *"≥ 63 % of 'is it down?' tickets attached right and sendable, with no unapproved statement, no other customer and no merged incident"*. Met on the answerable share; **not releasable:** two replies went where a person had to answer, and 0 of 3 drafts for the incident commander were publishable (`evals/report_v0.md`).
- **Eval v1 (100 cases, same frozen prototype, automatic checks):** 33 of 34 answerable right, attach precision 0.92 — and **6 replies on person-only tickets**, so the floor misses generalise (`evals/README.md`).
- **Guardrails:** 0 unapproved statements and 0 other-customer mentions in 100 cases; checked on every change (`prototype/evals.py`); red team 4 of 5 attacks held (`evals/adversarial_v0.csv`).
- **What the test must prove** (`06_07` §1–§2): "is it down?" tickets closed without a person and not reopened in 48 h, **from 0 % to ≥ 70 % of the answerable ones** (Inputs D22). The calculator says ~9 tickets per arm (baseline 0 %, smallest gain that pays +63 points), but tickets in one incident share one update, so the unit is the region: **5 incidents per region arm, two quarters**, because incidents are rare (~5 a quarter, Inputs G39).
- **Sizing:** base **+€1.8k** a year vs the hurdle **€50k** (incident banner); EV **−€5.5k**; do-nothing **€15k** a year while incident tickets grow to ~€330k in 12 months (Decision D17, D23, D19, D22; `01_problem_statement.md` §7).

## 3 · Rollout steps — only once the conditions of §1 hold
| Step | Scope | Duration | Gate (metric · threshold · read date) | Signs the next step |
|---|---|---|---|---|
| 0 | shadow, staging: replays of past incidents (once the DPO clears their reuse) | 3 weeks | floors at 0 on eval v1 · ≥ 2 of 3 IC drafts publishable · no red row · rollback tested | Head of Support |
| 1 | shadow mode on live incidents: the agent drafts, people send | one quarter (~5 incidents) | attach precision ≥ 0.90 on the weekly sample · 0 floor misses · the IC publishes ≥ 80 % of drafts with minor edits (H2) | Head of Support |
| 2 | stepped wedge: one region live, chosen at random; the other is the control | two quarters (5 incidents per arm) | ≥ 70 % of answerable tickets closed without a person · first update ≤ 10 min · ship / iterate / kill as written on 17 Nov 2026 | Head of Support + VP Engineering |
| 3 | both regions live | ongoing | monthly: four layers green, knowledge-drift review, eval v1 re-run at every change | Head of Support |

## 4 · Rollback & the switch
Trigger: any harmful-class incident (an unapproved statement or another customer's name sent) · a wrong-reply rate above 6 % in a segment (Inputs C26) · attach precision under 0.90 on a live incident · an API down for 10 minutes · Who decides: the **IC or support lead on duty** (at night: the **on-call support lead**) · Action: SUGGEST_ONLY first, then OFF — one click in the IC console · Time to execute: under 2 minutes · What people see: support engineers get "automatic replies paused — the cluster is in your queue"; customers get the auto-acknowledgement with the status-page link · **Last tested: 17 November 2026, on the prototype (our laptop is our staging), by Till Lüder playing the support lead on duty — all three positions passed.**

## 5 · Owners — and who signs
| Decision | Owner | Written where |
|---|---|---|
| run an experiment on real users | Head of Support signs; VP Engineering co-signs; the DPO reads | 06_07 §1–§2 · governance.md |
| read the weekly numbers and act | Head of Support, with the support lead | 06_07 §3 |
| press the switch | IC or support lead on duty; at night the on-call support lead | 06_07 §4 · governance.md |
| approve a release (rule, template, prompt, model, incident map) | Head of Support with the VP Engineering, with the eval re-run | evals/README.md |
| keep the trace, answer a customer or a regulator | engineering keeps it; Legal and the DPO answer | governance.md |

**This decision is signed by the Head of Support (owner of the agent) and the CFO (owner of the business case).**

## 6 · What we do not know yet
- **Is the incident volume big enough?** 20 incidents × 1,500 tickets is a guess (PagerDuty analogy) — next: count the 12-month ticket log and status-page history, read on 14 January 2027.
- **Does attach hold on real tickets?** Precision 0.90 on the held-out cases sits exactly on the floor, on synthetic inputs — next: build spec v2, then replay 200 tickets from ~10 past incidents once the DPO clears the reuse.
- **Will the incident commander publish the draft?** 0 of 3 with the mock drafter — next: the LLM drafter on 10 replayed incidents, graded by an on-call engineer (H2); and three real conversations with an IC, a support engineer and an SRE — our user research is still simulated.
- **The number we could not measure:** the minutes from the first ticket to the first update (40 is a guess) — how: first-ticket time vs first status-page post in the last 12 postmortems.
