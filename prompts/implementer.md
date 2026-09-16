# Implementer subagent — brief template

Write the brief to `<workspace>/task-N-brief.md`, then dispatch with the prompt below.
Files, not pasted text: the brief and the report stay in the workspace.

```
Agent (general-purpose), model: <per executing-plans.md table>, description: "Implement Task N: <name>"

You are implementing Task N: <name> of the plan at <plan path>.

Working directory: <absolute worktree path>. Work only there.
Brief: <workspace>/task-N-brief.md — read it first; it holds the full task text,
the interfaces you consume and produce, and the environment state already verified.
Spec (for intent, not for scope changes): <spec path>.

## Do
<numbered list copied from the plan's steps, each with its verify check>

## Skip
<what is already done, with evidence>

## Do not
- Touch files outside the task's file list; don't "improve" adjacent code.
- Perform any of these — they are held by the orchestrator: <checkpoints for this task:
  mainnet tx / publish / deploy / faucet / push to shared branch / running side-effectful tests>.
- Handle credentials or run credential-touching smokes; report what needs one.
- Dispatch subagents of your own; review is the orchestrator's job.
- Build on a deprecated API surface; if a needed call exists only there, stop and report.

## Rules that bite here (wayne-workflow, verbatim)
<inline the 2–5 rules that matter for this task, e.g. fail-loud accounting; minimal removal;
exact test filters one at a time; raw-data-first fixtures; expand→migrate→contract>

## Testing
<"TDD: red first, watch it fail for the right reason, then green" for logic tasks |
"Verification command: <cmd>, expected <output>" for glue tasks>
Run the focused test while iterating; the full suite once before committing.

## Commit
One commit per logical unit on this branch, message `<type>: <what>`. No collateral
churn: never run a repo-wide formatter — format only the files you touched, and `git add`
explicit paths rather than reverting files a tool re-serialized.

## If you are stuck
It is always fine to stop. Report BLOCKED (can't complete) or NEEDS_CONTEXT (missing
information) with what you tried and what you need. Don't guess at architectural
decisions or restructure beyond the plan; report DONE_WITH_CONCERNS instead. A test you
cannot make green honestly stays red and goes in the report — leaving it in place is more
valuable than patching production to satisfy it.

## Report
Write the full report to <workspace>/task-N-report.md: what you implemented, files
changed, tests run with the exact command and the relevant output (RED and GREEN
evidence for TDD tasks), concerns. Then reply with only these fields — the report file
carries the detail:
- Status: DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
- Commits (short SHA + subject)
- One-line test summary
- Concerns, if any
- Report path
If BLOCKED or NEEDS_CONTEXT, put the specifics in the reply itself.
```

After a review round, resume the same agent with the findings; it appends a fix report
(what changed, covering tests, command, output) and replies with the same status contract.
