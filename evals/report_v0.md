# Eval report v0 — Team 9 · Incident Messenger (P3)

**Date:** 17 November 2026 (one run of the prototype, 15:55 UTC)   **Eval-set:** `evals/eval_set_v0.csv`, 50 cases   **Prototype:** the four steps of `/prototype` + the harness, run on the complete working tree (committed afterwards by their authors: step-1 … step-4 and eval-v0) with `python prototype/evals.py evals/eval_set_v0.csv` (output: `evals/outputs_v0.csv`)

## 1. The number against the criterion
| | Value |
|---|---|
| Success criterion (`03_product_brief.md` §7) | *"By Session 5, on our eval-set […], at least 63 % of 'is it down?' status tickets are attached to the right incident and get a reply that two graders would send unchanged — and no reply states a cause, ETA, scope of impact or data loss that the incident commander has not approved, names another customer, or merges two different incidents."* |
| Status tickets in the set | 33 — of which **16 should get an automatic reply**; the other 17 must go to a person or get only the auto-acknowledgement (other language, unaffected region, two incidents, no facts yet, scope of impact, reopen) |
| Replies produced that pass the automatic checks (right incident, facts version in force, policy pass) | 16 / 33 = 48 % |
| **Replies both graders would send unchanged** (graded by hand, `evals/judge_rubric.md`) | **15 / 33 = 45 %** |
| … on the 16 status tickets that should get an automatic reply | **15 / 16 = 94 %** — re-weighted to the 90 % answerable share of `02_sizing.xlsx`: 0.9 × 15 / 16 = **84 %** |
| Replies sent on tickets that must go to a person (must be 0) | **2** — P3-08 (wrong incident) and P3-34 (scope of impact) |
| Merged incidents (must be 0) | 0 |
| Unapproved cause, ETA, data-loss claim or other customer in a sent text (must be 0) | 0 |
| Policy blocks | 0 |
| Routing (category) accuracy · tickets | 0.93 — 3 errors: P3-15 and P3-36 stopped by later rules; P3-17's mis-route ("impact") is what sent it to a person |
| Attach precision · recall (H1 floor 0.90) | 0.94 (17 / 18) · 1.00 |
| Action accuracy (what the agent decided vs the label) | 0.96 (48 / 50) |
| Auto-acknowledgements both graders would send · cluster update | 5 / 5 · 1 / 1 |
| **Status-update drafts for the IC that both graders would publish unchanged** | **0 / 3** |

**Verdict: criterion met on the answerable share (84 % against 63 %), but the prototype is not releasable.** Two floor misses — a reply on a ticket that must go to a person — block the release whatever the score, and none of the three drafts for the incident commander could be published unchanged.

**What the number means.** The 63 % threshold is a share of real status traffic (`02_sizing.xlsx`: 90 % answerable × 70 % deflection). Our eval-set oversamples the hard cases on purpose, so only 16 of its 33 status tickets are answerable: even a perfect agent scores 48 % on the set as written. We report both denominators (`spec.md` M5).

## 2. The most frequent misses
| # | What went wrong (one line) | Example | Which component | What it becomes in `spec.md` v2 |
|---|---|---|---|---|
| 1 | **No draft for the IC was publishable unchanged** (3 of 3): the mock drafter pastes the IC's shorthand ("Impact: EU ingestion, dashboards delayed.") instead of a sentence on what customers may see, and P3-13 gives the time of the IC's message as the time the recovery started | P3-12, P3-13, P3-24 | 3b status-update drafter (mock, no model) | **M1** — a "what customers may see" sentence, "since" only from an explicit time; the LLM drafter or a sentence per component before a pilot |
| 2 | **Questions about other customers got an automatic reply** — "which other customers are hit, is it everyone in the EU?" asks for the scope of impact, which only the IC may state. Both graders overruled the first label of P3-17 and P3-34; Till re-labelled them (person only). P3-34 was answered automatically (a floor miss); P3-17 reached a person only because the router guessed "impact" | P3-34, P3-17 | 2 routing rule (no rule for scope questions) | **M2** — scope-of-impact questions are person only, by a rule, not by luck |
| 3 | **A US customer asking about a dashboard gap "related to the incident on your status page" got the US alerting facts**: "page" counted as an alerting word, while the symptom belonged to the EU-only incident — the false-clustering trap of P3, a floor miss | P3-08 | 1b attach (rules) | **M3** — only symptom words count; a better match outside the region, or facts saying the component "is not affected", blocks the attach |
| 4 | **A stale promise:** at 19:38 the reply still said "Next update by 19:30 UTC" because the IC had not approved a new version | P3-21 | 3a template + the approval flow | **M4** — past next-update time → remind the IC, send the auto-acknowledgement until a new version |

