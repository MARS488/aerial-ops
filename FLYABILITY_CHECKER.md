# Flyability Checker — Can You Fly This Property?

**Use this checklist when a new inquiry comes in. Takes 5 minutes. Tells you YES or NO.**

---

## Step 1: Airspace Check (2 Minutes)

### Is This in Valdosta Service Area?

- [ ] **YES** — Property is in Valdosta or Lowndes County
- [ ] **NO** — Outside service area → Refer to another pilot or decline

**If NO:** Stop here. Can't serve this property.

---

### Check LAANC Airspace

**How to check:**
1. Open Airmap, Aloft, or Skyward app
2. Enter property address or coordinates
3. Check airspace class + restrictions

| Airspace Class | Flyable? | Action |
|----------------|----------|--------|
| **Uncontrolled (E)** | ✅ YES | No authorization needed, fly freely |
| **Class D** | ⚠️ YES | Need LAANC authorization (usually instant, <1 min) |
| **Class C or B** | ❌ HARD | Need written authorization from ATC (takes days) |
| **Restricted/Military** | ❌ NO | Cannot fly here (Moody AFB area) |
| **TFR (Temporary Flight Restriction)** | ❌ NO | Cannot fly here |

**Decision:**
- [ ] **Flyable** — Airspace permits flying, or LAANC auth available
- [ ] **Not Flyable** — Restricted/controlled airspace without auth → Decline

**If Not Flyable:** Stop here. Can't serve this property.

---

## Step 2: Weather Check (2 Minutes)

### Forecast for Proposed Flight Date

**Open:** Weather.com or weatherunderground.com  
**Enter:** Property address

| Condition | Flyable? | Your Limit |
|-----------|----------|-----------|
| **Wind speed** | ✅ < 15 mph | YES / ⚠️ 15-20 mph | YES but risky / ❌ > 20 mph | NO |
| **Rain/Precipitation** | ⚠️ Light | Maybe / ❌ Heavy | NO |
| **Visibility** | ✅ > 3 miles | YES / ❌ < 3 miles | NO (fog, heavy rain) |
| **Temperature** | ✅ 40-110°F | YES / ⚠️ Outside range | Check battery performance |
| **Time of Day** | ✅ Daylight | YES (sunrise to sunset) / ❌ Night | NO |

**Decision:**
- [ ] **Flyable** — Weather permits flying on proposed date
- [ ] **Not Flyable** — Weather too risky → Offer alternative date
- [ ] **Marginal** — Conditions borderline → Tell client "weather dependent"

**If Not Flyable:** Offer 2-3 alternative dates within 2 weeks.

---

## Step 3: Property/Site Check (1 Minute)

### Will You Be Able to Operate?

**Ask client or check via Google Maps:**

| Factor | Flyable? | Notes |
|--------|----------|-------|
| **Site Access** | ✅ YES | Property accessible, land available | ⚠️ MAYBE | Landlord permission needed | ❌ NO | Gated/restricted access |
| **Obstacles** | ✅ Clear | No power lines, tall structures | ⚠️ SOME | Manageable with caution | ❌ TOO MANY | Too risky to fly |
| **People** | ✅ Clear | Can clear flight zone | ⚠️ MAYBE | Ongoing activity, risky | ❌ IMPOSSIBLE | Can't clear zone safely |
| **Flight Zone Size** | ✅ > 1 acre | Enough space to operate | ⚠️ 0.5-1 acre | Tight but doable | ❌ < 0.5 acre | Too small |

**Decision:**
- [ ] **Flyable** — Site conditions permit safe flying
- [ ] **Marginal** — Doable with caution, but require client's help clearing zone
- [ ] **Not Flyable** — Too risky or constrained → Decline

**If Not Flyable:** Decline respectfully. Safety first.

---

## Step 4: Business Check (30 Seconds)

### Do You Want This Job?

| Factor | Check |
|--------|-------|
| **Service Type** | ☐ Storm (YES) ☐ LiDAR (YES) ☐ Monitoring (YES) ☐ Other (__?) |
| **Acreage** | ☐ < 1 acre (small, $500-800) ☐ 1-5 acres (medium, $1,000-2,000) ☐ 5+ acres (large, $2,500+) |
| **Timeline** | ☐ This week (doable) ☐ Next week (doable) ☐ Next month (accept, book out) ☐ ASAP/Rush (extra charge) |
| **Access** | ☐ Easy access ☐ Somewhat challenging ☐ Very difficult (higher cost) |

