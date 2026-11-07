# Independent review

Status: `PENDING`

The person who built this package does not complete this page. A separate reviewer does, after the archive is unpacked, and ideally after the parent has also run `python3 tests/shared_e2e_scenario.py --api-only --output run-output` on the Linux computer.

## Checks

1. `sha256sum -c SHA256SUMS.source` from the unpacked directory.
2. `python3 verify_stronghold.py` prints `status=ORIGINAL_SOURCE_NOT_LOCATED`.
3. Open `vm-evidence/sandbox.sqlite` read-only and confirm one record, two events, one score event, NULL amount, and NULL points. Queries are in `README.md`.
4. Confirm `vm-evidence/run-report.md` says `API_ONLY_PASSED_BROWSER_SKIPPED_REVIEW_BLOCKED`, with `browser.capture` as `SKIPPED_NOT_RUN` and `independent.review` still `BLOCKED`. That skipped browser stage is not evidence of a UI pass.
5. Confirm the ledger and the castle view in that report agree on `TS-0001`, `in_review`, and `green_walls` 0.
6. On the parent's own run, confirm `run-output/run-report.md` has no `FAIL` stage, `browser.capture` is `SKIPPED_NOT_RUN`, and `tests/expected-counts.json` still matches the counts.

## Signoff

Leave these blank until that review happens.

- Reviewer:
- Date:
- Raw database matched the ledger: 
- Parent local run seen:
- Notes:

Do not mark the 19 board rows complete from this sandbox. Do not treat the new castle drawing as the Nov 6 sketch.
