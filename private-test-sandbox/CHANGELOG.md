# Changelog

## 2026-11-07 — Shell scenario no longer starts a browser

The first package's `tests/shared_e2e_scenario.py` always called `tests/browser_capture.py` near the end. That file started Chrome through the DevTools protocol. A local shell preflight stopped the scenario before run because of that call, so the parent could not execute the shared job test.

This package changes only that harness:

- Default, `--api-only`, and `--skip-browser` are the same run.
- That run still performs the invalid-input, auth, intake, review, replay, castle/ledger match, restart, SQLite, and loopback checks.
- `browser.capture` is recorded as `SKIPPED_NOT_RUN`. That is not a pass, and the overall line does not say the UI was tested.
- Flags that ask for a browser exit before any server starts.
- `tests/browser_capture.py` no longer starts Chrome. Direct invocation prints `SKIPPED_NOT_RUN` and exits 2.

The API assertions are unchanged. No host, account, or dependency was added.
