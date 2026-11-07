# Shared scenario run

Environment: `cloud_vm_loopback`
Overall: `VM_STAGES_PASSED_REVIEW_BLOCKED`

Independent review is BLOCKED. This process does not certify the result.
Parent local run is BLOCKED when this file was produced on the cloud VM.

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
| invalid.stored_nothing | PASS | jobs=0 |
| valid.intake | PASS | TS-0001 |
| replay.intake | PASS | jobs=1 |
| castle.same_job | PASS | shared record at received |
| review.stage | PASS | in_review |
| replay.review | PASS | events=2 paid_rejected |
| evidence.once | PASS | score_events=1 points_uninitialized |
| delete.rejected | PASS | 405 |
| invoice.absent | PASS | 404 |
| fixture.readonly | PASS | 405 |
| compliance.not_green | PASS | green_walls=0 preserved 2/2/15 |
| refresh.match | PASS | one job, same three reads |
| bind.loopback | PASS | 127.0.0.1 only |
| restart.reauth | PASS | 401 until secret is presented again |
| restart.readback | PASS | same id, status, history, score, green_walls |
| sqlite.counts | PASS | records=1 events=2 score_events=1 |
| original.lookup | NOT_LOCATED | expected; new castle is not the Nov 6 sketch |
| bind.refusal | PASS | exit 1 |
| screenshots | PASS | 4 loopback screenshots |
| log.redaction | PASS | secret not in server log |
| parent.local_run | BLOCKED | not a substitute for the parent running this script |
| independent.review | BLOCKED | a separate reviewer must check the raw database after the artifact is returned |
