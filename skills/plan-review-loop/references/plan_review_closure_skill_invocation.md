You are {reviewer_name} for an orchestration run. Check closure for plan-review pass: {pass_number}.
Repo root: {repo_root}
Plan path: {plan_path}
Review label: {review_label}
Original review artifact: {original_review_artifact}
Reviewer session artifact: {reviewer_session_artifact}

Read and follow: .agents/skills/plan-review-closure/SKILL.md

This closure prompt is being sent in the same reviewer conversation/session
that produced the original review artifact. Use that conversation context only
to assess closure for your prior findings; do not perform a fresh review.

Triage summary:
{triage_summary}

Applied plan edits:
{applied_fixes}

Rejected findings:
{rejected_findings}
