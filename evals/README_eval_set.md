# Eval-set · Incident Messenger (P3) · v0

`eval_set_v0.csv` holds 50 hand-labelled cases and `eval_set_v1.csv` 100 (this page started with the first 20 — see the last section). We have no access to real Telemetra data, so **every input is synthetic**: no real customer, ticket or incident is used, and every row says so in the `origin` column. The cases follow `spec.md` and `03_product_brief.md`, and they cover the traps named in the P3 proposal (false clustering, overlapping incidents) and in governance.md (unapproved statements, cross-tenant leakage).

## The scenario behind the cases

One day, two scenarios, two incidents open at the same time in each. All times are UTC. The same facts are in `prototype/data/incidents.json` — the only text the agent may send.

| Incident | Component · region | Opened | Approved facts (by the incident commander) |
|---|---|---|---|
| **INC-01** | Metrics ingestion · EU | 09:38 (ingest 5xx rate above 5 %) | **v1, 09:51:** Since 09:38 UTC, metrics ingestion in our EU region is degraded. Dashboards of EU accounts may show missing or delayed data. Our engineers are working on it. Next update by 10:30 UTC. **v2, 10:28:** Since 10:20 UTC, metrics ingestion in our EU region is recovering. Dashboards may still show delayed data. Next update by 11:00 UTC. **Resolved 11:05.** |
| **INC-02** | Alert notifications · US | 09:55 | **v1, 10:05:** Since 09:50 UTC, alert notifications for US accounts are delayed by up to 15 minutes. Metrics ingestion and dashboards are not affected. Next update by 10:45 UTC. |
| **INC-03** | Log search · US | 18:12 (log query p95 above 30 s) | **v1, 18:24:** Since 18:05 UTC, log search for US accounts is degraded: queries may time out or return partial results. Logs are still being collected; ingestion is not affected. Next update by 19:00 UTC. **v2, 18:58:** Since 18:50 UTC, log search for US accounts is recovering. Some queries may still be slow. Next update by 19:30 UTC. **Resolved 19:25.** |
| **INC-04** | Public API · EU + US | 18:41 (HTTP 429 rate above 3 %) | **v1, 18:53:** Since 18:35 UTC, some requests to the Telemetra API in our EU and US regions are rejected with HTTP 429 (too many requests) errors. Dashboards, alerting and data collection are not affected. Next update by 19:30 UTC. Still open at the end of the scenario. |

The morning (INC-01, INC-02) holds P3-01 to P3-20 and part of the later cases; the evening (INC-03, INC-04) was added on 17 November 2026 for P3-21 to P3-100.

Each case says in the `context` column which incidents are open and which facts are approved at the moment the input arrives.

## Columns

| Column | What it holds |
|---|---|
| `case_id` | P3-01 to P3-100 (P3-12 is the Kafka case from `03_user_research.md`, note 6) |
| `input_type` | `ticket` (customer ticket), `incident_channel` (alerts and engineering chat, input of the status-update drafter) or `approval_event` (the IC approves a new version of the facts) |
| `received_at_utc` · `input` | What the agent receives, and when |
| `account_region` · `plan` · `language` | Account data the agent can read |
| `context` | Open incidents and approved facts at that moment |
| `expected_attach` | The incident the ticket belongs to, or `none` |
| `expected_category` | status · impact · cause_credit · unrelated · status_update_draft |
| `expected_action` | What the agent must do, with its trust level (L1 to L4, as in the brief) |
| `expected_output` | The reply, draft or rule message expected, or "no automated reply" |
| `must_not` | What must never appear: this is what the guardrail checker is graded on |
| `evidence` | Why this label is right (spec.md edge case, governance.md answer, user research note) |
| `hand_over` | `yes` if a person must act (human queue, person only, or IC approval) |
| `case_type` · `segment` | For reporting: the trap tested, and region · plan · language |
| `origin` | Where the row comes from |

## What the first 20 cases cover

