# 03 — User research · Incident Messenger (P3)

> **Status: simulated interviews.** The three conversations and the usability test below were written as role-play scenarios with the agreement of the lecturer (C. Oprean, 6 November 2026), because we could not reach real users before the deadline. **They are not real user evidence.** We will replace them with real conversations (or classmates in role) before Session 6, and update brief v2 if the findings change.
> Mom Test rules (Rob Fitzpatrick): past behaviour, no pitching, never "would you use…?".

## Who we "talked" to (simulated personas)
| # | Who (role, company type) | Real user or simulated? | Date | Interviewer · note-taker |
|---|---|---|---|---|
| 1 | Support engineer, B2B monitoring SaaS (~40 people in support) | simulated | 6 Nov 2026 | Benjamin · Till |
| 2 | On-call SRE at a fintech using a third-party observability tool | simulated | 6 Nov 2026 | Benjamin · Coline |
| 3 | Engineering lead who acts as incident commander, DevOps SaaS | simulated | 6 Nov 2026 | Benjamin · Evaluna |

## Interview guide (P3 version — about the past)
1. Tell me about the last time a tool you depend on went down. What happened, step by step?
2. How did you find out whether the problem was yours or theirs? How long did that take?
3. What did you do while you waited — ticket, status page, Slack? What did you get back?
4. *(Support)* The last flood of tickets during an incident: how did you sort them? How did you spot the ones not about the incident?
5. *(IC)* The last status update you wrote: who gave you the facts, how long did it take, what did you leave out on purpose?
6. When it went wrong (wrong update, missed urgent ticket), what happened next?
7. If you could change one thing in that moment, what would it be?

## What we heard (simulated, paraphrased notes)
| # | Quote or observed behaviour | Which part of our brief it confirms or contradicts |
|---|---|---|
| 1 | Support engineer: during the last outage they pasted the same macro "about 300 times" and only noticed two hours later that a customer's account-lockout ticket had been tagged as incident. | **Confirms** pain step 2 and the false-clustering trap; supports keeping "Not this incident" one click away. |
| 2 | Support engineer: the first thing they check on a new ticket is the customer's region, "because half the time it's not even the affected region". | **Changes** the cluster view: show the account region on every ticket, not only in the recipient list. |
| 3 | SRE: last time their dashboards went blank they spent ~20 min checking their own agents before opening the vendor's status page, which still said "all systems operational". | **Confirms** the 40-min gap and the do-nothing pain; the value is being told early, not a chatbot. |
| 4 | SRE: what they wanted from the vendor was "which region, since when, and when the next update comes" — not the cause. | **Confirms** the guardrail: an update without cause/ETA is still useful if it gives a next-update time. |
| 5 | SRE: they ignore ticket replies that look like a generic macro and refresh the status page instead. | **Contradicts** part of our value: the reply must carry account-specific facts (region) to be read. |
| 6 | IC: in the last incident, an engineer posted "probably the Kafka deploy" in the channel; it ended up in a customer email and was wrong. | **Confirms** the drafter must not copy unconfirmed causes from the channel (eval case P3-12). |
| 7 | IC: they approve status updates from their phone, often while still on the bridge call. | **Changes** the surface: the approval screen must work on a phone, with approve in one tap. |
| 8 | IC: "if I have to read 40 tickets before approving, I won't"; they trust a count and a few examples. | **Changes** the console: show the recipient count and 3 sample tickets, not the whole list, by default. |

## Usability test — one task, think aloud, don't help (simulated)
**Prototype link:** see `03_prototype_link.md`
**Task:** "An incident has just been declared on EU ingestion. Fix the draft so it can be published, find the ticket that should not be in the cluster, and approve."

| Tester | Finished without help? | Where they hesitated | What they expected instead |
|---|---|---|---|
| IC persona (#3) | yes, ~3 min | Did not understand at first why "Approve" was greyed out; read the red guardrail box after ~30 s | The blocked words highlighted directly in the draft |
| Support persona (#1) | yes, ~4 min | Scrolled the cluster twice before spotting the billing ticket (T-4823, confidence 0.81) | A visual flag on tickets whose words do not match the incident component |

## Desirability gate — do they want it? (on simulated evidence)
- [x] 2 of 2 testers finished the task without help
- [x] They told us what they did last time — not what they would do
- [x] At least one said "I want this before…" — the IC: before the next on-call rotation
- [x] Our out-of-scope list grew (no cause speculation copied from the channel); our success criterion did not move

**Decision:** go to the Session 4 build with brief v2 — **provisional**, to be confirmed by real interviews before Session 6.
