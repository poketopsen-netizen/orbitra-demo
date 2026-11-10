# Orbitra V17 — Bot Lab (DEMO ONLY)

## Features
- Separate AI Bot navigation page with an explicitly scripted seven-step demo: WIN, LOSS, WIN, LOSS, LOSS, WIN, WIN.
- Virtual independent 50 USDT simulator ledger; each outcome is +/-5 USDT; ends at 55 USDT, NOT 2000.
- Separate persistence for logged-in users via SQLite bot_demo table; guests via Flask session cookie.
- FX reference estimates from Frankfurter reference rates with explicit 1 USDT ≈ 1 USD assumption. No quote shown when unavailable.
- Test-only wallet/card withdrawal requests. No sensitive card or wallet details, no actual payouts, no real balances.
- API endpoints /api/bot-demo, /start, /step, /reset, /withdraw, /fx.

## Deployment
Keep existing Render service and existing SECRET_KEY. Keep DATABASE_PATH on persistent storage if required. Back up SQLite before deploying.

## Future real integration
Use separate exchange execution adapters, market risk engine, audit ledger, authenticated payment providers, KYC/AML and applicable licensing. Never reuse scripted outcomes for real trades. Do not claim guaranteed profit. Add CSRF protection, rate limiting, and production session handling before financial integration.
