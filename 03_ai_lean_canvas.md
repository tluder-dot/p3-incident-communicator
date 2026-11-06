# 03 · AI Lean Canvas · Incident Messenger (P3)

> One screen. Nine blocks from the classic Lean Canvas (Ash Maurya) + five blocks an AI product cannot skip. Short phrases; details in 01, 02 and 03_product_brief.md.

## The nine classic blocks
| Block | Our answer | Comes from |
|---|---|---|
| 1. Problem — top 3 pains | ×10 tickets per incident, 70 % "is it down?" · ~40 min from first ticket to first public update · unrelated urgent tickets buried for hours | 01 |
| 2. Users / customer segments | Support engineers (Malik) · incident commanders (approvers) · customers' on-call SREs (Sara) at Telemetra's 5,000 accounts | 01 (persona) |
| 3. Unique value proposition | One fast, approved, consistent update per incident instead of hundreds of duplicate tickets waiting in the queue | 01 (press release) |
| 4. Solution — the MUST features | IC console (draft + approve + pause) · ticket → incident attach with confidence · guardrail checker · eval-set of replayed incidents | 03 brief §3 |
| 5. Channels — where it lives | Inside the incident tool (IC) and the ticketing inbox (support); customers get a normal ticket reply | 03 brief §6 |
| 6. Value — per year | Base +€1.8k · EV −€5.5k vs do-nothing €15k and hurdle €50k → **NO-GO this year**; reopens at ~2× incident volume | 02 |
| 7. Cost structure | Integration €23k/yr · evaluation €15k · supervision €17.5k · monitoring €15k · re-evaluation €9k · tokens €0.3k · cost of error €3.7k (fixed lines = 95 %) | 02 |
| 8. Key metric | ≥ 63 % of status tickets correctly attached and sendable as is, with zero unapproved statements, zero cross-tenant mentions, zero merged incidents | 03 brief §7 |
| 9. Unfair advantage | Our own account → component/region map and incident history — no vendor has them | 02 (build / buy) |

## The five AI blocks
| Block | Our answer | Comes from |
|---|---|---|
| 10. Data — sources, rights, gaps | Tickets, monitoring, incident channel, status page, account map · contract + legitimate interest, eval reuse to clear with DPO · gaps: non-English, overlapping incidents, enterprise | governance.md · S3 |
| 11. Model — rung per part | Rules (trigger, reply template, guardrails) · classical ML (category) · embeddings (attach) · LLM (status draft only) → hybrid | 03 brief §5 |
| 12. Evaluation | `evals/eval_set_v0.csv`: 20 invented cases now, 200 replayed incident tickets by S5, two graders | evals/ |
| 13. Human in the loop | L4 trigger and confident attach · L1 below threshold · L2 IC approves update + first reply · L4 follow-ups on approved facts · person only for cause/ETA/data loss/credits · reply "human" or one-click pause = way back | 03 brief §2 |
| 14. Risks & governance | Never state unapproved cause/ETA/impact/data loss; never name another customer · rollback: any unapproved statement or precision < 90 % → pause, fall back to auto-acknowledge | governance.md |
