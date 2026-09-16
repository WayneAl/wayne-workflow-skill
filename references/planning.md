# Planning

The plan is the Tier-2 artifact: written for a clean-context executor subagent who is a
skilled engineer but knows nothing about this codebase, its toolset, or the design
conversation. It argues from the approved spec. The user does not read it — say so when you
hand it over, and offer the already-approved decision list if they want a summary.

Save to `docs/superpowers/plans/YYYY-MM-DD-<feature>.md` and commit. If the spec covers
independent subsystems that weren't split during design, split into one plan each — every
plan must produce working, testable software on its own.

## Header

```markdown
# <Feature> — implementation plan

**Goal:** one sentence.
**Architecture:** 2–3 sentences.
**Spec:** docs/superpowers/specs/<file>.md — executors read both.
**Stack:** the languages/tools/versions in play.

## Global constraints
The spec's project-wide requirements, one line each, exact values copied verbatim
(version floors, dependency limits, naming rules, deprecated surfaces to avoid,
fail-loud accounting, checkpointed actions). Every task inherits this section.

## File map
Which files are created or modified and what each is responsible for. This locks in
decomposition: one responsibility per file, split by responsibility not by layer,
follow existing repo patterns.
```

## Tasks

A task is the smallest unit that carries its own verification and is worth a fresh
reviewer's gate: fold setup, config, and docs into the task whose deliverable needs them;
split only where a reviewer could reject one task while approving its neighbor. Each task
ends with an independently verifiable deliverable and a commit.

```markdown
### Task N: <component>

**Files:** Create `exact/path.rs` · Modify `exact/path.ts:120-160` · Test `tests/exact.rs`

**Interfaces:**
- Consumes: exact signatures this task uses from earlier tasks
- Produces: exact names, parameter and return types later tasks rely on
  (the implementer sees only their own task — this is how neighbors agree on names)

**Steps:** each step is one action with its check.
- [ ] 1. Write the failing test `<name>` (code below) → verify: run `<exact cmd>`,
        expect FAIL with `<reason>`
- [ ] 2. Implement `<thing>` (code below) → verify: same cmd, expect PASS; full suite green
- [ ] 3. Commit: `git add <files> && git commit -m "<type>: <what>"`

**Wayne-workflow rules for this task:** the ones that bite here, inlined verbatim.
```

Test code is included in the plan for **logic tasks** (invariants, math, parsers, state
machines, Move entries, money paths). **Glue tasks** (wiring, config, UI plumbing,
codegen) get a verification command instead of a test ritual — see `testing.md`. Either
way every step says how it is checked; "add validation" without a check is a plan failure.

## No placeholders

These are plan failures: "TBD", "TODO", "implement later"; "add appropriate error
handling" / "handle edge cases"; "write tests for the above" without the test; "similar to
Task N" (repeat it — tasks are read out of order); steps that say what without showing
how; references to types or functions no task defines.

## Self-review before handing over

Run this yourself; no subagent needed:

1. **Spec coverage** — every requirement in the spec points at a task. Add tasks for gaps.
2. **Placeholder scan** — search for the patterns above; fix inline.
3. **Type consistency** — names and signatures in later tasks match what earlier tasks
   define. `clear_layers()` in Task 3 and `clear_full_layers()` in Task 7 is a bug.
4. **Checkpoints** — every side effect that needs the user's confirmation (mainnet, publish,
   deploy, faucet beyond testnet, tests that sign real txs) is marked as held back for the
   orchestrator, never left to an implementer.

Then hand over to `executing-plans.md`.
