# Executing and orchestrating plans

How a multi-task plan (`planning.md`) gets run: isolated worktree, one fresh subagent per
task, a ledger that survives compaction, one reviewer per task, a final whole-branch
review, then `finishing.md`. You are the orchestrator: you keep the checkpoints, verify
every report yourself, and hold your own context for coordination — the task work happens
in subagents.

## Worktree isolation (never yank the user's checkout)

Isolate the feature branch in a **git worktree** — never `git checkout -b` in the main
working tree. Switching the main checkout yanks the user off whatever they were working on.

```bash
git worktree add .claude/worktrees/<branch> <branch>   # .claude/worktrees/ is the repo convention, gitignored
```

- A branch can't be checked out in two trees at once — if it's in main, switch main away
  first. `Agent` with `isolation: "worktree"` does the same for a single dispatch.
- Pass the worktree's **absolute path** to every subagent as its working directory.
- Subagent worktrees snapshot HEAD at dispatch. If `main` advances after dispatch, copy
  the critical changed files into each worktree ("worktree overlay").
- Never start implementation on `main` for a multi-task plan without the user's explicit OK.

## Workspace and ledger

Conversation memory does not survive compaction; orchestrators that lost their place have
re-dispatched whole completed task sequences. Track progress in a file, not only in todos.

- Workspace: `.claude/sdd/<plan-basename>/` (gitignore it if the repo doesn't already
  ignore `.claude/sdd/`). Home to this plan's ledger, briefs, reports, and diffs. Another
  plan's directory is never yours.
- Ledger: `<workspace>/progress.md`, first line `# ledger — plan: <plan path>`. Append
  per task: the agent id of every dispatch (implementer, reviewer, fixer), status, commit
  SHAs, review verdict, and every ruling as `Ruling: <what> — <why> — <cost if wrong>`.
  After compaction, trust the ledger and `git log` over recollection. The id is what a
  usage-limit resume needs once compaction or a restart has dropped it from context.
- Pre-flight: read the plan against its spec before dispatching anything. Rule on defects
  you can rule on, ledger them; stop only if every path forward is a guess.

## Resuming a usage-limit-killed subagent

The main session is woken by the harness once a usage limit resets (v2.1.234+, on by
default with a claude.ai login), but a subagent killed by that limit is not brought back with
it: it ends `failed` while its transcript survives. Once woken, `SendMessage` to its agent
id continues it with full context; a `Workflow` run resumes with `resumeFromRunId`. A
fresh dispatch throws that progress away. This survives a session restart too: after `/login` or a
model switch starts a new session id, `ListAgents` stops listing the agent and its
`/tmp/.../tasks/<id>.output` is gone, yet the transcript is still at
`~/.claude/projects/<project>/<old session>/subagents/agent-<id>.jsonl` and `SendMessage`
to the id resumes it — neither sign means the agent is lost. For a multi-agent run (a forked
skill, a review with finders), resume the parent and tell it to resume its children by id
(2026-09-14: a `/code-review` resumed across a restart brought back its six finders by id,
6/6 with their instructions, none re-dispatched). All of this needs the id written down —
the ledger above is where it lives.

## Per-task loop

1. **Brief** — write `<workspace>/task-N-brief.md` from `prompts/implementer.md`: task text
   copied from the plan, interfaces from neighbors, environment state you've verified,
   what to skip (already done), what's held back (checkpoints), and the wayne-workflow
   rules that bite for this task, inlined verbatim. Subagents don't consult this skill.
   Copy the spec's **named failure modes** into the brief of whichever task satisfies
   each one — reviewers grade against the brief, not the spec, so a spec bullet no brief
   quotes has no owner and passes review unimplemented.
2. **Dispatch** the implementer with the brief path and the worktree path. Model per the
   table below. Between dispatches the user-facing text is one status line per task;
   the ledger carries the full record.
3. **Status** — DONE / DONE_WITH_CONCERNS / BLOCKED / NEEDS_CONTEXT. Concerns about
   correctness or scope get addressed before review; observations get noted. BLOCKED or
   NEEDS_CONTEXT: supply context and re-dispatch, break the task apart, or step up the
   model — if the plan itself is wrong, rule, ledger, re-dispatch with the ruling.
4. **Verify yourself** before review: `git log`, `git diff --stat` against the task's file
   list, run the focused test. A report is a claim. When the output is an artifact a test
   cannot judge — a rendered page, a generated document, a chart — open it yourself
   against realistic input; reviewers scoped to brief + diff are blind here.
   "Tests pass" is a claim about the tests, not the code: ask whether those tests predate
   the change — an agent that pins its new behaviour with its own new digest has proved
   only that the behaviour is now fixed. For a parity or refactor claim, re-derive the old
   value independently (same fixture on `main`) before believing it. An agent that hands
   back a red test intact instead of patching production did the more valuable thing.
