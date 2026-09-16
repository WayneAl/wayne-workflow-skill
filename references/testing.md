# Testing

The stacks this skill targets have real test suites (Move `#[test]`, `cargo test`, vitest,
pytest, Deno), and their completion logs are full of red→green counts. Tests earn their keep where they encode an
invariant; they are ritual where they only restate wiring. This file says which is which.

## Where TDD applies — red first, watched

For logic: invariants, accounting and margin math, parsers, state machines, scheduling,
Move entry functions, anything on a money or consensus path.

1. **RED** — write one minimal test for one behavior, named for the behavior. Run it and
   **watch it fail for the right reason** (feature missing, not a typo or import error).
   A test that passes immediately is testing existing behavior; fix the test.
2. **GREEN** — the simplest code that passes. No extra options, no speculative
   flexibility. Run the focused test, then the suite, and read the output — pristine, no
   warnings.
3. **REFACTOR** — names, duplication, helpers; stay green; add no behavior.

Code written before its test isn't automatically thrown away (that's the dogmatic
version), but it doesn't count as tested until a test that would have failed without it
exists and has been seen failing — comment the implementation out or revert it to check
when that's cheap.

## Where a verification command applies instead

For glue: wiring, config, UI plumbing, generated code, one-off scripts, prototypes the user
has labeled throwaway. The plan step names the command that proves it (build, `tsc`, a curl,
a rendered frame, a dry-run) and the expected output. Don't manufacture unit tests that
assert a mock was called.

## Bug fixes — always a repro test first

Regardless of the category above, a bug fix starts with a test that reproduces the
symptom and fails. It proves the diagnosis, proves the fix, and prevents the regression.
Where the framework makes it cheap, confirm the red-green pairing: test passes with the
fix, fails with the fix reverted.

## What makes a test honest

- Before writing it, name the production change that would make it fail. If nothing
  would, it asserts nothing.
- Assert real behavior, never mock behavior. Mocks only where the dependency is genuinely
  unavailable, and understand its side effects before mocking it.
- One behavior per test; "and" in the name means split it.
- Test-only hooks stay in test utilities, not in production types.
- Fixtures come from dumped **real** data or ground-truth code, never from a guessed
  shape or re-derived math — guessed fixtures let unit tests pass while the live path is
  broken (`verifying-claims.md`).
- Pure-math unit tests miss boundary bugs in mirrored layers; add an end-to-end boundary
  test across the module seam (`executing-plans.md`, mirrored layers).

## Running tests

- While iterating, run the focused test; run the full suite once before committing.
- **Side-effectful repos** (tests that sign real transactions or share funded accounts):
  exact filters only (`cargo test --lib "path::name" -- --exact`, vitest `-t` and pytest
  `-k` are substring matches too), one test at a time, and running tests at all is a
  checkpoint — get the user's OK first; `cargo check` / `build` are always free.
- Mocked suites repeatedly pass where the live path fails. Green tests do not satisfy the
  golden-sample gate for code that crosses an external system.
