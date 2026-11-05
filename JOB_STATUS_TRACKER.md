# Job Status Tracker — Marcus Jay Herring LLC

**Central place to track every job from inquiry to completion. Use Google Sheets for easy updates and sharing.**

---

## Master Job Log

| Job ID | Client | Service | Quote $ | Status | Flight Date | Delivered | Paid | Feedback | Notes |
|--------|--------|---------|---------|--------|-------------|-----------|------|----------|-------|
| CIV-2026-08-001 | [Name] | Storm | $1,500 | ✓ Complete | 08/15/2026 | 08/16/2026 | ✓ | 5-star | First paid job |
| CIV-2026-08-002 | [Name] | LiDAR | $2,500 | ⏳ Processing | 08/20/2026 | | | | Due 09/15 |
| | | | | | | | | | |

---

## Job Status Definitions

| Status | Meaning | Next Action |
|--------|---------|-------------|
| **📋 Quote** | Quote sent, awaiting response | Follow up in 3 days |
| **✍️ Signed** | Service agreement signed, awaiting flight | Schedule flight date |
| **🚁 Scheduled** | Flight scheduled, ready to execute | Execute on flight date |
| **📸 Flown** | Flight completed, processing data | Begin post-processing |
| **⚙️ Processing** | Data being processed into deliverables | Aim for turnaround target |
| **📦 Delivered** | Deliverables sent to client | Send invoice, request feedback |
| **💰 Invoiced** | Invoice sent, awaiting payment | Follow up if unpaid after 30 days |
| **✓ Paid** | Payment received in full | Collect feedback, close job |
| **⏳ Feedback** | Waiting for client feedback | Follow up after 1 week |
| **🎉 Complete** | Job complete, feedback collected | Archive and reference for future |

---

## Current Jobs Pipeline

### Stage: Quote (Awaiting Signature)

| Job ID | Client | Service | Quote Date | Days Pending | Next Action | Due Date |
|--------|--------|---------|-----------|--------------|-------------|----------|
| | | | | | | |

---

### Stage: Scheduled (Ready to Execute)

| Job ID | Client | Service | Flight Date | Checklist Prepared | Status |
|--------|--------|---------|-------------|-------------------|--------|
| | | | | | |

---

### Stage: Processing (Data → Deliverables)

| Job ID | Client | Service | Flight Date | Processing % | Est. Delivery | On Track? |
|--------|--------|---------|-------------|--------------|----------------|-----------|
| | | | | | | |

---

### Stage: Delivered (Invoiced)

| Job ID | Client | Service | Delivered | Invoice $ | Invoice Date | Paid? | Payment Date |
|--------|--------|---------|-----------|-----------|--------------|-------|--------------|
| | | | | | | | |

---

### Stage: Complete (Feedback Collected)

| Job ID | Client | Service | Completed | Feedback | Score | Margin | Lessons Learned |
|--------|--------|---------|-----------|----------|-------|--------|-----------------|
| | | | | | | | |

---

## Weekly Review Template

**Every Friday, review jobs and move them through stages:**

| Week of: __________ |
|---|
| **New inquiries this week:** __________ |
| **Quotes sent:** __________ |
| **Flights scheduled:** __________ |
| **Flights completed:** __________ |
| **Deliverables sent:** __________ |
| **Payments received:** __________ |
| **Stage 0 progress (target: 3 jobs + 2+ feedback + 1 paid):** |
| — Total jobs: __________ ✓ |
| — Positive feedback: __________ ✓ |
| — Paid jobs: __________ ✓ |
| **Gate clear?** ☐ Yes ☐ No |
| **Priority actions for next week:** |
| — __________ |
| — __________ |
| — __________ |

---

## Monthly Summary Report

**Run at end of each month for dashboard:**

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| **Jobs completed** | 3+ | __________ | |
| **Total revenue** | | $__________ | |
| **Avg job revenue** | | $__________ | |
| **Jobs paid** | 50%+ | __________ | |
| **Avg turnaround** | 5 days | __________ | |
| **Positive feedback %** | 70%+ | __________% | |
| **Gross margin %** | 80%+ | __________% | |
| **Repeat customer rate** | 30%+ | __________% | |

---

## Job Folder Structure

Each job should have its own folder:

```
/Jobs/CIV-YYYY-MM-###/
├── 01_INTAKE_FORM.md
├── 02_SERVICE_AGREEMENT_SIGNED.pdf
├── 03_PRE_FLIGHT_CHECKLIST.md
├── 04_QUOTE_CALCULATOR.md
├── 05_FLIGHT_LOG.md
├── 06_RAW_FOOTAGE/
│   ├── Photos/
│   ├── Video/
│   └── Metadata/
├── 07_PROCESSED_DELIVERABLES/
│   ├── Final Images/
│   ├── Report/
│   └── 3D Model/
├── 08_DELIVERABLE_CHECKLIST.md
├── 09_INVOICE_SENT.pdf
├── 10_PAYMENT_TRACKING.md
└── 11_FEEDBACK_SUMMARY.md
```

---

## Escalation Rules

**Move job to next stage when:**

- **Quote → Signed:** Client signs service agreement
- **Signed → Scheduled:** Client confirms flight date
- **Scheduled → Flown:** Flight is completed
- **Flown → Processing:** Raw footage transferred to secure storage
- **Processing → Delivered:** QA checklist complete, deliverables sent
- **Delivered → Invoiced:** Invoice sent to client
- **Invoiced → Paid:** Payment received and deposited
- **Paid → Complete:** Client feedback collected

---

## Red Flags & Escalations

| Red Flag | Action |
|----------|--------|
| Quote sitting >7 days without response | Send follow-up email |
| Job delayed >2 days past promised turnaround | Contact client with update |
| Invoice unpaid >15 days | Send payment reminder |
| Client complaint on quality | Offer revision or partial refund |
| Equipment failure during flight | Document, assess impact, communicate |

---

## Dashboard View (Summary for Weekly Review)

**Quick glance at business health:**

```
┌─────────────────────────────────────┐
│ STAGE 0 PROGRESS (Target: 3/2/1)    │
│ Jobs Completed: 1/3  ████░░░░░░     │
│ Positive Feedback: 1/2  ████░░░░░░  │
│ Paid Jobs: 1/1  ██████████░░░░░░    │
│ Revenue: $1,500 (Target: $2,500)    │
└─────────────────────────────────────┘

Current Pipeline:
- Awaiting Quote Response: 1
- Scheduled for Flight: 1
- In Processing: 2
- Invoiced, Awaiting Payment: 1
- Complete: 1
```

---

## Use This Tracker To:

1. **Know job status at a glance** — where is each job in pipeline?
2. **Avoid missing follow-ups** — what needs attention this week?
3. **Track toward Stage 0 gate** — are we hitting 3 jobs + 2 feedback + 1 paid?
4. **Monitor business health** — revenue, turnaround, feedback trends
5. **Manage workload** — how many jobs in process? Am I overloaded?

---

**Create Google Sheets version with this structure. Update weekly. Reference for all job decisions.**

