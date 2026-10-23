# 01 · Problem statement

**Team:** Team 8 · **Agent:** P3 · Proactive incident communicator · **Last updated:** 23 October 2026

> Every number says where it comes from: **measured**, **analogy** (a comparable, with its source) or **guess** (and how we will test it).

## 1. The problem in one sentence
**Support engineers at Telemetra, a DevOps and observability SaaS with 5,000 customer accounts, receive about 1,500 tickets, 70 % of them asking the same question, when an outage hits the platform their customers use to watch their own production, and customers wait about 40 minutes from the first ticket to the first update. This costs about €300k a year in support time over roughly 20 incidents, and pushes first response on every other ticket from minutes to hours. Today they answer with a copy-paste macro and update the status page by hand once engineering confirms the facts. Success looks like a median time from first ticket to first customer-facing update under 10 minutes, and at least 40 % of incident tickets closed without a human, with CSAT on incident tickets unchanged.**

| Number in the sentence | Value | Measured / analogy / guess | Source or test |
|---|---|---|---|
| Customer accounts | 5,000 | measured | Project proposals, P3 |
| Ticket volume during an incident | ×10 | measured | Project proposals, P3 |
| Incident tickets that say the same thing | 70 % | measured | Project proposals, P3 |
| Normal ticket volume | about 4,500 a month (150 a day) | guess | Not given in P3. About 0.9 tickets per account a month. Test: 12-month ticket log |
| Support team | about 12 engineers | guess | Test: HR headcount |
| Tickets per major incident | about 1,500 | guess (derived) | 150 a day × 10, for an impact window of about one day. Test: ticket log around past incidents |
| Major incidents a year | about 20 | analogy | PagerDuty survey (27 June 2024, n = 500 IT leaders): 25 high-priority incidents a year on average. Test: 12 months of status-page history |
| Time from first ticket to first customer-facing update | about 40 min | guess | Test: first ticket timestamp vs first status-page post in the last 12 postmortems |
| Cost of one ticket handled by a human | €10 | analogy | Session 2: €5 to €15 all-in for a B2B support ticket |
| Yearly cost of incident tickets | about €300k | guess (derived) | 20 incidents × 1,500 tickets × €10 |

## 2. Problem tree: from symptom to cause
- **Symptom** (what people complain about): tickets explode ×10 during every incident, the queue backs up, and first response on unrelated tickets slips from minutes to hours.
- **Problem** (what is actually going wrong): customers cannot tell quickly whether the problem is theirs or ours, and whether it touches their region or product, so they open a ticket.
- **Root cause** (5 Whys):
  1. Why do they open a ticket? The status page says nothing yet, or something generic.
  2. Why is it late and generic? Engineers are fixing the incident and nobody is assigned to write for customers. Support waits for engineering to confirm facts.
  3. Why does support wait? Support cannot see the incident channel in real time and does not know which accounts use the affected component or region.
  4. Why not? Monitoring, incident tooling, the status page, the ticketing tool and the account data are separate systems with no link between them.
  5. Why? Customer communication was never designed as a step of incident response: the runbook covers the fix, not the message.
- **What would fix the cause:** an owner and a pipeline from the incident signal to an approved, account-specific message. That fix has four parts:

| Part of the fix | Type of fix |
|---|---|
| Add a "comms lead" role and an approval step to the incident runbook | **Process change**, needed whatever we build |
| Status update and reply templates per incident type | **Documentation fix** |
| Auto-acknowledge every ticket that arrives during a declared incident, with the status-page link | **Rule** |
| Spot the incident signature before it is declared, match free-text tickets to the right incident, draft the first update from alerts and engineering chat, answer per account with approved facts only | **AI**, the part a rule cannot do reliably |

The process change and the rule come first. They are cheap, they belong to our baseline, and the AI must beat them.

## 3. Is AI the right tool?
| Question | Our answer |
|---|---|
| Is there a rule that solves 80 % of it? | No, but a rule solves part of it. "Auto-reply to every ticket opened during a declared incident" handles plain "are you down?" tickets. It fails three ways: it also catches unrelated tickets opened at the same time (false clustering), it misses everything before the incident is declared, and it cannot tell a customer whether their region or product is affected. Guess: 30 to 50 % of incident tickets handled correctly. In S4 we run the rule on the same 200 tickets as the prototype, as the baseline to beat. |
| Is it a prediction / generation problem, or an organisational decision? | Both, and we split them. Who may speak publicly, what must be approved and how fast are **organisational decisions**: they go into the runbook and governance.md, not into the model. Spotting the signature and matching tickets (classification), drafting the update (generation) and answering per account are what the AI executes. |
| Do we have the data, which, how much, who owns it? | Partly, to be checked. Monitoring error rates (ours), ticket history with incident tags (probably incomplete), incident timelines and postmortems (ours), status-page history (ours), the account to component and region mapping (billing or CMDB). Ticket text holds names and emails of customer employees: personal data, see governance.md. |
| What does one error cost, and who pays it? | It depends on the step. A wrong public statement (cause, ETA, "no data lost") is expensive and public: trust, contracts, maybe legal. Telemetra pays. An unrelated ticket wrongly attached gets a useless answer and waits: the customer pays, worst when that ticket is urgent. An incident ticket the agent misses is answered by a human, as today: low cost. |

**Level chosen: a bounded agent** (threshold rule on the monitoring stream as trigger, embedding similarity for clustering, an LLM for drafting and replies), with L2 gates on everything public. **Why not the level below:** a rule cannot match free text to the right incident or answer per account (see above). Classical ML alone needs labelled examples per incident type, but every incident is new and rare, and clustering cannot draft or answer. A single GenAI call (a copilot) covers drafting only, while the job chains five systems (monitoring, incident tool, status page, ticketing, account data) and sends messages. So it is an agent, kept small: seven steps, all listed in the README.

