# Git Commit Message

Read the cached stat/full diff, or an explicitly supplied full parent/head SHA
comparison, without changing files/index/branches. Stop if empty. For a squash,
describe the branch's own complete change; exclude inherited predecessor work.
Use the plan/PR context and recorded checks for why, impact and verification;
report checks truthfully, including any pending checks.

Return only an imperative subject (at most 72 characters), a blank line and
a body covering what changed, why, impact and verification; no Git commands.
Caller owns committing, merging and pushing.
