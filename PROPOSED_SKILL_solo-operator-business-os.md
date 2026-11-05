---
name: "solo-operator-business-os"
description: "Generalized operating skeleton for running an entire company by one person, in any country, any currency, any trade. Derived from the five-verdict pattern proven in mjh-operate (a real, working single-operator drone/training business), stripped of every business-specific fact and replaced with explicit configuration slots. Use this to stand up the operating logic for a NEW solo business — then fill in the Required Configuration before relying on any verdict. Never state a price, currency, licensing rule, or jurisdiction-specific fact from this file itself — it has none on purpose."
status: "PROPOSED — draft skeleton, written 2026-08-26. Generalizes real, tested logic (mjh-operate) rather than inventing new logic. Needs review by someone actually deploying it for a second business before treating the abstraction as correct — a pattern proven once, for one business, is a hypothesis about generality, not a confirmed one."
---

# Solo Operator Business OS — generalized skeleton

**This file contains zero prices, zero currencies, zero jurisdiction-specific legal rules, on purpose.** Every fact of that kind belongs in the Required Configuration block below, filled in once per business, referenced everywhere else — never restated. This is the same discipline `Entity Facts - Source of Truth.md` enforces in the MJH system, applied from the start instead of retrofitted after a fact drifted.

## Why this file has no numbers in it

A skill that hardcodes "$325" or "USD" or "Georgia requires X" is correct for exactly one business, in one currency, in one place, until something changes — and something always changes. The proven fix, found the hard way in the system this generalizes from: separate the **logic that doesn't change** (should I take this job, can I say this, can I actually deliver this) from **the facts that do** (how much, in what currency, under which country's rules). This file is only the first kind.

---

## REQUIRED CONFIGURATION — fill in before using any verdict below

```
BUSINESS_NAME:              [legal entity name]
ENTITY_TYPE:                [sole proprietor / LLC / Ltd / GmbH / etc. — per local law]
JURISDICTION(S):            [country, state/province, and any sub-jurisdiction that regulates this trade]
LICENSED/REGULATED?:        [is this trade licensed here? by whom? what's the licensing body's actual name]
CURRENCY(IES) ACCEPTED:     [list — e.g. USD, EUR, a specific stablecoin, cash-only. Each currency may have its own legal/tax handling — do not assume they're interchangeable]
PAYMENT RAILS:              [bank transfer, card processor, crypto wallet, cash — each has its own compliance obligations in most jurisdictions; list what's actually set up]
TAX REGISTRATION STATUS:    [what's registered, what isn't, what the correct sequence is for adding a new one — verify locally, never assume]
INSURANCE HELD:             [what's bound, what isn't — this is the single most common gate across trades]
GEAR/CAPABILITY CEILING:    [what can actually be delivered today, honestly — see ④ below]
PRICING MODEL:              [link to an external price sheet — never restate numbers inside this skill file]
```

**Rule: if any verdict below needs one of these values and it isn't filled in, the correct answer is "I don't know, and neither should you assume" — not a guess.**

**Every legally-loaded slot above (jurisdiction, licensing, tax registration, payment rails, insurance) is filled in and kept current via the `legal-exposure-map` sub-skill.** That sub-skill deliberately does not state what the law is — it names what must be checked, where the primary source is, and when the last check happened, so a stale answer announces itself instead of quietly becoming wrong. Never fill these slots from an AI's summary, from this file, or from any secondhand source.

---

# THE FIVE VERDICTS (generalized)

## ① TAKE IT? — should this engagement be accepted

Run when any work comes in. Any single REFUSE stops it.

| Gate | REFUSE if | Why (generic) |
|---|---|---|
| **Licensed-scope boundary** | The ask crosses into work a *different* license/certification covers in this jurisdiction | Almost every regulated trade has a neighboring regulated trade it must not perform or imply performing |
| **Coverage** | Required insurance/bonding for this jurisdiction/trade isn't bound, and the work is paid | Same shape as any insurance gate — the specific requirement varies by trade and place |
| **Price** | Zero, missing, or currency-ambiguous (which currency, at what rate, as of when) | Never invoice an undefined amount |
| **Deposit math** | Deposit exceeds total, in the actual settlement currency | Prevents a negative balance from a currency-conversion error as much as a math error |
| **Counterparty** | No identifiable client/payer | — |
| **Location/scope** | No defined site, region, or scope of engagement | Cannot check any location-dependent rule (safety, licensing, tax nexus) without one |
| **Tax sequencing** | Engagement is taxable here but the required registration isn't done yet | Charging a tax you're not registered to collect is a real liability in most systems, not just the US |
| **Labor/materials threshold** | Work crosses into a licensed-contractor threshold for this jurisdiction (if one exists) | Refer, don't perform, across the line |

All clear → proceed to invoicing per the configured pricing model.

**The deposit trap, generalized:** quote **tax-inclusive, in the settlement currency, at a stated rate if currency conversion is involved.** "$540 all in" beats "$500 plus whatever tax and whatever the exchange rate is by the time you pay."

## ② EXECUTE IT? — is doing the actual work cleared today

Booking clear ≠ execution clear. Re-check same-day.

**Hard gates, generic shape — fill in the trade-specific version:**
- Any regulatory pre-check specific to the trade and location (equivalent to airspace/weather for drone work — could be a permit, a site inspection, a professional sign-off)
- Environmental/external conditions that make the work unsafe or non-compliant today, not yesterday
- Equipment/certification actually current — not "usually current"
- Permission from whoever actually controls the site/subject of the work, confirmed, not assumed
- The physical/practical space to actually do the work safely

