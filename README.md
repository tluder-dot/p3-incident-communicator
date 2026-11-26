# Team 9 · Proactive incident communicator for DevOps SaaS

**Course:** Data & AI Product: From Diagnosis to Delivery (MSA-DAT07-04) · Albert School · shared project with Agentic Workflows
**Cohort:** M2-INTER-1

## Team
| Name | Git handle |
|---|---|
| Till Lüder | tluder-dot |
| Evaluna Barth | evalunab |
| Benjamin Rasson | benji1759 |
| Teo Desquatrevaux | teodesquatrevaux |
| Coline Renauld | colinernld |

## Our agent
- **Starting point:** P3 · Proactive incident communicator, DevOps / observability SaaS
- **The company:** Telemetra, a DevOps and observability SaaS (metrics, logs, alerting) with 5,000 customer accounts. About 4,500 tickets a month in normal times, ×10 during a platform incident, when 70 % of tickets say the same thing. About 12 support engineers.
- **The job, in one sentence:** When error rates in our monitoring stream cross a threshold or a spike of similar tickets arrives, the agent clusters the incoming tickets under that incident, drafts the status update for the incident commander, and replies to affected customers with the approved facts and the status-page link, producing one fast, consistent update per incident instead of hundreds of duplicate tickets waiting in the queue.
- **Trust level per step** (course scale: L1 suggests · L2 drafts, a human approves every reply · L3 acts on a scope, with sampling · L4 acts autonomously under a threshold · L5 fully autonomous):

| # | Step | Trust level | Why |
|---|---|---|---|
| 1 | Detect an incident signature (error-rate threshold in the monitoring stream, a spike of similar tickets, or an incident declared in the incident tool) and open a cluster | L4 | Internal only, reversible, alerts the support lead |
| 2 | Attach incoming tickets to the cluster | L4 above the confidence threshold · L1 below it | Internal tag, reversible. Uncertain tickets go to a human queue: false clustering is the P3 trap |
| 3 | Draft the status update from alerts and the incident channel | **L2** | Public and irreversible: the incident commander approves or edits before it is published |
| 4 | First reply to the cluster and proactive message to affected accounts, with the status-page link | **L2** | The incident commander approves the first message of each cluster and the list of affected accounts |
| 5 | Follow-up replies and update notifications, using only approved facts | **L4** | Only once the cluster is approved. Same content as the approved update, matched to the account's components and region |
| 6 | Questions beyond the approved facts (root cause, an ETA not yet published, data loss, SLA credits, contracts) | L1 | The agent suggests a summary, a human answers |
| 7 | Resolution notice and closing of clustered tickets | L2 for the notice · L4 for sending it to the cluster | Same pattern as steps 3 to 5 |

- **One thing it must never do:** publish or send a statement about the cause, the ETA, the scope of impact or data loss that the incident commander has not approved.
- **Since Session 3** (`03_product_brief.md`): proactive messages to accounts that have not written are out of scope (WON'T), and customer replies are templates filled with the approved facts — no model writes to a customer.

## Where we stand (26 November 2026)
- **The prototype** (`/prototype`, four steps by four authors): on 50 hand-labelled cases, **15 of the 16 status tickets that should get an automatic reply got one two graders would send unchanged** (94 %; 84 % re-weighted to real traffic) — criterion 63 %. Attach precision 0.94, zero unapproved statements, zero merged incidents (`evals/report_v0.md`).
- **Not releasable yet:** two replies went where a person had to answer (six on the 100-case set) and none of the three drafts for the incident commander was publishable unchanged. Every miss is a line of `spec.md` v2.
- **The decision** (`08_launch_memo.md`): **no-go for customers this year, conditional go** at about 2× today's incident volume and zero floor misses — reply quality is not the bottleneck, incident volume is. From 1 December the comms-lead role, the auto-acknowledge rule and the incident banner; re-decided on 14 January 2027. `06_07_experiments_operations.md` says how we would then prove it.
- **Run it:** `pip install -r prototype/requirements.txt` · `python prototype/evals.py evals/eval_set_v1.csv` · `streamlit run prototype/app.py` (details in `prototype/README.md`).

## Repository structure
One numbered file per session. Every member authors commits in at least four of the numbered files.

| File | Session | Status |
|---|---|---|
| `00_pitch.md` | before S3, only if you bring your own idea | not needed (we start from P3) |
| `01_problem_statement.md` | S1 and S2, Assignment 1 | done · where the hypotheses stand after S4–S5 (§6) |
| `governance.md` | created for Assignment 1, one line added every session | Sessions 1 to 7 done (checkpoints and switch, harm threshold, experiments, trace) |
| `02_sizing.xlsx` | S2, Assignment 2 | done |
| `02_investment_memo.md` | S2, Assignment 2 | done · §6 after the prototype: still NO-GO |
| `03_product_brief.md` | S3, final in S8 | final (v1.0): v2 + §11 what the eval changed + §12 the decision |
| `03_ai_lean_canvas.md`, `03_user_research.md`, `03_prototype_link.md` | S3, Assignment 3 | canvas with the measured numbers · interviews simulated (agreed with the lecturer, 6 Nov) · clickable mock v0.1 + working prototype v1 |
| `04_architecture.md` | S4, Assignment 4 | done |
| `05_metrics.md` | S5, Assignment 5 | done |
| `06_07_experiments_operations.md` | S6 + S7, Assignment 6 + 7 (one file instead of `06_ab_protocol.md` and `07_operations.md`) | done |
| `08_launch_memo.md` | S8 | done · no-go this year, conditional go |
| `spec.md` | skeleton in S3, final in S8 | final (v1.0): v2, every eval miss is a line |
| `/prototype` | from S4, Assignment 4 | four steps (router + attach, routing rule, drafter, guardrail checker), one commit per step by four authors · IC console · rollback drill |
| `/evals` | from S4, Assignments 4 and 5 | `eval_set_v0.csv` (50) and `eval_set_v1.csv` (100), labelled by hand before the run · `report_v0.md` · grading guideline, two graders, LLM judge · red-team rows · switch test log |

## Rules
- Commit with your own Git account: the individual question at the oral is about a commit you signed.
- Tag the final version `v1.0` before the first oral of your cohort. No commits after the first oral starts.
