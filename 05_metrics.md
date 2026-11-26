# 05 · Metrics — Team 9 · Incident Messenger (P3)

> Session 5 deliverable. Five sections = the five moves of the session. Every number comes from `02_sizing.xlsx` (cell named) or `evals/report_v0.md` and the eval folder it summarises (`evals/README.md`). Declared exceptions: the 40-minute baseline and the ≤ 10-minute target of `01_problem_statement.md`, and the ~2× volume flip of `02_investment_memo.md` §2. Three numbers are thresholds we chose, marked *(chosen)*: the 2× gap for equal error rates, the ± 0.5-point churn band, the 5 % weekly sample.

## 1 · Place the number — the stack for our agent
| Level | Question | Our metric | Value today | Produced by | Owner | Clock |
|---|---|---|---|---|---|---|
| 5 Business | does it move the P&L? | yearly cost of the incident tickets people handle | €300k a year (02_sizing: Inputs D6 2,500 tickets/month × D9 €10 × 12) — nothing measured with the agent yet | finance data + ticket log | CFO, with the Head of Support | months |
| 4 Product | does the user get the job done? | share of "is it down?" tickets closed by the agent's reply and **not reopened within 48 h** (the deflection of 02_sizing, Inputs G22) | not yet — needs live incidents (planning number: 70 % of the answerable ones, Inputs D22) | shadow mode, then the stepped-wedge test of `06_07` | Head of Support | per incident, read weekly |
| 3 Guardrails & responsible AI | does it stay inside the lines — for everyone? | replies sent on tickets that must go to a person · unapproved statements · other-customer mentions · merged incidents | **2** · 0 · 0 · 0 on 50 cases (report_v0) — two floor misses | eval-set + adversarial rows each release, then the trace in production | Head of Support + DPO | days |
| 2 AI system | does the workflow complete the task? | share of status tickets attached right **and** sendable unchanged for both graders | **15 / 33 = 45 %** — 94 % of the 16 answerable ones, 84 % re-weighted to the sizing's 90 % answerable (criterion 63 %) | eval-set + two graders | engineering team (VP Engineering) | hours |
| 1 Model | is the component right? | attach precision · recall · router accuracy | 0.94 · 1.00 · 0.93 (report_v0) — on the 50 held-out cases 0.90 · 0.89 (`evals/README.md`) | offline eval-set | engineering team (VP Engineering) | seconds |

Read it bottom-up: a better attach precision is a hypothesis about fewer wrong replies (level 3), which is a hypothesis about tickets closed and not reopened (level 4), which is a hypothesis about cost (level 5). The CFO's number moves last.

## 2 · Decide when to stop — the stop criterion
> **"We stop improving the share of sendable replies at the 63 % of our criterion, because the level above — the investment decision — no longer responds to it: in 02_sizing even 75 % deflection gives a net value of +€5.1k a year, €9.9k below do-nothing (Decision C36 and E36); the decision flips on incident volume (about 2×, memo §2), not on quality. The next points would cost labelling and grading time — the €15k-a-year evaluation line (Decision D10) — for no change of decision."**

- **Component metric and value:** sendable share 94 % on the answerable status tickets (report_v0) against the 70 % deflection the sizing assumes (Inputs D22).
- **The level-above metric that stops responding:** the net annual value against do-nothing and the hurdle (02_sizing, Decision rows 32–36): flat, the bottleneck is volume — the "flat" curve of Session 5.
- **Cost of the next point:** labelled replays of past incidents and two graders (Decision D10, €15k a year), plus the IC's time on every draft.
- **What is a floor, not a stop:** zero replies on tickets that must go to a person, zero unapproved statements, zero other-customer mentions, zero merged incidents, attach precision ≥ 0.90 (H1). Report_v0 found two floor misses (P3-08 wrong incident, P3-34 scope of impact): they block the release whatever the sendable share.

## 3 · Choose what to protect — the hierarchy, by segment
| Kind | Metric | Numerator / denominator | Level | Lag | Source & owner |
|---|---|---|---|---|---|
| **Primary (1)** | "is it down?" tickets closed by the agent and not reopened within 48 h | status tickets answered by the agent and not reopened in 48 h / all status tickets of the incident | 4 product | 48 h after each incident | ticket log · Head of Support |
| Guardrail | unapproved statements and other-customer mentions sent | sent texts with an unapproved cause, ETA, scope, data-loss claim or another customer / all sent texts — **floor 0** | 3 | real time (the trace) | trace · IC on duty; DPO for other customers |
| Guardrail | attach precision on the weekly sample (false clustering) | sampled attached tickets that belong to their incident / sampled attached tickets — **≥ 0.90** (H1; 0.94 in report_v0) | 1–3 | one incident | weekly 5 % sample *(chosen)* · support lead |
| Guardrail | time to first human answer for the tickets the agent did **not** answer | median minutes, human queue during an incident — **not above the same incident type without the agent** | 4 | hours | ticket log · Head of Support |
| Counter-metric | wrong replies: "Not this incident" clicks + agent replies reopened as wrong | wrong agent replies / agent replies — the line between "sent wrong" and "harmful" is the harm threshold below | 4 | 48 h | ticket log + trace · support lead |
| Counter-metric | churn of accounts that went through an incident | accounts lost / accounts hit by an incident, per year — 8 % today (02_sizing, Inputs G67) | 5 | 3–12 months | billing + exit survey · CFO |

