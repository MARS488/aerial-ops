---
name: "mjh-surface-audit"
description: "Catch drift between the vault's real facts (Entity Facts, Price Card) and anything published to a surface outside the vault — a GitHub repo, a Base44 app, a public artifact, a client-facing page. The vault's own weekly llc-system-audit only reaches the vault and Notion; nothing currently checks external surfaces once a fact leaves the system that watches it. Use before publishing anything with a hard number or fact to an external platform, and periodically against any external surface already live."
status: "PROPOSED — not yet live. Written 2026-08-26 by a cloud/web session with no vault file access, after finding real, live drift in its own working repo: a client demo and a Base44 build spec both shipped with pricing ($149/$349) that had gone stale relative to the live CivilitySync package card ($175/$325/$299) by the time this session actually saw the current numbers. Nothing flagged it automatically — it was found by chance, mid-conversation. Needs a session with real save-skill access to review and register."
---

# MJH Surface Audit

**One job: nothing that leaves the vault should be allowed to go stale silently.** The weekly `llc-system-audit` protects the vault and Notion against each other. This protects everything else.

## The gap this fixes, with the actual case that found it

Earlier this session (before `mjh-operate` existed as loadable content here), a demo prototype and a full Base44 app-build spec were written using pricing pulled from a vault note dated 2026-08-10 ($149 Quick Look / $349 Full Assessment). Two weeks later the numbers had moved. **This case study originally recorded the correction wrongly, and the error is instructive enough to keep visible rather than quietly fix:** it cited the Herring Drones service card ($325 / $395 / $450 / $550 / $1,200-1,900mo) as the demo's correct successor. It is not. The demo is a *CivilitySync package* page, so its card is Quick Look $175 / Full Assessment $325 / Seasonal $299 — confirmed by Marcus 2026-09-12, who ruled that the two price lists are **two coexisting product lines** and that you must always quote the named card and never mix them.

So this skill, written to catch drift, initially committed the exact adjacent error — pulling a real number off the wrong card. That is worth stating plainly, because it shows the failure mode is not only "the number went stale" but also **"the number is current but belongs to a different product line."** A surface audit must therefore check *which card a number came from*, not merely whether the digits match something authoritative somewhere.

**The general failure mode:** any fact that gets copied out of the vault onto an external surface — a git repo, a live app, a printed flyer, a client email template — is a snapshot the moment it's written. Nothing currently re-checks that snapshot against the source. The vault's own audit can't reach these surfaces; most of them aren't files Claude has any standing access to at all.

## What counts as an external surface

Anything with vault-derived facts (pricing, entity name, EIN, insurance status, service descriptions, disclaimer language) living somewhere the weekly vault audit doesn't reach:
- A GitHub repo (like this one)
- A Base44 (or similar) app, once built
- A published Claude artifact (a demo, a dashboard)
- A client-facing document, once sent
- A social media bio, a Google Business profile, a printed flyer

## The check, in two modes

**Mode 1 — before publishing (prevention).** Any session about to write a hard fact onto an external surface should, in the same turn, ask: *"is this number/fact something the vault already has an authoritative value for, and have I confirmed it against the current source rather than an older note I happened to read?"* If the honest answer is "I'm working from a note that's more than a few weeks old," say so explicitly rather than publish silently — same discipline `mjh-operate`'s house rules already require ("say what you did not check").

**Mode 2 — periodic re-check (detection).** For a surface already live: pull the current value from whatever source is reachable this session (Entity Facts, Price Card, or `mjh-operate` itself if loaded), diff it against what's actually published, and report drift plainly — which surface, which fact, old value, new value, date the drift was found. Log the finding the same way any other fact-drift finding gets logged (append to the relevant change log, don't silently fix and move on unless it's routine maintenance the way the vault audit already treats duplicate-fact fixes).

## Known external surfaces as of this writing (seed the tracking list)

