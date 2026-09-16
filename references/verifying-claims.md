# Verifying claims

The user reads source, on-chain state, and logs themselves and will catch an unfounded assertion.
Ground every "this is wrong / broken / working / done" claim.

## Before you claim — four steps

1. **Identify** the command or observation that would prove the claim.
2. **Run it fresh**, in this session, on the tree or state you are claiming about.
3. **Read the whole output** — exit code, failure count, warnings.
4. **Then claim, with the evidence attached.** If the output doesn't support the claim,
   report the actual state instead.

"Should pass", a previous run, a linter for a build claim, a subagent's "success" (check
the diff and state yourself), or a partial check are not evidence. The word choice
doesn't matter — "looks good", "fixed", "ready" all carry the same obligation.

## Evidence chains, not vibes

State *how* you know, and grade your confidence honestly. Keep these three levels distinct:

- **Vendor/docs say X** — an upstream doc or spec claims it.
- **Our usage does X** — our tenant/config/code actually exercises it that way.
- **Verified X end-to-end** — you just ran it and observed the result.

Don't collapse the first into the third. When you cite evidence, point at the concrete thing
(object id, log line, test output, file:line), not a summary.

## Verify live state before declaring a dependency/address/config wrong

Especially on Sui: don't call an address "wrong" or "non-canonical" from a local `Move.lock`
or a git-fetched source alone.

1. `git fetch` the fork before reading its branch — you may be reading a stale cached HEAD.
2. Check `published-at` in the *resolved* `Move.toml` on the branch the dep actually points to
   (it exists — don't claim it doesn't).
3. Cross-check the address on-chain (`sui client object <id>`) if there's any ambiguity.
4. State the evidence chain when claiming an address is wrong — not "this looks off."

(Real miss this prevents: telling the user a canonical wormhole package was "wrong" because two
similar-looking packages were confused and a stale fork HEAD was being read.)

## Live smoke tests — never weaken security to make them pass

When smoke-testing something that enforces auth (e.g. a Supabase Edge Function behind RLS),
exercise it **as a real authenticated user**, going through the real policy path. Do **not**
disable RLS, use the `service_role` key, or forge/self-sign a JWT to get a green result — that
validates the wrong thing and trips safety classifiers.

Recipe for a locally-served, auth'd function (Supabase shape, adapt as needed):

1. `supabase functions serve <fn> --env-file supabase/functions/.env`
   (first request cold-starts — curl with `--retry 12 --retry-all-errors --retry-connrefused
   --retry-delay 2`).
2. Get a **real user JWT**: `POST /auth/v1/signup` with header `apikey: <ANON_KEY>` (from
   `supabase status -o env | grep ANON_KEY`), body `{"email","password"}`; if the user exists,
   `POST /auth/v1/token?grant_type=password`. Keep `.access_token` and `.user.id`.
3. Seed any prerequisite rows through REST with that JWT (`Authorization: Bearer <jwt>`,
   `apikey`, `Prefer: return=representation`) — this also validates the RLS insert policy.
4. Call the function with the JWT. For SSE responses, parse `data: {json}` lines.
5. Verify in the DB via `docker exec <supabase_db container> psql -U postgres -d postgres -c
   "..."` if `psql` isn't on PATH.

**Credential-touching live smokes stay in the main session** — don't delegate them to a
subagent, which will get blocked by classifiers and may try risky workarounds. Subagents are
fine for `deno check` / pure-function `deno test` and other non-credential verification.

## Tests with live side effects — exact filters, one at a time

`cargo test <name>` filters are SUBSTRING matches. In repos where tests sign real
transactions or share funded accounts, a loose filter can run several same-named tests
concurrently — equivocating the shared gas coin and firing unintended on-chain txs
(this happened: `test_add_authorized_user` matched 3 modules at once). Always run
`cargo test --lib "full::module::path::test_name" -- --exact`, and run side-effectful
tests one at a time. Same principle for any test runner whose name filter is a
substring/pattern match (vitest `-t`, pytest `-k`). In such repos, running tests at all
is a checkpoint: get the user's OK first (`cargo check` / `build` are always free).

## Golden-sample live run before merge

Mocked suites repeatedly pass where the live path fails (wrong User-Agent, API shape
drift, CLI flag semantics, ffmpeg quirks). When a branch adds or changes code whose
real path crosses an external system — LLM CLI, TTS, ffmpeg, chain RPC, third-party
HTTP — run **one real end-to-end sample on the branch** before merging, and fix
live-path issues there. "All N tests green" alone does not qualify as the
verified-end-to-end evidence level for such code.

## Platform-runtime behavior — verify on a real preview deployment

A local production server (`next start`, `wrangler dev`, a container run locally) does not
exercise the hosting platform's runtime. Caching, response headers, edge/CDN behavior, ISR,
image optimization, and middleware placement are all decided by the platform adapter — code
that never runs locally. **Local green is not evidence for any of them.** Push the branch,
wait for the preview URL, and run the real `curl` assertions there (status code, the cache
header you care about, the platform's own `x-*-cache` verdict) before merging.

If preview URLs sit behind deployment protection, use the platform's automation-bypass
mechanism (Vercel: `vercel project protection enable <proj> --protection-bypass`, then send
`x-vercel-protection-bypass: <secret>`) — ask before enabling it, since it loosens a
protection setting on the user's project.

(Two real misses this prevents: a cache-tag header only the hosting adapter emits 500'd
every page in production while local was green; and a route handler's own `Cache-Control`
passed straight to the CDN, so an expensive render re-ran on nearly every request while
local showed a clean MISS→HIT.)

## Read the raw data first — fixtures and "source is empty" claims

Before writing a parser + test fixtures for an external data shape, dump the REAL shape
from the live system and derive fixtures from that dump — fixtures encoding guessed shapes
let unit tests pass while the live path is broken. Symmetrically, never declare "the
source has no data / source-side limit" from parser output alone: fetch the raw payload
and read it before blaming the source — such claims made without reading raw have
consistently turned out to be parser bugs.

## The consumer's artifact, not your tests

"All tests green + tsc clean" can be true while the app is broken: tests import `src/`,
the consumer loads the built artifact (`dist/`, a published tarball, an image). After
regenerating or rebuilding a shared layer, rebuild the artifact and verify through the
real consumer path; treat a stale artifact as a first-class failure mode (a CI freshness
guard is worth considering).

## Fail-loud accounting

When decrementing a **persistent accounting counter or balance** (TVL, open interest, pool
sizes, locks), use native subtraction so an underflow **aborts** — do not write a saturating
clamp (`if x >= y { x - y } else { 0 }`). If the invariant guarantees `y <= x`, the else
branch only ever fires when accounting is *already* broken, and clamping to 0 silently "heals"
the drift, hiding the bug permanently. Fail-loud surfaces the real bug at first violation.

Distinguish this from **legitimate `max(0, …)` floors and `min` bounds**, which are defined
semantics, not masks, and should stay:

- margin lock `max(0, req − max(0, Σ nov))`, option intrinsic `max(0, S − K)`
- **reads** of spendable funds `max(0, bal − locked)` (0 is the right answer for an underwater
  account; never written back to state)
- input bounds `min(qty, pos_mag)`, conservative over-provisioning `min(a, b)` where surplus
  is reclaimed later
- payout cascades that **surface** a shortfall via an event (settlement → `BadDebt`) or pay
  the actual amount rather than the requested one

Rule of thumb: **persistent-state decrement → native subtract, abort on underflow;
floor/bound/read/cascade → clamp is fine.** When adding a new counter, re-run the sweep for
`else { 0 }` and `if (.*>=.*) … else` decrement patterns.
