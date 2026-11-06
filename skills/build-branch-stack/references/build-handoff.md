# Build Progress and Handoff

Update one compact table on state, review, commit, restack or verification changes:

```text
| Plan | Owner | Worker complete | Accepted/restacked | Checks / Reviews | Branch / Commit | Next action / Waiting on |
```

Use `scheduling.md` for waiting reasons/resume conditions and
`orchestration-final-handoff.md` for shared branch reporting, including current-tip
evidence, dependencies, restacks, caps/dispositions and deferred checks.
Additionally report selection, spec order/current spec, tail, child/parent stages,
immutable transition evidence, pauses/exclusions, audit decisions, planning
references and incomplete work.

Draft publication uses stable accepted pins. State whether authorized draft CRs were
published or remain next.

Pending required acceptance blocks production decisions unless an authorized
decision explicitly accepts the limitation. Apply `orchestration-plans-layout.md`
for fulfillment and final-merge requirements.

For selected releases, hand the branch qualification and acceptance checklist from
`orchestration-final-handoff.md` to `prepare-release-integration`. It coordinates
`rebuild-staging-with-branches` and `verify-staging-acceptance`. Read sibling
`prepare-release-integration/references/release-preparation.md` for concurrent
snapshots/handoffs; import membership/stage handoffs before shared moves or repairs.
