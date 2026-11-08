# 03 · Product brief · Incident Messenger (P3) · v2

> Session 3. One page. Built from `01_problem_statement.md`, `02_sizing.xlsx` and `02_investment_memo.md`.
> v1 now. v2 after the users: sections 9 and 10 are filled only from `03_user_research.md`.

**Team:** Team 8 · **Starting point:** P3 · Proactive incident communicator · **Version:** v2 — 6 November 2026 (v1 → v2 after simulated user research)

## 1. Problem, user, do-nothing *(from 01)*
- **Problem in one sentence:** during a platform incident, Telemetra's 12 support engineers receive about 1,500 tickets, 70 % of them asking "is it down?", and customers wait about 40 minutes for the first update; incident tickets cost about €300k a year (20 incidents × 1,500 tickets × €10).
- **User (persona):** Malik, support engineer — goal: clear the incident queue without missing the urgent unrelated tickets — pain: 1,500 near-identical tickets, no approved facts yet. **Approver:** the incident commander (IC), who owns every public word. **End customer:** Sara, on-call SRE, who wants to know in minutes whether it is Telemetra or her own stack.
- **Do-nothing baseline:** better macros and status templates, about 5 % more efficient a year (≈ €15k), while volume grows; incident tickets cost ≈ €330k in 12 months. The cheap alternative to beat: a comms-lead role in the runbook + an auto-acknowledge rule.

## 2. The process — as-is and to-be (per incident of ~1,500 tickets)
| # | Step | Who today | Minutes (source) | Error rate (source) | Cost of an error | Automate / augment / keep human (test it fails) | Trust level | Minutes after | Metric for this step |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Notice the incident and tell support | On-call engineer → support lead | ~15 min after the first alert before support knows (guess: postmortem timestamps) | support learns late in most incidents (guess) | 15 min of tickets with no answer | **Automate** — passes all 8 tests (clear signal: error-rate threshold, declared incident) | L4 (internal, reversible) | 0 | minutes from threshold crossed to cluster opened |
| 2 | Read each ticket, decide if it is about the incident, tag it | Support engineers | 2 min × 1,500 = 50 h (guess, ticket-log sample) | ~10 % wrongly tagged (guess) | unrelated urgent ticket buried (€10–50, worse if security) | **Augment / automate above a threshold** — fails test 6 (errors not always cheap: false clustering) | L4 above confidence threshold · L1 below (human queue) | 0.2 min/ticket (only the low-confidence ones) | attach precision and recall vs labels |
| 3 | Collect the facts (component, region, impact) from the incident channel | Support lead, waiting for engineering | ~15 min per update (guess) | facts outdated or incomplete (guess) | wrong reply to hundreds of accounts | **Augment** — fails tests 4 and 7 (facts change minute by minute) | L1 (agent summarises the channel; IC confirms) | 5 | share of drafts with no fact missing |
| 4 | Write and publish the status update | Incident commander / engineer | ~10 min of writing, first post ~40 min after first ticket (guess: status-page vs ticket timestamps) | generic or late (guess) | **public, irreversible: cause/ETA/data-loss statement** | **Augment** — fails tests 5 and 6 (must be explainable, error is public) | L2 (agent drafts, IC approves) | 2 | minutes first ticket → first public update; % drafts approved with minor edits |
| 5 | Reply to each ticket (macro + link) | Support engineers | 3 min × 1,050 status tickets = 52 h (guess) | ~5 % wrong region or outdated (guess) | customer debugs own stack, asks again (~€25, sizing) | **Automate after approval** — first message L2, follow-ups L4 on approved facts only | L2 first message of the cluster · L4 follow-ups | 0.1 | share of replies sendable as is (two graders) · reopen rate 48 h |
| 6 | Questions beyond approved facts (cause, ETA, data loss, SLA credits) | Support engineers + IC | 8 min each, ~450 tickets (guess) | — | legal/contractual (€400–1,500, sizing) | **Keep human** — fails tests 5, 6 and 7 | Person only (agent attaches a summary, L1) | 8 | time to first human answer on these tickets |
| 7 | Resolution notice, close the clustered tickets | Support engineers | 1 min × 1,500 = 25 h (guess) | tickets closed that were not about the incident (guess) | a real problem closed silently | **Automate after approval** | L2 notice · L4 sending it to the cluster | 0.05 | reopen rate after closing |

