# Minimal Client Intake — Test Findings (2026-08-11)

**Goal tested:** can a client's entire input be reduced to "where I live + what I want," with everything else automated? Tested against the real, live `Drone Jobs — Herring Drones` Notion database (not a hypothetical form) via a disposable test row, `MJH-3`, `Client = "TEST - Minimal Intake Prototype..."`. Safe to delete in Notion — left for Marcus/next session to clear once reviewed (these tools can't delete/archive Notion pages, only create/update).

---

## What was tested

Simulated the **4-question instant quote** already recommended in the vault's 2026-08-10 Competitor Scan (address / how many photos / video? / edited?) but never actually built as a client-facing form. Mapped those answers onto the real schema:

| Client answer | Real field |
|---|---|
| Address | `Site Address` |
| Photo count + edited?/video? | `Deliverables` (free text) |
| (nothing) | `Found Us Via`, `Status` — system defaults |

## What broke: no price signal

`Package Price` was left blank on purpose. Result: `Total Quote`, `Margin`, `Balance Due` all came back as unreadable `formulaResult://` stubs — **which independently confirms a limitation the vault's own testing already found**: Notion formula columns can't be read back via the API at all. Any automation (a watcher, a form handler) has to compute the dollar figure itself from base fields, never assume it can read the formula result.

**The real gap: 4 questions describe scope but not price.** Address + photo count + video?/edited? tells you what the client wants, not what to charge.

## The fix: package tiers as both scope and price

Don't add a 5th "how much do you want to pay" question — nobody answers that honestly. Instead, replace "how many photos / video? / edited?" with a **tier pick**, matching the pricing framework already in the vault (the $300 / 18-22-still package, and the gap it flagged: no named video tier).

**Client-facing form becomes exactly 2 fields:**
1. Property address
2. Package: Basic ($X, N stills) / Standard ($X, stills + short video) / Premium ($X, stills + video + rush edit)

Tier selection sets `Deliverables` (from a lookup, not free text) **and** `Package Price` (fixed per tier) in the same action. No separate price question, no ambiguity for the automation to guess at.

## Routing to "other places" — already-built infrastructure, just needs a rule

`Assigned Pilot` (`Marcus (me)` / `Subcontractor`) already exists in this schema, and the vault's brokered-job testing already built and tested the paperwork chain for it (Subcontractor Pilot Agreement, COI/W-9 tracking, margin-guard against unprofitable assignments). The only missing piece is a **distance rule on `Site Address`**: outside Marcus's normal flying radius → auto-set `Assigned Pilot = Subcontractor`, which triggers paperwork already built. This is wiring a rule onto tested infrastructure, not new development.

## What's still not built (the one real remaining gap)

A public-facing box the client actually types into. These MCP tools can create/update Notion *pages*, not turn on Notion's native **Forms** feature on a database — that's a one-time manual toggle (Notion → Drone Jobs database → Add Form view → map to `Site Address` + tier-select property) that only Marcus can click. That toggle is the entire remaining distance between "described" and "a client can actually submit this."

## Recommended next concrete step

1. Add a `Package Tier` select property to the real Drone Jobs database (Basic/Standard/Premium) with the price baked into each option's name or a paired lookup.
2. Turn on Notion Forms for that database, exposing only `Site Address` + `Package Tier` to the public form.
3. Confirm the existing `drone-job-flow-watcher` computes `Package Price` from the tier selection (base fields, not the formula) before generating any paperwork — matching the "compute totals itself" fix already made during the 2026-08-10 test run.
4. Still gated on insurance binding before any real submission can be invoiced — this doesn't change that.

---

## Round 2 (2026-08-11, same day) — testing beyond the drone job database

Marcus asked to run as many free tests as possible before insurance is paid for, against everything real that's connected, not just this repo. Four more tests, all read-only or self-cleaning:

**1. Training Clients — Personal Training database (real, read-only check).** Queried both real rows. `Bill Herring` and `Jamie Herring` both still show `Status = Pending onboarding`, `Onboarding Packet Signed = No`, `Physician Clearance Received = No`. This confirms the roster-drift issue the vault already flagged (its own `Client-Roster.xlsx` says Jamie is "Active") is still live and unresolved — Notion is the more cautious value and is being treated as operative, per the vault's own standing rule. Not a new bug, but a real hiccup risk if left as-is: a client believing they're active to train while the system correctly says not-cleared. No test data was written to this database — it holds two real clients, so read-only only.

**2. Dropbox storage (real, read-only check).** `/LLC Business/Drone Business Plan/` still contains the 929MB editing-templates zip and a 126MB video flagged in the vault back on 2026-08-05 — unaddressed. `Tax and Legal/` has the two real files the vault logged (EIN record, Part 107 cert). `Client and Financial/` is still empty. No quota-percentage tool was available to confirm the "over quota" claim precisely, but the specific large files it was attributed to are confirmed still present.

**3. Real client-quote email, drafted not sent (Gmail, real account).** Created an actual Gmail draft (id `r7289739259783520909`) implementing the 3-tier package idea from Round 1 — Basic $250 / Standard $300 (matches the real baseline package) / Premium $450 (adds the named video tier the 2026-08-10 Competitor Scan flagged as missing). Draft created successfully with no formatting errors from the API side. **Marcus should open the draft once and eyeball it** — draft creation succeeding doesn't confirm visual rendering, only that Gmail accepted it. Clearly marked as a test in the subject line and body; safe to discard.

**4. Scheduling automation, full create+delete cycle (Google Calendar, real account).** Created a private test event (`TEST - Flight Auto-Schedule Check`) with zero attendees, then deleted it — confirmed `status: cancelled` in the response. Proves the "auto-schedule the flight" step of the automation is mechanically sound and fully reversible, with no notifications sent to anyone (`notificationLevel: NONE`).

**Net result:** nothing new broken. One already-known gap (training roster drift) reconfirmed still open. Everything tested this round is real infrastructure already connected — no new signups, no money spent.

---

*Test artifacts: Notion page `MJH-3` (drone job, prefixed `TEST -`), Gmail draft `r7289739259783520909` (marked test in subject/body). Both safe to delete/discard once reviewed. The calendar test event was already deleted by this session.*
