#!/usr/bin/env python3
"""Validate, fingerprint and verify a composed merge message."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys


def read_message(path):
    raw = Path(path).read_bytes().decode("utf-8")
    if "\r" in raw or "\0" in raw:
        raise ValueError("merge message must use UTF-8 text and LF line endings")
    message = raw.rstrip("\n") + "\n"
    subject, separator, body = message.rstrip("\n").partition("\n\n")
    if not subject.strip() or "\n" in subject or len(subject) > 72 or not separator or not body.strip():
        raise ValueError("merge message needs a subject of at most 72 characters, a blank line and a body")
    return {"message": message, "subject": subject, "body": body,
            "sha256": hashlib.sha256(message.encode()).hexdigest()}


def verify_message(path, commit):
    expected = read_message(path)
    raw = subprocess.check_output(["git", "cat-file", "commit", commit]).decode("utf-8")
    observed = raw.split("\n\n", 1)[1].rstrip("\n") + "\n"
    if observed != expected["message"]:
        raise ValueError("landed commit message differs from the recorded message")
    return expected


if __name__ == "__main__":
    try:
        if len(sys.argv) not in {2, 3}:
            raise ValueError("usage: merge_message.py <message-file> [landed-sha]")
        result = verify_message(*sys.argv[1:]) if len(sys.argv) == 3 else read_message(sys.argv[1])
        print(json.dumps(result))
    except (OSError, UnicodeError, ValueError, subprocess.CalledProcessError) as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(4)
