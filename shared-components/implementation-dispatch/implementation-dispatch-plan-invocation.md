You own this implementation in a persistent chat. Reuse this chat for later fixes.

Coordinator: {coordinator_provider} / {coordinator_session_id} / {coordinator_name}
Report route: {return_route}; evidence directory: {evidence_dir}
Chat name: {implementation_chat_name}
Repo / checkout: {repo_root} / {worktree}
Plan; spec / slice: {plan_path}; {spec_slug} / {slice_slug}
Branch / pinned authoring parent: {authoring_branch} / {authoring_base_sha}
Code prerequisites: {code_prerequisites}
Manifest (read-only): {build_manifest_path}; role: {candidate_role}
Owned scope: {owned_files_or_modules}
Bundled instructions: {implementation_instructions_paths}
Authoring push lease or coordinator push route: {publication_handoff}

Read the bundled instructions. Complete implementation, checks, trim,
correctness review loops, closure and fixes against the pinned authoring base.
Use fresh independent reviewers and preserve caps. Keep canonical state, plan
moves, accepted refs and restacking with the coordinator. Report to that
coordinator with branch, commit, authoring parent, checks, review outcomes,
receipts, remaining dependencies and evidence paths: first at the verified
candidate, then at worker completion or a blocker. Save the handoff for retrieval
if direct report messaging is unavailable or unauthorized.

Draft and refresh the structured `operator_handoff` under operational-records;
mark it ready only for the verified candidate. Distinguish suggested acceptance
from executed checks. Wait for the coordinator's lease before changing accepted
refs; use this same chat for amendments and restack-invalidated work.
