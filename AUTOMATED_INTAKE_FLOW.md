# Automated Intake Flow — Full Pipeline

**Complete end-to-end automation: Client submits form → System checks flyability → Auto-responds with decision + quote → Logs to CRM → Notifies Marcus.**

This is the vision. It works in phases. Start at Phase 1, add Phase 2 when comfortable, scale to Phase 3+.

---

## The Full Automation Vision

```
CLIENT SUBMITS FORM
    ↓ (automatic)
Google Form response → Google Sheets
    ↓ (automatic)
Zapier reads form data
    ↓ (automatic)
Zapier triggers flyability logic:
    • Check: Is location in Valdosta? (yes/no)
    • Check: Get airspace class from LAANC (via lookup table)
    • Check: Get weather forecast (via API)
    • Check: Evaluate site hazards
    ↓ (automatic)
Zapier generates decision:
    ✅ FLYABLE → Generate quote via calculator
    ⚠️ MARGINAL → Generate conditional offer
    ❌ NOT FLYABLE → Generate referral response
    ↓ (automatic)
Zapier sends auto-response email to client with decision + quote
    ↓ (automatic)
Zapier logs inquiry to HubSpot CRM (tagged by status)
    ↓ (automatic)
Zapier sends notification to Marcus (email/SMS/Slack)
    ↓ (you act)
Marcus reviews notification, contacts hot leads within 1 hour
    ↓
CLIENT FOLLOWS UP (inquiry pre-qualified + hot)
```

**Result:** 80% of intake is automated. Marcus only engages with hot, pre-qualified leads.

---

## Phase 0: Manual (Now — Baseline)

**What you do:**
- Client emails/calls inquiry
- You manually check: airspace (LAANC app), weather (weather.com), site (Google Maps), business (calculator)
- You manually send response email with decision/quote
- You manually log to spreadsheet

**Time per inquiry:** ~15-20 minutes  
**Frequency:** As needed  
**Tools:** Phone, LAANC app, UNIVERSAL_QUOTE_CALCULATOR.py, Gmail, Google Sheets