**Decision:**
- [ ] **YES** — Interested, can serve this
- [ ] **MAYBE** — Interested but timeline/scope needs discussion
- [ ] **NO** — Not interested (outside service area, too complex, too small, etc.)

---

## Step 5: Feasibility Decision

**Based on all checks above:**

```
Airspace:  ✅ Flyable  / ⚠️ LAANC needed  / ❌ Not flyable
Weather:   ✅ Flyable  / ⚠️ Marginal      / ❌ Not flyable
Site:      ✅ Flyable  / ⚠️ Marginal      / ❌ Not flyable
Business:  ✅ Want it  / ⚠️ Maybe         / ❌ Don't want
═════════════════════════════════════════════════════════
RESULT:    ✅ FLY IT   / ⚠️ CONDITIONAL   / ❌ DECLINE
```

### If ✅ FLY IT
- Send quote immediately (use UNIVERSAL_QUOTE_CALCULATOR.py)
- Schedule flight for proposed date
- Proceed with standard workflow

### If ⚠️ CONDITIONAL
- Email client: "Interested, but [condition]. Here are options:"
  - Option 1: Fly on [alternate date] when weather clears
  - Option 2: Fly as-is, but [limitation], lower price
  - Option 3: Schedule for next month when [obstacle] resolved
- Wait for client response

### If ❌ DECLINE
- Email client: "Thanks for reaching out. Unfortunately, [reason]. Here's a referral: [other drone service]"
- Keep their info in case situation changes
- Move on

---

## Quick Reference Decision Tree

```
Property inquiry arrives
    ↓
Is it in Valdosta service area?
    ├─ NO → DECLINE
    └─ YES ↓
    
Is airspace flyable (check LAANC)?
    ├─ NO (restricted/military) → DECLINE
    ├─ YES but needs LAANC → Continue
    └─ YES unrestricted → Continue ↓
    
Is weather flyable on proposed date?
    ├─ NO (wind > 20, heavy rain, night) → Offer alternate dates
    ├─ MARGINAL (wind 15-20, light rain) → "Weather dependent" offer
    └─ YES (clear) → Continue ↓
    
Can you safely operate at site?
    ├─ NO (no access, too many hazards) → DECLINE
    ├─ MARGINAL (need client help) → Continue with conditions
    └─ YES (safe, accessible) → Continue ↓
    
Do you want this job?
    ├─ NO (outside service scope) → DECLINE
    ├─ MAYBE (interesting but complex) → Quote high or conditional
    └─ YES (fits your services) → SEND QUOTE ✅
```

---

## Time to Flyability Check

**Total time: 5 minutes**

- Airspace check: 1 min (app, one tap)
- Weather check: 1 min (weather website)
- Site check: 1.5 min (Google Maps + client Q&A)
- Business check: 0.5 min (quick decision)
- Decision: 1 min (template, done)

**Do this BEFORE sending a quote.**

---

## When You Get an Inquiry (Real Example)

**Client emails:** "Hi Marcus, I have a 3-acre property in Valdosta. Storm damaged it last week. Can you fly it this Friday? How much?"

**You do (5 min):**

1. **Airspace:** Open Airmap, enter address → "Uncontrolled airspace, no LAANC needed" ✅
2. **Weather:** Check Friday forecast → "15 mph wind, clear skies, good visibility" ✅
3. **Site:** Google Maps shows rural property, no obstacles visible. Ask client: "Any power lines, trees blocking?" They say no. ✅
4. **Business:** 3 acres, storm damage (your specialty), Friday (this week, doable) ✅
5. **Decision:** ✅ FLY IT

**You respond:** "Thanks! I can fly Friday at 10 AM. Your property qualifies for the Storm Assessment ($1,500). Here's the agreement to sign..."

**Total time to response: 5 min check + 5 min to customize quote = 10 min.**

---

## Store This In Your Phone

**Take a photo or screenshot of the decision tree above.**

**When inquiry comes via text/call:**
1. Pull up decision tree
2. Ask the 5 questions
3. Decide YES/NO in real-time
4. Respond immediately

**Clients love fast responses. You'll be fastest in Valdosta.**

---

## What This Checklist Prevents

✅ Saying YES to a restricted airspace job → Illegal flight → Liability  
✅ Saying YES to a storm in high winds → Equipment damage  
✅ Saying YES to a property you can't access → Wasted trip  
✅ Saying YES to too many jobs → Overwhelmed, quality drops  
✅ Sending quote for unmarked property → Client expects low price, you need high  

**Use this checklist. Never say YES blindly.**

---