## 4. Why this agent: the four selection questions
| Criterion | Our answer, one line |
|---|---|
| High frequency: is the work done every day or every hour? | **No, and we know it** (P3 is the exception). About 20 major incidents a year. We justify it by intensity: about 1,500 tickets in a few hours per incident, plus smaller degradations almost every week. So we size per incident and evaluate on replays of past incidents. |
| Bounded decision space: can we list its tools and outcomes on one slide? | Yes. Tools: read monitoring error rates, read incident tool and channel, read account to component map, search and tag tickets, draft update, send reply with approved content, escalate. Three outcomes per ticket: attach and reply, attach and escalate, do not attach. |
| Measurable success: can we say in one sentence whether it succeeded on one ticket? | Yes. Per ticket: correctly attached and closed with approved content, not reopened within 48 h. Per incident: minutes from first ticket to first customer-facing update (the P3 primary metric). |
| Recoverable failure: if it is wrong, is the damage limited and reversible? | Mostly. A wrong reply can be corrected with a follow-up. A wrong public statement cannot be taken back, so it stays L2. A wrongly attached ticket can be urgent, so low-confidence matches go to a human and any reopen goes to the top of the queue. |

## 5. Press release (Working Backwards)
**Paris, 15 October 2027.** Telemetra today launched Incident Messenger, which tells engineering teams within minutes when a Telemetra incident affects them, before they lose time debugging their own stack. When error rates on the platform spike, every affected account now receives an update written for its own regions and products, approved by Telemetra's incident commander, and every follow-up question is answered from the same approved facts. Since the pilot, the median time from a customer's first ticket to Telemetra's first update has dropped to **8 minutes, from 40**. "Last month our dashboards went quiet at 2 am. Before I had even opened Slack, Telemetra had told us it was their EU ingestion and that our data was buffered, so we went back to sleep instead of paging three people," said the head of SRE at a fintech customer. Support engineers now spend incidents on the customers who need a person, not on pasting the same reply all night.

## 6. What would have to be true?
| # | Hypothesis | Measured / analogy / guess | How we will test it | Session |
|---|---|---|---|---|
| 1 | The agent attaches tickets to the right incident: at least 90 % of the tickets it attaches really belong to the incident (precision), it catches at least 70 % of them (recall), and it never merges two different incidents. | guess | Replay 200 labelled tickets from two past incidents, including unrelated tickets opened in the same hours and one window with two overlapping incidents. Compare with the time-window rule. | S4 prototype |
| 2 | The incident commander approves the first draft with minor edits only in at least 80 % of incidents, and the draft is ready within 5 minutes of the error-rate threshold being crossed. | guess | Run the prototype on the monitoring data, alerts and incident channel of 10 past incidents. An on-call engineer grades the drafts. Metric defined in S5. | S4 prototype · S5 metrics |
| 3 | Accounts in regions where the agent is live open at least 30 % fewer tickets per incident than accounts in regions where it is not live yet, and the effect still holds after the first weeks. | guess | Incidents cannot be randomised, so we argue for a **stepped-wedge** design: the agent goes live region by region in a random order over several weeks, so every incident has treated and not-yet-treated accounts. Effect read by time since go-live, to separate the real effect from the **novelty effect**. Sample size in S6. | S5 metrics · S6 A/B |

## 7. Do-nothing baseline
Doing nothing is not standing still, and it is not free.

- **What gets better on its own:** the team improves its macros and status-page templates, and more customers subscribe to status-page emails. About **5 % efficiency gain a year** on incident tickets (guess, same order as Session 2), worth about 5 % × 30,000 tickets × €10 ≈ **€15k a year**.
- **What gets worse on its own:** accounts and incident volume keep growing. If accounts grow 15 % a year (guess), incident tickets cost about €300k × 1.15 × 0.95 ≈ **€330k in 12 months**, up from €300k today.
- **What is not in that number:** first response on every other ticket still slips for hours during each incident, and customers still wait about 40 minutes for the first update.
- **The cheap alternative we must also beat:** the process change (comms lead role) plus the auto-acknowledge rule from section 2. A few days of work that capture part of the value. The agent is only worth building if it clearly beats this.

## 8. Persona, journey and stakeholders
- **Customer persona:** Sara, 31, on-call SRE at a fintech using Telemetra. *"When my dashboards go quiet at 2 am, I want to know within minutes whether it is Telemetra or us, so that I don't wake up my team for nothing, without opening a ticket and waiting."*
- **Agent persona:** Malik, 27, support engineer at Telemetra. Goal: clear the queue at good quality. Pain during incidents: 1,500 near-identical tickets, no facts yet, and the unrelated urgent tickets drowning underneath. Fear: sending something wrong in Telemetra's name.
- **Customer journey today:** alert fires → checks own stack (10 to 20 min) → checks status page (nothing yet) → opens a ticket → gets a generic macro → refreshes the status page → finally an update (about 40 min). **With the agent:** alert fires → proactive message about their region within minutes → no ticket, or a ticket answered with the approved facts.
- **Stakeholder map:** *Manage closely:* Head of Support (owner of the agent), VP Engineering and incident commanders (own every public word). *Keep satisfied:* Legal and DPO (cross-tenant leakage, AI disclosure), CFO (the business case). *Keep informed:* support engineers and CSMs, who carry adoption. *Monitor:* most customers, but one wrong public statement moves them up fast.
