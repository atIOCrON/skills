---
name: next-plan
description: Review draft plans one at a time, recommend implement, investigate, hold or supersede, and handle next-plan decisions.
metadata:
  layer: capability
---

# Next Plan

Present one plan in about 100 words, then wait for the user's decision.

## Choose

- Review the supplied plan or choose from the requested folder; default to the
  active project's `plans/specs/draft`.
- Respect exclusions and decisions in chat and review records. Skip previously
  presented plans and, unless requested, plans created today. Use creation
  evidence, not modification time.
- Prioritise customer, security or operational benefit against effort, risk,
  verification cost and dependencies. Check the plan, metadata, relevant current
  code and related owners for completed or superseded work. Separate current
  evidence from historical findings and uncertainty.

## Present

**[Plan title](absolute-path)** — **Recommend: implement / investigate / hold / supersede.**

- **Proposal:** The outcome, in one sentence.
- **Reason:** Value and rationale.
- **Effort:** Small, moderate or large, plus the decisive caveat if any.

End with a short decision question. Include only decision-relevant detail.

## Continue

- “Next” skips without a status change. Answer follow-up questions before advancing.
- Record explicit decisions through the project's lifecycle conventions. Preserve
  approvals and evidence; move folders as requested or required and repair metadata
  and current links. Hold, superseded and completed remain distinct.
- Confirm decisions briefly, then present the next plan unless asked to stop.
  Implementation, deployment and external messages require separate instructions.
