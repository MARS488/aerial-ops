# Business Dashboard Setup — Marcus Jay Herring LLC

**Google Sheets or Excel dashboard formulas for LLC-level metrics. One honest view of the business.**

---

## The Philosophy

Don't track everything. Track what matters:
- **Stage 0:** Jobs completed + feedback
- **Stage 1:** Revenue + jobs per month + recurring contracts
- **Stage 2:** Monthly Recurring Revenue (MRR) + churn + gross margin
- **Stage 3:** MRR + churn + margin + cash runway

Right now: Stage 0-1. Keep it simple.

---

## Setup (Google Sheets or Excel)

### Sheet 1: Flight Log (Your Data Source)

**Columns:**
```
Date | Division | Service Type | Client | Acres | Paid? | Amount | Days to Deliver | Feedback | Notes
```

**Example rows:**
```
8/11/2026 | CivilitySync | Storm | [Client Name] | 3 | Yes | $1,500 | 2 | "Very helpful" | First paid job
8/15/2026 | CivilitySync | LiDAR | [Client Name] | 15 | Yes | $2,500 | 5 | "Would use again" | Recurring potential
8/20/2026 | CivilitySync | Scan | [Client Name] | 0.5 | No | $0 | 1 | Demo | Proof of concept
```

**Entry discipline:**
- Add immediately after completion (or within 24 hours)
- Get feedback within 48 hours (one text: "Was that useful?")
- Mark feedback accurately (it matters more than you think)

---

### Sheet 2: Dashboard Summary (Auto-Calculated)

Copy these formulas into dedicated cells. Update the cell references for your data.

#### Stage 0-1 Summary (Overall)

**Total Jobs Flown:**
```
=COUNTA(Sheet1!A2:A999)
```

**Jobs by Division:**
```
=COUNTIF(Sheet1!B2:B999,"CivilitySync")
=COUNTIF(Sheet1!B2:B999,"[Other Division]")
```

**Paid vs. Free:**
```
Paid jobs: =COUNTIF(Sheet1!F2:F999,"Yes")
Free/demo: =COUNTIF(Sheet1!F2:F999,"No")
```

**Total Revenue:**
```
=SUM(Sheet1!G2:G999)
```

**Average Job Revenue:**
```
=AVERAGE(IF(Sheet1!G2:G999>0,Sheet1!G2:G999))
```
(Use array formula: Ctrl+Shift+Enter in Excel)

**Feedback Score:**
```
=COUNTIF(Sheet1!I2:I999,"Would use again") / COUNTA(Sheet1!A2:A999)
```
(Multiply by 100 for percentage)

**Positive Feedback Count:**
```
=COUNTIF(Sheet1!I2:I999,"Would use again")
```

**Days Since First Job:**
```
=TODAY() - MIN(Sheet1!A2:A999)
```

**Jobs Per Month (Annualized):**
```
=(COUNTA(Sheet1!A2:A999) / (TODAY() - MIN(Sheet1!A2:A999))) * 30
```

#### Cost & Margin Analysis (Stage 1)

If you start tracking costs in a separate sheet:

**Sheet 2B: Expense Log**
```
Date | Category | Amount | Job | Notes
------|----------|--------|-----|--------
8/15  | Battery  | $30 | Storm_123 | Wear
8/15  | Travel   | $50 | Storm_123 | Mileage
8/20  | Software | $50 | General | Monthly
```

**Then calculate:**

**Total Costs (Month/YTD):**
```
=SUM(ExpenseLog!C2:C999)
```

**Gross Margin (Month/YTD):**
```
=SUM(Sheet1!G2:G999) - SUM(ExpenseLog!C2:C999)
```

**Margin %:**
```
=Gross Margin / SUM(Sheet1!G2:G999)
```

**Cost Per Job:**
```
=SUM(ExpenseLog!C2:C999) / COUNTA(Sheet1!A2:A999)
```

---

### Sheet 3: Monthly Breakdown (Optional)

**If you want monthly view:**

```
Month | Jobs | Revenue | Costs | Margin | Margin % | Feedback Score
-------|------|---------|-------|--------|----------|----------------
Aug    | 3    | $4,000  | $150  | $3,850 | 96%      | 67%
Sep    | 5    | $8,200  | $280  | $7,920 | 96%      | 80%
Oct    | 7    | $12,500 | $420  | $12,080| 97%      | 85%
```

**Use SUMIF/COUNTIF to pull from Sheet 1 by month:**
```
Jobs this month: =COUNTIF(Sheet1!A2:A999,">="&DATE(2026,8,1)) - COUNTIF(Sheet1!A2:A999,">"&DATE(2026,8,31))
Revenue this month: =SUMIFS(Sheet1!G2:G999,Sheet1!A2:A999,">="&DATE(2026,8,1))
```

