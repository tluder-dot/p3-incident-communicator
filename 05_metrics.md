# 05 · Metrics — Team 8 · Incident Messenger (P3)

> Session 5 deliverable. Five sections = the five moves of the session. Every number comes from `02_sizing.xlsx` (cell named) or `evals/report_v0.md` and the eval folder it summarises (`evals/README.md`). Declared exceptions: the 40-minute baseline and the ≤ 10-minute target of `01_problem_statement.md`, and the ~2× volume flip of `02_investment_memo.md` §2. Three numbers are thresholds we chose, marked *(chosen)*: the 2× gap for equal error rates, the ± 0.5-point churn band, the 5 % weekly sample.

## 1 · Place the number — the stack for our agent

_To be completed._

## 2 · Decide when to stop — the stop criterion

_To be completed._

## 3 · Choose what to protect — the hierarchy, by segment

_To be completed._

## 4 · Derive the business metrics — three, with expected effects

_To be completed._

## 5 · Make the judge trustworthy — the evaluation plan
- **Eval-set v1:** `evals/eval_set_v1.csv`, 100 cases, stratified by region, plan, language, case type and morning / evening scenario; inputs synthetic and tagged in `origin`, labels written by a person (Till Lüder); **golden set of 30** = the 30 cases both graders graded — they never change.
- **Grading guideline:** `evals/judge_rubric.md` — five binary criteria, boundary examples, a three-way verdict (SEND · EDIT · ESCALATE), written before grading. Two graders (Till Lüder, Benjamin Rasson) on the same 30: **human–human agreement 100 %** (30 of 30 verdicts, 149 of 150 criterion answers).
- **Judge:** Claude Opus 5.5, run as a separate Claude Code agent, one prompt per case (`evals/judge_prompt.txt`), blind to labels and human grades. **Human–judge agreement 77 % (23 / 30) before the fix, 100 % (30 / 30) after it**, on the cases where both humans agree. **Known bias:** the eval inputs were drafted by a Claude model too (same family — they may read "natural" to it); the customer replies are templates, so the judge does not grade its own family's writing there. **Re-aligned once, on 17 November 2026:** the judge had not been given the graders' notes on auto-acknowledgements, and it passed IC drafts that paste the IC's note; both went into the guideline and the prompt (`evals/README.md`). The 100 % is measured on the same 30 cases the fix came from — in-sample; the weekly human sample on new incidents is the real test.
- **Cadence:** eval-set + judge on every change of a rule, template, prompt, model version or the incident → component map; a 5 % human sample of sent replies every week, plus every disagreement.
- *Optional, not graded* — **red rows:** `evals/adversarial_v0.csv`, five attacks by OWASP line run through the prototype on 17 November 2026: four held (prompt injection, another customer's data, excessive agency, a poisoned channel line); one passed — a question about **yesterday's traces** outage got today's ingestion facts (LLM09 misinformation) → new `spec.md` line (red row A05). A red row that passes blocks the release, like a floor miss.
