---
name: "mjh-constraint-check"
description: "Shared sub-skill: check whether a blocker (insurance, first flight, or anything else) has already been acknowledged/muted per the Phase Rule before naming it to Marcus. Every specialized MJH skill that might name a constraint (mjh-first-dollar, mjh-deadline-watch, mjh-growth-playbook, etc.) should call this first. Not a standalone skill Marcus invokes directly — a rule module the other skills lean on, so the same check doesn't get duplicated (and drift) five different ways."
status: "PROPOSED — not yet live. Written 2026-08-26 by a cloud/web session with no vault file access, in response to a real gap found this session: mjh-first-dollar named insurance as the binding constraint for several turns before mjh-operate's Phase Rule corrected it. mjh-first-dollar's own text has no reference to the acknowledgment system. This sub-skill is the fix, written so any specialized skill can reference one shared rule instead of each reimplementing (and inevitably drifting on) its own version. Needs a session with real save-skill access to review and register."
---

# MJH Constraint Check — shared sub-skill

**One job: stop a specialized skill from naming an acknowledged constraint as if it's news.** Called by other skills, not invoked directly.

## The problem this fixes

`mjh-operate`'s Phase Rule says insurance-not-bound and no-first-flight are permanently acknowledged — Marcus decided, on purpose, to finish the machine before flying it. Don't raise them as news, don't nag. But that rule lives in one file. Every *other* skill that might independently reach for "what's blocking this business" — `mjh-first-dollar`, `mjh-deadline-watch`, `mjh-growth-playbook` — was written before or separately from that rule, and none of them currently check it. A session loading only `mjh-first-dollar` has no way to know a constraint it's about to name has already been decided on.

**Observed failure, this session:** an AI session ran `mjh-first-dollar`'s method for several turns, correctly identified insurance as Stage A's binding constraint each time, and named it repeatedly — exactly matching the acknowledgment system's definition of nagging, because it never checked that system. Only loading `mjh-operate` directly caught it.

## The rule

Before any skill states a blocker, gap, or "what's stopping this" finding to Marcus:

1. **Check `.mjh-acknowledged.json`** if you have file access. If the constraint appears there and is inside its re-check window (see below), **do not name it as a finding.**
2. **If you don't have file access** (a cloud/mobile/text session with no vault reach), and the constraint is one already established earlier in *this same conversation* as acknowledged, treat it the same way — don't re-name it.
3. **If genuinely unsure whether something is acknowledged**, it's safer to ask once — *"is X still an open question or a decision you've already made?"* — than to state it as a fresh finding.
4. **Stating an acknowledged constraint once, inside a direct answer to a question that's actually about it**, is fine. Example: Marcus asks "can I bill this job" and the honest answer requires mentioning insurance isn't bound — say it, that's not nagging, that's answering. The violation is naming it as *the finding of the check-in*, unprompted, again.

## Re-check window (the piece that didn't exist before)

An acknowledgment with no expiry silently becomes invisible rather than intentional. Default: **60 days.** After that, the constraint may be named **once**, framed as a re-confirmation, not a reminder: *"You acknowledged insurance-unbound back on [date] — still the plan, or has anything changed?"* Then re-acknowledge (reset the 60-day window) or actually address it. A constraint whose acknowledgment predates today by more than the window should never sit permanently silent — that's a different failure mode than nagging, and just as real.

**Exception: Georgia Annual Registration is never muted**, per `mjh-operate` — dissolution risk overrides any acknowledgment system. This sub-skill doesn't change that; it inherits it.

## What "calling" this looks like in another skill

Add one line near wherever a skill decides what to report as blocking:

> *"Before naming a constraint here, check it against `mjh-constraint-check` — has it been acknowledged, and is it inside the 60-day re-check window? If so, don't name it as a finding; if the window has passed, name it once as a re-confirmation."*

That's the entire integration. No new data structure, no new file beyond the existing `.mjh-acknowledged.json` — this sub-skill just makes every other skill actually read it.
