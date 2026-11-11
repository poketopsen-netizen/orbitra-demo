# Orbitra V24 — Telegram Admin DEMO

This version is a virtual-money educational demonstration. No real payment processing, deposits, payouts or wallet custody are implemented. Never publish real bank or crypto payment details in the DEMO instructions.

## Setup
Keep existing Render env vars: TELEGRAM_BOT_TOKEN, TELEGRAM_ADMIN_IDS (personal Telegram user IDs), TELEGRAM_WEBHOOK_SECRET, SECRET_KEY. Keep the webhook `/telegram/webhook` registered.

## Telegram
- `/start` — inline-button main menu (users, balances, requests, geo, stats)
- New registrations notify admins automatically, with a profile button.
- Profile shows the registered user's separate demo trading balance.
- Choose `Set DEMO balance` and send `/setbalance <internal_numeric_id> <amount>`; max 1,000,000.00. All changes are audited.
- `/geo Albania | crypto | USDT TRC20 | Тестовый адрес: SAMPLE-ONLY` — add DEMO instructions for a country.
- `/geo ALL | bank | Test Bank | DEMO account: SAMPLE-ONLY` — fallback for all countries.
- `/geodel Albania | crypto` — remove method.
- Bot activation requests still use 50 virtual USDT and can be approved once; they do not represent actual payments.

## Database and persistence
SQLite tables `users`, `demo_deposit_requests`, `geo_demo_methods`, `admin_audit` are used. To persist data on Render, configure a persistent disk with DATABASE_PATH pointing to it, or migrate to managed PostgreSQL before production. SQLite stored in the ephemeral service filesystem can be lost on redeploy. No PostgreSQL migration is included in this release.

## Limitations
- The payment methods shown on the site are TEST instructions only; real bank and crypto accounts are deliberately not accepted.
- The per-user trading DEMO balance is distinct from the AI Bot's virtual session balance.
- Admin balance edits require a command after pressing a button, not a Telegram form; authorization is restricted to admin IDs.
- Real-money payment verification, compliance, and refunds are not implemented.
