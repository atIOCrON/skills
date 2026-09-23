# Definitions

- A **material finding** is either reproduced on the pinned review SHA through
  a supported production-like path using existing facilities, or deductively
  proven from committed code and a binding contract, policy, or repository
  standard. It includes missing reader updates and required verification gaps.
  It excludes static hypotheses, nits, hypothetical future needs, unsupported
  inputs, unplanned scale, and architecture preferences.
- A **failure family** is one invariant, runtime owner, supported operational
  path, and observable failure. Reviewer wording, files, implementation shape,
  and architecture epoch do not change its identity.
- A **root cause** is the underlying defect that produces one or more findings
  in a failure family.