**Where the pain sits (the two steps):** step 2 (triage of ~1,500 tickets, ~50 h per incident, and the false-clustering trap) and step 4 (the 40-minute wait for the first public update, which is what creates the ticket flood).
**The way back to a person (designed first):** every automated message ends with "reply *human* to reach an engineer"; any reply that is not a thank-you, any low-confidence ticket and any reopen goes to the top of the human queue; the IC or support lead pauses all automated sending in one click and the system falls back to the plain auto-acknowledge rule.
**Where the governance line sits:** between step 3 and step 4. Nothing about cause, ETA, scope of impact or data loss leaves Telemetra without the IC's approval; nothing about another customer ever leaves at all.

*Minutes after, per incident: ≈ 50 + 4 + 52 + 60 + 25 h of human time before → ≈ 5 + 1 + 2 + 60 + 1 h after (step 6 stays human). All minutes are guesses to measure on 12 postmortems and a two-week ticket sample.*

## 3. Features — RICE and MoSCoW
Reach = incident tickets a month touched by the feature, from `02_sizing.xlsx` (2,500 incident tickets, 1,750 status questions).

| Feature | Reach / month | Impact (0.25–3) | Confidence | Effort (pw) | RICE | MoSCoW |
|---|---|---|---|---|---|---|
| Guardrail checker: block any unapproved cause / ETA / impact / data-loss wording and any other customer's name | 1,750 | 2 | 100 % | 0.5 | 7,000 | **MUST** |
| Auto-acknowledge rule during a declared incident (the baseline, and the fallback) | 2,500 | 0.5 | 100 % | 0.25 | 5,000 | SHOULD |
| Eval-set: replay of past incidents, labelled by two people | 2,500 | 1 | 100 % | 1 | 2,500 | **MUST** |
| Category router: status / impact / cause-credit / unrelated | 2,500 | 1 | 80 % | 1 | 2,000 | SHOULD |
| Ticket → incident attach, with confidence score and a human queue below threshold | 2,500 | 3 | 50 % | 3 | 1,250 | **MUST** |
| IC console: drafted status update + first cluster reply + recipient list, approve / edit, pause switch | 1,750 | 2 | 50 % | 2 | 875 | **MUST** |
| Proactive message to affected accounts before they open a ticket (needs account → component map) | 1,750 | 3 | 50 % | 4 | 656 | WON'T |
| Early detection from the error-rate stream, before the incident is declared | 2,500 | 1 | 50 % | 2 | 625 | COULD |
| Answers to "is my data or alerting affected?" | 500 | 2 | 50 % | 3 | 167 | WON'T |
| Multilingual replies | 250 | 1 | 50 % | 2 | 63 | WON'T |

- **MUST (4):** IC console (draft + approve + pause) · ticket → incident attach with confidence · guardrail checker · eval-set of replayed incidents.
- **SHOULD:** auto-acknowledge rule (fallback) · category router.
- **COULD:** early detection from the error-rate stream.
- **WON'T this time (dated 6 Nov 2026) — the out-of-scope list:** (1) proactive messages to accounts that have not written; (2) "is my data affected?" answers (expected error cost €15.6k > value €5.6k, sizing); (3) root cause, ETA, SLA credits, compensation; (4) multilingual replies; (5) publishing anything to the status page without the IC; (6) LLM-written replies to customers (replies are templates filled with approved facts); (7) incidents not on the Telemetra platform (customer's own outage).
- **The feature that tests our flip assumption, and why it is a MUST:** ticket → incident attach. Its RICE is only 5th of 10 because our confidence is 50 %: false clustering is the P3 trap, and whether follow-ups can run at L4 at all depends on its precision. It is the riskiest assumption (H1), so we build it first to learn. The other half of the flip — incident **volume** (×2 needed, memo §2) — is not a feature: it is checked on the 12-month ticket log.
- **The cut that hurt the most:** proactive messages to accounts that have not written yet. It is the heart of our press release, but it needs the account → component map and a higher trust level than this MVP can earn.

## 4. Data *(six-question audit — details in governance.md, Session 3)*
Real sources at Telemetra: ticket text (customer-written, personal data), monitoring error rates, incident tool timeline and channel, status-page history, account → component/region map. Incident tags in the ticket tool are incomplete and have no labelling guideline, so we relabel. Coverage gaps: non-English tickets, overlapping incidents (rare but catastrophic), enterprise accounts. Legal basis: contract (answering) and legitimate interest (clustering); reusing past tickets for the eval-set is a new purpose to clear with the DPO. Leakage: one cluster mixes hundreds of tenants, so replies are built only from approved facts + that tenant's own data; eval splits by incident. Freshness: component names and regions change, so only the last 12 months. **For the MVP we use invented incidents only — never real customer data.**