5. **Review** — `git diff BASE..HEAD > <workspace>/task-N.diff`; dispatch a reviewer from
   `prompts/task-reviewer.md` with brief, report, and diff paths. Skip per-task review for
   plans of three tasks or fewer (the final review covers them).
6. **Fix rounds** — resume the implementer with the findings; a scoped re-review of the
   fix. Cap at three rounds; on the fourth, adjudicate each open finding yourself: fix
   load-bearing ones with a fresh implementer, park the rest in the ledger with a ruling.
   A finding that conflicts with plan text is ruled on, not dismissed — the plan doesn't
   grade its own work.
7. **Ledger** the completion, mark the todo, next task. No "should I continue?" between
   tasks — the user asked for the plan to run.

**Four things stop the loop, and only these:** an irreversible or destructive operation;
a security-sensitive action; a side effect outside the worktree that is a checkpoint
(mainnet, publish, deploy, faucet beyond testnet, push to a shared branch when that's
gated); a plan so broken every path forward is a guess. Credential-touching live smokes
are yours, not a subagent's (`verifying-claims.md`).

**Batch** small same-shape tasks (three one-line config edits, a rename across files) into
one dispatch; the reviewer then checks every listed file made it into the diff.

## Model selection

The biggest cost lever. An omitted model inherits the session's most expensive one.

| Work                                                                  | Implementer | Reviewer |
| --------------------------------------------------------------------- | ----------- | -------- |
| Mechanical / glue: wiring, config, codegen, renames, docs             | `sonnet`    | `opus`   |
| Ordinary feature logic with clear interfaces                          | `opus`      | `opus`   |
| Move contracts, money/consensus paths, tricky concurrency, migrations | `opus`      | `fable`  |

Step up one tier after a BLOCKED or a fourth fix round.

## Final review and hand-off

After the last task: run `/code-review` on the branch (whole-branch, correctness-focused).
One fix dispatch for the findings, one scoped re-review, adjudicate residuals in the
ledger. Then `finishing.md`.

If the user asks for a `Workflow`, the same loop expressed as a script:
`pipeline(tasks, implement, review)` with the brief/report/diff files as the hand-off.
Not the default — checkpoints are harder to hold inside a script.

## Doc-over-script for coordination

If a plan needs a "sync" or "status" mechanism, prefer a written protocol in the
source-of-truth doc over a script + hook. For solo work a clear written rule (e.g. an
explicit checkbox→emoji mapping in STATUS.md) is as effective at zero maintenance cost.
Automate only for multi-person drift, genuinely complex rules, or when the user says "run a script."

## Large migrations and refactors

- **Expand → migrate → contract:** land the new version additively beside the old,
  migrate consumers, then delete — every commit compiles and stays green.
- **Back-compat entrypoints:** when injecting dependencies into an existing entrypoint,
  keep the old signature as a wrapper over a new `_with(...)` variant so binaries never
  break and rollout flips incrementally.
- **No dead-weight indirection:** consume new types directly; delete pure alias shims —
  keep only shims that do real work.
- **Pure moves get a multiset diff, not a green suite.** When a refactor only relocates
  code (a big `main.rs` split into `commands/`), verify every line of the old file appears
  exactly once across the new ones: `sort old.rs > a; cat new/*.rs | sort > b; diff a b`
  — only `mod`/`use` lines should differ. Tests cover only what they covered before.
- **Orphan audit before scoping:** find dead/orphaned files first — they skew progress
  metrics and get pointlessly migrated.
- **Mirrored layers** (multi-language ports, hand bindings): prefer codegen over
  hand-rolling ("every manual port is an opportunity for drift"); when the source of
  truth changes, re-diff hand mirrors field-by-field — the deployed source wins, never
  carry a mirror-only field; propagate convention fixes to ALL ports and verify each
  ("the SSOT mirror is only as good as its least-updated copy"); route scale/convention
  constants through a mirrored SSOT helper and cover module boundaries with an
  end-to-end boundary test — pure-math unit tests miss boundary bugs.

## Long-running automation and scripts

- Daemons/crankers/keepers degrade per-iteration, never die: catch-and-log every step
  inside the loop (no bare `?`; `let _ = expr?` still propagates), harden pre-loop
  setup the same way, set explicit HTTP timeouts, sleep between iterations.
- Scripts consuming rate-limited external resources (faucets, quota'd APIs): persist
  generated state to reusable files, abort cleanly with clear operator instructions
  when quota hits, and support a resume/reuse flag — don't retry-loop to death, and
  distrust server-provided backoff hints.
- **Ops scripts that mutate an external system are apply-gated:** investigation → script
  → local `--verify` → dry run → commit+push → an explicit `--apply` / `--deploy` /
  `*_SEND=1` flag, default read-only. That is what makes the change reviewable and
  reversible — keep the shape even when you could run the write directly.