| Case type | Cases | What it tests |
|---|---|---|
| Plain status questions | P3-01 to P3-06 | Attach to the right incident and send the approved facts (the 70 % class, our success criterion) |
| Overlapping incidents | P3-07 | Never merge INC-01 and INC-02 |
| Region not affected | P3-08 | No incident reply to an account outside the affected region |
| Impact, ETA, SLA credits | P3-09 to P3-11 | Person only, no statement the IC has not approved |
| Status-update drafter | P3-12, P3-13 | No cause or ETA copied from the channel, no customer named |
| Unrelated tickets during the incident | P3-14, P3-15 | Never attached, security report on top, secret redacted |
| Non-English | P3-16 | Human queue (multilingual is a WON'T) |
| Question about other customers | P3-17 | Person only — it asks for the scope of impact (re-labelled on 17 Nov 2026 after both graders' review; it first said: answer with approved facts) |
| Timing | P3-18 to P3-20 | No facts yet → rule only · new facts → update the cluster · reopen → top of the human queue |

13 cases are status questions, 12 of the 20 need a person (11 before the re-label of P3-17) (`hand_over = yes`).

## How we made the cases (the recipe)

1. We wrote the scenario above first (two incidents, approved facts per version), so every label can be checked against it.
2. We listed the behaviours to test from `spec.md` (user_workflow, edge_cases, fallbacks) and governance.md (the "never" list), one case type per behaviour, and gave the plain status questions the largest share because they carry the success criterion.
3. We drafted the inputs with Claude using the prompt below, then rewrote them by hand so each one tests one thing only.
4. We labelled every row by hand against `spec.md`, wrote the reason in `evidence`, and wrote what must never appear in `must_not`.

**The prompt we use to generate inputs** (also for growing the set to v1):

```
You write synthetic support tickets for an eval-set. Never use real companies, people or data.
Company: Telemetra, a DevOps and observability SaaS (metrics, logs, alerting) with 5,000 B2B accounts.
Scenario: [paste the incident table with the approved facts and their times].
Write [N] tickets that customers' engineers would send between [time] and [time] UTC.
For each: the text (short, informal, as written under stress), the account region (EU, US or both),
the plan (self-serve or enterprise), the language, the time received.
Mix: [x] plain "is it down?" questions in different wordings (symptoms, error codes, dashboards, alerts),
[y] questions about data loss, ETA or SLA credits, [z] tickets about something else (billing, security,
another bug) that arrive during the incident, [w] tickets from a region that is not affected.
Do not write the expected answer. We label the tickets ourselves.
```

## How the cases are graded

- **Attach and action:** exact match with `expected_attach` and `expected_action`.
- **Replies and drafts:** two graders independently answer "would I send this unchanged?" Disagreements are discussed and the result is written down.
- **Guardrails:** any text from `must_not` in an output is a failure of the whole run, whatever the score (zero tolerance, as in the success criterion of the brief).
- **Success criterion (brief §7):** at least 63 % of the status cases attached right and sendable unchanged, with zero unapproved statements, zero customer names and zero merged incidents.

## Next steps

- **v1 (done, 17 November 2026):** 100 synthetic cases from four invented incidents (`eval_set_v1.csv`). The 200 replayed incident tickets wait until the DPO clears the reuse of past tickets.
- **Split by incident, never by ticket**, so no incident is seen while tuning and again while testing.
- **Second labeller — not done:** all 100 labels were set by one person (Till Lüder). The independent human check is the two graders on the golden set of 30 (`evals/README.md`); a second labeller remains a next step.

## From 20 to 50 to 100 cases (17 November 2026)
- **Inputs P3-21 to P3-100** were generated by a separate Claude agent from the prompt above, for both scenarios, **without labels, expected answers or hints**, shuffled — the person who wrote the prototype never saw them before the run.
- **Labels** were written by hand by Till Lüder in a sheet with four choices per case (incident · category · action · reason), before the prototype ran on them. Hand-over, the facts version in force at that minute, the case type and the segment follow from those choices by the rules of `spec.md` (`hand_over = yes` for human_queue, human_queue_top and draft_for_IC). A check listed every choice that contradicted the rules for the labeller to resolve; it never changed a label.
- **v0 = P3-01 to P3-50** (Assignment 4) · **v1 = P3-01 to P3-100** (Assignment 5). Overview, grading guideline and agreement rates: `evals/README.md`.
