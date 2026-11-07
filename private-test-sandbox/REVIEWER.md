# Independent review

Status: `PENDING`

The person who built this package does not complete this page. A separate reviewer does, after the archive is unpacked, and ideally after the parent has also run `python3 tests/shared_e2e_scenario.py --output run-output` on the Linux computer.

## Checks

1. `sha256sum -c SHA256SUMS.source` from the unpacked directory.
2. `python3 verify_stronghold.py` prints `status=ORIGINAL_SOURCE_NOT_LOCATED`.
3. Open `vm-evidence/sandbox.sqlite` read-only and confirm one record, two events, one score event, NULL amount, and NULL points. Queries are in `README.md`.
4. Confirm `vm-evidence/run-report.md` says `VM_STAGES_PASSED_REVIEW_BLOCKED`, with `independent.review` still `BLOCKED`.
5. Confirm the castle screenshot shows `Green segments: 0` and the same `TS-0001` / `in_review` text as the review screenshot.
6. On the parent's own run, confirm `run-output/run-report.md` has no `FAIL` stage and that `tests/expected-counts.json` still matches the counts.

## Signoff

Leave these blank until that review happens.

- Reviewer:
- Date:
- Raw database matched the ledger: 
- Parent local run seen:
- Notes:

Do not mark the 19 board rows complete from this sandbox. Do not treat the new castle drawing as the Nov 6 sketch.
