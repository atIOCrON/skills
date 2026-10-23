# Cross-Pass Triage Ledger

Orchestrator alone writes `<feature_dir>/<plan_slug>.reviews/code-review-triage-ledger.md`
from triage and closure proposals; reviewers never write it. Tables:

```text
| ledger_id | first_pass | last_pass | reviewers | concern (one line) | files | architecture source | status | resolution evidence |
| family_id | invariant / runtime owner / supported path / observable failure | first_pass | last_pass | accepted_fix_cycles | epochs | disposition |
```

Non-terminal: open, accepted-fix-pending, re-opened, recurring-escalation,
architecture-review-required; all block clean completion. Terminal: resolved,
rejected, deferred-by-user. Allocate sequential `ledger-NN` and `family-NN`.

Match all prior passes/epochs before creating entries: family identity is invariant,
runtime owner, supported path and observed failure; concern is root cause within
family. Reviewer/ID/wording/files/design/epoch do not change identity. Static
hypotheses, nits/advice/nonmaterial mismatches/nonblocking existing issues/closure
observations/skill feedback create no entries. On match update last_pass/reviewers,
broaden concern/files only with evidence; no duplicate. Otherwise create smallest
root-cause row open with first/last=current. Accepted dispatch increments family
fix cycles; retain epochs/counts across redesigns. Architecture source names new
coordinator/state/retry/lifecycle/verification/layer, else `-`; add missing column
on old ledgers without losing history.

| Trigger | Required transition/action |
| --- | --- |
| Matched resolved/rejected concern recurs | re-opened; surface in current triage |
| Nonterminal last_pass - first_pass >= 2 | recurring-escalation with root-cause/design action; blocks completion, not in-scope continuation |
| New material failure modes from one family/architecture in any two discovery passes | architecture-review-required before further incremental dispatch; reassess native owner/removal/simplification/upgrade/narrow correction/prerequisite split; record selected new epoch/prior class in evidence |
| Two epochs fail for same reason | No third mechanism variation; change owner/mechanism or block if no viable in-scope design |
| Two accepted family fix cycles | Autonomous continuation, no third local variation |

Two-pass architecture trigger spans distinct findings/designs/epochs, not merely
consecutive passes or three appearances of one concern. Architecture-required
entries must retain that stronger gate while recording any recurrence escalation.
Continuation records trigger, confirmed/rejected hypotheses, fix/epoch history,
removal/simplification/native owner/upgrade/correction/split alternatives, decision
and one authorized next action. Allowed decisions: reject, complete, redesign,
change-owner, upgrade, dependency-correction, split, blocked-authority. One decision
authorizes at most one edit-and-pass cycle for a confirmed defect with viable
non-repeated disposition. Ask only when all viable options cross caller authority.

At exhausted five-pass cap retain nonterminal concerns and add durable marker:

```text
## Review Cap
- status: review_cap_reached
- limit: 5
- completed_passes: 5
- last_reviewed_sha: <full SHA>
- current_verified_sha: <full SHA>
- remaining_review_requirement: <why completion still needs another discovery pass>
```

No pass 6. This is plan outcome, not finding status/whole-run block. Finish accepted
fixes/checks/push/closure; caller may move to review with proportionate trim and
passed branch checks, keeping unresolved findings for separate human disposition.
Verified pinned tip may parent dependent work.

Consolidate three or more open/re-opened concerns sharing family/binding standard
into one fix request named for it; tag each resolution evidence
`consolidation_group: <short-name>` without merging distinct concern identities.
