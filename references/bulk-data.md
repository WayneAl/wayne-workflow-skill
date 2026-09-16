# Bulk data operations

For migrations, scrapes, merges, dedupes, and cleanups over many rows, the north star is
**data quality over saving manual effort.** The user is sensitive to metadata quality
(leftover disclaimers, footnote marks, noisy meta in descriptions) and would rather review a
300-row report for an hour than let a fallback rule silently write wrong data. Automatic cleanup rules
never catch everything; a human scanning a table catches them in minutes.

## Three-bucket output — don't hard-merge the ambiguous

Split every bulk merge/cleanup run into three buckets:

- **(a) auto-applied** — high-confidence rows only. Set a strict bar: e.g. sentence-level
  Jaccard ≥ 70%, or one value fully contains the other after normalization.
- **(b) skipped → review report** — anything ambiguous. Do **not** resolve it with a fallback
  like "concatenate both" or "keep the longer one"; those produce duplicated or semantically
  garbled content.
- **(c) unchanged** — nothing to do.

Write the skipped bucket to `reports/<task>_review.md`. For each row list: the title/key, the
competing values side by side, the script's tentative suggestion, and a blank for the user's
verdict.

**Order irreversible steps after review.** `DROP COLUMN` and other one-way operations go after
the user has reviewed the report — never before.

## Markdown review round-trip

For large imports (>50 rows), prefer a round-trip through a markdown table the user edits in
their IDE, treating the edited markdown as the source of truth:

1. **Scrape/prepare phase** — write `<source>.json` (full data) plus a human-facing
   `<source>_review_report.md`: one row per markdown table line, columns like
   title / author / year / category / tags / cover. Use `、` to separate
   list-y fields (tags). The user deletes a whole row to drop it and edits a cell to fix a
   field.
2. **Apply phase** — read the markdown back as SSOT: match rows by a leading `|` and a numeric
   first cell, split cells on `|`, then cross-reference the JSON for things markdown can't
   express (cover URLs, db ids).
3. **Apply idempotently** — SELECT-by-key before insert/update so re-runs are safe.

Tool-budget note: don't inline 100KB+ of SQL into a single migration tool call — it eats the
output-token budget. For large applies, POST rows to the REST endpoint (e.g. PostgREST with a
`service_role` key via a small `urllib`/`fetch` script) instead of one giant inline migration.
Still write the `supabase/migrations/<n>_seed_<source>.sql` file for schema history / staging
replay, even if the real prod apply goes through REST.

## Multi-source merges — best field wins

Evaluate per-field quality and upgrade to the best source rather than COALESCE-filling
NULLs — "only fill blanks" exists to protect human-edited fields, not to pin bad
scraped data. Keep upgrade logic in preprocessing code, not SQL CASE forests.

## Own the assets

Never hotlink third-party URLs into owned data — download and re-host on owned
storage. A non-owned domain in a stored URL means redo it, not shortcut it.

## Audit before "done"

After any bulk seed/rescrape, run a data-quality audit — per-source coverage breakdown
plus noise-marker scan with explicit thresholds — before claiming completion. Parsers
fail silently per-row; bad rows stay invisible until a user hits them.

## Destructive operations

- Before deleting or merging rows, check FK fan-out on every referencing table and
  explicitly repoint children first — never trust CASCADE. Persist the fix as an
  idempotent numbered migration.
- Applied migrations are immutable — extend with a new migration, never edit the
  applied one (fix forward, same principle as pushed commits).
- Dropping data a live writer feeds: ship the writer-side change first, wait days of
  stable operation before the drop, and leave mass-destructive statements for the user to
  run themselves.

## Publish gating

If rows shouldn't go live immediately, INSERT with a `is_published=false` (or equivalent) flag,
let the user review, then flip in a second pass. If they'd rather review the markdown report
first and publish in one shot, do that and skip the extra migration — follow their call per run.
