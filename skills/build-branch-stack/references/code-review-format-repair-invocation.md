# Coordinator Review Normalization

Use complete, understandable reviews even if formatting validation fails.
Repair headings and finding IDs yourself; never resume or restart a reviewer
solely for formatting. Preserve the original and save a normalized copy without
changing findings, severity, evidence, recommendations, uncertainty or conclusions.
Disposition false positives in triage; retain them in the review.

Preserve valid IDs. Assign `code-p<pass_number>-<reviewer_slug>-NN` to malformed
or absent IDs from confirmed launch context and update references. Disambiguate
duplicate labels by source occurrence/location only when references are clear;
record each occurrence without merging findings.

Use the usual seven sections when faithful to the response. Never invent proof,
severity, proportionality, a clean verdict, or `- None` for an omitted section.
Otherwise keep a faithful representation and retain serialization diagnostics.
Check completeness, scope and commit identity against the whole review and saved
prompt, pack and session evidence. Existing proof requirements still govern
accepted material findings; reject unsupported findings in triage.

Clarify only missing or unclear substance, scope or commit identity. Recover
saved evidence first, then ask the originating reviewer a focused content question
or the user for decisions they own. Never accept an incomplete review or silently
resolve conflicting SHAs.

If automatic repair is insufficient, save a normalized draft and assessment JSON
inside the pass directory. Confirm completeness and preservation before setting
the fields below; hashes bind the assessment to the exact responses:

```json
{
  "normalized_path": "/absolute/pass/cursor-normalized-draft.md",
  "source_sha256": "<SHA-256 of preserved raw response>",
  "output_sha256": "<SHA-256 of normalized draft>",
  "reviewer": "cursor",
  "pass_number": 1,
  "review_sha": "<confirmed full review commit SHA>",
  "review_scope": "<confirmed base, tip and scope>",
  "scope_identity_evidence": "<saved prompt/pack/session paths and identity confirmation>",
  "semantic_complete": true,
  "all_findings_preserved": true,
  "identity_confirmed": true,
  "completeness_reason": "<why coverage is complete; resolution of apparent content gaps>",
  "preservation_reason": "<how all findings and their meaning were retained>",
  "finding_ids": [{"source_occurrence": 1, "old": "cursor-1", "new": "code-p1-cursor-01"}],
  "changes": ["<presentation edits and any remaining serialization diagnostics>"]
}
```

Run the helper with `--coordinator-assessment <json>` as shown in
`multi-review-pass-runner.md`. Link the original, draft, assessment and resulting
normalization record from triage/pass evidence. Proceed with triage; all three
reviews must be complete and reconciled before counting the pass. Repair adds
no pass or user override and does not change operational JSON schemas.
