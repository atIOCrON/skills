#!/usr/bin/env python3
"""Resolve Codex thread titles or IDs from the local Codex state database."""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
from pathlib import Path
from typing import Any


UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)


def codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "title": row["title"],
        "id": row["id"],
        "archived": bool(row["archived"]),
        "source": row["source"],
        "cwd": row["cwd"],
        "updated_at": row["updated_at"],
        "rollout_path": row["rollout_path"],
    }


def resolve_target(conn: sqlite3.Connection, target: str) -> dict[str, Any]:
    if UUID_RE.match(target):
        rows = conn.execute(
            """
            SELECT title, id, archived, source, cwd, updated_at, rollout_path
            FROM threads
            WHERE id = ?
            ORDER BY updated_at DESC
            """,
            (target,),
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT title, id, archived, source, cwd, updated_at, rollout_path
            FROM threads
            WHERE title = ?
            ORDER BY updated_at DESC
            """,
            (target,),
        ).fetchall()

    matches = [row_to_dict(row) for row in rows]
    if len(matches) == 1:
        status = "resolved"
    elif not matches:
        status = "missing"
    else:
        status = "ambiguous"

    return {"target": target, "status": status, "matches": matches}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Resolve Codex thread IDs from exact thread titles or UUIDs."
    )
    parser.add_argument("targets", nargs="+", help="Thread titles or thread IDs to resolve")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    parser.add_argument(
        "--db",
        default=str(codex_home() / "state_5.sqlite"),
        help="Path to Codex state SQLite DB",
    )
    args = parser.parse_args()

    db_path = Path(args.db).expanduser()
    if not db_path.exists():
        print(f"Codex state database not found: {db_path}", file=sys.stderr)
        return 2

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    try:
        results = [resolve_target(conn, target) for target in args.targets]
    finally:
        conn.close()

    if args.json:
        print(json.dumps(results, indent=2, sort_keys=True))
    else:
        for result in results:
            target = result["target"]
            status = result["status"]
            print(f"{target}: {status}")
            for match in result["matches"]:
                archived = "archived" if match["archived"] else "active"
                print(f"  {match['id']}  {archived}  {match['title']}")

    return 0 if all(result["status"] == "resolved" for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
