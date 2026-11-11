# Orbitra V25 — DEMO top-ups by region

- Wallet button opens a mobile-first modal listing available country-specific demonstration methods. Crypto appears first and has a clearly marked **+10% virtual bonus**.
- Users enter a virtual amount and send a DEMO request; no actual payment is required or accepted.
- Admin receives a Telegram notification and can approve/reject using inline buttons. Approval credits the user's virtual wallet with the requested amount plus the crypto demo bonus exactly once; actions are audited.
- Only methods configured for the user's country (or ALL) appear. Admin's existing `/geo Country | crypto/bank | Name | DEMO instructions` workflow is retained. Do not publish real payment credentials in the demonstration.
- Bot activation requests remain separate from wallet top-up requests.
- SQLite remains local: on free Render the database can be reset on redeployment. For production use persistent PostgreSQL and proper migrations before accepting real users.
- All balances and bonuses are simulated and have no cash value. Real payments, crypto transfers, withdrawals and guaranteed returns are not supported.

Deploy: extract ZIP, open CMD in `orbitra_v14`, and push to your existing GitHub repo. Existing Render Telegram variables and webhook are reused.
