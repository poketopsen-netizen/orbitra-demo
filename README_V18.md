# Orbitra V18 — automated scripted DEMO bot

- 50 virtual USDT -> 3000 virtual USDT across 7 **pre-scripted** results over 3h30m. This is not a trading strategy, investment return, or exchange activity.
- Start once. Server derives due simulated settlements from UTC start timestamp on GET /api/bot-demo. No cron needed; refresh/back navigation catches up.
- Simulation outcome schedule is not displayed in advance. History clearly marks SIMULATED.
- Wallet displays bot virtual funds separately from the existing demo trading balance, to avoid double-counting. No real payouts.
- No local-currency FX section in the bot screen.
- Signed-in users: SQLite state; guests: Flask session cookie state (may be lost if secret changes).
- IMPORTANT: Existing V17 bot sessions can have older state; use Reset after completion or clear demo session. Existing user state may need manual migration.
- Production: use a persistent database and proper transactions/locking. Never use this scripted simulation as proof of real trading performance.
