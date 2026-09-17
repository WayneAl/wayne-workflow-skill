# Designing

How the user wants the front half of any architectural task run: triage, the design
conversation, the two-tier artifacts, and idea-level review. Grounded in antirez's
"Control the ideas, not the code", ThePrimeagen's interfaces-first floor, and Karpathy's
think-before-coding guidelines. The user's review attention goes to ideas — architecture,
data structures, interfaces, invariants — not to every generated line or page.

The failure mode this fixes: interviewing the user with shallow requirement questions, then
handing them a spec too long to read. They skip the document, and the design decisions
never actually pass through them.

## Triage first

Say the classification in one line so the user can override it:

- **Spike** — feasibility question, answer is the deliverable. Say what you'll try in a
  sentence, then find out. No spec, no plan. Anything built is labeled throwaway; keeping
  it is a new request that gets its own classification.
- **Bounded** — the flow you're changing already exists in the repo to read. State intent
  in a line (approach, files, how you'll verify), then go. If there is no existing flow to
  change, it isn't bounded.
- **Architectural** — new subsystem, interface others depend on, restructure, new repo.
  The rest of this file applies.

If the request describes several independent subsystems, decompose first — which pieces,
how they relate, what order — and design the first one. Each sub-project gets its own
spec → plan → execution cycle.

## Design conversation, not an interview

- Explore the codebase first (files, docs, recent commits, `docs/workflow/STATUS.md` —
  or `docs/superpowers/STATUS.md` in older repos, which keep that directory).
  Native plan mode is fine for this read-only exploration, but the approval surface is the
  chat skeleton below, not a plan file.
- Open with a **design skeleton for the user to shoot at**: the data structures, interface
  signatures, ownership/state boundaries, invariants, error paths, and where it's most
  likely to break — with one recommended approach. They're the architect; PM-style
  questions about purpose and constraints they already implied waste the exchange.
- Where real ambiguity exists, **lay out the 2–3 interpretations explicitly**, labeled so
  the user can answer in a single letter. Batch the load-bearing questions into one synthesis;
  never a one-question-at-a-time interview.
- YAGNI every approach. Design for isolation: each unit has one purpose, a defined
  interface, and can be understood and tested alone. Where existing code has problems
  that affect the work (a file grown too large, tangled responsibilities), include the
  targeted improvement in the design; don't propose unrelated refactoring.
- Before any mass generation the user must own, at minimum: **interfaces, data structures, and
  module boundaries**. Don't proceed to the plan while any of these is still implicit.

## Two-tier artifacts

**Tier 1 — for the user (the approval surface).** A short design doc, hard cap ~60 lines,
saved to `docs/workflow/specs/YYYY-MM-DD-<topic>-design.md` and committed. Sections:

```
# <Topic> — design
Goal / non-goals            2–4 lines
Data structures             each: the idea it embodies, its invariants, the trick
Interfaces                  signatures, ownership, who calls whom
Invariants & failure modes  what must always hold; what happens when it doesn't
Verification                how we'll know it works (which live sample, which tests)
Open decisions              the ones the user needs to rule on, lettered
```

When asking for approval, paste the 5–10 load-bearing decisions inline in chat. Never gate
on "please review the spec file" — the file is the durable record; the chat synthesis is
the review. Before committing, self-check the spec for placeholders, contradictions, and
requirements that could be read two ways; fix inline.

**Tier 2 — for executors.** The full plan (`references/planning.md`), written after Tier 1
approval for clean-context subagents. Tell the user explicitly they don't need to read it;
if they ask about it, answer at the interface level.

## Review at the idea level

When work comes back (per task, or at plan completion), report against these questions —
this is where the user's review attention goes instead of line-by-line diff reading:

1. **Architecture** — built as agreed? Call out any deviation from the approved design
   explicitly, with the reason it was necessary.
2. **Interfaces** — do signatures and types match what the user approved? List any drift.
3. **Tests** — do they cover the failure modes named at design time? Map each named
   failure mode to the test that catches it.
4. **Localization** — when it breaks, will logs/asserts point at the failing unit quickly?
5. **Blast radius** — did anything outside the named scope change? Evidence is
   `git diff --stat` against the plan's file list, not an assurance.

Line-level reading still happens — targeted, not exhaustive: hot spots the user names,
money-touching/consensus-critical paths (Move contracts, fund flows), and the invariants
recorded in the design doc. The gates in `SKILL.md` and the golden-sample run in
`verifying-claims.md` still apply.
