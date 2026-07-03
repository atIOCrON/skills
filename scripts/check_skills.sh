#!/usr/bin/env bash
set -euo pipefail

target_dir="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"

python3 - "$target_dir" <<'PY'
import pathlib
import re
import sys

import yaml

target = pathlib.Path(sys.argv[1])
if not target.exists():
    print(f"missing target directory: {target}", file=sys.stderr)
    sys.exit(2)

allowed_layers = {"runner", "capability", "reference"}
allowed_keys = {
    "name",
    "description",
    "compatibility",
    "metadata",
    "license",
    "allowed-tools",
}
errors = []
skill_files = sorted(target.glob("*/SKILL.md"))

if not skill_files:
    errors.append(f"no SKILL.md files found under {target}")

def parse_frontmatter(text):
    if not text.startswith("---\n"):
        raise ValueError("missing opening frontmatter marker")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("missing closing frontmatter marker")
    return text[4:end]

for path in skill_files:
    rel = path.relative_to(target)
    text = path.read_text(encoding="utf-8")
    if len(text.splitlines()) >= 500:
        errors.append(f"{rel}: SKILL.md must be under 500 lines")
    try:
        frontmatter_text = parse_frontmatter(text)
    except ValueError as exc:
        errors.append(f"{rel}: {exc}")
        continue

    try:
        fields = yaml.safe_load(frontmatter_text)
    except yaml.YAMLError as exc:
        errors.append(f"{rel}: invalid YAML frontmatter: {exc}")
        continue

    if not isinstance(fields, dict):
        errors.append(f"{rel}: frontmatter must be a mapping")
        continue

    for key in fields:
        if key not in allowed_keys:
            errors.append(f"{rel}: unsupported frontmatter key {key}")

    name = fields.get("name")
    if not isinstance(name, str) or not name:
        errors.append(f"{rel}: missing name")
    elif name != path.parent.name:
        errors.append(f"{rel}: name {name!r} does not match directory {path.parent.name!r}")
    elif len(name) > 64:
        errors.append(f"{rel}: name must be 64 characters or fewer")
    elif not re.fullmatch(r"[a-z0-9-]+", name):
        errors.append(f"{rel}: name must match [a-z0-9-]+")

    description = fields.get("description")
    if not isinstance(description, str) or not description:
        errors.append(f"{rel}: missing description")
    elif len(description) > 1024:
        errors.append(f"{rel}: description must be 1024 characters or fewer")

    metadata = fields.get("metadata")
    if not isinstance(metadata, dict):
        errors.append(f"{rel}: metadata must be a mapping")
        metadata = {}
    layer = metadata.get("layer")
    if layer not in allowed_layers:
        errors.append(f"{rel}: metadata.layer must be one of {sorted(allowed_layers)}")

if errors:
    print("\n".join(errors), file=sys.stderr)
    sys.exit(1)
PY

while IFS= read -r script; do
  bash -n "$script"
  if [[ ! -x "$script" ]]; then
    echo "$script: script must be executable" >&2
    exit 1
  fi
done < <(find "$target_dir" -path '*/scripts/*.sh' -type f | sort)

echo "skills OK: $target_dir"
