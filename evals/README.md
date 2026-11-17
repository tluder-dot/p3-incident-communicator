# evals/ — how we judge Incident Messenger (P3)

| File | What it is |
|---|---|
| `eval_set_v0.csv` | 50 cases (Assignment 4): P3-01–P3-20 from Session 3, P3-21–P3-50 added on 17 November 2026 |
| `eval_set_v1.csv` | 100 cases (Assignment 5): v0 + P3-51–P3-100 |
| `README_eval_set.md` | the scenario, the columns and the recipe we use to make cases |
| `report_v0.md` | the first run: the number against the criterion, the misses (M1–M5), demo vs eval data |
| `outputs_v0.csv` · `outputs_v1.csv` | what the prototype did on every case (written by `prototype/evals.py`) |
| `judge_rubric.md` | **the grading guideline** — five yes/no criteria and a verdict, written before anyone graded |
| `judge_prompt.txt` | the LLM judge: the guideline, copied, + one case |
| `grades/` | the two human graders' sheets and the judge's answers on the golden set |
| `rollback_tests.csv` | every test of the switch ⏻ (who, when, result) — the first (17 Nov) ran on the complete prototype in the working tree on top of commit 8cc2b95, before the files were committed by their authors |
| `sample_size.xlsx` | the calculator of Session 6, filled for our test (optional) |
| `adversarial_v0.csv` | five attacks by OWASP line, run through the prototype (optional, not graded) |

**Rules we keep.** Inputs are synthetic and say so in `origin`; labels are written by a person **before** the prototype runs on them; a case looked at while changing the code becomes demo data and is named in the report; the set is never used to tune. Re-run with `python prototype/evals.py evals/eval_set_v1.csv`.

## The grading guideline (summary — full text in `judge_rubric.md`)
For every output, five yes/no questions: **(1)** may the agent answer this automatically at all? **(2)** is it the right incident? **(3)** is it the facts version in force at that minute? **(4)** is there nothing unapproved (cause, ETA, data-loss claim, internal number, other customer, secret)? **(5)** could the customer — or the IC, for a draft — receive it unchanged? Verdict: **SEND** (all yes) · **ESCALATE** (no to 1: a person must answer) · **EDIT** (otherwise). A case counts as "sendable as is" only when both graders say SEND.

## The golden set and the two agreement rates (Assignment 5 §5)
- **Golden set:** 30 cases that never change — the 27 cases of `eval_set_v0.csv` where the agent produced a text (18 replies, 5 auto-acknowledgements, 3 IC drafts, 1 cluster update) and 3 escalations (P3-07, P3-17, P3-32).
- **Graders:** Till Lüder (A) and Benjamin Rasson (B), alone, with `judge_rubric.md`; sheets in `grades/grader_A.csv` and `grades/grader_B.csv`. Grader B graded P3-18 after the other 29 and passed it to Till by message (SEND, five YES).
- **Human–human agreement: 100 %** — the same verdict on 30 of 30 cases; 149 of 150 criterion answers.
- **Judge:** Claude Opus 5.5, run as a separate Claude Code agent, one prompt per case (`judge_prompt.txt`), blind to the labels and to the human grades; answers in `grades/judge_v1.csv` (before the fix) and `grades/judge_v2.csv` (after it).
- **Human–judge agreement: 77 % before the fix (23 of 30), 100 % after it (30 of 30)** — on the cases where both humans agree, and the same with each grader alone.
- **Known biases:** the eval inputs were drafted by a Claude model, the same family as the judge; the customer replies are templates, so the judge never grades its own family's prose there; for the IC drafts it would, once the LLM drafter replaces the mock. Grader A also labelled the eval-set and re-labelled P3-17 and P3-34 after grading; grader B never saw the labels.

