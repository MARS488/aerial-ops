# CivilitySync — Base44 Build Spec

**Paste this into Base44 to generate the real, backend-connected version of the demo already built this session. This is the spec, not the app — Base44 does the actual building from it. Written so nothing has to be guessed or reconstructed from scratch: real pricing, real data model, real constraints already validated against the live Notion databases and the vault's own Customer & Partner Front Door design.**

---

## What to build

A small business app for **CivilitySync** (Marcus Jay Herring LLC), a drone property-documentation and coordination service in Valdosta, GA. Two views:

1. **Client intake** — a property owner enters an address and picks a package, gets an instant quote.
2. **Owner dashboard** — Marcus sees every submission, its status, and can move it through a pipeline.

---

## Critical constraint — build this in from the start, don't bolt it on later

**The business isn't legally allowed to take real paying clients yet — insurance isn't bound.** The app must ship with a single toggle:

```
LIVE_INTAKE_ENABLED = false   // flip to true only when Marcus says insurance is bound
```

While `false`:
- The client intake screen is still fully built and testable, but requires an access code to reach (Marcus's own testing use) — public visitors see a simple "booking opens soon" page instead, not a working form that could collect a real stranger's real address before there's a policy behind it.
- The owner dashboard works normally regardless — it's internal, not public-facing, and carries no insurance risk.

When `true`: the access-code gate on client intake is removed and it's fully public. **This is a single flag flip, not a rebuild** — that's the point of building the gate in from day one.

---

## Data model

```
Job {
  id: auto-increment, format "HD-000N"
  client_name: text
  phone_or_email: text
  site_address: text
  package_tier: enum ["Quick Look", "Full Assessment", "Seasonal Plan"]
  price: number  // set by package_tier, never client-editable — see pricing table below
  service_type: enum ["Real Estate", "Storm Damage", "Construction/Site Progress", "Business & Marketing", "Land & Terrain", "Agriculture", "Custom"]
  status: enum ["Lead", "Booked", "Assigned", "Flown", "Delivered", "Invoiced", "Paid", "Cancelled"]
  found_us_via: enum ["Website", "Referral", "Social media", "Repeat client", "Other"]
  submitted_at: datetime
  notes: text (internal only, never shown to client)
}

Owner {
  // single user — Marcus. Simple email+password auth, no public signup.
}
```

## Pricing — DO NOT HARDCODE, pull from the live Price Card

> ⚠️ **Corrected 2026-08-26.** This section previously listed specific prices ($149 / $349) copied from a note dated 2026-08-10. **Those numbers were already stale when written into this spec** — the real Price Card had moved to a different tier structure and different amounts. This is exactly the fact-drift failure the business's own `Entity Facts - Source of Truth` discipline exists to prevent, reproduced here by copying a number instead of referencing its source.

**Build rule: the app must read its price tiers from a single configurable source (an admin-editable settings table or config record), not from values compiled into the client or the codebase.** Marcus updates prices in one place; the intake screen and the quote both read from it.

**Before building, pull the current tier names and amounts from `Price Card & Rate Model.xlsx` (read its "Do Not Quote" sheet first) — do not use any number from this document or any other secondhand copy.**

Also configurable, not hardcoded — because these genuinely change:
- **Currency** — the app should store an explicit currency code with every price and every transaction, not assume one. Accepted rails (bank transfer, card, cash, crypto) each carry their own compliance handling; don't assume they're interchangeable.
- **Tax treatment** — whether a given service is taxable, and at what rate, varies and changes. Quote **tax-inclusive** ("$X all in") rather than "plus tax," and never collect a tax the business isn't registered to collect.

Price is set server-side from `package_tier` — never accept a client-submitted price.

---

## Screen 1 — Client intake (gated by `LIVE_INTAKE_ENABLED`)

Two inputs only, matching the real design principle behind this business: **"enter address once → tap → done."**

1. Property address (text input)
2. Package (three cards: Quick Look / Full Assessment (default-selected) / Seasonal Plan) — show price and description on each card, no separate pricing page

On submit: create a `Job` row with `status: "Lead"`, `found_us_via: "Website"`, show a confirmation screen ("We'll be in touch within 24 hours"). **Do not promise a specific flight date or claim booking is confirmed** — this is a lead, not a scheduled job, until Marcus reviews it.

Disclaimer footer, always visible, exact text:
> "CivilitySync documents and coordinates — this is not a certified survey, engineering report, or legal determination."

## Screen 2 — Owner dashboard (auth required, Marcus only)

- Table of all `Job` rows, sortable by status and date
- Status can be changed inline (Lead → Booked → Assigned → Flown → Delivered → Invoiced → Paid → Cancelled)
- A summary strip at top: count of Leads this week, count Paid this month, total $ invoiced this month, total $ collected this month
- **If total $ invoiced or collected is $0, show it as $0 plainly** — no placeholder chart, no "coming soon" styling that implies more than zero
- Filter by status; search by client name or address

## Notifications

On new Lead submission (only relevant once `LIVE_INTAKE_ENABLED = true`): send Marcus an email/SMS with client name, address, package, price. Base44's built-in email should cover this; SMS can wait until there's real volume to justify it.

---

## Design direction

Warm, grounded, not generic-SaaS: navy/slate blue as the primary accent (aerial, sky, altitude), a warm clay/terracotta for calls-to-action, off-white paper background rather than pure white. Serif headings, clean sans body text. Avoid stock "purple gradient hero" styling — this is a local, one-person aerial documentation business, not a tech startup.

---

## What NOT to build yet

- Payment processing — no Stripe/Square integration until `LIVE_INTAKE_ENABLED = true` is actually flipped and a real client is ready to pay
- Document/report generation — the actual report templates live elsewhere (Marcus's system); this app tracks jobs, it doesn't generate deliverables
- Subcontractor/pilot assignment flow — real, but a later phase once this core loop is proven
- Any integration claiming to sync with Notion — worth doing later via Base44's webhook/API support once this app's data model is confirmed stable, not on day one

---

## Why this spec exists

This mirrors — deliberately — the real "Customer & Partner Front Door" design already written for this business (address in, one tap, pre-laid-out plans). It is not a new idea; it's the already-decided design, finally given a real backend instead of a demo page. The `LIVE_INTAKE_ENABLED` gate is the one addition specific to this build, because a real backend means a real stranger's real data could get stored before the business is legally ready to act on it — the same reasoning that kept the earlier browser-only demo from being public.
