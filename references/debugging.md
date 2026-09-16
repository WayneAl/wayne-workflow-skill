# Debugging

Find the root cause before proposing a fix. The user reports symptoms tersely — "still the
same" / "還是一樣", "still broken" / "還是壞的" — and each one means the previous change was a
surface patch. They expect the drill-down to the underlying schema, infra, or state problem,
and they will catch a guess.
Systematic investigation is also faster than guess-and-check thrashing, especially under
time pressure.

## Phase 1 — root cause

1. **Read the error completely.** Stack trace, line numbers, error codes; they usually
   contain the answer.
2. **Reproduce consistently.** If you can't trigger it reliably, gather more data before
   theorizing.
3. **Check what changed.** `git diff`, recent commits, new dependencies, config,
   environment differences between where it works and where it doesn't.
4. **Instrument component boundaries** in multi-component systems (CI → build → sign;
   frontend → edge function → DB; cranker → RPC → chain). Log what enters and exits each
   layer, run once, and read where it breaks before investigating that layer.
5. **Trace the bad value backward** to where it originates; fix at the source, not where
   it surfaced.
6. **Read the raw data before blaming the source.** "The API returns nothing" claims made
   from parser output alone have consistently turned out to be parser bugs (see
   `verifying-claims.md`). For chain state, read the actual object.

## Phase 2 — pattern

Find working code that is similar (same repo, reference implementation, the other port
of a mirrored layer) and list every difference, however small. Read the reference
completely — a partially understood pattern guarantees a wrong adaptation.

## Phase 3 — hypothesis

State one hypothesis: "X is the root cause because Y." Test it with the smallest change
that would confirm or refute it, one variable at a time. If it doesn't hold, form a new
hypothesis; don't stack fixes. If you don't understand something, say so.

## Phase 4 — fix

- Write the failing reproduction first (`testing.md`: bug fix = repro test before the
  fix). One-off script if there's no framework.
- One change addressing the root cause. No bundled refactoring or "while I'm here".
- Verify per `verifying-claims.md`: the original symptom, the repro test, the rest of the
  suite, and — if the real path crosses an external system — the live sample.

## Three failed fixes → question the architecture

If each fix reveals new coupling or a new symptom somewhere else, or a fix would need
"massive refactoring", stop. That is not a failed hypothesis; it is a wrong pattern.
Discuss it with the user at the design level before attempting a fourth fix.

## When there is genuinely no root cause

Timing-dependent, environmental, or external issues exist. Document what you
investigated, implement the appropriate handling (retry with a bound, timeout, clear
error), and add the logging that would catch it next time. Most "no root cause" cases are
incomplete investigation, so say what you ruled out. For flaky waits, poll for the
condition instead of sleeping an arbitrary duration.
