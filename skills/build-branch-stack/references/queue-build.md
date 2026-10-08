# Build Selection and Stack Ownership

Read before selection or resumption. One coordinator owns the canonical build
manifest in the original workspace. Give workers its absolute path; worktree
`plans/` copies are not authoritative.

## Selection

Explicit scope overrides the queue. Resolve named specs through approved maps;
named slices select only those slices. Honor explicit order, base, exclusions,
layout, and repair/resume inputs. Add only demonstrated prerequisites within
existing build authority; otherwise record the missing input.

Without scope, run the queue without asking the user to choose plans. Inspect
unfinished manifests, sessions, refs, and handoffs first. Resume a uniquely
applicable build, including its `in_progress` specs/slices; do not duplicate
branches or take over a live coordinator. Investigate ambiguous ownership or
build selection and ask only for the unresolved choice. Never infer the tail
from folder dates or branch names.

Discover approved specs in `plans/specs/to_do/`. Resolve approved maps by slug;
select their `to_do` slices and unfinished slices owned by the resumed build.
Group explicitly classified standalone legacy slices by their own slug; report
other unmapped slices. Record missing/stale maps, unapproved children, pending
plan reviews, or inconsistent selection as blockers. Do not invent scope or
silently implement backlog children. Complete required plan review when
build authority permits; continue eligible specs meanwhile.

Record scope before dispatch. At scheduling checkpoints, append newly selected
approved `to_do` specs and record the additions. Preserve started blocks and
frozen candidates; do not discover drafts/backlog as extra scope. Finish when
no selected eligible work or active worker remains. Report blockers and pending
external/release work without polling indefinitely. An empty queue with no
resumable build is a successful no-op.

## Spec Order

Order whole specs by cross-spec prerequisites, explicit user priority, then
estimated time/complexity and risk. Favor quick eligible specs and prerequisites
that unlock others. Break ties by slug and record the rationale. Within a spec,
respect slice prerequisites, then prefer quick eligible slices. Keep each spec
contiguous in the final linear stack; slice-only scope excludes unselected siblings.

Prioritize the current spec's implementation/fixes and acceptance. Append all
its selected slices before the next spec, but dispatch later specs concurrently
when prerequisites and capacity permit. Advance after the current block is
committed, verified, and pushed; ancestor reviews and external release
acceptance may continue.

For a blocked spec, continue other preparation. If none of its slices is
accepted, record its deferral and reorder only wholly unaccepted blocks. If
part is accepted, keep later results prepared until it finishes; splitting the
block requires an explicit user override. Preserve the accepted prefix.
Resolve spec-level dependency cycles through landed prerequisites or existing
plan authority; record a blocker if contiguous blocks cannot satisfy them.
Never fabricate dependencies or silently violate the user's order.

## Linear Assembly

New builds default to linear; explicit dependency/base-targeted layout overrides
this. Resumes preserve layout unless a change is authorized. The first accepted
slice uses the pinned starting branch; later slices use the accepted tail.
If that anchor differs from the eventual integration base, record it as manifest
`base`, identify the eventual base in scope, and account for inherited unmerged
work before release.

`parent`/`target` record Git placement; `stacking_reason` explains linear order.
`code_prerequisites` lists required slice slugs; `dependency_reason` explains
code needs or is `none`. One verified cumulative parent may satisfy several
prerequisites; prove their inclusion and qualification before dependent work.

Reserve names/order in `schedule.work`. Create branches when workers start from
a verified commit, without empty branches or placeholder SHAs for future work.
Independent workers may share a verified authoring base. Record that base and
the result SHA separately from the final pin; candidates remain `prepared`
until accepted in order. Provisional reviews follow `scheduling.md`; import
receipts and link packs and ledgers in `schedule.work`. Update `prepared_sha`,
checks, and handoffs after verified fixes.
Do not advance the tail or move prepared slices to `review/`.

Under `git-branch-commit.md`, the coordinator backs up each candidate, transfers
only its owned commit range onto the tail, resolves ordinary conflicts, compares
changes, verifies the exact new commit, and pushes with the expected lease.
Finish or isolate any in-flight pass before rewriting its source or pack.
Transfer receipts, counts, and valid current-tip results into the accepted branch
record without resetting pass numbers or the cap. Retain conclusions through
`code-review-loop.md` mappings and `trim-review.md` carry-forward rules; those
references govern invalidated results. Review coverage may remain pending at
acceptance. Add the verified, pushed branch to `branches` and advance
`schedule.tail`. Prepared candidates are neither accepted tails nor releasable
slices. Reviews and final candidate checks remain separate gates.

## Ownership and Concurrent Release Work

Only the coordinator writes canonical manifests, moves plan folders, accepts
stack branches, or restacks them. Workers own isolated authoring checkouts and
evidence paths and return results. Delegate shared mutations through a handoff
naming scope, expected SHAs, owner, and return condition. Register contexts in
`sessions`; provenance alone grants no branch-write lease.

Other agents may review pinned prepared or accepted commits and prepare release
snapshots.
Assign review ownership to avoid duplicate passes. The coordinator imports
evidence and CR state; other agents own separate outputs/preparation records.
Default to a qualified, ancestry-closed prefix. Pin commits and evidence links
in `plans/releases/active/<release-id>/preparation.json`; never freeze unfinished
queue work or omit inherited unfinished ancestors.

Before ready publication, assembly, or merge, record a handoff and keep leased
source heads stable. Only affected rewrites wait; later work continues. Upstream
fixes require withdrawing affected ready requests and invalidating stale
candidates before restacking. After a final base merge, the coordinator
reconciles landed work and remaining descendants; preserve sources/evidence
until then. Queue execution adds no merge, deployment, notification, or
publication authority beyond the user's instructions.