---

### Sheet 4: Partner Tracker (Relationship Pipeline)

**Track outreach and partnership progress:**

```
Partner Name | Contact | Last Contact | Status | Next Action | Date for Next Action
---|---|---|---|---|---
Southeastern Survey | Barbara | [date] | Proposal sent | Schedule coffee | [date]
Environmental Firm | [name] | [date] | Initial research | Send proposal | [date]
Marketplace (Zeitview) | - | [date] | Account created | First job upload | [date]
```

**Status options:**
- Initial research
- Proposal sent
- Coffee scheduled
- Pilot flight planned
- Pilot flight completed
- Partnership active
- On hold

---

## Dashboard Visual (Nice-to-Have)

### Simple Chart (Cumulative Revenue Over Time)

1. Create two columns: Date + Cumulative Revenue
   ```
   8/11 | $0
   8/15 | $1,500
   8/20 | $1,500
   8/25 | $4,000
   ```

2. Insert line chart (Google Sheets: Insert > Chart)
3. X-axis: Date, Y-axis: Cumulative Revenue
4. Add a horizontal line at your Stage 0 gate (if goal is $5,000 by Sept 1, draw that line)
5. Bookmark this chart (visual proof of progress)

---

## Reading Your Dashboard

### Weekly Check-In (Friday)

- Total jobs flown: ___
- Feedback score: ___ %
- Total revenue: $___
- Average job size: $___
- "Would use again" count: ___

**Questions to ask:**
- Am I on track for Stage 0 gate? (3 jobs + 2 positive + 1 paid)
- What type of job had best feedback?
- What's the real average job size (ignore outliers)?

### Monthly Review

- Jobs this month: ___
- Revenue this month: $___
- Costs this month: $___
- Gross margin %: ___
- Feedback score: ___ %

**Questions to ask:**
- Is margin holding (should be 80%+ on well-priced jobs)?
- Are costs what I expected?
- Which feedback scores are trending up?
- What's the lag time on delivery?

### Quarterly Deep Dive

- Jobs per quarter: ___
- Revenue per quarter: $___
- Revenue per job (average): $___
- Margin per job (average): $___
- "Would use again" rate: ___ %

**Questions to ask:**
- Are we moving toward Stage 1 gate? (recurring contracts?)
- Is pricing right? (margin healthy?)
- Which service type has best feedback?
- What partnerships are closest to activation?

---

## When to Update

- **After every job:** Log it immediately (date, service, amount, feedback)
- **Every Friday:** Update dashboard (refresh formulas, spot-check data)
- **Every month:** Review monthly breakdown (trends?)
- **Every quarter:** Deep dive (are gates clearing?)

**Total time:** 10 minutes per week, 30 minutes per month.

---

## The Gate Checks

### Stage 0 → Stage 1 Gate Clears When:

```
IF(
  AND(
    COUNTA(jobs) >= 3,
    COUNTIF(feedback,"Would use again") >= 2,
    COUNTIF(paid_status,"Yes") >= 1,
    Processes written down = TRUE
  ),
  "READY FOR STAGE 1",
  "IN PROGRESS"
)
```

**Translation:** You need 3 jobs done, at least 2 people saying they'd use you again, at least 1 payment received, and your process documented.

### Stage 1 → Stage 2 Gate Clears When:

```
IF(
  AND(
    COUNTIF(jobs_this_month) >= 3,
    COUNTIF(recurring_contracts) >= 1,
    Delegation starting = TRUE
  ),
  "READY FOR STAGE 2",
  "IN PROGRESS"
)
```

**Translation:** 3+ paying jobs per month consistently, at least one customer on recurring/seasonal contract, and you're not flying every job yourself.

---

## Pro Tips

1. **Ignore first 2 jobs:** They're learning. Don't expect them to be representative of margin or speed. Gate clears on job #3+.

2. **Feedback > perfection:** A mediocre job with feedback is better data than a perfect job you did alone.

3. **Margin math:** If a job's margin is < 70%, it's a warning sign. Either you priced wrong or costs are higher than expected. Investigate.

4. **Recurring is the goal:** One $2,500/month recurring contract is worth 5 one-off $1,500 jobs. Track this separately.

5. **Turnaround matters:** Track average delivery time. If it's creeping up, something's wrong.

---

## Template (Bare Minimum)

If you don't want to copy all formulas, here's the absolute minimum:

**Sheet 1: Flight Log**
- Date, Division, Service, Client, Paid?, Amount, Feedback

**Sheet 2: Summary**
- Total jobs: [Count]
- Total revenue: [Sum]
- Feedback score: [%]
- Stage 0 gate cleared: [Yes/No]

**That's it.** Everything else is nice-to-have.

---

*Update this dashboard every Friday. It's your business at a glance.*
