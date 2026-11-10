# Orbitra V22 — gated auto demo bot

- Registration required to access the demo bot. New registrations redirect to #bot.
- Registered users explicitly credit 50 **virtual** USDT for free; no crypto address or payment required.
- Seven automatic simulated position closes at 5, 15, 35, 65, 105, 155, 210 minutes after start.
- Current position shows exact close time and countdown; history shows open/close timestamps.
- Simulated cash-out panel removed. Demo funds are not transferable or withdrawable.
- The fixed 3000 USDT educational endpoint is synthetic, not market profit.
- Uses existing bot_demo SQLite table. Configure a persistent DATABASE_PATH and SECRET_KEY in production for persistence.
- Does not implement actual trading, deposits, payment cards or withdrawal.
