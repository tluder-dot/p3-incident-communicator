# 02 · Investment memo (one page)

**Recommendation: NO-GO this year.** At today's incident volume the agent is worth about −€5k a year in expected value, against €15k for doing nothing and €50k for the next-best project. We reopen the decision if the 12-month ticket log shows at least **twice** our estimated incident volume (≈ 59,000 incident tickets a year).

> Same base case as `02_sizing.xlsx`. All figures are year 1.

| €/year, year 1 | Pessimistic | Base | Optimistic | Expected value |
|---|---|---|---|---|
| Net annual value | −€136k | +€2k | +€206k | **−€5.5k** |
| Probability | 0.35 | 0.45 | 0.20 | |
| Do-nothing (value of the current process improving on its own) | €9k | €15k | €19k | |
| Next-best project: in-product incident banner with per-component status subscriptions, no AI (the hurdle) | €80k | €50k | €30k | |

## 1. How much?
About 20 major incidents a year × 1,500 tickets = **2,500 incident tickets a month**. In scope: only "Is it down?" status questions (70 % of incident tickets, measured in P3). 90 % are answerable from the approved status update, and we assume 70 % close without a human. With the adoption ramp (10 → 60 % by quarter) that is **about 5,000 tickets in year 1**, worth €49.6k of support time, minus €3.7k of expected error cost and €0.3k of tokens. We add €36k of retained revenue (3 accounts kept a year). Net after fixed costs: **+€1.8k**, and −€34k without the retention line. **Measured:** 5,000 accounts, ×10 during incidents, 70 % same question. **Analogies:** 20 incidents a year (PagerDuty), €10 a ticket (Session 2). **The one guess that matters:** incident volume (see 2).

## 2. How sure?
We weight the pessimistic case more than the optimistic one: few incidents to learn from and false clustering are the known P3 traps. **The flip point is volume, not deflection.** In the sensitivity table every deflection rate stays below do-nothing: even 100 % on status questions only reaches about €21k, below the hurdle, and beating do-nothing would need 90 %, above our optimistic case. The decision flips at **about 2× our incident volume**, where the sheet reads CONDITIONAL GO. That number comes from the ticket log, so we check it before anything else. The S4 prototype then tests what the case needs next: attach precision and deflection on 200 replayed tickets (H1 in 01_problem_statement.md).

## 3. What if we're wrong?
Base cost lines a year: integration €23k (€70k over 3 years), evaluation €15k, supervision €17.5k (0.25 FTE), monitoring and on-call €15k, re-evaluation €9k, tokens €0.3k, cost of error €3.7k. **Fixed lines are 95 % of the cost**, and tokens are so small that the decision is the same whether prices stay flat or halve every year: the problem is low frequency, not the model. **The tail:** we excluded "Is my data affected?" questions, whose expected error cost (€15.6k) is three times their value (€5.6k). **The governance line:** a wrong public statement is a reputational and contractual risk owned by the VP Engineering through the incident commander, and cross-tenant leakage is a legal risk owned by the DPO. That is why the first message of each cluster stays L2.

## 4. Compared to what?
**Do-nothing** is worth €15k a year: better macros and status emails make the current process 5 % more efficient on its own. **The next-best project** is an in-product incident banner with per-component status subscriptions (no AI), worth about €50k a year for a few weeks of one engineer. It targets the same tickets. **The pessimistic case does not clear the hurdle** (−€136k vs €80k). We also checked buying a vendor bot per resolution (EV about €30k) and year 2 at full adoption (EV about €25k): neither clears €50k. **What we do instead:** ship the banner, add a comms-lead role and the auto-acknowledge rule to the incident runbook, and keep the agent as our S4 prototype so the volume check and H1 are answered before we decide again.

## 5. Build, buy or orchestrate?
**We would buy, because at about 5,000 resolutions a year vendor fees (≈ €6k at Zendesk's $1.50 per resolution) are far below our own fixed lines (≈ €47k).** Weighted scores from the `Build or buy` tab: Build 2.5 · Buy 3.7 · Orchestrate 3.55. The two are within 0.3, and the condition that would change our mind: we orchestrate if volume passes about 38,000 resolutions a year, or if no vendor can use our account to component map.

*Sources: P3 project proposals and sign-up sheet · Session 2 slides (13 Oct 2026) · PagerDuty survey, 27 June 2024 · Claude API pricing, checked 23 Oct 2026 · Zendesk AI pricing (eesel.ai, edited 14 Oct 2026) · Intercom Fin pricing (gleap.ai, checked 26 Sep 2026). Full list in the Inputs tab of 02_sizing.xlsx.*