**Abort criteria, decided in advance, not improvised on site:** any hard gate above failing · conditions outside the trade's known safe operating limits · cannot maintain whatever oversight/control the trade requires · people present who shouldn't be · rushed or pressured into skipping a check · any required authorization not actually confirmed, only assumed.

**"I already traveled here" is never a reason to proceed past a failed gate.**

**After execution, before leaving:** log what was done · secure/back up any data or materials produced · note anything anomalous · run ③'s same-day disclosure check · record what could not be completed and why.

**If something goes wrong:** safety of people first · stop · document the scene before anything changes · record it the same day · notify whoever needs notifying (insurer, regulator) per this jurisdiction's actual rule and timeline — **look this up per trade/place, don't assume a specific number of days** · tell the counterparty factually · never speculate on cause or admit fault in the moment.

## ③ SAY IT? — can this communication go out

**Governs every message, report, quote, and call.** Violated one word at a time, same as the original.

### The general boundary

Every regulated trade has a neighboring, *more* regulated activity that looks similar from outside but requires a different license — a photographer describing damage is not the same act as an adjuster valuing a claim; a bookkeeper is not an accountant; a handyman is not a licensed contractor past a threshold. **Identify that neighboring boundary for this specific trade and jurisdiction, and never cross it in writing, however casually.**

### Pattern for the "never say / say instead" table (build this per trade)

| Never say (implies the regulated neighboring act) | Say instead (states only what was directly observed/done) |
|---|---|
| Any word that implies certification/licensure you don't hold | The plain factual description of what was actually done |
| Any statement of value, cost, or professional opinion outside scope | *Nothing* — refer to the licensed party for that judgment |
| Any claim of accuracy/tolerance not actually measured | Only what was verified, stated as verified |

### The same-day disclosure rule, generalized

If the work reveals something **plainly hazardous or actively worsening**, disclose it to the affected party the same day, in plain factual terms, before the formal deliverable — regardless of what the normal turnaround time is. Follow with the written record. This holds in every trade: a report delivered on schedule that sat on a known hazard for days is a bad document to have your name on, in any jurisdiction.

## ④ DELIVER IT? — can this actually be produced with what's on hand

**State the real capability ceiling, and never quote past it.**

### The pattern (fill in per trade)
List explicitly what current tools, certifications, and access **cannot** honestly produce — the "Do Not Quote" list. This is not a limitation to hide; stating it plainly and offering the honest alternative (refer, or "not yet, here's what would need to change") is a trust-building move, not a lost sale, in every trade this pattern has been tested against.

### The refusal, as a pattern to fill in
> *"I can't produce [X] with what I currently have, and I won't guess at it — a wrong [X] costs you [real consequence]. I can do [what's actually deliverable], and [alternative resource] can get you [X] for about [their cost]."*

**Unlock order, generalized:** identify the cheapest, highest-leverage missing piece first (usually software/processing before hardware) · confirm the next piece actually works before promising anything built on it · never add a capability to the price list until it's been tested end to end on a real case, not assumed to work because the tool exists.

## ⑤ WHAT NOW? — what's actually blocking progress today

Ask what's *binding*, not what's merely undone. **Run this through the constraint-acknowledgment check before naming anything** — see `mjh-constraint-check` (already proposed, generalizes cleanly: any solo operator can decide, on purpose, to be in a build phase, and a skill that nags about an already-made decision is worse than useless, it's actively unpleasant to work with).

**The one category of deadline that should never be muted, in any jurisdiction:** whatever keeps the legal entity itself alive — an annual filing, a renewal, a registration lapse that would dissolve the liability shield. **Identify this specific deadline for the actual jurisdiction in use and treat it the way `mjh-operate` treats Georgia's April 1 registration — always raised, regardless of acknowledgment state.**

Otherwise, ranked: a job stuck mid-pipeline → move it · money owed past terms → chase it · a real, imminent deadline → handle it · otherwise → the distribution problem, which is universal regardless of trade: **who knows this business exists.**

---

# HOUSE RULES (these generalize directly, unchanged)

1. **Verify before claiming.** Read the output back. Do not report success from intention.
2. **Say what you did not check.** An honest "I didn't verify X" beats a confident wrong answer, in any business.
3. **One consolidated source per fact, never competing versions.** This is the entire reason the Required Configuration block exists instead of numbers scattered through prose.
4. **Never state a tolerance, a legal rule, or a currency fact you did not confirm for this specific jurisdiction and moment.** "This is how it works" has legal weight; "verify this locally, rules change" is the honest default.
5. **Refuse in plain language, with the reason** — every gate above should be a sentence the operator can say out loud to a client, in any language, in any trade.
6. **Respect an acknowledged decision.** A muted constraint is a choice, not an oversight — per `mjh-constraint-check`.
7. **When a fact changes — price, currency accepted, a legal threshold — fix it in the Required Configuration block first, then everywhere that references it, never in a downstream document alone.** This is the fix for the exact bug (a hand-typed fact drifting out of sync) that this whole pattern was built to prevent.

---

## What this file is not

Not a substitute for local legal, tax, or licensing advice in whatever jurisdiction it's deployed — the honest promise here is "asks the right question every time," not "knows every country's law." Not proven at scale — this generalizes a pattern that has worked for exactly one real business so far. Deploying it for a second, genuinely different trade and confirming the five verdicts still hold is the actual test of whether this abstraction is correct, not an assumption to make in advance.
