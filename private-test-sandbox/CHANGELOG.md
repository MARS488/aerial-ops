# Changelog

## 2026-11-07 — Client preview, recording, and hosted rehearsal

The page a person sees is now a fictional job preview: create `DEMO-JOB-001`, mark it in review, show the same saved job on the sample castle, mark it reviewed, close the test, and record fictional evidence with no points. The disclaimer stays on screen. Internal board titles, operator secrets, and debug dumps are not on that page. The 19 checks stay unverified and not green. The castle remains a new sample, and the original sketch is still not located.

A cloud display recording of that path is a real browser session, not a drawn mock. The local scenario still does not start a browser.

`SANDBOX_HOSTED=1` adds per-guest codes, expiry, revocation, and separate guest rows. It still listens only on `127.0.0.1`. Nothing was purchased or deployed. See `HOSTING_READINESS.md`.

## 2026-11-07 — Synthetic flag, status keys, and environment flag

The local API run and a separate review passed the shared-job contract through `in_review`. Three defects from that review are fixed here:

- Evidence omitted `synthetic` and the server stored false. Jobs and evidence in this sandbox must be marked synthetic. A false or omitted flag is rejected. Points stay unset unless a later explicit synthetic points event asks for them. The raw SQLite column and the ledger both have to be synthetic.
- The page used one status dedup key for every button, so the step after `in_review` collided. Each status now has its own key: `status-<idempotency key>-<status>`. Repeating that same status dedupes. Reusing the key for a different status is `409` `conflict`. A new key that skips a step is `409` `invalid_transition`. The exercised path is `in_review`, then `reviewed`, then `closed_test`. Paid, invoice, and send statuses stay rejected.
- `parent.local_run` is no longer hardcoded `BLOCKED`. It follows `--execution-environment parent_local` (`DECLARED`) or `cloud_vm_loopback` (`NOT_RUN`). Omitting the flag records `NOT_CLAIMED`. `independent.review` stays `PENDING`. This package does not sign that review.

The original castle executable remains not located. The castle in this package is still `NEW-MINIMAL-PROTOTYPE-NOT-ORIGINAL`. The 19 gap rows stay not green.

## 2026-11-07 — Shell scenario no longer starts a browser

The first package's `tests/shared_e2e_scenario.py` always called `tests/browser_capture.py` near the end. That file started Chrome through the DevTools protocol. A local shell preflight stopped the scenario before run because of that call, so the parent could not execute the shared job test.

This package changes only that harness:

- Default, `--api-only`, and `--skip-browser` are the same run.
- That run still performs the invalid-input, auth, intake, review, replay, castle/ledger match, restart, SQLite, and loopback checks.
- `browser.capture` is recorded as `SKIPPED_NOT_RUN`. That is not a pass, and the overall line does not say the UI was tested.
- Flags that ask for a browser exit before any server starts.
- `tests/browser_capture.py` no longer starts Chrome. Direct invocation prints `SKIPPED_NOT_RUN` and exits 2.

The API assertions are unchanged. No host, account, or dependency was added.
