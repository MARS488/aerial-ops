# System Setup Guide — Marcus Jay Herring LLC

**How to organize your digital workspace for smooth operations. Set this up once, then maintain it.**

---

## Overview

This system uses:
- **Google Drive/Dropbox** for file storage + backup
- **Google Sheets** for tracking (dashboard, job log, payments)
- **Email** for client communication
- **Square** (or similar) for payments
- **Local backup** on computer SSD

Total setup time: **2-3 hours** (done once)

---

## Part 1: Folder Structure (Local + Dropbox/Google Drive)

### Recommended Structure

```
Marcus Jay Herring LLC/
├── 01_OPERATIONS/
│   ├── Business License & EIN
│   ├── Insurance/
│   │   ├── General Liability Policy
│   │   ├── Drone Liability Policy
│   │   └── Certificates of Insurance
│   ├── Bank Account Documents
│   ├── Tax Planning
│   └── Contracts
│
├── 02_TEMPLATES/
│   ├── SERVICE_AGREEMENT_TEMPLATE.md
│   ├── INVOICE_TEMPLATE.md
│   ├── JOB_INTAKE_FORM.md
│   ├── PRE_FLIGHT_CHECKLIST.md
│   ├── FLIGHT_LOG_TEMPLATE.md
│   ├── DELIVERABLE_CHECKLIST.md
│   ├── PAYMENT_TRACKING.md
│   └── EMAIL_TEMPLATES.md
│
├── 03_JOBS/
│   ├── CIV-2026-08-001/
│   │   ├── 01_INTAKE_FORM.md
│   │   ├── 02_SERVICE_AGREEMENT_SIGNED.pdf
│   │   ├── 03_PRE_FLIGHT_CHECKLIST.md
│   │   ├── 04_QUOTE_CALCULATOR_RESULTS.txt
│   │   ├── 05_FLIGHT_LOG.md
│   │   ├── 06_RAW_FOOTAGE/
│   │   │   ├── Photos/
│   │   │   ├── Video/
│   │   │   └── Metadata/
│   │   ├── 07_PROCESSED_DELIVERABLES/
│   │   │   ├── Final_Images/
│   │   │   ├── Report/
│   │   │   └── 3D_Model/
│   │   ├── 08_DELIVERABLE_CHECKLIST.md
│   │   ├── 09_INVOICE_SENT.pdf
│   │   ├── 10_PAYMENT_TRACKING.md
│   │   └── 11_FEEDBACK_SUMMARY.md
│   │
│   ├── CIV-2026-08-002/
│   │   └── [same structure]
│   │
│   └── ARCHIVE/
│       ├── CIV-2026-07-001/ [completed jobs]
│       └── ...
│
├── 04_BOOKKEEPING/
│   ├── 2026_INCOME_EXPENSE_LOG.md
│   ├── BUSINESS_DASHBOARD.xlsx
│   ├── FLIGHT_LOG_MASTER.xlsx
│   ├── PAYMENT_TRACKING_MASTER.xlsx
│   └── Tax_Filings/
│
├── 05_PARTNERSHIPS/
│   ├── Southeastern Survey/
│   │   ├── Contact Info
│   │   ├── Proposal Sent [date]
│   │   └── Follow-up Log
│   │
│   ├── Environmental Firms/
│   │   ├── Contact List
│   │   └── Proposal Status
│   │
│   └── Marketplace Networks/
│       ├── Zeitview Account
│       └── DroneUp Account
│
├── 06_MARKETING/
│   ├── Sample Deliverables/
│   ├── Portfolio Photos/
│   ├── Google Business Profile/
│   │   └── Credentials
│   ├── Website Copy/
│   └── Partnership Sell Sheets/
│
└── 07_REFERENCE/
    ├── STRATEGIC_SYNTHESIS.md
    ├── LLC_BUSINESS_STRUCTURE.md
    ├── OPERATIONS_CHECKLIST.md
    ├── JOB_EXECUTION_PLAYBOOK.md
    ├── INSURANCE_PROCUREMENT_GUIDE.md
    ├── DAILY_OPERATIONS_CHECKLIST.md
    └── EMAIL_TEMPLATES.md
```

### How to Set Up

1. **Create on Dropbox OR Google Drive** (choose one):
   - Dropbox: Easier for file sync + backup
   - Google Drive: Easier for Sheets/Docs collaboration

