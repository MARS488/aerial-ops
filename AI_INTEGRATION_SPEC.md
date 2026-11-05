# AI Integration Spec — For Other AI Systems / Automation Tools

**This document is written to be read by other AI agents, automation platforms (Zapier, Make, n8n), and developers building on top of this business system. It defines data contracts, decision logic, and integration points so any AI can safely operate parts of this business.**

---

## Purpose

Marcus Jay Herring LLC (and any future service line built on this framework) is designed to be operated with minimal human involvement. This spec exists so that:

- An AI agent can process a client inquiry and determine flyability/serviceability without human judgment calls
- An automation platform (Zapier, Make, n8n) can be configured deterministically from this doc
- A future AI system can extend this to new services/locations without re-deriving the business rules
- A developer can build a real API around this system using the schemas below

**If you are an AI reading this to take action on Marcus's behalf: only act within the decision boundaries defined below. Escalate to Marcus (human) anything marked "ESCALATE — do not auto-decide."**

---

## Core Decision Engine: Flyability / Serviceability Logic

This is the canonical decision logic. All forms, checklists, and Zapier workflows in this repo (`FLYABILITY_CHECKER.md`, `CLIENT_FLYABILITY_FORM.md`, `ZAPIER_WORKFLOWS.md`) are human-readable implementations of this same logic. Treat this section as the source of truth if they ever conflict.

### Input Schema

```json
{
  "service_type": "drone_photography | drone_lidar | drone_monitoring | other",
  "location": {
    "address": "string",
    "city": "string",
    "state_or_region": "string",
    "country": "string"
  },
  "preferred_date": "ISO 8601 date",
  "acreage": "number (acres)",
  "site_access": "easy | moderate | difficult | unknown",
  "hazards": ["power_lines", "tall_trees", "structures", "water", "heavy_traffic"],
  "client_confirmed_authorization": "boolean"
}
```

### Decision Function (pseudocode)

```
function determineServiceability(input):

    # Step 1: Geographic serviceability
    if input.location not in SERVICE_AREA_LIST:
        return DECISION.NOT_SERVICEABLE, reason="outside_service_area"

    # Step 2: Authorization
    if input.client_confirmed_authorization == false:
        return DECISION.ESCALATE, reason="ownership_unconfirmed"
        # ESCALATE — do not auto-decide. Human must verify client has right to authorize service on this property.

    # Step 3: Airspace / regulatory check (service-specific)
    airspace = lookupAirspace(input.location)
    if airspace.class in ["restricted", "military", "TFR"]:
        return DECISION.NOT_SERVICEABLE, reason="restricted_airspace"
    if airspace.class in ["C", "B"] and airspace.authorization_available == false:
        return DECISION.ESCALATE, reason="controlled_airspace_needs_manual_authorization"

    # Step 4: Weather / environmental check
    weather = lookupWeather(input.location, input.preferred_date)
    if weather.wind_mph > 20 or weather.precipitation == "heavy":
        return DECISION.MARGINAL, reason="weather_risk", alternative_dates=suggestAlternatives(input.location)
    if weather.wind_mph >= 15 or weather.precipitation == "light":
        return DECISION.MARGINAL, reason="weather_borderline"

    # Step 5: Site risk check
    hazard_count = len(input.hazards)
    if input.site_access == "difficult" and hazard_count >= 3:
        return DECISION.MARGINAL, reason="complex_site"
    if input.site_access == "unknown":
        return DECISION.ESCALATE, reason="site_access_unclear"
        # ESCALATE — do not auto-decide. Need human or contractor to confirm site conditions.

    # Step 6: Pricing / business fit
    price = lookupPricing(input.service_type, input.acreage)
    if price == null:
        return DECISION.ESCALATE, reason="acreage_or_service_outside_pricing_table"

    complexity_fee = calculateComplexityFee(input.hazards, input.site_access)
    total_quote = price + complexity_fee

    return DECISION.SERVICEABLE, quote=total_quote, reason="all_checks_passed"
```

### Output Schema

