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

_To be completed._

## §4 Contain the incident — trace, classes, rollback

_To be completed._

## §5 Own the system — the five owners

_To be completed._