## 5. Model — one rung per part
| Part | Rung | Why the rung below fails |
|---|---|---|
| Trigger: open a cluster (error-rate threshold, declared incident, ticket spike) | 1 · rules | — (lowest rung; thresholds are explainable and enough) |
| Category of a ticket (status / impact / cause-credit / unrelated) | 2 · classical ML (TF-IDF + logistic regression) | keyword rules miss free-text phrasing ("dashboards blank", "502s since 9:40") |
| Attach a ticket to the right incident | 3 · pretrained embeddings + rule features (time window, component, region) | a time-window rule also catches unrelated tickets and cannot split two overlapping incidents; a supervised classifier needs labels per incident, and every incident is new |
| Draft the status update from alerts + incident channel | 3 · pretrained LLM, inputs restricted to alerts and channel, IC approves | templates cannot summarise a free-text engineering channel |
| Reply to the cluster and follow-ups | 1 · template filled with approved facts + the account's region + status link + AI disclosure | — (an LLM here would add the risk of unapproved wording for no gain) |
| Guardrail checker | 1 · rules (approved-facts allowlist, ETA/cause/data-loss patterns, tenant-name list) | — (the model is not trusted with this) |
| **The MVP** | **4 · hybrid** | each part on its own rung, not because it sounds advanced |

## 6. Where it lives (integration surface)
- **IC console:** a panel inside the incident tool / incident channel: the cluster, the drafted update, the first reply, the recipient list, Approve · Edit · Pause. Speed: draft ready within 5 min of the trigger.
- **Support engineer:** a view inside the ticketing inbox: the cluster tag, the confidence, the low-confidence queue, "human only" tickets on top.
- **Customer:** a normal ticket reply (email / portal) with the AI disclosure line and the status-page link.
- **Fallback:** if the agent is paused or down, the auto-acknowledge rule answers with the status-page link.
- **Who sees the log:** support lead, IC, auditor — every draft, approval, sent message and model version.

## 7. Success criterion — one sentence
> **By Session 5, on our eval-set (20 cases now, 200 replayed incident tickets by Session 5), at least 63 % of "is it down?" status tickets are attached to the right incident and get a reply that two graders would send unchanged — and no reply states a cause, ETA, scope of impact or data loss that the incident commander has not approved, names another customer, or merges two different incidents.**

*Threshold = our base case in `02_sizing.xlsx`: 90 % of status tickets answerable × 70 % deflection = 63 % of status tickets (≈ 44 % of all incident tickets). The memo shows the decision is flipped by volume (×2), not by deflection: this criterion checks that the base case holds; the volume check runs on the ticket log.*

## 8. Risks and rollback trigger
- **Top risks:** false clustering buries an urgent unrelated ticket (security report, billing lockout); a wrong public statement (cause, ETA, "no data lost"); cross-tenant leakage in a cluster of hundreds of accounts; the IC is too busy to approve and nothing goes out (worse than today); low incident frequency gives too few cases to learn from.
- **Rollback trigger (one line):** any unapproved statement or cross-tenant mention sent, or attach precision below 90 % on a live incident → the IC or support lead pauses the agent in one click and the auto-acknowledge rule takes over.

---
*v2 only — after the users (fill from `03_user_research.md`, never invent)*

## 9. What the users changed
*Source: `03_user_research.md` — simulated interviews (agreed with the lecturer), to be confirmed with real users before Session 6.*

| Change | Evidence (who said / did what) |
|---|---|
| Account region shown on every ticket in the cluster | Support persona checks the region first on every new ticket (note 2) |
| Customer reply always states the affected region and the next-update time | SRE ignores generic macros (note 5) and wants region + next update, not the cause (note 4) |
| Drafter never copies a cause from the incident channel, even "probably…" | IC saw an unconfirmed Kafka cause reach a customer email (note 6) |
| Approval screen works on a phone; approve in one tap | IC approves from the phone during the bridge call (note 7) |
| Console shows the recipient count + 3 sample tickets by default, full list on demand | IC will not read 40 tickets before approving (note 8) |
| Blocked words highlighted inside the draft | IC hesitated ~30 s on the greyed-out Approve button (usability test) |
| Flag on attached tickets whose words do not match the incident component | Support persona scrolled twice before finding the billing ticket (usability test) |

**Out-of-scope list grew:** cause speculation from the channel (added to WON'T). **Criterion did not move:** still ≥ 63 % of status tickets correctly attached and sendable.

## 10. What they could not decide
- **The threshold (63 %)** — set by our sizing (02), not by users.
- **The model per part** — decided by the eval-set in Session 4.
- **The legal basis for reusing past tickets** — the DPO decides (governance.md).
- **Whether the IC approval step stays L2** — the VP Engineering decides; users can only tell us how fast they need it.
