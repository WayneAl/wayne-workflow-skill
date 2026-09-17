---
name: wayne-workflow
description: >-
  A personal development operating protocol — how the user wants engineering work done
  across all of their repos (Sui/Move contracts, Rust cranker/keeper backends, TypeScript
  SDKs, Next.js frontends, data/scraping, and quant). Self-contained: it carries the whole
  lifecycle (triage → design → plan → execute → debug → test → verify → finish) and needs
  no other plugin. Consult it, whether or not the user names it, before any of these:
  designing a feature or writing a spec or plan; executing or orchestrating a plan or
  dispatching subagents; debugging or proposing a bug fix; deciding what to test or
  weakening a check to make a test pass; git commit/branch/push decisions; bulk data
  migrations, merges, or auto-merging data; verifying live/on-chain claims or claiming
  that something works; reporting a task or plan complete; adding automation (a sync
  mechanism, hook, or script to keep something consistent).
---

# wayne-workflow

This skill is a cross-project working agreement, distilled from corrections made one at a
time across many repos. It is self-contained — the lifecycle, the formats, and the
subagent prompts all live here. Each rule carries its reason; apply the reason with
judgment rather than the letter. There are no iron laws below except the three gates.

## Who you're working with

An experienced engineer who owns or architected the stack you're working in. Default to
**high technical depth** and treat the user as the decision-maker on architecture. They
read source, on-chain state, and git history themselves and will correct you when you
misread; when they state a fact about chain state or their own code, trust it over your
first read and ask for the evidence only if it changes the plan.

## Communication

