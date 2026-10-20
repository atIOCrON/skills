# Build Selection and Stack Ownership

Read before selection or resumption. One coordinator owns the canonical build
manifest in the original workspace. Each plan has its persistent owner chat,
or one for an approved dependency chain. Record readable names and provider IDs;
give each owner the coordinator identity, return route and manifest's absolute
path. Worktree
`plans/` copies are not authoritative.

## Selection

Explicit scope overrides the queue. Resolve named specs through approved maps;
named slices select only those slices. Honor explicit order, base, individual pauses, exclusions,
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
other unmapped slices. Record missing/stale maps, unapproved children, or
inconsistent selection as blockers. Approved `to_do` plans have already been
reviewed and selected by a human; missing agent plan-review artefacts are not a
blocker. Do not launch a plan-review phase, invent scope, or silently implement
backlog children; continue eligible specs meanwhile.

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
prerequisites; prove their inclusion and code verification before dependent
work. Ancestor review qualification remains a release gate.

Reserve names/order in `schedule.work`. Create branches when workers start from
a verified commit, without empty branches or placeholder SHAs for future work.
Independent workers may share a verified authoring base. Record that base and
the result SHA separately from the final pin; candidates remain `prepared`
until accepted in order. Owners finish checks, trim and correctness on pinned
authoring bases.
Provisional reviews follow `scheduling.md`; promptly import
receipts and link packs and ledgers in `schedule.work`. Update `prepared_sha`,
checks, and handoffs after verified fixes.
When implementation, trim and correctness finish on the prepared tip, record
`provisionally_complete` and its evidence plus three clean `reviews` under
`schedule.work`, as defined in `operational-records.md`.
Record a worker-completion receipt in work extensions, including capped
outcomes and dependencies. Display worker complete separately from acceptance;
never leave a completed handoff labelled implementation started. Keep the
original completion pin when later coverage becomes pending.
Do not advance the tail or move prepared slices to `review/`.

After an owner completes against its pinned authoring base and returns its
write lease, the coordinator assembles that result. Under `git-branch-commit.md`,
it backs up each candidate, transfers
only its owned commit range onto the tail, resolves ordinary conflicts, compares
changes, verifies the exact new commit, and pushes with the expected lease.
Finish or isolate any in-flight pass before rewriting its source or pack.
The coordinator decides check/review applicability after each restack and
returns needed implementation fixes or fresh reviews to the existing owner.
Transfer receipts, counts, and valid current-tip results into the accepted branch
record without resetting pass numbers or the cap. Retain conclusions through
`code-review-loop.md` mappings and `trim-review.md` carry-forward rules; those
references govern invalidated results. Review coverage may remain pending at
acceptance. Replace `provisionally_complete` with `clean` after valid current-tip
mapping, or `running` with null phase SHA while coverage is incomplete. Never
copy it into accepted `branches`. Add the verified, pushed branch to `branches`
and advance `schedule.extensions.tail`. Prepared candidates are neither accepted tails nor releasable
slices. Reviews and final candidate checks remain separate gates.

## Ownership and Concurrent Release Work

Only the coordinator writes canonical manifests, moves plan folders, accepts
stack branches, or restacks them. Persistent owners complete implementation,
checks, trim, correctness loops,
closure and fixes in isolated authoring checkouts and evidence paths. They
return candidate and completion handoffs; reuse their chats for amendments,
findings and user feedback. The coordinator owns publication and may lease
only specified authoring pushes. Keep one active execution owner per session.
Delegate shared mutations through a handoff
naming scope, expected SHAs, owner, and return condition. Register contexts in
`extensions.sessions`; provenance alone grants no branch-write lease.

Other agents may review pinned prepared or accepted commits and prepare release
snapshots.
Assign review ownership to avoid duplicate passes. The coordinator imports
evidence and CR state; other agents own separate outputs/preparation records.
For release progression, default to a qualified, ancestry-closed prefix.
Explicitly authorized local testing may use an assembled ancestry-closed
prefix with pending review gates: pin its sources and checks, retain those
gates, and route feedback to existing owners. Testing alone grants no release,
staging or deployment authority. Pin commits and evidence links
in `plans/releases/active/<release-id>/preparation.json`; never freeze unfinished
queue work or omit inherited unfinished ancestors.

Before ready publication, assembly, or merge, record a handoff and keep leased
source heads stable. Only affected rewrites wait; later work continues. Upstream
fixes require withdrawing affected ready requests and invalidating stale
candidates before restacking. After a final base merge, the coordinator
reconciles landed work and remaining descendants; preserve sources/evidence
until then. Queue execution adds no merge, deployment, notification, or
publication authority beyond the user's instructions.