2. **Create local mirror** on your computer:
   - `/Users/Marcus/Marcus_Jay_Herring_LLC/` (Mac)
   - `C:\Users\Marcus\Marcus_Jay_Herring_LLC\` (Windows)
   - Keep synced with Dropbox app or Google Drive sync

3. **Create second backup drive**:
   - External SSD: `Marcus_Jay_Herring_LLC_BACKUP`
   - Copy entire folder monthly
   - Store offsite (safety box or other location)

---

## Part 2: Google Sheets Setup

### Master Spreadsheet: Business Dashboard

**Create file:** `Marcus Jay Herring LLC — Business Dashboard 2026`

**Sheets to create:**

#### Sheet 1: Flight Log (Source of Truth)

| Date | Division | Service Type | Client | Acres | Paid? | Amount | Days to Deliver | Feedback | Notes |
|------|----------|--------------|--------|-------|-------|--------|-----------------|----------|-------|
| 8/15/2026 | CivilitySync | Storm | [Name] | 3 | Yes | $1,500 | 2 | Would use again | First paid |
| ... | | | | | | | | | |

**Formulas:**
- Total jobs: `=COUNTA(A2:A999)`
- Total revenue: `=SUM(G2:G999)`
- Positive feedback: `=COUNTIF(I2:I999,"Would use again")`
- Paid jobs: `=COUNTIF(F2:F999,"Yes")`

#### Sheet 2: Dashboard Summary (Auto-calculated)

```
STAGE 0 PROGRESS

Total Jobs Flown:        [formula = COUNTA(Flight Log!A:A)]
Positive Feedback:       [formula = COUNTIF(Flight Log!I:I,"Would use again")]
Paid Jobs:               [formula = COUNTIF(Flight Log!F:F,"Yes")]
Total Revenue:           [formula = SUM(Flight Log!G:G)]
Average Job Revenue:     [formula = AVERAGE(Flight Log!G:G)]
Gross Margin %:          [formula = (Revenue - Costs) / Revenue * 100]

