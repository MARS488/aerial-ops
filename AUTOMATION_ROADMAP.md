# Automation Roadmap — Phased Implementation Plan

**Clear path from manual operations to full automation. Milestones, decision points, effort, and what to do at each phase.**

---

## Current State (Phase 0 - Today)

**What exists:**
- ✅ FLYABILITY_CHECKER.md (manual 5-min decision tree)
- ✅ CLIENT_FLYABILITY_FORM.md (Google Form template)
- ✅ UNIVERSAL_QUOTE_CALCULATOR.py (CLI tool)
- ✅ EMAIL_TEMPLATES.md (15 copy-paste templates)
- ✅ All job documents (intake, agreements, checklists)
- ❌ No automation tooling connected
- ❌ No form→response pipeline
- ❌ All work is manual

**Workflow:**
```
Client calls/emails
    ↓ (Marcus)
Marcus manually checks airspace + weather + site
    ↓ (Marcus)
Marcus runs Python calculator
    ↓ (Marcus)
Marcus sends email from template
    ↓ (Marcus)
Marcus logs job manually
```

**Time per inquiry:** ~15-20 minutes  
**Inquiry capacity:** ~3-5/month (limited by Marcus's time)

---

## Phase 1: Google Form + Manual (Week 1)

**Goal:** Standardize client intake, reduce manual data entry

**What to build:**
- Google Form (CLIENT_FLYABILITY_FORM.md template)
- Google Sheets connection
- Gmail filter for notifications

**Effort:** 30-45 minutes  
**Cost:** $0  
**Tools needed:** Google (Forms, Sheets, Gmail)

**Setup steps:**

1. Create Google Form (15 min)
   - Copy CLIENT_FLYABILITY_FORM.md questions
   - Set as "Quiz" or "Form"
   - Publish + share link

2. Connect to Google Sheets (5 min)
   - Form → Responses tab → Create Sheets
   - New spreadsheet: "Marcus Jay Herring LLC — Inquiries"

3. Set Gmail filter (5 min)
   - Create filter: Subject "Google Forms response received"
   - Auto-label: "Clients/Inquiry"

4. Test (10 min)
   - Submit test form
   - Verify response appears in Sheets
   - Verify Gmail notification arrives

**New workflow:**
```
Client fills form
    ↓
Google Sheets auto-populates
    ↓
Gmail notifies Marcus
    ↓ (Marcus)
Marcus opens FLYABILITY_CHECKER.md (printed, laminated)
Marcus runs calculator (Python)
Marcus sends response (email template)
Marcus logs to Job Status Tracker
```

**Time per inquiry:** 10-15 minutes (faster than calling, cleaner data)  
**Inquiry capacity:** ~5-8/month  
**Metric to track:** Response time (goal: < 30 min)

**Decision point at end of Phase 1:**
- Have you received 5+ inquiries? → Move to Phase 2
- Still <5 inquiries? → Stay in Phase 1, keep promoting form link

---

## Phase 2: Zapier Auto-Response (Week 2-3)

**Goal:** Automate decision email response, keep Marcus engaged

**What to build:**
- Zapier account
- 5 workflows (notification → logging → auto-email by decision)
- Marcus tags each row (FLYABLE/MARGINAL/NOT_FLYABLE) after manual check
- Zapier auto-sends email based on tag

**Effort:** 1.5-2 hours  
**Cost:** $0 (free tier) or $20/month (Pro tier)  
**Tools needed:** Zapier, Google Sheets, Gmail

**Setup steps:**

1. Create Zapier account (5 min)
   - Sign up at zapier.com
   - Connect Google Forms + Google Sheets + Gmail

2. Build Workflow A: Notification (15 min)
   - Trigger: New form response
   - Action: Email Marcus with summary
   - Test with form submission

3. Build Workflow B: Logging (15 min)
   - Trigger: New form response
   - Action: Add row to Job Status Tracker
   - Test with form submission

4. Build Workflow C: FLYABLE auto-email (15 min)
   - Trigger: Row updated where Marcus Decision = "FLYABLE"
   - Action: Send quote email (EMAIL_TEMPLATES.md #1)
   - Test by manually tagging row

5. Build Workflow D: NOT_FLYABLE auto-email (15 min)
   - Trigger: Row updated where Marcus Decision = "NOT_FLYABLE"
   - Action: Send decline email (EMAIL_TEMPLATES.md #14)
   - Test by manually tagging row

6. Build Workflow E: MARGINAL auto-email (15 min)
   - Trigger: Row updated where Marcus Decision = "MARGINAL"
   - Action: Send conditional email
   - Test by manually tagging row

7. Test all workflows (30 min)
   - Submit 3 test forms
   - Verify all emails send correctly
   - Verify Google Sheets updates

**New workflow:**
```
Client fills form
    ↓
Zapier adds row to tracker
Zapier notifies Marcus
    ↓ (Marcus - 5 min)
Marcus runs FLYABILITY_CHECKER.md
Marcus runs calculator
Marcus tags row (FLYABLE/MARGINAL/NOT_FLYABLE)
    ↓
Zapier auto-sends decision email based on tag
Zapier updates status in sheet
    ↓ (Marcus)
Marcus logs job metadata if flyable
```

**Time per inquiry:** 5-7 minutes (still manual decision, but email automation saves 3-5 min)  
**Inquiry capacity:** ~8-12/month  
**Metrics to track:** Response time, decision consistency, quote accuracy

**Decision point at end of Phase 2:**
- Have you sent 10+ quotes from Zapier? → Confident in decision logic? → Move to Phase 3
- Decision logic inconsistent? → Refine rules, stay in Phase 2
- <10 inquiries? → Stay in Phase 2, accumulate more data

---

## Phase 3: Automated Flyability Logic (Week 4+)

**Goal:** Automate decision-making, Marcus only calls hot leads

**What to build:**
- Lookup tables (airspace, weather, pricing)
- Complex Zapier workflow with decision logic
- HubSpot CRM integration
- Slack notifications to Marcus

**Effort:** 2-3 hours  
**Cost:** $20/month (Zapier Pro) + $0 (HubSpot free)  
**Tools needed:** Zapier Pro, Google Sheets (lookup tables), HubSpot, Slack (optional)

**Prerequisites:**
- At least 10 inquiries through Phase 2
- Confident in decision consistency (90%+ accuracy)
- Ready to invest in automation

**Setup steps:**

1. Create lookup tables in Google Sheets (30 min)
   - Airspace Reference (address → class → restriction)
   - Weather Data (date → conditions → flyable)
   - Pricing Tiers (service × acres → price)
   - Complexity Adjustments (hazards → fee)

2. Populate lookup tables (30 min)
   - Manual research: Valdosta airspace classes
   - Manual research: Moody AFB restrictions
   - Manual input: Your pricing structure
   - Set weather data source (manual weekly or API)

3. Create HubSpot free account (10 min)
   - Sign up
   - Create "Inquiries" list
   - Connect to Zapier

4. Build Phase 3 mega-workflow (60-90 min)
   - Trigger: New form response
   - Condition: Check location (Valdosta?)
   - Condition: Check airspace (lookup)
   - Condition: Check weather (lookup)
   - Condition: Check site (hazards/access)
   - Action: Generate decision (FLYABLE/MARGINAL/NOT_FLYABLE)
   - Action: Generate quote if FLYABLE
   - Action: Send decision email
   - Action: Create HubSpot contact + tag
   - Action: Update Google Sheets
   - Action: Slack notify Marcus

5. Test with 10 inquiries (1-2 hours)
   - Submit test forms covering all decision types
   - Verify auto-decisions match your manual decisions
   - Adjust lookup tables if accuracy < 90%
   - Verify email personalization
   - Verify HubSpot logging

**New workflow:**
```
Client fills form
    ↓
Zapier auto-checks: location + airspace + weather + site
    ↓
Zapier auto-decides: FLYABLE / MARGINAL / NOT_FLYABLE
    ↓
Zapier auto-generates quote
Zapier auto-sends decision email
Zapier logs to HubSpot
Zapier Slack notifies Marcus
    ↓ (Marcus - 1 min)
Marcus reviews Slack notification
If FLYABLE: Calls client to confirm
If MARGINAL: Reviews, decides to pursue
If NOT_FLYABLE: Done (already declined)
    ↓
Client follows up on pre-qualified inquiry
```

**Time per inquiry:** 1-2 minutes (notification only, decision automated)  
**Inquiry capacity:** 15-25/month  
**Conversion should improve:** Pre-qualified leads, faster response, better accuracy  
**Metrics to track:** Decision accuracy (target 95%+), inquiry-to-booking conversion, average time to first contact

**Red flags in Phase 3:**
- Decision accuracy < 90% → Adjust lookup tables before going further
- Email personalization wrong → Test email templates
- HubSpot not capturing contacts → Check connection
- Slack notifications unclear → Reformat message template

**Decision point at end of Phase 3:**
- Handling 15+ inquiries/month smoothly? → Move to Phase 4
- Still < 15/month? → Stay in Phase 3, optimize decision logic
- Phase 3 too complex? → Go back to Phase 2 (still automated)

---

## Phase 4: Full Platform Automation (Month 2+)

**Goal:** 100% self-serve funnel, zero manual intake work

**What to build:**
- Service agreement auto-generation (DocuSign)
- Payment collection automation (Stripe)
- Calendar scheduling (Calendly)
- Complete data pipeline (form → decision → agreement → payment → calendar → CRM)

**Effort:** 6-8 hours (professional-level integration)  
**Cost:** $20/month Zapier + $10-20/month DocuSign + 2.2% per transaction Stripe + $0 Calendly free  
**Tools needed:** Zapier Pro, DocuSign, Stripe, Calendly, HubSpot

**Prerequisites:**
- Comfortable running Phase 3
- Handling 15+ inquiries/month
- Want to fully hand off intake

**Setup steps:**

1. Set up payment processing (30 min)
   - Create Stripe account
   - Connect to Zapier
   - Test payment link generation

2. Set up document automation (45 min)
   - Create DocuSign account
   - Create service agreement template
   - Connect to Zapier
   - Test auto-generation + sending for signature

3. Set up calendar sync (30 min)
   - Create Calendly account (or use Google Calendar)
   - Create booking link
   - Connect to Zapier
   - Test auto-scheduling

4. Build Phase 4 mega-workflow (2-3 hours)
   - Inherit Phase 3 decision logic
   - If FLYABLE: Auto-generate service agreement
   - Zapier sends agreement to client via DocuSign
   - Client signs → Zapier receives signature
   - Zapier generates Stripe payment link
   - Zapier sends payment request email
   - Client pays → Zapier confirms payment
   - Zapier creates Calendly booking
   - Zapier adds to HubSpot pipeline (deal stage)
   - Zapier sends Marcus notification: "Booking confirmed: [Client] [Date]"

5. Test end-to-end (2-3 hours)
   - Submit 5 test forms
   - Verify agreement auto-generates
   - Verify client can sign
   - Verify payment link works
   - Verify calendar event created
   - Verify HubSpot deal created
   - Verify Marcus notification clear

**New workflow:**
```
Client fills form
    ↓ (automated)
Zapier auto-decides + auto-sends quote email
    ↓
Client clicks quote email → Clicks "I'm Ready"
    ↓ (automated)
Zapier generates service agreement
DocuSign sends for signature
    ↓
Client signs
    ↓ (automated)
Zapier captures signature
Zapier generates payment link
Zapier sends payment request
    ↓
Client pays deposit
    ↓ (automated)
Zapier captures payment
Zapier auto-schedules flight on Calendly
Zapier creates HubSpot deal
Zapier sends Marcus notification: "✅ Booking Confirmed: [Name] [Date]"
    ↓ (Marcus - 30 sec)
Marcus reviews notification
All the work is done — just show up and fly
```

**Time per inquiry:** <1 minute (monitor Slack, confirm booking)  
**Inquiry capacity:** 25-50+/month  
**Client experience:** Self-serve start to finish, deposit collected pre-flight, calendar auto-synced  
**Marcus workload:** Pre-flight + flight + post-flight only (not intake)

**Metrics to track:** Inquiry-to-booking conversion rate, average days-to-payment, average days-to-flight, client satisfaction

---

## Phase Progression Guide

| Phase | Setup Time | Cost | Time/Inquiry | Capacity | When Ready | Decision Point |
|-------|------------|------|--------------|----------|------------|-----------------|
| 0 (Manual) | 0 | $0 | 15-20 min | 3-5/mo | Now | 5+ inquiries |
| 1 (Form) | 45 min | $0 | 10-15 min | 5-8/mo | Week 1 | 5+ inquiries |
| 2 (Zapier Emails) | 2 hours | $20/mo | 5-7 min | 8-12/mo | Week 2 | 10+ inquiries |
| 3 (Automated Logic) | 3 hours | $20/mo | 1-2 min | 15-25/mo | Week 4 | 15+ inquiries |
| 4 (Full Platform) | 8 hours | $40+/mo | <1 min | 25-50+/mo | Month 2 | Comfortable with 3 |

---

## Weekly Rollout Schedule

### Week 1: Phase 1 Go-Live
- Monday: Create Google Form (15 min)
- Tuesday: Connect to Sheets + Gmail (10 min)
- Wednesday: Test with form submission (5 min)
- Thursday-Friday: Promote form link to warm prospects
- **Milestone:** 2+ inquiries received

### Week 2: Stay in Phase 1, Accumulate Data
- Collect 3-5 more inquiries through form
- Verify response time < 30 min
- Test FLYABILITY_CHECKER.md process
- Decide: Ready for Phase 2?
- **Milestone:** 5+ inquiries total

### Week 3: Phase 2 Go-Live (If Ready)
- Monday: Create Zapier account, build Workflows A-B (30 min)
- Tuesday: Build Workflows C-E (60 min)
- Wednesday: Test all workflows (30 min)
- Thursday-Friday: Run on live mode with new inquiries
- **Milestone:** 2+ decisions auto-emailed from Zapier

### Week 4: Stay in Phase 2, Refine
- Continue collecting inquiries through form
- Marcus manually tags decision (FLYABLE/MARGINAL/NOT_FLYABLE)
- Zapier auto-sends email based on tag
- Measure: Decision accuracy, email quality
- Decide: Ready for Phase 3?
- **Milestone:** 10+ inquiries auto-responded

### Week 5: Phase 3 Go-Live (If Ready)
- Monday-Tuesday: Create lookup tables, populate data (1 hour)
- Wednesday: Create HubSpot account, connect Zapier (30 min)
- Thursday: Build Phase 3 mega-workflow (1.5-2 hours)
- Friday: Intensive testing with 5-10 test forms
- **Milestone:** Automated decisions 90%+ accurate

### Week 6+: Phase 3 Live, Optimize
- Run Phase 3 on all new inquiries
- Monitor: Decision accuracy, conversion rate
- Adjust lookup tables based on real data
- Track: Are you handling inquiries 2x faster?
- Decide: Phase 4 worth the effort?

### Month 2: Phase 4 (If Handling 15+/month)
- Build on Phase 3 foundation
- Add DocuSign agreements
- Add Stripe payments
- Add Calendly scheduling
- Fully automated funnel

---

## Go / No-Go Decisions

### Phase 1 → Phase 2 Decision

**Go to Phase 2 if:**
- ✅ Received 5+ inquiries through Phase 1 form
- ✅ Response time consistently < 30 min
- ✅ Comfortable with FLYABILITY_CHECKER.md process
- ✅ Want to reduce manual email work

**Stay in Phase 1 if:**
- ❌ < 5 inquiries (too small volume)
- ❌ Response time erratic (need more process work)
- ❌ Decision consistency poor (refine checklist first)
- ❌ Zapier cost ($20/mo) not worth it yet

### Phase 2 → Phase 3 Decision

**Go to Phase 3 if:**
- ✅ Received 10+ inquiries through Zapier
- ✅ Auto-email sending 100% reliably
- ✅ Decision consistency 90%+ (compare manual vs. Zapier)
- ✅ Ready to invest 2-3 hours in lookup tables
- ✅ Handling 8+/month and want to scale further

**Stay in Phase 2 if:**
- ❌ < 10 inquiries (build data first)
- ❌ Decision accuracy < 90% (refine logic first)
- ❌ Lookup tables would be inaccurate (get more data)
- ❌ Don't mind manual decision-making

### Phase 3 → Phase 4 Decision

**Go to Phase 4 if:**
- ✅ Handling 15+/month smoothly in Phase 3
- ✅ Automated decisions 95%+ accurate
- ✅ Want to remove all manual intake work
- ✅ Client demand high enough to justify complexity
- ✅ Ready to manage DocuSign + Stripe integration

**Stay in Phase 3 if:**
- ❌ < 15/month (Phase 3 already handles this)
- ❌ Don't want complexity of agreements + payments auto
- ❌ Prefer human touch on every inquiry (that's OK)
- ❌ Stripe fees hurt margin too much

---

## Metrics Dashboard to Track

**Weekly review (every Friday):**

| Metric | Phase 1 | Phase 2 | Phase 3 | Phase 4 |
|--------|---------|---------|---------|---------|
| Inquiries received | Track | Track | Track | Track |
| Response time | < 30 min | < 30 min | < 5 min | < 1 min |
| FLYABLE → Quote sent | Manual | Auto | Auto | Auto |
| NOT_FLYABLE → Declined | Manual | Auto | Auto | Auto |
| Decision accuracy | Manual | ~90% | 95%+ | 95%+ |
| Quotes per inquiry | 1.0 | 1.0 | 1.0 | 1.0 |
| Inquiry → Booking time | N/A | N/A | Track | Track |
| Booking rate | Track | Track | Track | Should ↑ |

**Monthly review:**

- Total inquiries vs. target
- Quote accuracy ($ vs. realized cost)
- Booking rate (inquiries → flights)
- Client feedback score
- System uptime (emails delivered, sheets updated, Zapier errors)
- Time spent on intake (should ↓ with each phase)

---

## Rollback Strategy

**If something breaks:**

**Phase 2 issue?**
- Disable individual Zapier workflow (2 min)
- Go back to Phase 1 (manual responses only)
- Fix workflow, test, re-enable
- No client impact (you handle response manually)

**Phase 3 issue?**
- Disable mega-workflow (2 min)
- Go back to Phase 2 (manual decisions, auto-email)
- Fix decision logic or lookup tables (30 min-1 hour)
- Test thoroughly, re-enable
- Clients get responses, just manually decided

**Key principle:** Each phase contains the previous one. Fallback is always one phase back.

---

## Success Metrics by Phase

### Phase 1 Success
- ✅ Form created and shared
- ✅ 5+ inquiries received
- ✅ All responses documented in Sheets
- ✅ No data lost, clean record

### Phase 2 Success
- ✅ Zapier workflows running
- ✅ 10+ inquiries auto-responded
- ✅ Zero manual email errors
- ✅ Response time < 15 min
- ✅ Client feedback positive

### Phase 3 Success
- ✅ 20+ inquiries processed
- ✅ Auto-decisions 95%+ accurate
- ✅ HubSpot contacts created automatically
- ✅ Inquiry-to-booking conversion rates improving
- ✅ Marcus spending <1 min per inquiry on intake

### Phase 4 Success
- ✅ 50+ inquiries/month processed
- ✅ Agreements signed automatically
- ✅ Deposits collected automatically
- ✅ Flights scheduled automatically
- ✅ Marcus has 0 manual intake work
- ✅ Funnel fully self-serve

---

## Long-term Vision (Phase 5+)

Once Phase 4 is stable (Month 3+):

- **Self-serve owner portal:** Clients check flyability themselves, schedule flights, upload photos
- **Recurring monitoring contracts:** "Subscribe to monthly property checks" → Auto-billed, auto-scheduled
- **Multi-pilot platform:** Hire second pilot, dispatch automatically via Zapier
- **City-scale services:** Valdosta contracts for routine aerial monitoring
- **API integration:** Other drone services integrate to refer their overflow

---

## Your Decision: Which Phase to Start?

**Read this carefully:**

Your situation today:
- ✅ Have all documents (forms, checklists, templates)
- ✅ Have FLYABILITY_CHECKER.md ready to use
- ❌ Have zero automation wired up
- ❌ Haven't received first inquiry yet

**Recommendation:** Start with Phase 1 this week.

1. **Today:** Set up Google Form (30 min)
2. **This week:** Collect first 2-3 inquiries
3. **Next week:** Decide if Phase 2 (Zapier) is worth it
4. **Week 3-4:** Add Phase 2 automation if volume justifies
5. **Week 5+:** Consider Phase 3 if handling 10+ inquiries

**Don't skip to Phase 3 now.** You don't have data yet. Build Phase 1, collect inquiries, then upgrade.

---

## Next 24 Hours

- [ ] Read AUTOMATED_INTAKE_FLOW.md (15 min)
- [ ] Read this document (20 min)
- [ ] Create Google Form from CLIENT_FLYABILITY_FORM.md (15 min)
- [ ] Connect to Google Sheets (5 min)
- [ ] Test with self-submission (5 min)
- [ ] Get form link to your phone, test once more
- [ ] Share link with 2-3 warm prospects (5 min)

**Total time: 60 minutes. Do this today.**

---

**Phase 1 starts now. Everything else follows.**

---
