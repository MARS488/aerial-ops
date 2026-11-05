# Zapier Workflows — Configuration Templates

**Copy-paste ready Zapier workflow setups for each phase. Use these exact configurations.**

---

## Prerequisites

- Zapier account (free tier OK for starting)
- Google Forms connected to Google Sheets
- Gmail account
- (Optional) Slack workspace
- (Phase 3+) HubSpot account (free tier)

---

## Phase 2 Workflows

### Workflow A: New Inquiry Notification to Marcus

**Name:** Form Submission → Marcus Notification  
**Trigger:** Google Forms — New Form Response  
**Actions:** Email (or Slack if available)

**Setup Steps:**

1. **Trigger: Google Forms - New Form Response**
   - Select your form: "Marcus Jay Herring LLC Flyability Form"
   - Action on trigger: "New Response"
   - Test trigger (submit test form)

2. **Action: Send Email**
   - To: marcus.jherring87@gmail.com
   - Subject: ✨ NEW INQUIRY: [Client Name] - [Acreage] acres
   - Body template:
   ```
   Hi Marcus,

   New flyability inquiry:

   CLIENT:
   Name: [Client Full Name]
   Email: [Email Address]
   Phone: [Phone Number]

   PROPERTY:
   Address: [Property Address]
   Acreage: [Property Acres]

   REQUEST:
   Service Type: [Service Type]
   Preferred Date: [Preferred Date]

   NEXT STEPS:
   1. Check FLYABILITY_CHECKER.md (5 min)
   2. Run UNIVERSAL_QUOTE_CALCULATOR.py
   3. Tag row in Job Status Tracker (FLYABLE/MARGINAL/NOT_FLYABLE)
   4. Zapier auto-sends response

   Form Response Link: [LINK TO GOOGLE FORM RESPONSE]
   ```
   - From: marcus.jherring87@gmail.com
   - Include attachments: No

3. **Test:** Submit form, verify email arrives in < 1 min

---

### Workflow B: Log Inquiry to Job Status Tracker

**Name:** Form Submission → Log to Tracker  
**Trigger:** Google Forms — New Form Response  
**Actions:** Google Sheets (Append)

**Setup Steps:**

1. **Trigger: Google Forms - New Form Response**
   - Same as Workflow A (can be same trigger, multiple actions)

2. **Action: Google Sheets - Create Spreadsheet Row**
   - Spreadsheet: "Marcus Jay Herring LLC — Business Dashboard"
   - Worksheet: "Job Status Tracker"
   - Columns to fill (in order):
     - Job ID: (leave blank — Marcus assigns manually)
     - Inquiry Date: [Timestamp] (auto-populated)
     - Client Name: [Client Full Name]
     - Email: [Email Address]
     - Phone: [Phone Number]
     - Address: [Property Address]
     - Acreage: [Property Acres]
     - Service Type: [Service Type]
     - Preferred Date: [Preferred Date]
     - Status: "Inquiry Received" (static text)
     - Marcus Decision: (leave blank)
     - Quote Amount: (leave blank)
     - Sent Date: (leave blank)
     - Paid: (leave blank)
     - Notes: "Auto-logged from form"

3. **Test:** Submit form, verify row appears in Google Sheets

---

### Workflow C: Auto-Send Quote Email (If Flyable)

**Name:** Marcus Tagged FLYABLE → Send Quote Email  
**Trigger:** Google Sheets — New or Updated Row  
**Conditions:** Marcus Decision = "FLYABLE"  
**Actions:** Email

**Setup Steps:**

1. **Trigger: Google Sheets - New or Updated Row**
   - Spreadsheet: "Marcus Jay Herring LLC — Business Dashboard"
   - Worksheet: "Job Status Tracker"
   - Trigger on: Any change

2. **Condition: Filter by Marcus Decision**
   - IF Marcus Decision column = "FLYABLE"
   - THEN continue to email action

3. **Action: Send Email**
   - To: [Email Address] (from row)
   - Subject: Good news! We can fly your property 🚁
   - Body: Use EMAIL_TEMPLATES.md #1 (Quote Follow-up)
   - Customize with:
     - [Client Name] = from row
     - [Address] = from row
     - [Acreage] = from row
     - [Price] = [Quote Amount] from row
     - Your name: Marcus Herring
     - Phone: [Your phone]
   - From: marcus.jherring87@gmail.com