STAGE 0 GATE CLEAR?      [IF all 3 metrics met: YES | NO]
```

#### Sheet 3: Monthly Breakdown

| Month | Jobs | Revenue | Costs | Margin | Feedback % | Notes |
|-------|------|---------|-------|--------|-----------|-------|
| Aug 2026 | 3 | $4,000 | $500 | $3,500 (87%) | 67% | On track |
| Sep 2026 | | | | | | |

#### Sheet 4: Payment Tracking

| Invoice # | Client | Amount | Due Date | Paid | Payment Date | Status |
|-----------|--------|--------|----------|------|--------------|--------|
| INV-2026-0001 | [Name] | $1,500 | 8/30 | $1,500 | 8/15 | ✓ Paid |
| ... | | | | | | |

#### Sheet 5: Partner Tracker

| Partner | Contact | Last Contact | Status | Next Action | Date |
|---------|---------|--------------|--------|------------|------|
| Southeastern Survey | Barbara | [date] | Proposal sent | Schedule coffee | [date] |
| ... | | | | | |

### How to Use These Sheets

1. **Every job:** Add row to Flight Log with all details
2. **Every Friday:** Dashboard auto-updates (check formulas)
3. **Every month:** Run monthly breakdown (SUMIF formulas by date)
4. **Every week:** Check Payment Tracking (follow up on unpaid)
5. **Ongoing:** Update Partner Tracker (relationship progress)

---

## Part 3: Email Setup

### Gmail Organization (or Outlook equivalent)

**Create labels:**
- `Clients/` — All client emails
- `Clients/Quote Sent` — Awaiting response
- `Clients/Agreement` — Service agreement stage
- `Clients/Flight Scheduled` — Confirmed flights
- `Clients/Processing` — Deliverables being worked on
- `Clients/Invoiced` — Awaiting payment
- `Clients/Paid` — Complete jobs
- `Partners/` — All partnership outreach
- `Partners/Warm` — Active conversations
- `Operations/` — Internal process emails
- `Tax/` — Tax-related (quarterly, annual)

**Gmail filters to auto-label:**
- From: @client-email-domain.com → Label: Clients
- Subject: "invoice" OR "payment" → Label: Clients/Invoiced
- From: [partner companies] → Label: Partners

### Email Best Practices

- **Response time:** <24 hours for client emails
- **Subject lines:** Include job ID (e.g., "CIV-2026-08-001: Quote")
- **Templates:** Use EMAIL_TEMPLATES.md (copy, customize, send)
- **Archive:** Move completed jobs to label folder

---

## Part 4: Payment Collection Setup

### Square Account (Free to Set Up)

**Do this:**
1. Go to square.com
2. Sign up with business email
3. Connect bank account
4. Create payment link for invoices

**For each invoice:**
- Generate Square payment link
- Include in email: `Pay here: [link]`
- Payments deposit to your business bank account (usually next business day)

### Tracking Payments

**Use PAYMENT_TRACKING.md sheet:**
- Log invoice date + amount
- Log payment received + date
- Check weekly for overdue (>15 days)
- Send reminders at day 15, 30

---

## Part 5: Backup Strategy

### Daily
- [ ] End-of-day: SD card → computer copy
- [ ] Computer copy + backup to Dropbox (automatic if using sync)

### Weekly (Friday)
- [ ] Check Dropbox/Google Drive has latest files
- [ ] Verify all jobs for week are backed up

### Monthly
- [ ] Copy entire Marcus_Jay_Herring_LLC folder to external SSD
- [ ] Store SSD offsite (safety deposit box, second location)
- [ ] Verify backup integrity (spot-check files)

### Tools
- **Dropbox** (50GB free, $100/year for 2TB)
- **Google Drive** (15GB free, $2-10/month for more)
- **External SSD** ($100-200 one-time)

---

## Part 6: Checklist Setup (Printable)

**Create printable checklists:**

1. **PRE_FLIGHT_CHECKLIST.md**
   - Print on cardstock (laminate for durability)
   - Keep one in vehicle
   - Use before every flight

2. **JOB_EXECUTION_PLAYBOOK.md** (Quick Reference)
   - Print summary version (1-2 pages)
   - Keep at desk
   - Reference for job stages

3. **DAILY_OPERATIONS_CHECKLIST.md**
   - Print weekly version
   - Tape to monitor
   - Check off daily

---

## Part 7: Phone Setup

### Apps to Download

- **LAANC App** (AirMap, Aloft, or Skyward) — Flight planning/airspace
- **Dropbox** — Access files on-site
- **Email** (Gmail app) — Client communication
- **Square** (for payments) — Process payments on-site if needed
- **Weather** (Weather.com or similar) — Pre-flight weather check
- **Calculator** — Quick math on site

### Phone Backup

- All flight photos → Dropbox backup immediately after flight
- Never rely on phone storage only

---

## Part 8: Security & Access

### Data Protection

- [ ] Dropbox password: Strong (20+ chars, symbols, numbers)
- [ ] Google Account 2-factor authentication enabled
- [ ] Email backup codes saved in secure location
- [ ] Bank account credentials NOT stored in cloud

### Client Privacy

- [ ] Blur faces/license plates in photos before delivery
- [ ] Don't share raw flight data (only processed deliverables)
- [ ] Dropbox links expire after 30 days
- [ ] Service agreement includes data ownership clause

---

## Quick Setup Checklist

**One-time setup (2-3 hours):**

- [ ] Create Dropbox/Google Drive folder structure
- [ ] Create Google Sheets dashboard
- [ ] Create Gmail labels
- [ ] Set up Square payment processing
- [ ] Download LAANC app + test
- [ ] Print pre-flight checklist (laminate)
- [ ] Create external backup drive
- [ ] Test backup process (copy one folder, verify)
- [ ] Download and save all templates to `/02_TEMPLATES/`

---

## Monthly Maintenance (30 minutes)

- [ ] Check backup folder sizes (growing as expected?)
- [ ] Verify Dropbox sync working (files current?)
- [ ] Archive completed jobs to `/ARCHIVE/` folder
- [ ] Check payment links still working (Square)
- [ ] Review folder organization (add new jobs correctly?)

---

## Disaster Recovery

**If computer crashes, you need to:**
1. Restore from Dropbox (automatic if using sync)
2. Restore from external SSD backup (if needed)
3. All client files, invoices, contracts still safe

**If Dropbox/Drive goes down:**
- Use local computer backup
- Use external SSD backup
- Sync back up when service restored

---

**Set this up once. Maintain it weekly. Never lose a file or invoice.**

