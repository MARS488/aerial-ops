# Job Execution Playbook — Marcus Jay Herring LLC

**Step-by-step guide for executing a complete job from inquiry to payment. Reference this for every job.**

---

## Overview: The Job Lifecycle

```
INQUIRY → QUOTE → AGREEMENT → FLIGHT → PROCESSING → DELIVERY → INVOICE → PAYMENT → FEEDBACK → COMPLETE
```

Each stage has specific documents, checklists, and timelines.

---

## Stage 1: Inquiry & Job Intake (Day 1)

**When you receive a new job inquiry:**

### What To Do

1. **Capture all details** using `JOB_INTAKE_FORM.md`
   - Client info, property location, service type
   - Client needs and turnaround expectations
   - Budget/decision timeline

2. **Preliminary airspace check**
   - Use LAANC app to verify property is flyable
   - If restricted airspace: note that authorization needed

3. **Assess feasibility** (weather, access, equipment)
   - Check weather forecast for proposed dates
   - Note any site access challenges
   - Identify if job matches your service offerings

4. **Assign Job ID**
   - Format: `CIV-YYYY-MM-###`
   - Example: `CIV-2026-08-001`

5. **Create job folder**
   - Directory: `/Jobs/CIV-YYYY-MM-###/`
   - File: `01_INTAKE_FORM.md`

### Documents Used
- JOB_INTAKE_FORM.md

### Timeline
- **Target:** Same day or next business day

### Success Criteria
- All intake form fields complete
- Job ID assigned
- Folder created with intake form filed

---

## Stage 2: Proposal & Quoting (Day 1-2)

**Turn intake details into a quote.**

### What To Do

1. **Run quote calculator**
   ```bash
   python3 UNIVERSAL_QUOTE_CALCULATOR.py civilitysync [storm|lidar|scan] [acres]
   ```
   - Tool outputs: customer-facing price + cost breakdown + margin assessment

2. **Customize quote for client**
   - Edit calculator output for client-specific factors (rush, complexity, location)
   - Ensure margins stay healthy (80%+ minimum)

