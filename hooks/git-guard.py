#!/usr/bin/env python3
"""wayne-workflow PreToolUse guard for destructive git operations.

Blocks exactly two things, both of which prose reminders failed to prevent
(the 2026-06-10 main/origin divergence):
  1. `git commit --amend` when HEAD is already on a remote ref
  2. plain `git push --force` / `git push -f` (use --force-with-lease)

Everything else passes through. Exit 0 = allow, exit 2 = block (stderr is
shown to Claude, which then surfaces it to the user).

Matching is done per git *command segment*, not on the raw command text:
quoted strings are blanked first (so an amend mentioned inside an echo, a
grep pattern, or a commit message does not trigger), `git` must sit in
command position (start of input or after ; && || | ( or a newline), and
`-f` is only looked for inside the `git push` segment itself.
"""
import json
import os
import re
import subprocess
import sys

# single-quoted, or double-quoted with backslash escapes
_QUOTED = re.compile(r"'[^']*'|\"(?:\\.|[^\"\\])*\"")
# `git` as the command word, capturing its arguments up to the next separator
_GIT_SEG = re.compile(r"(?:^|[;&|(\n]\s*)(?:\S*/)?git\s+([^\n;|&)]*)")
_FORCE = re.compile(r"(^|\s)(--force|-f)(\s|$)")


def git_segments(cmd: str):
    """Argument strings of every git invocation in command position."""
    return [m.group(1) for m in _GIT_SEG.finditer(_QUOTED.sub('""', cmd))]


def head_on_remote(cwd: str):
    """Name of a remote ref containing HEAD, or None (also None on failure)."""
    try:
        r = subprocess.run(
            ["git", "branch", "-r", "--contains", "HEAD"],
            cwd=cwd, capture_output=True, text=True, timeout=10,
        )
    except Exception:
        return None  # can't determine — don't block on guard failure
    if r.returncode == 0 and r.stdout.strip():
        return r.stdout.strip().splitlines()[0].strip()
    return None


def check(cmd: str, cwd: str):
    """Return a block message, or None to allow."""
    for seg in git_segments(cmd):
        if re.match(r"push\b", seg) and "--force-with-lease" not in seg \
                and _FORCE.search(seg):
            return (
                "wayne-workflow guard: plain force-push is blocked. Verify origin has "
                "no unique commits, then use `git push --force-with-lease` "
                "(see wayne-workflow > Git for the recovery procedure)."
            )
        if re.match(r"commit\b", seg) and re.search(r"(^|\s)--amend(\s|$)", seg):
            remote_ref = head_on_remote(cwd)
            if remote_ref:
                return (
                    f"wayne-workflow guard: HEAD is already on a remote ({remote_ref}); "
                    "amending a pushed commit diverges local from origin. "
                    "Make a new commit instead (fix forward)."
                )
    return None


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0  # malformed input — never break the session over the guard

    if data.get("tool_name") != "Bash":
        return 0
    cmd = (data.get("tool_input") or {}).get("command") or ""
    cwd = data.get("cwd") or os.getcwd()

    msg = check(cmd, cwd)
    if msg:
        sys.stderr.write(msg + "\n")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