4. **Action: Update Google Sheets Row**
   - Spreadsheet: Same as trigger
   - Worksheet: "Job Status Tracker"
   - Find row: Match Email Address
   - Update cells:
     - Status: "Quote Sent"
     - Sent Date: [Today's Date]

5. **Test:** 
   - Manually enter a row with Marcus Decision = "FLYABLE"
   - Verify email sends to client
   - Verify Sent Date updates in sheet

---

### Workflow D: Auto-Send Decline Email (If Not Flyable)

**Name:** Marcus Tagged NOT_FLYABLE → Send Decline Email  
**Trigger:** Google Sheets — New or Updated Row  
**Conditions:** Marcus Decision = "NOT_FLYABLE"  
**Actions:** Email

**Setup Steps:**

1. **Trigger: Google Sheets - New or Updated Row**
   - Spreadsheet: "Marcus Jay Herring LLC — Business Dashboard"
   - Worksheet: "Job Status Tracker"

2. **Condition: Filter by Marcus Decision**
   - IF Marcus Decision column = "NOT_FLYABLE"
   - THEN continue to email action

3. **Action: Send Email**
   - To: [Email Address] (from row)
   - Subject: About your flyability assessment
   - Body: Use EMAIL_TEMPLATES.md #14 (Decline with Referral)
   - Customize with:
     - [Client Name]
     - [Reason] (e.g., "outside service area", "military airspace", "insufficient weather window")
     - [Referral contact] if available
   - From: marcus.jherring87@gmail.com

4. **Action: Update Google Sheets Row**
   - Status: "Declined"
   - Sent Date: [Today's Date]

5. **Test:** 
   - Manually enter row with Marcus Decision = "NOT_FLYABLE"
   - Verify decline email sends
   - Verify status updates

---

### Workflow E: Auto-Send Conditional Email (If Marginal)

**Name:** Marcus Tagged MARGINAL → Send Conditional Email  
**Trigger:** Google Sheets — New or Updated Row  
**Conditions:** Marcus Decision = "MARGINAL"  
**Actions:** Email

**Setup Steps:**

1. **Trigger: Google Sheets - New or Updated Row**
   - Spreadsheet: "Marcus Jay Herring LLC — Business Dashboard"
   - Worksheet: "Job Status Tracker"

2. **Condition: Filter by Marcus Decision**
   - IF Marcus Decision column = "MARGINAL"
   - THEN continue to email action

3. **Action: Send Email**
   - To: [Email Address]
   - Subject: We can fly your property with conditions
   - Body: Use EMAIL_TEMPLATES.md adapted for marginal:
   ```
   Hi [Client Name],

   Great news! We can absolutely fly your property, but with a few conditions:

   [INSERT CONDITION HERE]:
   ⚠️ WEATHER: Forecast shows strong winds Wed-Fri. We recommend flying [next week] when conditions are better.
   — OR —
   ⚠️ HAZARDS: Your property has [power lines, trees]. We can work around these, but may take extra time.
   — OR —
   ⚠️ ACCESS: Site access is challenging. We'll need your help clearing the flight zone.

   ADJUSTED QUOTE:
   Base Price: $[Quote Amount]
   Complexity Adjustment: +$[Additional]
   Total: $[Total]

   OPTIONS:
   1. Proceed now as-is (${Total})
   2. Wait for better conditions (${Quote Amount}, lower complexity)
   3. Let's discuss [call 555-XXXX]

   Which works best for you?

   Best,
   Marcus Herring
   [Phone]
   ```

4. **Action: Update Google Sheets Row**
   - Status: "Quote Sent (Conditional)"
   - Sent Date: [Today's Date]

5. **Test:** Verify conditional email sends correctly

---

## Phase 3 Workflows

### Workflow F: Automated Flyability Decision Logic

**Name:** Form Submission → Auto-Decide → Send Response  
**Trigger:** Google Forms — New Form Response  
**Conditions:** Complex logic (multiple IF/THEN)  
**Actions:** Multiple (decision logic → email → logging)

**Setup Steps:**

1. **Trigger: Google Forms - New Form Response**
   - Select form

2. **Condition: Check Location (Valdosta Area)**
   - IF [Property Address] contains "Valdosta" OR "Lowndes County"
   - THEN Continue
   - ELSE: Set Decision = "NOT_FLYABLE" (out of area), skip to email action

3. **Condition: Check Airspace**
   - Lookup [Property Address] in Google Sheets "Airspace Reference" table
   - IF Airspace Class = "E" (uncontrolled)
   - OR Airspace Class = "D" (LAANC available)
   - THEN Continue
   - ELSE: Set Decision = "NOT_FLYABLE" (restricted airspace), skip to email

4. **Condition: Check Weather**
   - Lookup [Preferred Date] in Google Sheets "Weather Data"
   - IF Wind <= 15 mph AND Visibility > 3 miles AND No heavy rain
   - THEN Continue
   - ELSE IF Wind 15-20 mph OR Light rain
   - THEN Set Decision = "MARGINAL", continue to quote
   - ELSE: Set Decision = "NOT_FLYABLE" (weather), skip to email

5. **Condition: Check Site**
   - IF Site Access = "Impossible" OR Hazards >= 4
   - THEN Set Decision = "NOT_FLYABLE", skip to email
   - ELSE IF Site Access = "Difficult" OR Hazards = 3
   - THEN Set Decision = "MARGINAL"
   - ELSE Continue

6. **Action: If Decision = FLYABLE → Generate Quote**
   - Lookup [Service Type] + [Acreage] in "Pricing Tiers"
   - Set Quote = Base Price from lookup
   - Calculate Total = Quote + (Hazards complexity adjustment if needed)
   - Set Decision = "FLYABLE"

7. **Action: If Decision = MARGINAL → Generate Conditional Quote**
   - Lookup [Service Type] + [Acreage] in "Pricing Tiers"
   - Set Quote = Base Price
   - Add Complexity Fee: +$[250-500] based on hazards/access
   - Set Total = Quote + Fee

8. **Action: Send Decision Email**
   - IF Decision = "FLYABLE":
     * To: [Email Address]
     * Subject: Good news! We can fly your property 🚁
     * Body: EMAIL_TEMPLATES.md #1 with [Quote Amount] = Total
   - ELSE IF Decision = "MARGINAL":
     * To: [Email Address]
     * Subject: We can fly your property with conditions
     * Body: Conditional email (see Workflow E)
   - ELSE IF Decision = "NOT_FLYABLE":
     * To: [Email Address]
     * Subject: About your flyability assessment
     * Body: EMAIL_TEMPLATES.md #14 (decline + referral)

9. **Action: Log to HubSpot CRM**
   - Create Contact:
     * Name: [Client Full Name]
     * Email: [Email Address]
     * Phone: [Phone Number]
   - Add to List: "Inquiries"
   - Tag by Decision: "flyable", "marginal", "not_flyable"
   - Set property "Flyability Decision": [Decision]
   - Set property "Quote Amount": [Total]
   - Set property "Inquiry Date": [Today's Date]

10. **Action: Update Google Sheets**
    - Add row to "Job Status Tracker"
    - Status: "Quote Sent" (or "Declined")
    - Marcus Decision: [Auto-generated Decision]
    - Quote Amount: [Total]

11. **Action: Notify Marcus on Slack** (if available)
    - Send to: #inquiries channel (or DM to Marcus)
    - Message:
    ```
    🎯 [DECISION TYPE] Inquiry Received
    Client: [Name]
    Property: [Acres] acres, [Address]
    Service: [Service Type]
    Quote: $[Total]
    Preferred Date: [Date]
    Decision: [FLYABLE/MARGINAL/NOT_FLYABLE]
    
    Link: [HubSpot deal link]
    Next: [If FLYABLE: Call to confirm | If MARGINAL: Review + decide | If NOT_FLYABLE: Done]
    ```

12. **Test with 10 inquiries:**
    - Check decision accuracy (compare auto-decision vs. your manual decision)
    - Adjust lookup tables if decisions are off
    - Verify emails send correctly
    - Verify HubSpot logging works
    - Verify Slack notification format is clear

---

## Lookup Tables Setup (For Phase 3)

### Google Sheets: "Airspace Reference"

| Address | City | Airspace Class | Restriction | LAANC Required | Notes |
|---------|------|----------------|-------------|----------------|-------|
| Downtown Valdosta | Valdosta | E | None | No | Unrestricted, clear to fly |
| Moody Air Force Base area | Moody area | D | Military | Yes | Special auth needed |
| Lowndes County rural | Rural | E | None | No | Clear to fly |
| Airport vicinity | Valdosta Regional | D | Controlled | Yes | LAANC instant approval |

### Google Sheets: "Weather Data"

| Date | City | High Temp | Low Temp | Wind MPH | Rain? | Visibility | Flyable? |
|------|------|-----------|----------|----------|-------|-----------|---------|
| 8/15/2026 | Valdosta | 92 | 78 | 12 | No | 8 miles | Yes |
| 8/16/2026 | Valdosta | 88 | 75 | 18 | Light | 5 miles | Marginal |
| 8/17/2026 | Valdosta | 85 | 72 | 22 | Heavy | 2 miles | No |

*(Populate weekly via manual lookup or integrate weather API)*

### Google Sheets: "Pricing Tiers"

| Service Type | 0.5-2 acres | 2-5 acres | 5-20 acres | 20+ acres | Deposit % |
|--------------|------------|----------|-----------|-----------|-----------|
| Storm | $500 | $1,000 | $2,500 | $5,000 | 25% |
| LiDAR | $800 | $1,500 | $3,500 | $7,000 | 25% |
| Monitoring | $400 | $800 | $2,000 | $4,000 | 25% |

### Google Sheets: "Complexity Adjustments"

| Factor | Adjustment |
|--------|------------|
| 1 hazard (power lines) | +$0 |
| 2 hazards (power lines + trees) | +$150 |
| 3+ hazards | +$300-500 |
| Difficult access | +$200 |
| Very difficult access | +$400 |
| Storm/emergency (same day) | +$200-500 |

---

## Testing Checklist

### Phase 2 Testing (1-2 hours)

- [ ] Workflow A: Submit test form, receive notification email
- [ ] Workflow B: Submit form, verify row appears in Job Status Tracker
- [ ] Workflow C: Manually tag row FLYABLE, verify quote email sends
- [ ] Workflow D: Manually tag row NOT_FLYABLE, verify decline email sends
- [ ] Workflow E: Manually tag row MARGINAL, verify conditional email sends
- [ ] All emails have correct sender, subject, formatting
- [ ] All Google Sheets updates work correctly
- [ ] Email templates have placeholders filled correctly

### Phase 3 Testing (2-3 hours)

- [ ] Automated decision logic works for FLYABLE case
- [ ] Automated decision logic works for NOT_FLYABLE case
- [ ] Automated decision logic works for MARGINAL case
- [ ] Quote calculation accurate (compare to manual calculator)
- [ ] HubSpot contacts created correctly
- [ ] HubSpot tagging works (flyable/marginal/not_flyable)
- [ ] Slack notifications clear and actionable
- [ ] Decision accuracy: 10 test cases vs. your manual decisions (aim for 90%+ match)
- [ ] Email personalization correct (client names, addresses, quotes)

---

## Troubleshooting

### Email not sending
- Check: Gmail account connected to Zapier
- Check: Email addresses valid (not blank)
- Check: Zapier action properly configured
- Solution: Test action in Zapier editor (there's a test button)

### Rows not appearing in Google Sheets
- Check: Google Sheets connected to Zapier
- Check: Correct spreadsheet + worksheet selected
- Check: Column mapping correct
- Solution: Try "Create Spreadsheet Row" action, test manually

### HubSpot contacts not creating
- Check: HubSpot account connected to Zapier
- Check: Email field is required (Zapier will error without it)
- Check: HubSpot list selected
- Solution: Create test contact in HubSpot manually, check if Zapier can find it

### Conditional logic not working
- Check: IF/THEN conditions formatted correctly (Zapier syntax)
- Check: Field names match exactly (case-sensitive)
- Check: Lookup values match exactly (e.g., "FLYABLE" vs "Flyable")
- Solution: Use Zapier's formatter "Split Text" if parsing address for keywords

---

## Cost Estimate

| Tool | Phase 2 | Phase 3 | Notes |
|------|---------|---------|-------|
| Zapier | Free (100 tasks/month) | $20/month (Pro, 750 tasks) | Upgrade when > 100 inquiries/month |
| Google Sheets | Free | Free | Unlimited rows |
| Google Forms | Free | Free | Unlimited responses |
| Gmail | Free | Free | Unlimited emails |
| HubSpot | Free | Free | Free tier sufficient for <500 contacts |
| **Total** | **$0** | **$20** | Setup cost only, no per-inquiry fees |

---

## Next Steps

1. **Start Phase 2 this week:** Set up Workflows A-E (2-3 hours)
2. **Test with 3-5 inquiries:** Verify everything works
3. **Move to Phase 3 next week:** Set up automated logic (2-3 hours)
4. **Test with 10 inquiries:** Check accuracy, adjust rules
5. **Go live:** Set workflows to active, monitor for 1 week

**Once Phase 3 is live, 80% of intake is fully automated.**

---