3. **Send quote to client**
   - Email with quote amount, scope, timeline, payment terms
   - Include: service description, what's included, turnaround time
   - Attach: certificate of insurance (proof you're insured)

4. **Log quote in tracker**
   - Update `JOB_STATUS_TRACKER.md` → move to "Quote" stage

5. **Set follow-up reminder**
   - If no response in 3 days, send follow-up email

### Documents Used
- UNIVERSAL_QUOTE_CALCULATOR.py
- JOB_STATUS_TRACKER.md

### Timeline
- **Target:** Quote sent within 24 hours of intake

### Success Criteria
- Quote accurate and competitive
- Margins calculated and healthy
- Client received quote with clear next steps

---

## Stage 3: Service Agreement & Deposit (Day 2-5)

**Get agreement signed and deposit collected (if required).**

### What To Do

1. **Send service agreement**
   - Template: `SERVICE_AGREEMENT_TEMPLATE.md`
   - Customize with: your LLC info, client name, job details, pricing
   - Include: scope, timeline, deposit (if hard costs), payment terms, data ownership

2. **Collect deposit** (for jobs with rental equipment or hard costs)
   - Deposit amount: typically covers drone rental costs (~$500-1,000)
   - Payment methods: Square, ACH, cash, check
   - Log deposit in `PAYMENT_TRACKING.md`

3. **Collect W-9** (if business client)
   - Request IRS W-9 form for tax records
   - File with job documentation

4. **Get signed agreement back**
   - Scanned or photographed version OK
   - File: `/Jobs/CIV-YYYY-MM-###/02_SERVICE_AGREEMENT_SIGNED.pdf`

5. **Schedule flight**
   - Once signed, confirm specific flight date/time
   - Coordinate with client on site access, weather windows

6. **Update tracker**
   - Move job to "Signed" → "Scheduled" stage

### Documents Used
- SERVICE_AGREEMENT_TEMPLATE.md
- PAYMENT_TRACKING.md

### Timeline
- **Target:** Agreement signed within 5 days of quote
- **Target:** Flight scheduled within 3 days of agreement

### Success Criteria
- Agreement signed and filed
- Deposit collected (if applicable)
- Flight date confirmed with client
- W-9 collected (if business client)

---

## Stage 4: Pre-Flight Preparation (1-2 Days Before)

**Prepare aircraft, review site, confirm all systems.**

### What To Do

1. **Create pre-flight checklist**
   - Template: `PRE_FLIGHT_CHECKLIST.md`
   - Customize for job specifics (location, weather, airspace)
   - Print or load on phone

2. **Aircraft maintenance check**
   - Charge batteries fully
   - Test camera/gimbal
   - Verify propellers, SD card, ND filters
   - Update firmware if needed

3. **Detailed site assessment**
   - Review property photos/maps
   - Identify hazards (power lines, trees, terrain)
   - Plan launch/recovery locations
   - Note any site-specific restrictions

4. **Weather check**
   - Final wind/rain forecast for flight day
   - Identify backup dates if needed

5. **Airspace verification**
   - Use LAANC app to check authorization
   - File flight plan if required

6. **Client communication**
   - Confirm flight time with client
   - Provide site arrival time (±30 min)
   - Confirm site contact (who will be there)
   - Send insurance certificate if requested

### Documents Used
- PRE_FLIGHT_CHECKLIST.md

### Timeline
- **Target:** Complete 1-2 days before flight

### Success Criteria
- Aircraft fully ready and tested
- Site hazards identified
- Airspace cleared
- Client confirmed and informed

---

## Stage 5: Flight Execution (Flight Day)

**Execute the mission safely and capture quality data.**

### What To Do

1. **On-site: Safety Brief**
   - Walk perimeter, identify hazards
   - Brief site contact on flight operations
   - Confirm no unauthorized personnel in flight zone

2. **Pre-flight ritual** (use checklist)
   - Weather conditions verified
   - Wind speeds within limits
   - Aircraft systems all green
   - GPS lock acquired
   - Return-to-home altitude set

3. **Execute flight mission**
   - Take notes during flight (weather, altitude, any issues)
   - Use `FLIGHT_LOG_TEMPLATE.md` for during/after notes
   - Capture required coverage (all areas)

4. **Post-flight inspection**
   - Aircraft condition check
   - Battery health assessment
   - SD card data secure
   - All equipment packed safely

5. **Immediate follow-up with client**
   - "Flight was successful, data looks good"
   - "Turnaround is 48 hours for deliverables"
   - "You'll receive a link by [DATE]"

6. **Data backup**
   - Transfer SD card to computer
   - Backup to Dropbox + local drive
   - Verify backup integrity (spot-check files)

7. **Log the flight**
   - File: `/Jobs/CIV-YYYY-MM-###/05_FLIGHT_LOG.md`
   - Document weather, operations, costs, client feedback

### Documents Used
- PRE_FLIGHT_CHECKLIST.md
- FLIGHT_LOG_TEMPLATE.md

### Timeline
- **Target:** Complete 1-2 hours total (flight + notes + backup)

### Success Criteria
- Flight executed safely
- Data captured and verified
- All backups complete
- Flight logged with details

---

## Stage 6: Processing & Deliverables (1-5 Days)

**Transform raw data into professional deliverables.**

### What To Do

1. **Organize raw footage**
   - Create folder: `/Jobs/CIV-YYYY-MM-###/06_RAW_FOOTAGE/`
   - Organize by: photos, video, metadata
   - Verify all files present and uncorrupted

2. **Process data**
   - Color correct images
   - Edit video (if required)
   - Generate 3D model (if LiDAR job)
   - Create orthomosaic or analysis (if needed)
   - Generate report (if applicable)

3. **Quality assurance** (use checklist)
   - Template: `DELIVERABLE_CHECKLIST.md`
   - Spot-check for: exposure, focus, coverage gaps
   - Verify no sensitive data exposed (blur faces/plates)
   - Professional presentation standards

4. **Organize deliverables**
   - Folder: `/Jobs/CIV-YYYY-MM-###/07_PROCESSED_DELIVERABLES/`
   - Naming: `CIV-2026-08-001_STORM_PHOTOS/`, etc.
   - Create README explaining file contents
   - Keep file sizes under 2GB for easy download

5. **Prepare delivery package**
   - Choose delivery method: Dropbox, Google Drive, WeTransfer
   - Create shareable link with download instructions
   - Test link before sending (verify access)

### Documents Used
- DELIVERABLE_CHECKLIST.md

### Timeline
- **Target:** 3-5 days turnaround (storm/scan) or 7-10 days (LiDAR/3D model)
- **Commit to:** Specific delivery date in service agreement

### Success Criteria
- All data processed and verified
- Quality meets professional standards
- Deliverables organized and named clearly
- Delivery link tested and working

---

## Stage 7: Delivery & Invoice (Day 5-7)

**Send deliverables and invoice to client.**

### What To Do

1. **Send deliverables to client**
   - Email with: delivery link, download instructions, access window (30 days)
   - Include usage terms and data ownership reminder
   - Request confirmation of receipt

2. **Create invoice**
   - Template: `INVOICE_TEMPLATE.md`
   - Number: INV-YYYY-####
   - Include: service description, amount, payment terms, due date
   - Attach: service agreement summary

3. **Send invoice**
   - Email with invoice PDF
   - Include payment methods and instructions
   - "Payment due [DATE] — thanks!"

4. **Update tracker**
   - File: `/Jobs/CIV-YYYY-MM-###/09_INVOICE_SENT.pdf`
   - Log in: `JOB_STATUS_TRACKER.md` (move to "Invoiced")
   - Log in: `PAYMENT_TRACKING.md` (add invoice record)

5. **Request feedback** (24-48 hours after delivery)
   - "Quick question: was this helpful?" (text or email)
   - "Would you use us again?" (yes/no)
   - Optional: "Any feedback for improvement?"

### Documents Used
- INVOICE_TEMPLATE.md
- PAYMENT_TRACKING.md
- JOB_STATUS_TRACKER.md

### Timeline
- **Target:** Invoice sent same day as deliverables

### Success Criteria
- Deliverables received and accessible
- Invoice sent with clear payment instructions
- Feedback requested

---

## Stage 8: Payment Collection (Day 7-30)

**Track payment and follow up if needed.**

### What To Do

1. **Monitor for payment**
   - Check email/Square/bank for payment notifications
   - Log payment immediately in `PAYMENT_TRACKING.md`

2. **Payment reminders** (if unpaid)
   - Day 15: Gentle email reminder ("Just checking in...")
   - Day 30: Second email reminder ("Your invoice INV-YYYY-#### is now due")
   - Day 45: Phone call or text ("Can we work something out?")

3. **Deposit payment**
   - Upon receipt, deposit check/ACH/cash to business bank account
   - Update `PAYMENT_TRACKING.md` with deposit date

4. **Record in books**
   - Log income in Google Sheets or Wave (your bookkeeping system)
   - Note: date, client, amount, job ID

5. **Update tracker**
   - Move job to "Paid" in `JOB_STATUS_TRACKER.md`

### Documents Used
- PAYMENT_TRACKING.md
- JOB_STATUS_TRACKER.md

### Timeline
- **Target:** Payment within 30 days of invoice
- **Payment terms:** Net 30 (adjust if needed for specific client)

### Success Criteria
- Payment received and deposited
- Payment logged in books
- No outstanding balances

---

## Stage 9: Feedback & Lessons (Day 30+)

**Close the loop with feedback and document learnings.**

### What To Do

1. **Collect formal feedback**
   - Reach out to client (if not already received)
   - Ask: "Overall, would you use us again?" (track response)
   - Rate response: ✓ Would use again / ? Maybe / ✗ Wouldn't use again

2. **Document feedback**
   - File: `/Jobs/CIV-YYYY-MM-###/11_FEEDBACK_SUMMARY.md`
   - Capture: quote, what went well, what could improve, overall rating

3. **Analyze job performance**
   - Actual cost vs. quoted cost (margin check)
   - Actual turnaround vs. promised turnaround
   - Feedback sentiment (positive/neutral/negative)

4. **Update dashboard**
   - Log feedback score in `BUSINESS_DASHBOARD_SETUP.md` (Flight Log sheet)
   - Update monthly dashboard with job metrics

5. **Identify improvements**
   - "What could we do better next time?"
   - Document 1-2 learnings for future jobs

6. **Close job**
   - Mark complete in `JOB_STATUS_TRACKER.md`
   - Archive job folder to `/Jobs/ARCHIVE/`
   - File remaining documents in job folder

### Documents Used
- FEEDBACK_SUMMARY.md
- BUSINESS_DASHBOARD_SETUP.md
- JOB_STATUS_TRACKER.md

### Timeline
- **Target:** Feedback collected within 30 days of payment

### Success Criteria
- Feedback captured
- Lessons documented
- Job marked complete and archived

---

## Stage Gate: Stage 0 Complete

**When you have completed 3 jobs with 2+ positive feedback and 1 paid job, Stage 0 gate clears.**

### Check:
```
✓ Total jobs: 3+
✓ "Would use again": 2+
✓ Paid jobs: 1+
✓ Process documented (this playbook)
```

### Then:
- Celebrate! You've proven the business model.
- Shift to Stage 1: land recurring contract (monthly LiDAR monitoring, seasonal checks)
- Implement Phase 2 automation (CRM, scheduling, invoicing automation)

---

## Quick Reference Checklist

**Print this and use before every job:**

```
□ INQUIRY: Intake form complete, job ID assigned, folder created
□ QUOTE: Calculator run, quote sent, follow-up reminder set
□ AGREEMENT: Service agreement signed, deposit collected (if needed)
□ PREP: Pre-flight checklist completed, airspace cleared, client confirmed
□ FLIGHT: Mission executed, data logged, backup complete
□ PROCESSING: Deliverables prepared and QA'd
□ DELIVERY: Deliverables sent, invoice sent, feedback requested
□ PAYMENT: Payment received and logged
□ FEEDBACK: Client feedback collected and documented
□ COMPLETE: Job archived, lessons captured
```

---

## Key Contacts & Tools

| What | Tool | Link |
|------|------|------|
| **Airspace/Flight Plan** | LAANC App (Airmap, Aloft, or Skyward) | [Download] |
| **Payment Collection** | Square / Stripe | square.com or stripe.com |
| **File Sharing** | Dropbox | dropbox.com |
| **Bookkeeping** | Wave or Google Sheets | wave.app or sheets.google.com |
| **Data Backup** | Dropbox + Local SSD | 2x backup (cloud + local) |

---

## Insurance & Compliance Reminders

**Before EVERY paid job, verify:**
- [ ] General liability insurance active
- [ ] Drone-specific insurance active
- [ ] FAA Part 107 current (expires Nov 2027)
- [ ] Drone registered with FAA
- [ ] Airspace authorization obtained (LAANC)

**Do NOT fly without these.**

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Weather delays flight | Contact client with new date options, extend agreement deadline |
| Client can't download deliverables | Re-upload to new link, send new link with detailed instructions |
| Payment delayed >30 days | Call client, offer payment plan, escalate if needed |
| Drone malfunction on site | Document incident, assess data salvage, communicate with client |
| Client unhappy with quality | Offer revision (within reason) or partial refund |

---

## Monthly Review (Every End of Month)

1. Run weekly checklist for all jobs
2. Update job tracker with final statuses
3. Review dashboard metrics (revenue, margin, feedback)
4. Note any process improvements
5. Plan next month's priorities

---

**This playbook is your job execution system. Follow it for every job to ensure consistency, quality, and profitability.**

