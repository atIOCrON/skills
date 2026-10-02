#!/usr/bin/env bash
# Read-only guard for deploying an assembled release without changing its SHA.
set -euo pipefail
[ "$#" -eq 3 ] || { echo "usage: verify_candidate.sh <base-sha> <expected-sha> <candidate-sha>" >&2; exit 2; }
for sha in "$@"; do
  [[ "$sha" =~ ^[0-9a-f]{40}$ ]] || { echo "error: full commit SHAs required" >&2; exit 2; }
  git cat-file -e "${sha}^{commit}"
done
[ "$2" = "$3" ] || { echo "error: candidate differs from the assembled release" >&2; exit 3; }
git merge-base --is-ancestor "$1" "$2" || {
  echo "error: base diverged from the release; update and retest before deployment" >&2; exit 3;
}
