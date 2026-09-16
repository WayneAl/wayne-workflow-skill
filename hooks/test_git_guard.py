#!/usr/bin/env python3
"""Stdin-level tests for git-guard.py. Run: python3 hooks/test_git_guard.py

Two working directories: this repo (HEAD is pushed) and a throwaway repo
with one local commit and no remote (HEAD is not pushed).
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
GUARD = os.path.join(HERE, "git-guard.py")
PUSHED = os.path.dirname(HERE)  # this repo


def run(cmd, cwd, tool="Bash"):
    payload = json.dumps({"tool_name": tool, "tool_input": {"command": cmd}, "cwd": cwd})
    r = subprocess.run([sys.executable, GUARD], input=payload, capture_output=True, text=True)
    return r.returncode


def unpushed_repo():
    d = tempfile.mkdtemp(prefix="git-guard-test-")
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    for c in (["git", "init", "-q"], ["git", "commit", "-q", "--allow-empty", "-m", "x"]):
        subprocess.run(c, cwd=d, env=env, check=True, capture_output=True)
    return d


AMEND = "git commit " + "--amend"          # split so this file never contains the literal
FORCE = "git push " + "-f origin main"

CASES = [
    # (description, command, cwd_kind, expected exit)
    ("real amend on pushed HEAD",            AMEND + " --no-edit",                       "pushed",   2),
    ("real amend on unpushed HEAD",          AMEND + " --no-edit",                       "unpushed", 0),
    ("amend after &&",                       "git add -A && " + AMEND,                   "pushed",   2),
    ("amend inside echo string",             "echo '" + AMEND + "'",                     "pushed",   0),
    ("amend inside double-quoted string",    'grep "' + AMEND + '" docs/',               "pushed",   0),
    ("amend in commit message",              'git commit -m "note: never ' + AMEND + '"', "pushed",  0),
    ("--amend as -m argument text",          'git commit -m "--amend"',                  "pushed",   0),
    ("plain force push",                     FORCE,                                      "pushed",   2),
    ("--force long form",                    "git push --force origin main",             "pushed",   2),
    ("force-with-lease allowed",             "git push --force-with-lease origin main",  "pushed",   0),
    ("-f belongs to rm, not push",           "rm -f x && git push origin main",          "pushed",   0),
    ("git not in command position",         "echo git push --force",                    "pushed",   0),
    ("non-Bash tool ignored",                AMEND,                                      "pushed",   0),
    ("ordinary commit + push",               'git commit -m "x" && git push',            "pushed",   0),
]


def main() -> int:
    cwds = {"pushed": PUSHED, "unpushed": unpushed_repo()}
    failed = 0
    for desc, cmd, kind, want in CASES:
        tool = "Read" if desc == "non-Bash tool ignored" else "Bash"
        got = run(cmd, cwds[kind], tool)
        ok = got == want
        failed += not ok
        print(f"{'ok  ' if ok else 'FAIL'} exit={got} want={want}  {desc}")
    print(f"\n{len(CASES) - failed}/{len(CASES)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
