# Implementation Readiness

Before implementation, classify each owned acceptance group by its
candidate-owned mechanism; whether the candidate introduces or modifies its
lifecycle implementation or only changes routing, selection, configuration, or
reachability; its runtime owner; and its branch-local, inherited, and external
evidence. A candidate can change the observable product outcome without
changing the dependency-owned lifecycle implementation.

Identify required verification for each touched surface, its prerequisites
(such as locked dependencies, services,
fixtures, or disabled components), and whether CI runs on the target branches.
Detect and select every applicable capability skill for specialized changed surfaces.
Require each selected capability to define fast authoring checks, exact
candidate verification, final integration verification, and the immutable
input identities and equivalence rules that permit safe reuse. A reusable check
must account for every determining input, including source, configuration,
locked dependencies and fixtures, toolchain, runtime binding, and effective
result; otherwise rerun it. The capability must also identify the source
representation and the effective generated or runtime result reviewers need.
Copy any review-required source or effective result from outside the reviewer
repository workspace into the neutral review pack; a path, hash, or replay log
alone is insufficient.
Record those commands and evidence here without copying ecosystem-specific
procedures into this orchestration skill.
Prepare reproducible local checks for requirements CI cannot run. If a required
agent-run gate or prerequisite is missing, resolve its scope and ownership before
implementation; do not silently add unrelated CI or tooling work. Distinguish
checks the agent can run from human or external acceptance (such as a sandbox
wallet test). Record intended commands, any agreed gate gap, and each external
check's procedure, owner, and pending result in plan evidence. Runtime lifecycle
logic introduced or modified by the candidate requires executable local
behavioural proof at the highest practical seam; source-shape assertions may
supplement but not replace proof of that owned runtime behaviour. Merely making
an unchanged dependency-owned lifecycle reachable does not require
reconstructing it locally when exact effective-code identity, applicable
inherited test evidence, and explicit external acceptance establish the
contract. Lightweight test doubles may prove candidate-owned routing or
binding, but transitions implemented by a fake provider, server, persistence
layer, account store, or order lifecycle are not evidence of production
behaviour owned elsewhere.