- **Segments reported** (from the Session 3 audit): region (EU · US · EU + US) · plan (self-serve · enterprise) · language (English · other) · single vs overlapping incidents.
- **Fairness metric, named:** **equal error rates** across segments — the wrong-reply rate EU vs US and self-serve vs enterprise must not differ by more than 2× *(chosen)*. **Selection-rate parity** by language is broken by design (non-English tickets never get an automatic reply — a WON'T): we report it, and guardrail 3 makes sure those customers do not wait longer for a person.
- **Harm threshold** (copied into `governance.md`): *If the wrong-reply rate in any region or plan exceeds 6 % during an incident — the pessimistic error rate of 02_sizing (Inputs C26) — or if one unapproved statement or other-customer mention is sent, the agent drops to SUGGEST_ONLY — for that segment once the per-segment switch is built (`spec.md`), for all clusters until then — until the cause is explained. Owner: the Head of Support; reviewed with the DPO every month.*
- **How it could be gamed → the repair:** closing tickets right after the reply moves the primary → the 48-hour reopen window and the wrong-reply counter-metric. Making "reply human" hard moves it too (Klarna) → guardrail 3, the time to first human answer for the people the agent does not serve.

## 4 · Derive the business metrics — three, with expected effects
| Business metric | Baseline | Expected effect | Lag | Read date | It is a hypothesis about… |
|---|---|---|---|---|---|
| Yearly cost of incident tickets handled by people | €300k (02_sizing: Inputs D6 × D9 × 12) | **−€49.6k in year 1** (Upside D12: 4,961 tickets deflected × €10). The eval says the customer replies are not the constraint: 94 % of the answerable ones are sendable (report_v0) against the 70 % deflection planned (Inputs D22); sendable is an upper bound of deflection, because the customer may still write back | 1 month | month 2 of the pilot | attach + template → tickets closed without a person → hours of support saved |
| Median minutes from the first ticket to the first customer-facing update | 40 min (`01_problem_statement.md` §1, a guess to measure on the last 12 postmortems — the one baseline not in the sizing) | **≤ 10 min**: the auto-acknowledge rule answers in seconds and the facts reply leaves as soon as the IC approves; but 0 of the 3 IC drafts were publishable unchanged (report_v0) — the drafter is what this metric waits for (`spec.md` M1), the H2 test of `01` | per incident | after 5 incidents (≈ one quarter: about 5 incidents a quarter, Inputs G39) | IC approval speed → first update → fewer duplicate tickets |
| Churn of accounts that went through an incident | 8 % a year (Inputs G67) | **unchanged, ± 0.5 point** *(chosen band)* — stated as a non-effect: the 3 accounts the sizing hopes to keep (Inputs D67, €36k) are 0.06 point of 5,000 accounts, too small to see; the band is there to catch harm. Above 8.5 % stops the rollout | 3–12 months | month 12, exit-survey reasons every quarter | that faster, tailored updates do not cost trust when one is wrong |

**The tree** (component → product → business, each arrow a hypothesis Sessions 6 + 7 test):
```
attach precision 0.94 · router 0.93 · floors: 2 misses            (component, report_v0)
        └─▶ sendable replies 94 % of the answerable ones · IC drafts 0 / 3   (AI system, two graders)
                └─▶ status tickets closed, not reopened in 48 h: 70 % planned (Inputs D22)   (product)
                        └─▶ −€49.6k of support time in year 1 (Upside D12) · first update 40 → ≤ 10 min · churn 8 % unchanged ± 0.5 pt   (business)
```

## 5 · Make the judge trustworthy — the evaluation plan
- **Eval-set v1:** `evals/eval_set_v1.csv`, 100 cases, stratified by region, plan, language, case type and morning / evening scenario; inputs synthetic and tagged in `origin`, labels written by a person (Till Lüder); **golden set of 30** = the 30 cases both graders graded — they never change.
- **Grading guideline:** `evals/judge_rubric.md` — five binary criteria, boundary examples, a three-way verdict (SEND · EDIT · ESCALATE), written before grading. Two graders (Till Lüder, Benjamin Rasson) on the same 30: **human–human agreement 100 %** (30 of 30 verdicts, 149 of 150 criterion answers).
- **Judge:** Claude Opus 5.5, run as a separate Claude Code agent, one prompt per case (`evals/judge_prompt.txt`), blind to labels and human grades. **Human–judge agreement 77 % (23 / 30) before the fix, 100 % (30 / 30) after it**, on the cases where both humans agree. **Known bias:** the eval inputs were drafted by a Claude model too (same family — they may read "natural" to it); the customer replies are templates, so the judge does not grade its own family's writing there. **Re-aligned once, on 17 November 2026:** the judge had not been given the graders' notes on auto-acknowledgements, and it passed IC drafts that paste the IC's note; both went into the guideline and the prompt (`evals/README.md`). The 100 % is measured on the same 30 cases the fix came from — in-sample; the weekly human sample on new incidents is the real test.
- **Cadence:** eval-set + judge on every change of a rule, template, prompt, model version or the incident → component map; a 5 % human sample of sent replies every week, plus every disagreement.
- *Optional, not graded* — **red rows:** `evals/adversarial_v0.csv`, five attacks by OWASP line run through the prototype on 17 November 2026: four held (prompt injection, another customer's data, excessive agency, a poisoned channel line); one passed — a question about **yesterday's traces** outage got today's ingestion facts (LLM09 misinformation) → new `spec.md` line (red row A05). A red row that passes blocks the release, like a floor miss.
