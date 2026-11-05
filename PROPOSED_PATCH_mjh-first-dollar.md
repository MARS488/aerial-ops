# Proposed patch to `mjh-first-dollar`

**Status: PROPOSED. Written 2026-08-26 by a cloud/web session with no vault file access. One addition, inserted into the existing skill's "Stages, and the binding constraint at each" section, right after the constraint is identified and before it's reported.**

---

## The addition (insert verbatim)

> **Before naming the binding constraint, run it through `mjh-constraint-check`.** If the constraint (insurance, first flight, or anything else) has already been acknowledged per `mjh-operate`'s Phase Rule and is inside its 60-day re-check window, **do not report it as this run's finding.** Find and report the next-ranked actionable item instead — for Stage A, that's the two things the skill already names as unblocked in parallel (portfolio flying under Angel Blue Jay, calling the warmest lead on file). If the acknowledgment has passed its 60-day window, name the constraint exactly once, framed as a re-confirmation ("you acknowledged X on [date] — still the plan?"), not as new information.

## Why this specific insertion point

The skill's own method is: *"Determine which stage → name the single binding constraint → prepare the artifact → say how long it's been stuck → report revenue reality."* The naming step is where the failure happens — everything after it (the prepared artifact, the escalation tone) inherits whatever got named. Fixing it at the naming step, rather than adding a disclaimer after, stops the downstream cascade instead of patching around it.

## What doesn't change

Nothing about the honesty rules changes. "Never report green while nothing is being billed" still holds — respecting an acknowledgment isn't the same as pretending revenue exists. The fix only changes *which* true thing gets reported when the most obvious one has already been decided on.

## Evidence this is needed

Observed directly this session: an AI instance ran this skill's method for several consecutive turns, correctly followed the stage logic each time, and named insurance as the binding constraint every time — which is exactly the nagging `mjh-operate`'s Phase Rule was written to stop, because this skill had no way to know that rule existed. The failure wasn't in the logic; it was in a check this skill never had a hook to make.
