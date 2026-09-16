# Finishing

What happens after the last task is done and the final review is clean: the integration
decision, workspace cleanup, and the completion ritual. Do all of it before reporting the
work as complete.

## 1. Full suite on the tree you will integrate

Run the project's full suite on the exact tree being merged — an earlier green run only
proves the tree it ran on. If it fails, report the failures and stop; the menu comes after
green. If the change crosses an external system, the golden-sample live run
(`verifying-claims.md`) must already be done on this branch.

## 2. Integration

- **Work done directly on `main`** (the push-as-you-go default for bounded work): there is
  no menu. Commits are already pushed; go to the completion ritual.
- **Work on a feature branch or worktree:** confirm the base branch if it isn't obvious
  from the plan or the branch's upstream (merging into the wrong base is expensive), then
  present one line with a recommendation and let the user answer with a number:

  1. Merge into `<base>` locally (`--no-ff` for multi-task plans), rerun the suite on the
     merged result, push.
  2. Push and open a PR against `<base>` (use the repo's PR template; report the URL). Keep
     the worktree — PR feedback gets fixed there.
  3. Keep the branch as-is.

  Push to a shared branch and PR creation are ordinary; mainnet txs, publishes, deploys,
  and history rewrites remain checkpoints. Discarding work happens only when the user asks
  for it in so many words; confirm the branch, commits, and worktree that would be lost first.

## 3. Workspace cleanup

- Remove only worktrees this flow created under `.claude/worktrees/`; anything else is
  the user's. Then `git worktree prune`. Delete the feature branch only after option 1 (merged).
- If removal is refused because of uncommitted files, they exist nowhere else: show the
  user the list and ask (commit / move / delete). Never `--force` on your own.
- **Landing check before deleting branches or worktrees:** fix commits made after a PR
  merge can silently never land (committed locally, remote branch deleted). Verify each
  post-merge fix exists on `main` with hard evidence — e.g. a file that commit added is
  present on `main` — and re-land via a follow-up PR if not.
- Delete the plan's `.claude/sdd/<plan>/` workspace once the final review is clean; git
  history and the completion log are the durable record.

## 4. Completion ritual (repos using `docs/superpowers/`)

1. **Dated log** at `docs/superpowers/log/YYYY-MM-DD-<plan-or-task>.md`: what landed
   (modules, entries, struct shapes, key constants — enough to understand the
   implementation without re-reading the plan); language/SDK/tool lessons that forced
   plan amendments; backlog carried forward (deferred items, follow-ups from final
   review).
2. **`docs/superpowers/STATUS.md`:** mark the plan ✅ COMPLETE with its log path; state
   what's next (scope, open decisions, blockers); keep the "Resumption recipe" current so
   `/clear` + reload works — on `/clear`, STATUS.md + `git log` are the trusted state.

Commit both together (e.g. `docs(log): plan N completion log + STATUS update`) so the
merge is the last thing the user sees, not trailing housekeeping.

New repos won't have `docs/superpowers/` yet. If the user is running plans there, create `specs/`,
`plans/`, `log/`, and `STATUS.md` the first time; if a repo clearly doesn't use this flow,
offer it rather than imposing it.

## 5. Report

Report at the idea level (`designing.md` → "Review at the idea level"): architecture
deviations, interface drift, failure mode → test map, localization, blast radius via
`git diff --stat` against the plan's file list. Lead with what's verified and how.