| Surface | What's on it | Last checked against source |
|---|---|---|
| **https://mars488.github.io/girl-talk/** (GitHub Pages, **public**) | As of 2026-10-28: a standalone **"Aerial Ops"** site in "Launching soon" mode — v3 price card (locked 2026-10-22), trust strip, add-ons, towns served, FAQ, call/text buttons removed. **All Angel Blue Jay branding removed** (`8b22b02`). | 2026-10-28, cold git read — **the live URL is not reachable from a cloud session (outbound blocked), so this is the branch content, not the served page.** Language boundary clean: "capture only," "we capture, your licensed team certifies," and an explicit not-a-survey / not-an-inspection / not-an-acreage-determination / not-a-takeoff / not-a-dollar-figure-for-a-carrier block. **Open flag: "Aerial Ops" is a brand name that appears in no locked-decisions file and no vault skill** — raised for Marcus/CoS, not reconciled. ⚠️ **This branch is the live Pages source: pushing to it publishes.** |
| github.com/mars488/girl-talk (the repo itself) | Operational toolkit, the CivilitySync demo, the Base44 spec, this bridge | 2026-10-28 — bridge's typed price-card copy **removed and replaced with a pointer**; demo banner rewritten to forbid copying prices in or out; `$149/$349` remains only here, as documented evidence |
| Published Claude artifacts — **"Business Showcase" deck** (`EADz6NybpyXUY5tXee8hH7`) | Published pricing, worked examples, financial model, status | **2026-09-28 content, two price locks behind as of 2026-10-28. Drifted without anyone touching it.** See the new failure mode below — this is the case that proves a pre-publish gate is not enough. Needs Marcus to rebuild or withdraw |
| Published Claude artifacts — **"MJH LLC Business Book"** (`2g9dJZu7vP78qzhCBaNCzY`) | Both service lines, Oct 3 price table, Billy's packet state, back office, "your list" | 2026-10-06 content; its price table is the **Oct 3** lock, superseded by Oct 22. Was not in this registry at all until 2026-10-28 |
| Published Claude artifacts — demo prototype (`DfDHXM5CjXB37w9aSzpP1Q`), Command Snapshot (`1dgqYJF7hdVoDncMvyLJSK`) | Client intake UX; live Notion job data | Demo re-published 2026-09-12 (v3); **the repo copy has since been re-stamped twice and the published copy has not — the same gap as before, still open.** Command Snapshot still holds a 2026-08-11 data pull |
| **`mjh-operate`** (vault skill) | The master card, payment terms, brand list | 2026-10-28 — **carrying a dead price card, a dead "Net 15" term, and a brand list the site no longer matches.** Last verified against disk 2026-08-24. Cannot be fixed without save-skill access |

**Whoever adopts this skill should keep this table current** — it's the registry of "things that can go stale outside the vault's normal reach," and it's short enough right now to maintain by hand.

## Two failure modes found 2026-10-16/28 that the first draft of this skill did not cover

**1. A surface can be correct when published and become wrong later, with nobody touching it.** The Business Showcase deck was accurate on 2026-09-28. The price card was re-locked on 2026-10-03 and again on 2026-10-22. The deck never changed, so it was never re-checked, so it silently became a wrong quote on a reviewer-facing surface. **This is the case that shows a pre-publish gate — `mjh-standard`, which checks "no price invented instead of read from the Price Card" — is necessary but not sufficient.** It fires when something is written. Nothing fires when the *source* moves underneath something already written. A surface registry with a re-check obligation is the only thing that catches this, and the re-check has to be triggered by *the card changing*, not by a calendar.

**2. The record can go stale behind the live surface, not just ahead of it.** The first draft assumed drift always runs outward: a fact leaks out of the vault and rots. The opposite happened here — Marcus updated the public page and the locked-decisions file directly, and the *internal* records (this bridge, `mjh-operate`) were the stale ones. An audit that only asks "does the published surface still match the vault?" would have reported the vault as correct and the page as wrong, which is backwards. **The check has to establish which side moved most recently, by date, before deciding which one is drifted.**

**The structural fix both point to: stop copying the card.** Three locks in eight weeks outran every typed copy. A file that holds a pointer plus a "pull it in the session you quote it" rule cannot go stale; a file that holds digits always will. This is the EIN lesson — `mjh-operate` trap 1, "duplicated facts drift" — applied to prices instead of identifiers, and it should be enforced the same way: quote it or link it, never retype it.

## Why this can't just be "run the weekly audit more broadly"

The weekly `llc-system-audit` works because it has direct file access to the vault and a Notion API connection. Most external surfaces (a live app, a printed flyer, someone's inbox) have neither. This skill is deliberately scoped to work the way `mjh-operate` does — usable by whatever session happens to be looking at the surface in question, with whatever access that session actually has, rather than assuming a single privileged auditor can reach everywhere. That's the only way it scales to surfaces the vault-side automation structurally can't touch.
