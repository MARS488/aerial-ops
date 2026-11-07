# Private test sandbox

One local process for a synthetic CivilitySync job and a new castle view. Both read the same SQLite row. Nothing here books a job, sends a message, creates an invoice, files a form, or takes a payment.

This is not the public website. It listens on `127.0.0.1` only. The original Nov 6 castle executable was not located. The castle screen is a new minimal prototype and is labeled `NEW-MINIMAL-PROTOTYPE-NOT-ORIGINAL`.

## What you need

- Python 3.9 or newer. The cloud VM run used Python 3.12.3.
- No `pip install`. `requirements.txt` is intentionally empty.
- No Base44, Notion, Dropbox, Stripe, Monday, GitHub Pages, or other account.
- A computer you already have. This package does not sign you up for hosting.

## Client preview

`python3 server.py` then open `http://127.0.0.1:8765/` on that computer. The first screen asks for the local secret and does not print it. After that, the page is a fictional job named `DEMO-JOB-001`. It can be saved, marked in review, shown on the sample castle, marked reviewed, and closed as a test. Sample checks stay unverified. The banner reads: Pre-release prototype • Fictional data • Not accepting operational customers.

The guest entrance at `/guest.html` stays off unless `SANDBOX_HOSTED=1`, and even then the process still binds only `127.0.0.1`. See `HOSTING_READINESS.md`. Nothing has been deployed.

## Run the shared scenario

From this directory:

```sh
python3 verify_stronghold.py
python3 tests/shared_e2e_scenario.py --api-only --execution-environment parent_local --output run-output
```

`--skip-browser` is the same run. So is omitting the mode flag. The default is API-only. The command does not start Chrome, and it does not skip the API, restart, dedupe, database, or auth checks. `tests/browser_capture.py` is not called. Running that file directly prints `SKIPPED_NOT_RUN` and exits 2.

The scenario is deterministic. It uses one synthetic job:

| Field | Value |
| --- | --- |
| Correlation id | `CORR-SYNTHETIC-JOB-0001` |
| Idempotency key | `idem-synthetic-job-0001` |
| Site label | `SYNTHETIC-JOB-0001` |
| Job id | `TS-0001` |
| Status after the allowed path | `closed_test` (`received` to `in_review` to `reviewed` to `closed_test`) |
| History events | 4: `record.created`, then three `record.status` events |
| Synthetic flags | job and evidence stored as synthetic; points stay unset |
| Score events | 1, points left uninitialized |
| Jobs after replay | 1 |
| Green compliance walls | 0 |
| Preserved board counts | 2 Built, 2 In progress, 15 Not started |

Those counts live in `tests/expected-counts.json`. The script fails if the run does not match them. Invalid address, price, and contact-detail submissions are rejected before the valid job is stored. Replaying the create, the review, and the evidence append does not add a second job, event, or score. The process is then stopped and started again. The database remains. The caller must present the local secret again. Civility, the castle view, and `GET /api/ledger` return the same job.

The script's overall line is not an independent review:

- `API_ONLY_PASSED_BROWSER_SKIPPED_REVIEW_PENDING` means the API stages passed under `--execution-environment cloud_vm_loopback`. Browser interaction was not run. Independent review is still pending.
- `LOCAL_API_ONLY_PASSED_BROWSER_SKIPPED_REVIEW_PENDING` means the API stages passed under `--execution-environment parent_local`. That flag records the invoker's declaration. It is not an independent review signature.
- `API_ONLY_PASSED_BROWSER_SKIPPED_ENVIRONMENT_UNDECLARED_REVIEW_PENDING` means the API stages passed and no environment flag was passed, so the run claims neither machine.
- `FAILED` means an API, restart, dedupe, database, or auth stage did not match. Read `run-output/run-report.md`. Do not treat a failed run as success.

`browser.capture` is `SKIPPED_NOT_RUN` on every successful shell run. That value is not a pass, and it does not mean the page was clicked through.

`parent.local_run` and `independent.review` stay `BLOCKED` inside the script. A separate person fills `REVIEWER.md` after inspecting the raw database. The implementation run does not do that.

## Initialize the local secret

The account name is `sandbox-operator`. That name is not a secret. The secret is created on the computer that starts the process and is never printed.

Manual use:

```sh
python3 server.py
```

The first start writes `data/access.token` with mode `0600`. Read that file on this computer and paste it into the page at `http://127.0.0.1:8765/`. Do not send the file contents in chat, email, or a ticket.

Check the mode without printing the secret:

