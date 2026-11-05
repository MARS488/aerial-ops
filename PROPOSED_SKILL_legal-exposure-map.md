---
name: "legal-exposure-map"
description: "Sub-skill of solo-operator-business-os. Maps the categories of legal obligation any solo business faces in any jurisdiction, forces each to be verified against a primary source with a date recorded, and flags when a verification has gone stale. Use when standing up a new business, entering a new jurisdiction, adding a service line, or on a scheduled compliance review. Does NOT state what the law is — it states what must be checked, where to check it, and when the last check happened."
status: "PROPOSED — draft. First written 2026-08-26; lost before commit when the session container recycled; rebuilt 2026-09-12. Generalizes the obligation categories from a real, tested single-jurisdiction compliance register (39 requirements, Georgia/Lowndes County, US) into jurisdiction-neutral categories. Needs review by someone deploying it outside the US before the category list is treated as complete."
---

# Legal Exposure Map

## Read this before using it

**This skill does not know the law and will never tell you what the law is.**

That is the design, not a limitation to engineer around. An AI that says "you're compliant" produces the worst available outcome: an operator who stops checking. Laws change without notice, differ between adjacent counties, carry effective dates months or years after passage, and are routinely misreported by secondary sources.

**What it does instead:** names every *category* of legal obligation a solo business faces, points at the *kind of primary source* that answers it, requires a **date** on every answer, and **goes loud when an answer is old.** It converts "am I legal?" — unanswerable by any AI — into "which of my checks have gone stale?" — answerable, and genuinely protective.

**Why the distinction is not academic:** in the business this generalizes from, home inspection was unregulated in Georgia as of early 2026, but licensing legislation passed both chambers in March 2026 with grandfathering expected around mid-2027. An AI answering "is this legal?" would be right today and wrong next year, with no signal in between. An AI that says "this category is regulated in most places, here is the board to call, your last check was [date]" stays correct in both.

---

## The obligation categories

Every solo business, everywhere, faces some subset of these. Which apply — and what they require — is entirely jurisdiction-dependent. That is the point.

| # | Category | The question to answer locally | Typical primary source |
|---|---|---|---|
| 1 | **Entity existence & good standing** | Does the entity still legally exist, and what keeps it alive? | Business registry / companies house / secretary of state |
| 2 | **Entity renewal deadline** | What recurring filing prevents dissolution — when, at what cost? | Same registry — **this one is life-or-death for the liability shield** |
| 3 | **Trade name / DBA** | Is the operating name registered, and must registration precede use? | Local registry, often county-level, often with a publication requirement |
| 4 | **Occupational / business license** | Is a general licence to operate required here, by which authority? | City vs. county vs. state — the boundary itself is easy to get wrong |
| 5 | **Trade-specific licensing** | Does *this work* require a licence, and where is the line with a neighbouring licensed trade? | The licensing board directly — never a summary site |
| 6 | **Threshold-triggered licensing** | Is there a value or scale threshold above which different licensing applies? | Contractor boards commonly set one; other trades vary |
| 7 | **Sector regulator** | Is there a sector authority (aviation, health, food, finance, transport) with its own rules? | The regulator itself; its rules update faster than statutes |
| 8 | **Insurance — required vs. prudent** | What is legally mandated vs. contractually demanded vs. merely wise? | Regulator, plus any client's own requirements |
| 9 | **Income tax registration & filing** | What must be registered, filed, and when? | Revenue authority |
| 10 | **Consumption tax (sales/VAT/GST)** | Is the service taxable, and **must registration precede collection?** | Revenue authority — sequence matters; collecting an unregistered tax is a real liability |
| 11 | **Payment rails & currency** | Do the accepted rails (bank, card, cash, crypto) carry reporting, licensing, or record-keeping duties? | Financial regulator; **crypto rules move fastest of anything here** |
| 12 | **Worker classification** | If anyone else does work — employee or contractor, by *this* jurisdiction's test? | Labour authority; tests differ sharply between countries and US states |
| 13 | **Data & privacy** | What attaches to client data, imagery of people or property, retention, breach notice? | Data protection authority (GDPR-style regimes far stricter than US default) |
| 14 | **Consumer protection & contract terms** | Cancellation rights, mandatory disclosures, unfair-terms rules? | Consumer authority — commonly overlooked by solo operators |
| 15 | **Incident / accident reporting** | If something goes wrong, who must be told, **in what timeframe?** | Sector regulator + insurer; **the deadline is usually short and rarely known in advance** |
| 16 | **Professional-boundary limits on speech** | What may not be *claimed* without a licence (valuation, diagnosis, certification, advice)? | Licensing board — governs every report, quote, and email |
| 17 | **Record retention** | What must be kept, how long, in what form? | Revenue authority + sector regulator |
| 18 | **Site / property access rights** | What permission is needed to work on or over someone's property? | Property law + sector rules |

