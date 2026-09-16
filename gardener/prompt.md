# Weekly memory gardening — wayne-workflow

You are running as a scheduled, unattended session. Your job: find working-style
preferences that emerged this week in per-project memories and stage them as *proposals*
for the wayne-workflow skill. You do NOT edit always-on.md, SKILL.md, or references/
yourself — the user reviews the inbox and decides.

## Steps

1. Scan `~/.claude/projects/*/memory/*.md` (skip `MEMORY.md` indexes) for files modified
   since the last successful scan: use `find ... -newer gardener/.last-scan` (the working
   directory is this repo). If the marker file doesn't exist, fall back to the last 8 days
   (`-mtime -8`).
2. Keep only memories that state a *cross-repo working preference* — how the user wants work
   done (git, scope, verification, communication, orchestration, data handling). Discard
   project facts (addresses, deploy state, API quirks specific to one system).
3. For each candidate, check whether `always-on.md`, `SKILL.md`, or `references/*.md` in
   this repo already covers it. Skip covered ones.
4. If anything genuinely new remains, append a dated section to
   `gardener/inbox/YYYY-MM-DD.md` (create the file; use today's date):
   - source memory path
   - the preference in one sentence
   - which skill section it should fold into, with suggested wording
5. Do not commit or push, and do not touch any other file. `gardener/inbox/` is gitignored:
   proposals quote private memories and stay local.
6. If nothing new: exit without writing anything. Silence means "no news".
