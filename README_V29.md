# Orbitra V29 — DEMO payment-method flow

- Cryptocurrency entries are configured independently per currency and network, e.g. `/geo Albania | crypto:USDT:TRC20 | USDT TRC20 | Тестовый адрес: SAMPLE-ONLY` and `/geo Albania | crypto:BTC:BITCOIN | BTC Bitcoin | Тестовый адрес: SAMPLE-ONLY`.
- Crypto cards appear only after admin configuration, with currency, network and copyable sample address. No crypto address request is created.
- Bank cards: if configured, show DEMO details; if not, user enters their sending bank and requests bank details (no amount or DEMO credit at this stage). Telegram admin receives this request.
- When admin sets bank DEMO instructions with `/geo <country> | bank | ...`, pending bank-detail requests for that country are marked READY. The user sees a one-time on-site notification (polled every 30s while site is open).
- Existing DEMO top-up approval and +10% crypto DEMO bonus remain. No actual payment is accepted. Never use real payment instructions on this demo.
- Data remains on SQLite; for production persistence use PostgreSQL.
