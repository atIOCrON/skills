#!/usr/bin/env python3
"""Send the fixed continue prompt to selected Codex threads through app-server."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Optional, Union


MESSAGE = "Continue. Claude usage has reset"
UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)


def codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()


def default_codex_bin() -> str:
    return (
        os.environ.get("CODEX_BIN")
        or shutil.which("codex")
        or "/Applications/Codex.app/Contents/Resources/codex"
    )


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


def print_resolution_problem(results: list[dict[str, Any]]) -> None:
    print("No messages sent. Resolve these targets first:", file=sys.stderr)
    for result in results:
        if result["status"] == "resolved":
            continue
        print(f"- {result['target']}: {result['status']}", file=sys.stderr)
        for match in result["matches"]:
            archived = "archived" if match["archived"] else "active"
            print(
                f"  {match['id']}  {archived}  {match['title']}",
                file=sys.stderr,
            )


def send_app_server_message(
    *,
    codex_bin: str,
    thread_id: str,
    message: str,
    timeout_seconds: int,
) -> dict[str, Any]:
    proc = subprocess.Popen(
        [codex_bin, "app-server"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    next_id = 1

    def send(
        method: str,
        params: Optional[dict[str, Any]] = None,
        id_: Optional[Union[int, bool]] = None,
    ) -> Optional[int]:
        nonlocal next_id
        request: dict[str, Any] = {"method": method, "params": params or {}}
        if id_ is None:
            id_ = next_id
            next_id += 1
        if id_ is not False:
            request["id"] = id_
        assert proc.stdin is not None
        proc.stdin.write(json.dumps(request) + "\n")
        proc.stdin.flush()
        return id_ if id_ is not False else None

    initialize_id = send(
        "initialize",
        {
            "clientInfo": {
                "name": "continue_codex_threads",
                "title": "Continue Codex Threads",
                "version": "1.0.0",
            },
            "capabilities": {"experimentalApi": True},
        },
    )
    send("initialized", id_=False)
    resume_id = send("thread/resume", {"threadId": thread_id})
    turn_start_id: Optional[int] = None
    turn_id: Optional[str] = None
    assistant_text: list[str] = []
    deadline = None if timeout_seconds <= 0 else time.monotonic() + timeout_seconds

    try:
        assert proc.stdout is not None
        while deadline is None or time.monotonic() < deadline:
            line = proc.stdout.readline()
            if not line:
                break

            event = json.loads(line)
            if event.get("id") == initialize_id and "error" in event:
                raise RuntimeError(f"app-server initialize failed: {event['error']}")

            if event.get("id") == resume_id:
                if "error" in event:
                    raise RuntimeError(f"thread/resume failed: {event['error']}")
                turn_start_id = send(
                    "turn/start",
                    {
                        "threadId": thread_id,
                        "clientUserMessageId": str(uuid.uuid4()),
                        "input": [{"type": "text", "text": message}],
                    },
                )
                continue

            if turn_start_id is not None and event.get("id") == turn_start_id:
                if "error" in event:
                    raise RuntimeError(f"turn/start failed: {event['error']}")
                turn_id = event.get("result", {}).get("turn", {}).get("id")
                continue

            if event.get("method") == "item/agentMessage/delta":
                assistant_text.append(event.get("params", {}).get("delta", ""))
                continue

            if event.get("method") == "turn/completed":
                turn = event.get("params", {}).get("turn", {})
                proc.terminate()
                return {
                    "turn_id": turn.get("id") or turn_id,
                    "status": turn.get("status"),
                    "assistant_text": "".join(assistant_text),
                }

        try:
            stderr = proc.stderr.read() if proc.stderr is not None else ""
        except ValueError:
            stderr = ""
        raise TimeoutError(
            f"Timed out waiting for turn/completed in {thread_id}"
            + (f"; stderr: {stderr.strip()}" if stderr.strip() else "")
        )
    finally:
        if proc.poll() is None:
            proc.terminate()


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Resolve exact Codex thread titles/IDs and send the fixed continue "
            "prompt with app-server `thread/resume` + `turn/start`."
        )
    )
    parser.add_argument("targets", nargs="+", help="Thread titles or thread IDs")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the CLI commands without running them",
    )
    parser.add_argument(
        "--db",
        default=str(codex_home() / "state_5.sqlite"),
        help="Path to Codex state SQLite DB",
    )
    parser.add_argument(
        "--codex-bin",
        default=default_codex_bin(),
        help="Path to the Codex CLI executable",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=0,
        help="Seconds to wait for each turn to complete; 0 waits indefinitely",
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

    if any(result["status"] != "resolved" for result in results):
        print_resolution_problem(results)
        return 1

    codex_bin = args.codex_bin
    for result in results:
        match = result["matches"][0]
        print(f"{match['title']} ({match['id']})")
        print("$ app-server thread/resume + turn/start")
        if args.dry_run:
            continue

        try:
            sent = send_app_server_message(
                codex_bin=codex_bin,
                thread_id=match["id"],
                message=MESSAGE,
                timeout_seconds=args.timeout,
            )
        except Exception as exc:
            print(
                f"Command failed for {match['title']} ({match['id']}): {exc}",
                file=sys.stderr,
            )
            return 3

        print(
            f"turn {sent['turn_id']} completed with status {sent['status']}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