**When to move to Phase 1:** After first 5 inquiries (you'll see the pattern)

---

## Phase 1: Google Form + Manual Response (Week 1-2)

**What changes:**
- Client fills out Google Form instead of emailing
- Responses auto-populate Google Sheets
- You still manually check flyability + send response

**Setup (30 minutes):**
1. Create Google Form using CLIENT_FLYABILITY_FORM.md questions
2. Connect form to Google Sheets (Form → Responses → Create Sheets)
3. Print FLYABILITY_CHECKER.md, keep at desk
4. Set Gmail reminder for form responses

**Workflow:**
```
Client fills Google Form
    ↓
Response auto-appears in Google Sheets
    ↓
Gmail notifies you (set up filter)
    ↓
YOU: Open FLYABILITY_CHECKER.md
YOU: Run UNIVERSAL_QUOTE_CALCULATOR.py
YOU: Send response email from EMAIL_TEMPLATES.md
YOU: Log to Job Status Tracker
```

**Time per inquiry:** ~10-15 minutes (faster, more organized)  
**Tools needed:** Google Forms, Google Sheets, Email, FLYABILITY_CHECKER.md, UNIVERSAL_QUOTE_CALCULATOR.py

**Metrics to track:**
- Response time (goal: < 30 min)
- Inquiry-to-job conversion rate
- Average quote amount

**When to move to Phase 2:** After 10 inquiries, when pattern is clear

---

## Phase 2: Zapier Auto-Responses (Week 3-4)

**What changes:**
- Zapier intercepts form submission
- Zapier auto-sends decision email (FLYABLE / MARGINAL / NOT FLYABLE)
- You review notification, follow up if needed
- Manual flyability check still required (you run calculator)

**Setup (1-2 hours):**

### Step 1: Create Zapier Account
- Go to zapier.com
- Sign up (free tier supports 100 tasks/month)
- Connect: Google Sheets, Gmail, Slack

### Step 2: Set Up 3 Zapier Workflows

**Workflow A: New Form Response → Notification to Marcus**

```
Trigger: New Google Form response
Action: Send Slack/Email notification to Marcus with:
- Client name
- Property address
- Service type
- Acreage
- Preferred date
- Summary: "New inquiry: 3 acres, storm, this week"
```

**Workflow B: Form Submitted → Log to Google Sheets**

```
Trigger: New Google Form response
Action: Find row in Google Sheets (match client email)
Action: Add form data to Job Status Tracker sheet
Action: Set status to "Inquiry Received"
```

**Workflow C: Marcus Confirms Flyable → Send Auto-Quote Email**

```
Trigger: New row in Google Sheets where Marcus tagged "FLYABLE"
Action: Fetch client email + acreage from row
Action: Send email template EMAIL_TEMPLATES.md #1 (quote follow-up)
Action: Include UNIVERSAL_QUOTE_CALCULATOR result
Action: Set status to "Quote Sent"
```

**Workflow D: Marcus Confirms Not Flyable → Send Auto-Decline Email**

```
Trigger: New row in Google Sheets where Marcus tagged "NOT_FLYABLE"
Action: Fetch client email from row
Action: Send email template EMAIL_TEMPLATES.md #14 (decline + referral)
Action: Set status to "Declined"
```

**Time per inquiry:** ~5 minutes (Marcus just tags the row, Zapier handles rest)  
**Tools needed:** Zapier (free tier $0, paid $20+/month for more tasks), Google Sheets, Gmail

**What you still do manually:**
- Decide if FLYABLE / MARGINAL / NOT FLYABLE (using FLYABILITY_CHECKER.md)
- Tag the Google Sheets row
- Follow up with client if needed

**When to move to Phase 3:** When you're confident in decision rules

---

## Phase 3: Automated Flyability Logic (Week 4-5)

**What changes:**
- Zapier automatically decides FLYABLE/MARGINAL/NOT_FLYABLE (no Marcus decision needed)
- Auto-generates quotes
- Auto-sends decision emails
- Marcus only engages on hot leads

**Setup (2-3 hours):**

### Step 1: Create Lookup Tables in Google Sheets

**Sheet: Airspace Reference**
```
| Property Address | Airspace Class | Restriction | Notes |
|------------------|----------------|-------------|-------|
| [Valdosta area addresses] | E | None | Unrestricted |
| [Moody AFB area] | D | Military | Cannot fly |
| [Controlled airspace] | C | ATC Auth | LAANC available |
```

**Sheet: Weather Data** (auto-populated by API or manual)
```
| Date | City | Wind | Rain | Visibility | Flyable |
|------|------|------|------|------------|---------|
| 8/15 | Valdosta | 12 | No | 8 miles | Yes |
```

**Sheet: Pricing Tiers**
```
| Service | 0.5-2 ac | 2-5 ac | 5-20 ac | 20+ ac |
|---------|----------|--------|---------|--------|
| Storm | $500 | $1,000 | $2,500 | $5,000 |
| LiDAR | $800 | $1,500 | $3,500 | $7,000 |
| Monitor | $400 | $800 | $2,000 | $4,000 |
```

### Step 2: Set Up Automated Flyability Workflow

```
Trigger: New Google Form response

Step 1: Extract form data
- Client name, email, address
- Service type, acreage, preferred date
- Hazards, access difficulty

Step 2: Check Location
- IF address contains "Valdosta" OR "Lowndes County" → Continue
- ELSE → Decision = NOT_FLYABLE (out of area)

Step 3: Check Airspace
- LOOKUP address in Airspace Reference sheet
- IF Airspace Class = "E" (uncontrolled) → Continue
- IF Airspace Class = "D" (LAANC available) → Continue
- IF Airspace Class = "C/B" OR Military → Decision = NOT_FLYABLE

Step 4: Check Weather
- FETCH weather forecast for preferred date
- IF wind > 20 mph OR heavy rain → Decision = MARGINAL (offer alternate date)
- IF wind 15-20 mph OR light rain → Decision = MARGINAL
- IF wind < 15 mph AND clear → Continue

Step 5: Check Site
- IF site access = "Difficult" AND hazards >= 3 → Decision = MARGINAL
- IF site access = "Impossible" → Decision = NOT_FLYABLE
- ELSE → Continue

Step 6: Check Business
- LOOKUP pricing tier from acreage + service type
- IF price tier matches your offerings → Decision = FLYABLE
- ELSE → Decision = NOT_FLYABLE

Step 7: Generate Quote
- IF Decision = FLYABLE:
  * Pull price from Pricing Tiers sheet
  * Calculate total quote amount
  * Generate quote text
- ELSE:
  * Skip quote generation

Step 8: Send Email
- IF Decision = FLYABLE → Send Quote email (EMAIL_TEMPLATES.md #1)
- IF Decision = MARGINAL → Send Conditional email (EMAIL_TEMPLATES.md #3)
- IF Decision = NOT_FLYABLE → Send Decline email (EMAIL_TEMPLATES.md #14)

Step 9: Log to CRM
- Create HubSpot contact
- Tag by decision (FLYABLE / MARGINAL / NOT_FLYABLE)
- Log inquiry date + decision date
- Set follow-up date

Step 10: Notify Marcus
- Send Slack message: "[FLYABLE] 3 acres, storm, $1,500, this week"
- Link to job intake form
- Link to client email
```

**Time per inquiry:** 0 minutes (fully automated)  
**Tools needed:** Zapier (Pro $20+/month), Google Sheets (formulas + lookup), HubSpot (free tier), LAANC data source

**What Marcus does:**
- Monitor Slack notifications
- Call hot FLYABLE leads within 1 hour
- Review MARGINAL cases (decide to pursue or decline)

**Accuracy required:**
- Airspace lookup 95%+ accurate (check manually on first 10)
- Weather forecast API reliable (test with 2 weeks of data)
- Pricing tiers locked in (don't change mid-automation)

**When to move to Phase 4:** When you've handled 20+ inquiries and want to fully hand off

---

## Phase 4: Full Platform Automation (Month 2+)

**What changes:**
- Quote calculator integrated into Zapier (no need to run Python manually)
- Service agreement auto-generated + sent for signature (DocuSign)
- Deposit collected automatically (Stripe)
- Flight scheduled automatically (Calendly sync)
- Everything pre-filled in your job system

**Architecture:**
```
Google Form → Zapier → Decision Logic → Quote Generation → Service Agreement → Deposit Collection → Calendar Sync → CRM → Notification → Marcus Action

All data flows through one pipeline. Zero manual work before Marcus engages.
```

**Setup (6-8 hours, professional-level):**
1. Host UNIVERSAL_QUOTE_CALCULATOR.py on cloud (AWS Lambda or Zapier CLI)
2. Integrate DocuSign for auto-generating service agreements
3. Integrate Stripe for automatic deposit processing
4. Integrate Calendly for automatic scheduling
5. Create full data sync: Form → Sheets → HubSpot → Calendly → Stripe

**Cost:** Zapier Pro ($20/month) + HubSpot free ($0) + DocuSign ($10-20/month) + Stripe (2.2% per transaction) + Calendly free ($0)

**Result:** Full self-serve funnel. Client fills form → Automatic email + agreement + payment collection → Scheduled on calendar → Marcus gets one notification per confirmed booking.

---

## Which Phase For You? Decision Tree

```
Do you have 1-3 inquiries/month?
├─ YES → Use Phase 0 (manual)
└─ NO ↓

Do you have 3-5 inquiries/month?
├─ YES → Use Phase 1 (Google Form + manual)
└─ NO ↓

Do you have 5-10 inquiries/month?
├─ YES → Use Phase 2 (Zapier auto-response)
└─ NO ↓

Do you have 10+ inquiries/month?
├─ YES → Use Phase 3 (Automated decision logic)
└─ NO ↓

Do you have 20+ inquiries/month?
└─ YES → Use Phase 4 (Full platform)
```

**Your next step:** Start with Phase 1 (this week). Get 5 inquiries through the Google Form. Then decide if Phase 2 makes sense.

---

## Implementation Checklist

### Phase 1 (This Week - 30 min)
- [ ] Create Google Form from CLIENT_FLYABILITY_FORM.md questions
- [ ] Connect to Google Sheets
- [ ] Set Gmail filter to label form responses
- [ ] Print FLYABILITY_CHECKER.md (laminate or plastic sheet)
- [ ] Keep at desk for quick reference
- [ ] Send form link to 3 warm prospects

### Phase 2 (Next Week - 1-2 hours)
- [ ] Create Zapier account (free)
- [ ] Connect Zapier to Google Forms + Gmail + Slack (if available)
- [ ] Build 4 Zapier workflows (Notification, Logging, Flyable Quote, Not Flyable Decline)
- [ ] Test with 2-3 form submissions
- [ ] Adjust email templates if needed

### Phase 3 (Week 3-4 - 2-3 hours, only if 5+ inquiries)
- [ ] Create lookup tables in Google Sheets (Airspace, Weather, Pricing)
- [ ] Build automated decision workflow in Zapier
- [ ] Connect to HubSpot (free tier)
- [ ] Test with 5 inquiries (check accuracy)
- [ ] Verify quote calculator integrates correctly
- [ ] Adjust decision rules if needed

### Phase 4 (Month 2+ - Professional build, only if 20+ inquiries)
- [ ] Host UNIVERSAL_QUOTE_CALCULATOR.py in cloud
- [ ] Integrate DocuSign for agreements
- [ ] Integrate Stripe for payments
- [ ] Integrate Calendly for scheduling
- [ ] Full data pipeline testing

---

## Weekly Ops With Automation

### Phase 1 Weekly (5 min/inquiry)
- Monday-Friday: Check form responses (Slack notification)
- When notified: Run FLYABILITY_CHECKER.md (5 min), send response, log job
- Friday: Review all inquiries, update Job Status Tracker

### Phase 2 Weekly (1-2 min/inquiry)
- Monday-Friday: Zapier handles notifications + auto-emails
- When notified: Review, tag row (FLYABLE/MARGINAL/NOT_FLYABLE)
- Zapier auto-sends response email
- Friday: Review metrics (conversion rate, average quote amount)

### Phase 3 Weekly (30 sec/inquiry)
- Monday-Friday: Get Slack notification with auto-generated decision
- If FLYABLE: Call client, confirm booking
- If MARGINAL: Review, decide to pursue or skip
- If NOT_FLYABLE: Already declined, move on
- Friday: Review metrics, check decision accuracy

---

## Metrics to Track at Each Phase

| Metric | Phase 1 | Phase 2 | Phase 3 | Phase 4 |
|--------|---------|---------|---------|---------|
| Inquiries/month | 3-5 | 5-10 | 10-20 | 20+ |
| Time per inquiry | 15 min | 10 min | 2 min | <1 min |
| Auto-response rate | 0% | 20% | 80% | 100% |
| Manual decision needed | 100% | 100% | 0% | 0% |
| Conversion rate | Track | Track | Should improve | Should improve |
| Average quote $ | Track | Track | Track | Track |
| Days to first contact | <1 day | <4 hours | <1 hour | Immediate |

---

## Red Flags to Watch

**Phase 1/2:**
- Decision consistency: Are you marking same types of properties consistently?
- Quote accuracy: Are quotes too high (losing deals) or too low (hurting margin)?
- Response time: Slow responses lose inquiries

**Phase 3:**
- Decision logic errors: If Zapier marks something NOT_FLYABLE but you disagree, adjust lookup tables
- Weather data accuracy: If forecasts are wrong, deals get missed
- CRM sync issues: If HubSpot isn't capturing all leads, troubleshoot connection

**Phase 4:**
- Integration complexity: More moving parts = more failure points. Test each phase before adding next.

---

## Next Steps

1. **This week:** Set up Phase 1 (Google Form, 30 min)
2. **Next week:** Collect 5 inquiries, measure response time
3. **Following week:** Decide if Phase 2 (Zapier) is worth the time ($20/month)
4. **After 10 inquiries:** Evaluate Phase 3 (Automated decision)
5. **After 20 inquiries:** Consider Phase 4 (Full platform)

**Start with Phase 1. Everything else follows.**

---
