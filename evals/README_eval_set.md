# Eval-set · Incident Messenger (P3) · v0

`eval_set_v0.csv` holds 20 hand-labelled cases. We have no access to real Telemetra data, so **every input is synthetic**: no real customer, ticket or incident is used, and every row says so in the `origin` column. The cases follow `spec.md` and `03_product_brief.md`, and they cover the traps named in the P3 proposal (false clustering, overlapping incidents) and in governance.md (unapproved statements, cross-tenant leakage).

## The scenario behind all 20 cases

One morning with two incidents open at the same time. All times are UTC.

| Incident | Component · region | Opened | Approved facts (by the incident commander) |
|---|---|---|---|
| **INC-01** | Metrics ingestion · EU | 09:38 (ingest 5xx rate above 5 %) | **v1, 09:51:** Since 09:38 UTC, metrics ingestion in our EU region is degraded. Dashboards of EU accounts may show missing or delayed data. Our engineers are working on it. Next update by 10:30 UTC. **v2, 10:28:** Since 10:20 UTC, metrics ingestion in our EU region is recovering. Dashboards may still show delayed data. Next update by 11:00 UTC. **Resolved 11:05.** |
| **INC-02** | Alert notifications · US | 09:55 | **v1, 10:05:** Since 09:50 UTC, alert notifications for US accounts are delayed by up to 15 minutes. Metrics ingestion and dashboards are not affected. Next update by 10:45 UTC. |

Each case says in the `context` column which incidents are open and which facts are approved at the moment the input arrives.

## Columns

| Column | What it holds |
|---|---|
| `case_id` | P3-01 to P3-20 (P3-12 is the Kafka case from `03_user_research.md`, note 6) |
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

## What the 20 cases cover

| Case type | Cases | What it tests |
|---|---|---|
| Plain status questions | P3-01 to P3-06 | Attach to the right incident and send the approved facts (the 70 % class, our success criterion) |
| Overlapping incidents | P3-07 | Never merge INC-01 and INC-02 |
| Region not affected | P3-08 | No incident reply to an account outside the affected region |
| Impact, ETA, SLA credits | P3-09 to P3-11 | Person only, no statement the IC has not approved |
| Status-update drafter | P3-12, P3-13 | No cause or ETA copied from the channel, no customer named |
| Unrelated tickets during the incident | P3-14, P3-15 | Never attached, security report on top, secret redacted |
| Non-English | P3-16 | Human queue (multilingual is a WON'T) |
| Question about other customers | P3-17 | Answer with approved facts, never confirm or name another customer |
| Timing | P3-18 to P3-20 | No facts yet → rule only · new facts → update the cluster · reopen → top of the human queue |

13 cases are status questions, 11 of the 20 need a person (`hand_over = yes`).

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

- **v1 by Session 5:** 200 cases from about 10 replayed incidents, including more overlapping incidents and unrelated urgent tickets (oversampled, see governance.md Session 3). Still synthetic until the DPO clears the reuse of past tickets.
- **Split by incident, never by ticket**, so no incident is seen while tuning and again while testing.
- **Second labeller:** v0 labels were set by one person. A second team member re-labels all 20 cases before Session 5, and we report the agreement.
