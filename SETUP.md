# Setup (Railway + Postgres + Telethon)

1) Create Telegram API ID/HASH at https://my.telegram.org
2) Create bots with @BotFather: uploader, payment, analytics
3) Make payment bot **admin** in premium group (ID in `.env`)
4) Create Railway Postgres; set `DATABASE_URL`
5) Run migration: `psql $DATABASE_URL -f migrations/schema.sql`
6) Fill env vars from `.env.example`
7) Create services:
   - `PROC=uploader`
   - `PROC=payment`
   - `PROC=analytics`
8) Deploy; watch logs