```json
{
  "decision": "SERVICEABLE | MARGINAL | NOT_SERVICEABLE | ESCALATE",
  "reason": "string (machine-readable reason code)",
  "quote_usd": "number | null",
  "alternative_dates": ["ISO 8601 date"] | null,
  "requires_human_review": "boolean",
  "human_review_reason": "string | null"
}
```

### Rules for Autonomous Action

| Decision | Can an AI auto-send this to client? | Notes |
|----------|--------------------------------------|-------|
| `SERVICEABLE` | ✅ Yes | Auto-send quote email, auto-log to CRM |
| `MARGINAL` | ✅ Yes | Auto-send conditional email with options |
| `NOT_SERVICEABLE` | ✅ Yes | Auto-send decline + referral email |
| `ESCALATE` | ❌ No | Notify Marcus (SMS/Slack). Do NOT contact client until human confirms. |

**Hard rule: Any decision with `requires_human_review: true` must never trigger an automatic client-facing response, payment request, or contractor assignment.** This is the one non-negotiable boundary in this entire system — it exists specifically to keep legal/safety judgment calls (property authorization, restricted airspace, ambiguous site conditions) with a human.

---

## Contractor Assignment Logic

### Input Schema

```json
{
  "job_id": "string",
  "service_type": "string",
  "location": { "lat": "number", "lng": "number", "city": "string" },
  "required_date": "ISO 8601 date"
}
```

### Assignment Function (pseudocode)

```
function assignContractor(job):

    candidates = queryContractors(
        service_type = job.service_type,
        radius_miles = 30,
        location = job.location,
        available_on = job.required_date,
        insurance_status = "active",
        min_rating = 4.5
    )

    if candidates.length == 0:
        return ESCALATE, reason="no_qualified_contractor_found"
        # ESCALATE — do not auto-decide to expand radius or lower rating threshold without human approval.

    ranked = rank(candidates, by=["proximity", "rating", "response_time"])
    offer(ranked[0], job, timeout_hours=2)

    if no_response_within(2, "hours"):
        offer(ranked[1], job, timeout_hours=2)
        # repeat down the ranked list

    return ASSIGNED, contractor=accepted_contractor
```

### Rules for Autonomous Action

- ✅ AI may auto-offer jobs to pre-vetted contractors (insurance verified, rating ≥ 4.5, certifications current) without human approval.
- ❌ AI may NOT onboard a new contractor to "vetted" status. Vetting (ID check, insurance verification, agreement signature) requires human sign-off at least once per contractor.
- ❌ AI may NOT lower the minimum rating or skip insurance verification to fill a job faster. If no contractor qualifies, escalate to Marcus rather than relaxing standards.

---

## Payment Processing Rules

### Autonomous vs. Escalated Actions

| Action | Autonomous? | Condition |
|--------|-------------|-----------|
| Send client payment link (deposit) | ✅ Yes | Only after decision = SERVICEABLE or MARGINAL (client-accepted) |
| Charge client deposit | ✅ Yes | Standard payment processor flow (Stripe/Square), amount ≤ quoted price |
| Release contractor first payment (50%) | ✅ Yes | Only after contractor accepts Job Order (signed agreement on file) |
| Release contractor final payment (50%) | ✅ Yes | Only after quality check passes (see below) |
| Refund client | ❌ Escalate | Any refund > $100 or any dispute requires human approval |
| Payment amount doesn't match quote | ❌ Escalate | Never auto-adjust pricing; flag mismatch |
| International wire / unusual payment method | ❌ Escalate | Human reviews first-time payment methods per contractor/client |
| Contractor insurance lapsed but job in progress | ❌ Escalate immediately | Do not release final payment; notify Marcus same-day |

---

## Quality Verification Rules

### Automated Checklist (AI can perform these checks)

