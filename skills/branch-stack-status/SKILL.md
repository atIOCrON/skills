---
name: branch-stack-status
description: Report the current status and completed review-loop counts for an ordered branch stack.
disable-model-invocation: false
metadata:
  layer: capability
---

# Branch Stack Status

Input: an ordered list of branch names and, when available, the release
manifest path.

Work read-only. Do not edit files, refs, plans, or the manifest.

1. Read the current release manifest. For each requested branch, resolve its
   plan file from the manifest. If absent, search plans/ and branch evidence.
   Never present a predecessor's plan as the branch's own plan; say "No
   dedicated plan" when appropriate.
2. Inspect the plan stage, exact branch tip, trim ledger, correctness triage
   ledger, reviewer artifacts, and documented mappings after restacks.
   Report a snapshot time. Preserve the user's branch order and include
   every requested branch exactly once.
3. Count completed loops across the recorded branch history:
   - Trim Loops: completed, validated three-reviewer trim passes.
   - Code Loops: completed, validated three-reviewer correctness discovery
     passes. Use historical_completed_passes plus completed_passes when
     the manifest records both as distinct periods. Otherwise confirm the
     numbered passes against their ledgers.
   - Do not count launched but incomplete passes, reviewer transport retries,
     same-session format repairs, targeted closures, test-only closure
     mappings, or valid restack mappings.
   - A documented zero-diff trim applicability decision counts as zero loops.
   - If counts conflict or cannot be verified, show "Unclear" and explain.
4. Assign one status using this precedence:
   - Exhausted: correctness review reached its cap without a clean result.
   - Complete: this branch's own correctness reviews are clean and finished.
     An unfinished ancestor or external release check does not change that.
   - Code Review Started: correctness discovery has begun but is not finished.
   - Trim Finished: trim is proportionate on the current tip, or formally
     inapplicable to a zero-diff branch, and correctness has not begun.
   - Trim Started: trim has begun but has no proportionate current-tip result.
   - Implementation Finished: a candidate is committed and verified, with no
     trim review begun.
   - Implementation Started: implementation or required branch verification
     has begun but no verified candidate is finished.
   - Not Started: no implementation work has begun.
5. Output a Markdown table with exactly these columns:
   Branch | Plan file | Status | Trim Loops | Code Loops

Use clickable absolute links for plan files. Briefly explain missing plans,
zero-diff branches, exhausted caps, and any provisional Complete branches.
Do not equate individual branch completion with release readiness.