The always-on rules (lead with synthesis + one recommendation, no premature
option-pickers, act-don't-re-confirm, root-cause fixes, take pushback seriously) live in
`always-on.md` at this skill's root, imported into the user's `CLAUDE.md` — source of
truth; never restate them here. Two nuances: terse symptom reports ("still the same" /
"還是一樣") expect a drill-down to the underlying schema/infra/state problem, not a surface
patch (see `references/debugging.md`); and the user's pushback has repeatedly reversed
wrong calls — re-derive from their argument, don't defend.

## The lifecycle

Classify every non-trivial request first, say the classification in one line, and let the
user override it:

- **Spike** — a feasibility question; the answer is the deliverable. Do it as cheaply as
  correctness allows; anything built stays labeled throwaway.
- **Bounded** — a change to a flow that already exists in the repo (a flag, an endpoint, a
  one-file fix). State the intent in one line, then go — the default is action, and the
  user can interrupt. No spec file, no plan file. Tests per `references/testing.md`.
- **Architectural** — new subsystem, an interface others depend on, a restructure, or a
  new repo. Design → spec → plan → execute → finish. When in doubt take the heavier path;
  complexity discovered mid-task upgrades the path, never downgrades it.

| Phase | When | Read |
|---|---|---|
| Design | before any architectural work; skeleton in chat, short spec | `references/designing.md` |
| Plan | after the design is approved; the plan is for executors, not the user | `references/planning.md` |
| Execute | running a plan: worktree, one subagent per task, ledger, reviews | `references/executing-plans.md` + `prompts/` |
| Debug | any bug, failing test, or "still the same" / "還是一樣", before proposing a fix | `references/debugging.md` |
| Test | deciding what gets red→green and what gets a verification command | `references/testing.md` |
| Verify | before saying wrong / broken / working / done | `references/verifying-claims.md` |
| Finish | integration menu, completion log, STATUS | `references/finishing.md` |
| Bulk data | migrations, scrapes, merges, cleanups over many rows | `references/bulk-data.md` |

Specs, plans, completion logs, and `STATUS.md` live under `docs/workflow/`. A repo that
already has `docs/superpowers/` (the pre-2026-09 name) keeps using that directory — the
references' `docs/workflow/` paths mean it there; never start a parallel `docs/workflow/`
beside it.

## Three hard gates

1. **No plan or code for architectural work until the user has approved the design skeleton** —
   data structures, interfaces, invariants, failure modes — in chat.
2. **Code whose real path crosses an external system does not merge without one real
   end-to-end sample on the branch** (LLM CLI, TTS, ffmpeg, chain RPC, third-party HTTP,
   hosting-platform runtime).
3. **No "done / fixed / passing" without fresh verification output in this session.**
   A subagent's report, an earlier run, or "should work" is not evidence.

## Git

The short rules (staged commit+push as you go, branch policy, never amend pushed commits,
pause before rewriting pushed history) are always-on in `always-on.md`. A
PreToolUse hook (`hooks/git-guard.py`) enforces the two destructive ones deterministically.
Procedural detail that belongs here:

- **Recovering from a pushed-amend divergence:** verify the origin-only commit is a
  superseded draft (`git cherry`, `git patch-id`, reflog showing the amend), confirm origin
  has no unique content, then `git push --force-with-lease`. Don't merge/rebase the two
  lines — that leaves near-duplicate commits in history.
- **Checkpoints — surface first and let the user confirm:** mainnet transactions, `npm publish`,
  production deploys, faucet use beyond testnet, force-push/history rewrites, and running
  tests at all in repos where tests sign real transactions. Ordinary push to the user's own
  branches (including `main`) is automatic.
- **Meaningful commits:** one logical unit each, clear messages — not one-per-file noise.
- **No collateral churn — prevent it, don't undo it:** never run a repo-wide formatter
  (`cargo fmt --all`; `-p <crate>` still takes the whole crate); format only the files you
  touched (`rustfmt --edition 2024 <file>`). The undo (`git checkout --` / `git restore`)
  reads as destructive and gets denied, so once churn exists the way out is `git add
  <explicit paths>`. Lint stays repo-wide. Pre-existing uncommitted changes never get
  bundled into yours.

## Scope discipline

- **Minimal removal** (elaborates the always-on smallest-diff rule). When asked to remove
  or hide a feature, remove only what the user named. Leave unreferenced imports, dead branches,
  unused exports, and orphaned assets — features come back, and the scaffolding makes
  restoration cheap. Mention related dead code as an optional follow-up.
- **Refactor storage, not input boundaries.** Drift is a property of long-lived state. When
  de-drifting parallel data, swap the *storage* to a keyed map and keep entry inputs as
  parallel vectors with length-asserts. Don't add hot-potato session structs or PTB-per-row
  machinery for a bug the asserts already catch.
- **Prefer a written protocol over a script/hook for solo workflows.** When the user asks
  for a "sync mechanism", "automation", or "X should happen automatically", first ask which
  need is in play: **consistency** (a written rule in the source-of-truth doc is enough,
  zero maintenance) or **literal execution** (a script is warranted). Default to the written
  protocol; reach for hooks/scripts only for multi-person drift, genuinely complex rules,
  or when the user says "run a script."
- **Never build new code on a deprecated API surface,** and never drift to one for
  convenience. Default to the successor stack; if a needed sub-API exists only on the
  legacy surface, surface it and confine the use to one isolated adapter file. Brief
  subagents with this explicitly.

## Native tools — use them, don't rebuild them

Claude Code already provides: `Agent` with `isolation: "worktree"` for isolated subagent
work, `/code-review` for the final whole-branch review, `/simplify` for quality cleanups on
a diff, `/security-review` for security-sensitive changes, the `Workflow` tool for
deterministic multi-agent pipelines (only when the user asks for one), and the per-project
memory directory for project facts. This skill never re-implements those; it says when to
reach for them.

## Subagents

Subagents start with a clean context and do not consult this skill on their own. Every
brief inlines the rules that matter for that task (fail-loud accounting, minimal diff,
which actions are checkpointed, no credential handling, no deprecated surfaces). Briefs,
reports, and diffs travel as files, never pasted into context. Credential-touching live
smokes stay in the main session. Templates: `prompts/implementer.md`,
`prompts/task-reviewer.md`.

**A subagent killed by a usage limit is resumed, not re-dispatched** — `SendMessage`
to its agent id (or `resumeFromRunId` for a `Workflow`) continues it with full context once
the limit clears, even across a session restart; a fresh dispatch throws that progress
away. Procedure and the signs that mislead: `references/executing-plans.md` § Resuming.