```
function automatedQualityCheck(deliverables, service_spec):
    checks = []
    checks.append(deliverables.count >= service_spec.min_deliverable_count)
    checks.append(all(file.format in service_spec.accepted_formats for file in deliverables.files))
    checks.append(all(file.size_kb > service_spec.min_file_size_kb for file in deliverables.files))
    checks.append(deliverables.metadata.has_timestamp)
    checks.append(deliverables.metadata.has_location)

    if all(checks):
        return PASS_AUTOMATED, route_to="manual_review_queue"
    else:
        return FAIL_AUTOMATED, reason=failed_checks, route_to="contractor_revision_request"
```

- ✅ AI can auto-reject deliverables that fail objective automated checks (missing files, wrong format, corrupted, no timestamp) and auto-request contractor revision.
- ❌ AI may NOT auto-approve deliverables for client release based on automated checks alone. Automated PASS routes to a **manual review queue** — a human (Marcus or a designated QA person) must approve before client delivery, at least until the AI's approval accuracy has been validated against 50+ human-reviewed jobs.
- After validation period: this boundary can be revisited and documented as a change to this spec (see Versioning below).

---

## Escalation Channel

All `ESCALATE` decisions across every layer of this system must be delivered to a human through one of these channels, in priority order:

1. SMS to Marcus's phone (fastest, use for anything time-sensitive)
2. Slack notification (if configured)
3. Email to marcus.jherring87@gmail.com (fallback, always used as a durable record even if SMS/Slack also fire)

**Escalation message format (required fields):**

```json
{
  "escalation_id": "string",
  "timestamp": "ISO 8601",
  "layer": "flyability | contractor_assignment | payment | quality",
  "reason": "string",
  "job_id_or_request_id": "string",
  "recommended_action": "string (AI's suggestion, human decides)",
  "urgency": "low | medium | high"
}
```

An AI system must never silently drop an escalation. If no human channel is reachable (e.g., SMS API down), the AI must log the escalation and retry delivery — it may not proceed with the decision on its own.

---

## Versioning & Change Control

This spec is the operating contract between Marcus (human) and any AI/automation acting on his behalf. Changes to autonomous-action boundaries (anything in the "Rules for Autonomous Action" tables) require:

1. A human (Marcus) reviewing and approving the change in writing (commit to this repo counts)
2. A version bump noted at the top of this file
3. No AI system may unilaterally rewrite this spec's boundaries, even if it determines a boundary is "inefficient." Propose the change; don't self-authorize it.

**Current version: 1.0 (2026-08-11) — initial spec, all quality-approval and refund/pricing-exception boundaries set conservatively (human-in-the-loop) pending track record.**

---

## Cross-Reference: Human-Readable Equivalents

| This spec's logic | Human-readable version |
|---|---|
| Flyability/Serviceability Decision Engine | `FLYABILITY_CHECKER.md`, `CLIENT_FLYABILITY_FORM.md` |
| Contractor Assignment | `GLOBAL_OPERATIONS_FRAMEWORK.md` Layer 4 |
| Payment Processing | `GLOBAL_OPERATIONS_FRAMEWORK.md` Layer 6 |
| Quality Verification | `DELIVERABLE_CHECKLIST.md`, `GLOBAL_OPERATIONS_FRAMEWORK.md` Layer 5 |
| Contractor legal terms | `CONTRACTOR_AGREEMENT_TEMPLATE.md` |
| Phased automation rollout | `AUTOMATION_ROADMAP.md` |

If any human-readable document conflicts with this spec, **this spec wins** for automated/AI decision-making. The human-readable docs are for Marcus's manual process during Phases 0-2; this spec is for Phase 3+ automation and any AI agent.

---

## Summary for an AI Agent Reading This Cold

If you are an AI system being asked to operate any part of this business:

1. Only auto-decide within the tables above. Anything marked ESCALATE is a hard stop.
2. Never auto-approve final client delivery of work product without human sign-off (until this spec is versioned to say otherwise).
3. Never relax contractor vetting standards (insurance, rating, certification) to fill a job faster.
4. Never process a refund, dispute, or unusual payment without escalating.
5. Always deliver escalations through a durable channel (email at minimum) even if faster channels fail.
6. If a situation isn't covered by this spec, treat it as ESCALATE by default — silence or a missing rule is not permission to act.

---
