# UGCINEMA — v9 (Telegram-only Features; MTProto + PostgreSQL)

**Content:** Original videos (confirmed)  
**Payments:** Kept (manual approval, button-only)  
**DB:** PostgreSQL on Railway  
**Library:** Telethon (native MTProto)

## What’s New in v9
- **A) `/stats`** — richer admin analytics (subs, uploads, categories, top engagement)
- **B) `/categories`** — user browser to view latest titles per category
- **C) Welcome message** — DM + group shout when activated
- **D) Anti-duplicate upload** — warns if title already exists, allows override
- **E) `/broadcast`** — admin broadcasts to Premium group

## Payment Flow (Buttons Only)
1. `/premium` → tap **Join Premium — UGX 3,000**
2. Bot asks for **phone number** (Ugandan formats allowed)
3. Bot shows **Open Payment** + **I have paid ✅** button
4. **Only the button** triggers admin approval
5. If user types “I have paid” → bot replies: **“Tap the ‘I have paid ✅’ button below 😊”**

## Free vs Premium Posting
- **Free channel:** upscale + **title + CTA description + payment button**
- **Premium group:** upscale + **title only** (no CTA)

## Services
- `uploader` — DM from uploaders (thumbnail + video + title + CTA/free), posting with FFmpeg overlay
- `payment` — payment UI, admin approvals, reminders, expiry, `/stats`, `/categories`, `/broadcast`
- `analytics` — engagement tracker for Premium group

## Deploy (Railway)
1. Create **Postgres** → copy `DATABASE_URL`
2. Set Railway Variables (see `.env.example`)
3. Run migration:
   ```bash
   psql $DATABASE_URL -f migrations/schema.sql
   ```
4. Create 3 services (same repo):
   - `PROC=uploader`
   - `PROC=payment`
   - `PROC=analytics`
5. Make **payment bot** admin in premium group.

## Legal
Operate **only with content you own or are licensed to distribute**.
