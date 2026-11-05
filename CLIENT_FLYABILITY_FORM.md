# Client Flyability Assessment Form

**Put this on your website or in an email. Clients fill it out. System tells them instantly if you can fly their property.**

---

## How It Works

1. **Client sees form** (on website, email link, or text link)
2. **Client answers 8 questions** (2 minutes)
3. **System checks answers** (instant)
4. **Client gets result:** "YES we can fly this" or "Not right now, here's why"
5. **If YES:** Quote appears automatically
6. **If NO:** Alternative options appear (refer to other pilot, wait for better weather, etc.)

---

## The Form (Copy/Paste Into Google Form)

### Question 1: Property Location
**Type:** Text input  
**Question:** "What's your property address? (Street, City, State)"

**Behind the scenes:**
- System checks: Is it in Valdosta/Lowndes County?
  - If NO: "We primarily serve Valdosta area. For properties outside our service area, [refer to other pilot]"
  - If YES: Continue to next question

---

### Question 2: Service Type
**Type:** Multiple choice  
**Question:** "What do you need?"

**Options:**
- [ ] Storm/Emergency Assessment (damage photos + report)
- [ ] LiDAR Scan (3D aerial data)
- [ ] Property Monitoring (before/after photos)
- [ ] Other (describe): ____________

**Behind the scenes:**
- System confirms: "We serve all of these. Perfect!"
- If "Other": Flag for manual review

---

### Question 3: Preferred Flight Date
**Type:** Date picker  
**Question:** "When would you like the flight?"

**Options:**
- [ ] This week (by Friday)
- [ ] Next week
- [ ] Next month
- [ ] Flexible/ASAP

**Behind the scenes:**
- System checks weather forecast for selected dates
- If bad weather this week: "Weather looks stormy Wed-Fri. How about next week?"
- If good weather: "Perfect! Conditions look good."

---

### Question 4: Airspace Verification
**Type:** Multiple choice  
**Question:** "Do you know if your property is near any airports or military bases?"

**Options:**
- [ ] No airports nearby (isolated rural area)
- [ ] Maybe (suburban area, unsure)
- [ ] Near Valdosta Regional Airport or Moody AFB
- [ ] Don't know

**Behind the scenes:**
- If "No airports": ✅ "Great! Airspace is clear."
- If "Maybe" or "Don't know": System checks LAANC database automatically
  - If unrestricted: ✅ "Airspace is clear."
  - If controlled/restricted: ❌ "This area requires special authorization. [Details]"
- If "Moody AFB area": ❌ "Unfortunately, we can't fly in this area due to military airspace restrictions."

---

### Question 5: Site Access
**Type:** Multiple choice  
**Question:** "Can we safely access your property?"

**Options:**
- [ ] Easy access (paved driveway, open area to launch)
- [ ] Moderate (gravel drive, some obstacles)
- [ ] Difficult (long walk, power lines, lots of trees)
- [ ] Unsure

**Behind the scenes:**
- If "Easy": ✅ "Perfect for flying."
- If "Moderate": ⚠️ "Doable, but may take extra time. Price might be slightly higher."
- If "Difficult": ⚠️ "We can fly this, but will need your help clearing the zone. Extra cost applies."
- If "Unsure": "Can you describe obstacles? [Text box]"

---

### Question 6: Property Size
**Type:** Number input  
**Question:** "Approximately how many acres is the property?"

**Input:** __________ acres

**Behind the scenes:**
- System calculates pricing tier:
  - 0.5-2 acres: Small ($500-800) - "Perfect size for our services"
  - 2-5 acres: Medium ($1,000-2,000) - "Standard scope"
  - 5-20 acres: Large ($2,500-5,000) - "Larger scope, may need multiple flights"
  - 20+ acres: Very Large ($5,000+) - "Premium scope. Let's discuss details"

---

### Question 7: Site Hazards
**Type:** Checkboxes (select all that apply)  
**Question:** "Are there any of these on or near your property?"

**Options:**
- [ ] Power lines
- [ ] Tall trees
- [ ] Structures (buildings, water towers)
- [ ] Water (pond, river)
- [ ] Heavy traffic nearby
- [ ] None of the above

**Behind the scenes:**
- If none checked: ✅ "Clear site! Ideal for flying."
- If 1-2 checked: ⚠️ "Manageable hazards. Standard flying conditions."
- If 3+ checked: ⚠️ "Complex site. Will require extra caution and possibly additional time/cost."

---

### Question 8: Contact & Confirmation
**Type:** Email + Phone  
**Question:** "How can we reach you with your quote?"

**Inputs:**
- Email: ____________________
- Phone: ____________________

**Behind the scenes:**
- System collects contact info
- Prepares auto-response email with results
- Logs inquiry in your CRM (HubSpot/Notion)

---

## The Automated Response (What Client Sees)

### If ✅ PROPERTY IS FLYABLE

**Email subject:** "Good news! We can fly your property 🚁"

```
Hi [Client Name],

Great news! Your property at [Address] is flyable, and we'd love to help.

QUICK SUMMARY:
✅ Location: Valdosta area (perfect!)
✅ Airspace: Clear (no restrictions)
✅ Weather: Forecast looks good for [date]
✅ Site: Ready for flying

YOUR QUOTE:
Service: [Storm Assessment / LiDAR / Monitoring]
Property Size: [Acreage]
Estimated Price: $[1,500]
Turnaround: 3-5 days from flight

NEXT STEPS:
1. Reply YES to confirm
2. We'll send a service agreement
3. We'll schedule your flight
4. You'll receive deliverables in 3-5 days

Any questions? Just reply to this email or call [Your Phone].

Ready to move forward?

Best,
Marcus Herring
Marcus Jay Herring LLC
[Phone]
```

---