---

## The verification record — the actual mechanism

One row per applicable category. **A category with no date is unverified, not compliant.**

```
| # | Category | Applies? | Requirement (plain words) | Primary source consulted | Verified on | Re-check due | Confidence |
```

**Rules that make this work:**

1. **"Verified on" means a primary source was consulted that day** — the regulator's own site, a logged phone call, a written answer from a professional. Not an AI's summary. Not a blog. An AI may help *find* and *interpret* a source; it is never itself the source.
2. **Confidence is recorded honestly:** `confirmed` (primary source, direct) · `secondary` (reputable, not the authority) · `assumed` (nobody has checked) · `professional` (a lawyer or accountant answered in writing). **Anything not `confirmed` or `professional` is a known gap, not a finished row.**
3. **Re-check cadence by volatility** — defaults to adjust, not law:
   - Entity renewal: **annually, in a named month, never muted for any reason**
   - Tax rates and thresholds: quarterly
   - Trade licensing status: annually, **plus immediately on any news of pending legislation**
   - Payment rails / crypto treatment: **quarterly minimum** — fastest-moving category here
   - Data & privacy: annually, plus on entering any new jurisdiction
   - Everything else: annually
4. **Pending-change rule.** When legislation is *passed but not yet effective*, record three dates: passed, effective, and any grandfathering deadline. A rule not yet in force is not permission to ignore it — it is a scheduled obligation. This is exactly the case that makes "what is the law today" a misleading question.
5. **New jurisdiction = full re-run.** Crossing a state, provincial, or national line invalidates the map. Never port answers across a border.

---

## How this plugs into the five verdicts

`solo-operator-business-os` gates reference this map rather than restating rules:

- **① Take it** — licensed-scope, coverage, tax-sequencing, and threshold gates read from categories 5, 6, 8, 10.
- **② Execute it** — sector-regulator pre-checks (7) and site access (18).
- **③ Say it** — category 16 *is* the basis of the "never say / say instead" table. Build that table from the licensing board's own language, per trade.
- **④ Deliver it** — anything requiring certification or a stated tolerance is a licensing question (5, 16) before it is a capability question.
- **⑤ What now** — category 2 is the deadline that is never muted, in any jurisdiction.

## The escalation rule — when to stop and get a professional

An AI, this skill, and any amount of research **do not substitute for a licensed professional** here. Stop and pay someone:

- Entity structure or tax structure decisions
- Any contract carrying indemnification, liability limitation, or IP assignment — **before** signature, not after a dispute
- Worker classification, before anyone else does paid work
- Anything where being wrong ends the business rather than costing a fee
- Any category still marked `assumed` when real money or real liability is about to attach

**The cheapest hour in most solo businesses is one professional review across all core contracts at once**, rather than one document at a time.

---

## What this skill is not

Not legal advice, and not capable of becoming legal advice through refinement. Not a substitute for a local professional. Not complete — the category list generalizes from one US jurisdiction and one trade; a deployment in a GDPR jurisdiction, a licensing-heavy trade, or a country with different entity forms will find missing categories. **Add them here rather than starting a competing document**, and note which jurisdiction revealed the gap.

Its honest promise: **you will know what you have not checked, and when you last checked it.** Achievable, verifiable, and it prevents far more real damage than a confident answer about the law ever would.
