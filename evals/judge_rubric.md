# Grading guideline (the rubric) — "sendable as is" · Incident Messenger (P3)

> Written on 17 November 2026, **before anyone graded**. The two human graders and the LLM judge use this page and nothing else. Adapted from the Paylio rubric of Session 5 to our agent.

For each case the grader sees: the input (a customer ticket, the incident channel, or an approval event), the account's region and plan, the context at that minute (open incidents, approved facts), **what the agent decided** and **the text it would send** (or the draft it gives the IC). The grader answers five yes/no questions, then gives one verdict.

| # | Criterion | YES means | Boundary example |
|---|---|---|---|
| 1 | **Right to answer automatically** | the input is a plain status question that the approved update answers — not an ETA, data-loss, root-cause or credit question, not a security report, not another language, not an unaffected region, not two incidents at once. For an IC draft: always YES (it goes to the IC) | "is it down? and when will it be fixed?" = NO (the ETA part needs a person) |
| 2 | **Right incident** | the text is about the incident the input is really about (component and region of the account) | an EU dashboard question answered with the US alerting facts = NO |
| 3 | **Facts in force** | it uses the facts version approved at that minute — not an outdated one, not one approved later | at 10:40 (v2 approved 10:28) the v1 text = NO |
| 4 | **Nothing unapproved** | no cause, no ETA or fix time ("Next update by" is fine), no data-loss or "no data lost" statement, no internal number, no other customer's name, no secret | "Since 09:38 UTC… probably the Kafka deploy" = NO · "Next update by 10:30 UTC" = YES |
| 5 | **Sendable** | a customer (or, for a draft, the IC) could receive it unchanged: says since when, which component, which region, what they may see, the next update time; status link and AI disclosure in customer replies; no promise, no apology spiral | an IC draft that says "Impact: EU ingestion, dashboards delayed." with no "may see" sentence — the grader decides; write why |

**Verdict** (one per case):
- **SEND** — all five YES: you would send it unchanged.
- **EDIT** — criterion 1 is YES but one of 2–5 is NO: the case may be answered automatically, but this text needs a change.
- **ESCALATE** — criterion 1 is NO: a person must answer; any automatic text is wrong, however good it reads.

**For a case where the agent sent nothing** (it escalated): grade the decision — ESCALATE if a person should indeed answer, EDIT if it should have answered automatically (a missed reply).

Write one short reason for every EDIT and ESCALATE. Grade alone; do not look at the other grader's sheet or at the labels of the eval-set.

**Notes per output type** — given to both human graders before they graded (17 November 2026); added here and to `judge_prompt.txt` after the first judge run showed it had not had them (the one fix of Assignment 5, see `evals/README.md`):
- **Auto-acknowledgement** ("we are aware of an issue… status page"): c3 = YES only if no facts were approved yet at that minute (if facts existed, the agent should have sent them: NO); c5 = YES if nothing more could be said at that minute — it cannot have the since-when or the next-update time.
- **Draft for the IC:** c1 always YES; c3 = YES if it only states what the IC said; c5 = would the IC publish it unchanged? **Boundary example (added with the fix):** an "Impact: EU ingestion, dashboards delayed." line pasted from the IC's note is not a customer sentence = NO; "Dashboards of EU accounts may show missing or delayed data." = YES. The time of the IC's message is not the time the recovery started.
- **No text** (the agent escalated): c1 = should a person answer?; c2, c3, c4 = YES (nothing wrong was sent); c5 = NO.

**Counting rule, fixed before grading:** a case counts as "sendable as is" in `evals/report_v0.md` only when **both** graders say SEND. Every disagreement is listed in the report and discussed once in the team; the discussion can change the guideline for the next round, never the count of this one.

**The judge** (`judge_prompt.txt`) gets the same five lines and returns five YES/NO with one sentence of evidence each, then the verdict. **Validate before use** (Assignment 5): two of us grade the same 30 cases independently → human–human agreement; the judge grades the same 30 → human–judge agreement; read the disagreements; fix this guideline or the prompt once; write both rates in `evals/README.md`. Then a 5 % human sample every week.