### If ⚠️ PROPERTY IS MARGINAL

**Email subject:** "We can fly your property with conditions"

```
Hi [Client Name],

We can definitely fly your property, but with a few considerations:

⚠️ WEATHER: Forecast shows strong winds Wed-Fri. We recommend flying [next week instead] when conditions are better.

⚠️ HAZARDS: Your property has [power lines, trees]. We can work around these, but it may take extra time.

⚠️ ACCESS: You mentioned difficult site access. We'll need your help clearing the flight zone.

ADJUSTED QUOTE:
Base Price: $[1,500]
Complexity Adjustment: +$[500] (for hazards/access)
Weather Delay: [Propose alternate dates]
Total: $[2,000]

OPTIONS:
1. Proceed now as-is ($2,000)
2. Wait for better weather next week ($1,500)
3. Let's discuss specific concerns [call Marcus]

Which works best for you?

Best,
Marcus Herring
```

---

### If ❌ PROPERTY NOT FLYABLE

**Email subject:** "About your flyability assessment"

```
Hi [Client Name],

Thanks for filling out our assessment. Unfortunately, your property has a challenge right now:

❌ AIRSPACE: Your property is in controlled airspace near [Airport/Military]. We'd need special authorization, which takes days to process.

❌ WEATHER: Forecast shows storms through [date]. Too risky for safe flying.

❌ LOCATION: We primarily serve Valdosta. Your property is outside our service area.

OPTIONS:
1. Wait until [date] when weather clears, then contact us
2. If it's an emergency, I can recommend another pilot who might serve your area: [Referral]
3. If airspace is the issue, we can explore special authorization (takes 3-5 days)

Feel free to reach out when conditions change. We'd love to help then!

Best,
Marcus Herring
```

---

## How to Set Up This Form (3 Steps)

### Step 1: Create Google Form
1. Go to **forms.google.com**
2. Create new form
3. Copy questions from above
4. Add your contact email at the end
5. Share link publicly

**Time: 15 minutes**

---

### Step 2: Connect to Google Sheets
1. In Google Form, click "Responses" tab
2. Click Google Sheets icon
3. Create new spreadsheet
4. Responses auto-populate there

**Time: 5 minutes**

---

### Step 3: Automate Responses (Optional - Stage 1)
1. Use **Zapier** ($20/month, free tier available)
2. Trigger: "New Google Form Response"
3. Action: "Send Email to Client" with your response template
4. Set up 3 email templates:
   - ✅ FLYABLE → Send quote
   - ⚠️ MARGINAL → Send conditional offer
   - ❌ NOT FLYABLE → Send alternative options

**Time: 1 hour setup**

**Result:** Form submitted → Auto-response sent in real-time (no Marcus needed)

---

## Where to Put the Form

### Option 1: Email Signature (Now)
```
---
Want a FREE flyability assessment? 
Click here: [Google Form Link]
Takes 2 min. Get instant answer.
```

**Use for:** Every email to prospects

---

### Option 2: Website/Landing Page (Stage 1)
- Create simple one-page site (Canva, Carrd, or built-in forms)
- Embed Google Form
- "Check if we can fly your property"

---

### Option 3: Social Media (Stage 1)
- Post form link on Google Business Profile
- Share on Facebook/Instagram
- Caption: "Not sure if we can fly your property? Check here (takes 2 min)"

---

### Option 4: Text Link (Now)
- Send clients text: "Check if we can fly: [Google Form Link]"
- Takes 2 minutes, instant answer

---

## What This Automates

| Before (Manual) | After (Form) | Time Saved |
|-----------------|--------------|-----------|
| Client calls → You answer 8 questions | Client fills form in 2 min | 10 min |
| You check airspace manually | Form + Zapier checks auto | 5 min |
| You check weather manually | Form auto-checks forecast | 5 min |
| You manually email quote | Zapier sends auto | 5 min |
| You log lead in CRM manually | Zapier logs to HubSpot/Notion auto | 3 min |
| **Total per inquiry: 28 min saved** | **Client gets answer in 2 min** | **26 min/inquiry** |

**At 5 inquiries/month: 2+ hours saved per month**

---

## Full Automation (The Vision)

```
Client submits form
    ↓ (automatic)
System checks: Airspace + Weather + Site + Acreage
    ↓ (automatic)
System generates: Decision + Quote + Conditions
    ↓ (automatic)
Zapier sends: Auto-response email to client
    ↓ (automatic)
Zapier logs: Inquiry in HubSpot CRM (tagged by status)
    ↓ (automatic)
Dashboard updates: New lead appears in pipeline
    ↓ (you act)
You receive notification: "New flyable lead: 3 acres, storm, $1,500"
    ↓ (you act)
You follow up: Call/email client within 1 hour
    ↓ (automatic)
Client accepts → Service agreement auto-sends via Zapier
    ↓ (you act)
You fly job → Log in system
    ↓ (automatic)
Everything else runs on autopilot (invoicing, feedback, payment tracking)
```

**Result: 80% of intake process happens without you.**

---

## This Is Your 10x Leverage Point

**Most drone businesses:**
- Every inquiry requires manual phone call (10 min each)
- Miss inquiries because slow responses
- Can't scale past the founder's phone

**You with this system:**
- Every inquiry filled out automatically
- You get instant alert with all info pre-filled
- You follow up fast (faster than 90% of competitors)
- System scales to 100+ inquiries/month
- You only engage with HOT leads (system pre-qualifies)

---

## Next Steps

1. **Create the Google Form** (15 min)
2. **Put link in your email signature** (1 min)
3. **Share form link with Southeastern Survey** (referral source)
4. **As inquiries come in, test the form** (refine questions)
5. **After 20 responses, connect Zapier for automation** (Stage 1)

---