### What the disagreements taught us
- **Between the two graders:** none on the verdict. One criterion differed: c3 on P3-13 — A said the facts were in force, B said no, because the draft gives the time of the IC's message (10:21) as the start of the recovery. Both said EDIT.
- **Between the graders and the labels:** both graders said a person must answer P3-17 and P3-34 ("which other customers are hit, is it everyone in the EU?"): they ask for the scope of impact, which only the IC may state. The labels said auto_reply. The labeller re-labelled both as person only — a label error, not a grading one (`spec.md` M2).
- **Between the humans and the judge (v1), seven cases, two patterns.** Five auto-acknowledgements (P3-18, P3-23, P3-28, P3-41, P3-49): the judge said EDIT because they have no since-time and no next-update time — the graders had a note that an acknowledgement sent before any facts cannot have them; the judge's prompt did not. Two IC drafts (P3-12, P3-24): the judge said SEND to an "Impact: …" line pasted from the IC's note; both graders said it is not a customer sentence — the judge was lenient exactly on our most frequent miss.

### What we changed, once
On 17 November 2026, once: the notes per output type that both graders had were added to `judge_rubric.md` and `judge_prompt.txt`, with one boundary example for IC drafts (a pasted "Impact:" line is not sendable; the time of the IC's message is not the time the recovery started). A fresh judge, blind to labels, grades and its first answers, re-graded the same 30 cases: 30 of 30 agree with the humans.
**Caveat:** that 100 % is measured on the very cases the fix was read from — it shows the fix closed these gaps, not that the judge generalises. The weekly 5 % human sample on new incidents is the real test; a rate below 77 % re-opens the guideline.

## Coverage of the 100 cases
`eval_set_v1.csv`, labelled by hand by Till Lüder on 17 November 2026 (P3-51 to P3-100 after the v0 run, before any run on them).

| Stratum | Cases |
|---|---|
| Scenario | morning (INC-01, INC-02) 55 · evening (INC-03, INC-04) 45 |
| Input type | ticket 93 · incident channel 5 · approval event 2 |
| Account region | EU 47 · US 44 · EU + US 9 |
| Plan | self-serve 62 · enterprise 31 · n/a (channel, approval) 7 |
| Language | English 94 · German 2 · French 2 · Spanish 2 |
| Expected action | human queue 45 · auto-reply 34 · auto-acknowledge 9 · draft for the IC 5 · top of the queue 5 · cluster update 2 |
| Expected category | status 69 · unrelated 12 · cause / ETA / credit 9 · impact 5 · status-update draft 5 |

20 case types; the largest is the plain status question (31), the traps are oversampled on purpose (no facts yet 9, region not affected 8, non-English 6, unrelated 12, overlapping incidents 4, scope of impact 3, reopen 2). **Thin segments, reported as such:** non-English (6) and EU + US accounts (9) — the known gaps of the Session 3 audit. The case types of eight cases whose reason the labeller typed in his own words were mapped from those words (e.g. "cancellation, not about the incident" → unrelated_other); no label was changed.

### The same frozen prototype on the 50 held-out cases (16:45 UTC)
`python prototype/evals.py evals/eval_set_v1.csv` → `outputs_v1.csv`. No code changed since the v0 run, so P3-51 to P3-100 are a clean held-out test: 17 of the 18 status tickets that should get an automatic reply got the right one, attach precision 0.90 (18 / 20, exactly the floor), action accuracy 0.84 — and **4 floor misses**: three automatic replies where a person had to answer (P3-53 CPU charts and P3-54 a broken export button, both attached through the "only incident in the region" rule; P3-75 "are our logs still being stored?", a data question the data-loss rule missed) and one auto-acknowledgement three minutes before INC-03 was opened (P3-79). No unapproved statement, no merged incident. The misses of v0 generalise; each one is a line of `spec.md` v2.

## Release approval
A new rule, template, prompt, model version or incident → component map ships only with this folder re-run attached: `eval_set_v1` through `prototype/evals.py` (floors at zero) and the judge on the golden set, approved by the Head of Support with the VP Engineering (`06_07_experiments_operations.md` §5). A 5 % human sample of sent replies is re-graded every week.
