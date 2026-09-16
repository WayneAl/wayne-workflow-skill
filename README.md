# wayne-workflow

A personal Claude Code skill that encodes one engineer's cross-project development working
preferences so they apply in **every** repo — not just ones with per-project memory.

It was distilled from process/feedback memories accumulated across many repos (Sui/Move
contracts, Rust backends, TypeScript SDKs, Next.js frontends, data pipelines): git
discipline, scope discipline, verification habits, bulk-data handling, subagent
orchestration, and the completion ritual. The rules are opinionated — fork it and adjust
them to how you work.

## Install

1. Clone the repo anywhere and symlink it into your skills directory:

   ```bash
   git clone https://github.com/WayneAl/wayne-workflow-skill.git
   ln -s "$PWD/wayne-workflow-skill" ~/.claude/skills/wayne-workflow
   ```

2. Import the always-on rules into your global `~/.claude/CLAUDE.md` (one line):

   ```
   @~/.claude/skills/wayne-workflow/always-on.md
   ```

3. Optional hooks, in `~/.claude/settings.json` (replace `<repo>` with the clone's absolute
   path):

   ```json
   {
     "hooks": {
       "PreToolUse": [
         {
           "matcher": "Bash",
           "hooks": [
             {
               "type": "command",
               "command": "python3 <repo>/hooks/git-guard.py",
               "if": "Bash(git *)",
               "timeout": 15
             }
           ]
         }
       ],
       "SessionStart": [
         {
           "hooks": [
             { "type": "command", "command": "zsh <repo>/hooks/inbox-reminder.sh", "timeout": 10 }
           ]
         }
       ]
     }
   }
   ```

## Layout

```
wayne-workflow-skill/
├── always-on.md                    # short rules loaded every session via a CLAUDE.md import
├── SKILL.md                        # router: who you're working with, lifecycle + triage, three gates, deltas
├── references/
│   ├── designing.md                # triage, design conversation, Tier-1 spec, idea-level review
│   ├── planning.md                 # Tier-2 plan format for clean-context executors
│   ├── executing-plans.md          # worktree isolation, ledger, per-task loop, model table, final review
│   ├── debugging.md                # root cause before fix, 3 failed fixes → question architecture
│   ├── testing.md                  # where TDD applies vs a verification command; honest tests
│   ├── verifying-claims.md         # claim gate, evidence chains, live smokes, golden sample, fail-loud
│   ├── finishing.md                # full suite, integration menu, cleanup, completion ritual
│   └── bulk-data.md                # three-bucket output + markdown review round-trip
├── prompts/
│   ├── implementer.md              # subagent brief template (rules inlined verbatim)
│   └── task-reviewer.md            # spec + quality reviewer template
├── hooks/
│   ├── git-guard.py                # PreToolUse guard: amend-after-push + plain force-push
│   ├── test_git_guard.py           # stdin cases for the guard (python3 hooks/test_git_guard.py)
│   └── inbox-reminder.sh           # SessionStart: pending gardener proposals
└── gardener/                       # memory-gardening runner, run manually (proposals only)
```

The skill is self-contained. It was originally written as a delta on top of the
`superpowers` plugin; since 2026-09-03 it carries the whole lifecycle itself (triage →
design → plan → execute → debug → test → verify → finish) with the parts of superpowers
that earned their keep folded in and rewritten as reasons rather than iron laws. The
`docs/superpowers/` directory name in repos is kept for continuity.

## Layered split of responsibilities

- **Deterministic guardrails** → `hooks/git-guard.py`, wired as a PreToolUse hook in
  `~/.claude/settings.json`. Only for destructive, mechanical never-rules that prose can
  forget under long context (amending pushed commits, plain force-push).
- **Always-on short rules** (lead-with-synthesis, act over re-confirm, git commit/push as
  you go, pushback, minimal diff) live in `always-on.md`, imported into the global
  `~/.claude/CLAUDE.md` so they load every session — that file is their **source of
  truth**; `SKILL.md` and `references/` must not restate them, only elaborate procedures.
  Rules that are yours alone (e.g. reply language) stay in your own `CLAUDE.md`.
- **On-demand procedures** live in this skill, loaded when the relevant context appears.
- **Project facts** stay in each project's memory, never here.

## Maintaining it

When a new durable working preference emerges (a correction repeated across repos, or a rule
the user states explicitly), fold it into the matching section here rather than leaving it in
a single repo's memory — `always-on.md` instructs sessions to propose this proactively, and
`zsh gardener/run.sh`, run manually when you want a sweep, drafts folds from recently
modified memories into `gardener/inbox/` for review (gitignored: proposals quote private
memories and stay local).
Keep `SKILL.md` under ~150 lines; push longer procedures into `references/`. Nothing is
injected at SessionStart except the inbox reminder — the always-on rules arrive through the
`CLAUDE.md` import.

## License

MIT — see [LICENSE](LICENSE).
