# Shared scenario run

Environment: `cloud_vm_loopback`
Mode: `api-only`
Overall: `API_ONLY_PASSED_BROWSER_SKIPPED_REVIEW_PENDING`

Browser interaction was not run. SKIPPED_NOT_RUN is not a pass.
Independent review stays PENDING. This process does not sign it.
The environment value comes only from --execution-environment.

| Stage | Outcome | Detail |
| --- | --- | --- |
| health | PASS | ready on 127.0.0.1 |
| auth.missing | PASS | 401 |
| auth.bad_secret | PASS | 401 |
| auth.bad_account | PASS | 401 |
| origin.rejected | PASS | 403 |
| invalid.address | PASS | 400 |
| invalid.price | PASS | 400 |
| invalid.identifier | PASS | 400 |
| synthetic.job_rejected | PASS | 400 |
| invalid.stored_nothing | PASS | jobs=0 |
| valid.intake | PASS | TS-0001 |
| replay.intake | PASS | jobs=1 |
| castle.same_job | PASS | shared record at received |
| review.stage | PASS | in_review |
| replay.review | PASS | events=2 paid_rejected |
| status.dedup_collision | PASS | 409 conflict |
| status.invalid_transition | PASS | 409 invalid_transition |
| status.reviewed | PASS | events=3 |
| status.closed_test | PASS | events=4 |
| synthetic.rejected | PASS | 400 |
| evidence.once | PASS | score_events=1 synthetic=true points_uninitialized |
| delete.rejected | PASS | 405 |
| invoice.absent | PASS | 404 |
| fixture.readonly | PASS | 405 |
| compliance.not_green | PASS | green_walls=0 preserved 2/2/15 |
| refresh.match | PASS | one job, same three reads |
| bind.loopback | PASS | 127.0.0.1 only |
| restart.reauth | PASS | 401 until secret is presented again |
| restart.readback | PASS | same id, status, history, score, green_walls |
| sqlite.counts | PASS | records=1 events=4 score_events=1 synthetic=1 |
| original.lookup | NOT_LOCATED | expected; new castle is not the Nov 6 sketch |
| bind.refusal | PASS | exit 1 |
| browser.capture | SKIPPED_NOT_RUN | api-only; Chrome was not started and UI interaction was not tested |
| log.redaction | PASS | secret not in server log |
| parent.local_run | NOT_RUN | invoker passed --execution-environment cloud_vm_loopback |
| independent.review | PENDING | this script does not sign a review |