```sh
python3 -c 'import pathlib; print(oct(pathlib.Path("data/access.token").stat().st_mode & 0o777))'
```

That should print `0o600`.

To rotate it, stop the process, delete `data/access.token`, and start again. Old browser tabs must paste the new value. Records already in `data/sandbox.sqlite` stay. There is no cookie session. After a restart the same file still works, and a request without it is rejected.

The shared scenario creates its own secret under `run-output/data/access.token`. That file is for the computer that ran the scenario. The packaged VM evidence does not include a secret. Inspect the packaged database with `sqlite3`, or run the scenario yourself and use the secret it creates on your machine.

## Open the two views

With the process running and the secret entered:

- Intake stores a synthetic record.
- Review reads it back and moves `received` to `in_review`, then `reviewed`, `closed_test`, or `rejected`.
- New castle draws the same stored job. Stone marks are not green. A `B` is a preserved Built label, not clearance.
- Scoreboard can append one uninitialized evidence event. Repeating it dedupes. Points do not change access, money, or wall color.

There is no price field. Payment, invoice, and booking statuses are rejected.

## Inspect the VM evidence

`vm-evidence/` is the cloud VM loopback run from 2026-11-07. It is not your local run and it is not a signed review.

```sh
sqlite3 vm-evidence/sandbox.sqlite "SELECT id, status, correlation_id, idempotency_key, billing_state, amount_cents FROM records;"
sqlite3 vm-evidence/sandbox.sqlite "SELECT kind, dedup_key FROM events ORDER BY seq;"
sqlite3 vm-evidence/sandbox.sqlite "SELECT dedup_key, points, review_state FROM score_events;"
```

Expected rows:

```text
TS-0001|closed_test|CORR-SYNTHETIC-JOB-0001|idem-synthetic-job-0001|disabled|
record.created|create:idem-synthetic-job-0001
record.status|status-idem-synthetic-job-0001-in_review
record.status|status-idem-synthetic-job-0001-reviewed
record.status|status-idem-synthetic-job-0001-closed_test
score-idem-synthetic-job-0001||uninitialized
```

`synthetic` is `1` on the job row and the evidence row. Points and amount are NULL. Add `synthetic` to the SQLite select when you want to see the flag.

The empty amount and empty points are SQL NULL, not zero.

## Verify the archive

`SHA256SUMS.source` covers the runnable source. Check it from the unpacked directory:

```sh
sha256sum -c SHA256SUMS.source
```

`vm-evidence/SHA256SUMS.vm-run` identifies the cloud VM outputs. Your own rerun writes different timestamps, so its ledger and database hashes will differ. Compare counts, not those file hashes.

## Boundaries

- Bind address is `127.0.0.1`. `SANDBOX_BIND=0.0.0.0` exits without listening.
- No outbound client calls are made by the server.
- The 19 board rows are a fixture copy. Their proof URL is the gap matrix. Nonempty proof does not paint a wall green.
- Preserved counts stay 2 Built, 2 In progress, 15 Not started. The two Built rows are labels for LLC Active and Part 107. This software did not recheck those conditions and does not call them software builds.
- Treasury opening balance is `UNKNOWN`, not zero.
- No live Notion connection. Base44 is not used.

## Cloud VM evidence for this archive

`vm-evidence/` is an API-only cloud loopback run with `--execution-environment cloud_vm_loopback`. Its overall line is `API_ONLY_PASSED_BROWSER_SKIPPED_REVIEW_PENDING`. `parent.local_run` is `NOT_RUN` on that evidence. It does not include browser screenshots, and it does not claim the page was driven. Passing it does not sign `independent.review`; that stage stays `PENDING`.

The previous package blocked a local shell preflight because the scenario always launched Chrome. See `CHANGELOG.md`.

## Earlier harness breaks

Two runs before the first recorded pass failed and were fixed in the scenario checker:

- The network check treated `sqlite3.connect` and `urllib.parse` as outbound clients. They are not. The checker now allows them.
- Restart reused a stale `listen.json`, so the client called a closed port and got connection refused. The waiter now requires the new process id.

Those were harness breaks, and they are fixed in this package. If your run fails, the report's failing stage is the break. Do not describe that stage as passed.

## Not done

- Parent execution on the persistent Linux computer: blocked until you run the commands above.
- Independent review of the raw database: blocked until a different reviewer does it.
- Original Nov 6 executable: not located. See `PROVENANCE.md`.
- Hosted deployment, including the Render note in `HOSTING_PROPOSAL.md`: not purchased and not started.
- Public launch, production restart, and edits under `docs/`: not part of this package.