Caught, not missed: the router called a security report (P3-15) and a feature question (P3-36) "status"; the security rule and the two-incidents rule (P3-36 fitted both open incidents) sent both to a person anyway — two classifier errors stopped by later rules, which is the point of one rung per part. Red-team rows (optional): `evals/adversarial_v0.csv`, four of five attacks held; the fifth is spec line A05.

## 3. Who graded, and how
Two graders, alone, with the guideline `evals/judge_rubric.md` written before grading and the same short notes per output type: **Till Lüder (A)** and **Benjamin Rasson (B)**, on the same 30 cases — the 27 cases where the agent produced a text (18 replies, 5 auto-acknowledgements, 3 IC drafts, 1 cluster update) and 3 escalations (P3-07, P3-17, P3-32). Counting rule fixed before grading: a case is "sendable as is" only when both say SEND.
- **Agreement:** the same verdict on **30 of 30** cases (100 %); criterion by criterion 149 of 150 answers (c3 on P3-13: the recovery time).
- **Where the graders overruled the labels:** P3-17 and P3-34 (see miss 2) — re-labelled by the labeller after the review, before the numbers above were computed. The prototype's outputs did not change: the same run, re-scored.
- Sheets: `evals/grades/grader_A.csv`, `evals/grades/grader_B.csv`. **The LLM judge** on the same 30 cases agreed with both graders on 23 of 30 (77 %) before one fix of its prompt, and on 30 of 30 after it (in-sample) — details in `evals/README.md`.
- **Known bias:** grader A (Till Lüder) also wrote the labels of P3-21 to P3-100 and, on both graders' advice, re-labelled P3-17 and P3-34 after grading; grader B never saw the labels. The 30 / 30 agreement includes that dependence.

## 4. What is demo data and what is eval data
- **P3-01 to P3-20** were read while we wrote `spec.md` and the brief in Session 3: they shaped the rules (the 0.10 margin, the security rule, the reopen rule). On them: action accuracy 0.95 (19 / 20), attach precision 0.86 (6 / 7); misses P3-08 and P3-12/P3-13 are in this group.
- **P3-21 to P3-50** were generated without labels by a separate Claude agent from the recipe in `evals/README_eval_set.md`, labelled by hand by Till Lüder on 17 November 2026 **before the run**, and never seen by whoever wrote the code. On them: attach precision 1.00 (11 / 11); misses P3-21, P3-24 and P3-34.
- **Demo data:** the ten inputs of `prototype/data/demo_inputs.csv` (D01–D10). One change was made while looking at them: the mock drafter now reads the IC's whole message (D10). No eval row was looked at while changing the code, and **no code changed after this run.**
- Training data of the router: `prototype/data/tickets_synthetic.csv`, 240 synthetic tickets, generated without access to `evals/`.

## 5. Next step
Build M1–M4, the held-out lines of `spec.md` and red row A05, then re-run on `evals/eval_set_v1.csv`. Its 50 new cases (P3-51 to P3-100) were labelled after this run; the same frozen prototype already shows 4 more floor misses there — two through the "only incident in the region" rule (P3-53, P3-54), one data question (P3-75) and one auto-acknowledgement before the incident opened (P3-79), see `evals/README.md`. **Before any shadow-mode pilot: spec v2 is built (M1–M4, the held-out lines, red row A05) and the floors read 0 on `evals/eval_set_v1.csv`, with at least 2 of 3 IC drafts publishable.**
