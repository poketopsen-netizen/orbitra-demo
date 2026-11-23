# Orbitra V50 — mobile i18n audit and DEMO badge

Based on V49. No changes to bot amounts, trading durations, or payment approval logic.

- Added localized UI text for deposit flow, crypto network/address selection, bank details, pending/approved/rejected top-up statuses and buttons.
- Localized AI Bot activation confirmation, payout/level controls and notices, profile trade history, password labels, bot status labels, FX date/source note, and 5-minute trade labels.
- Kept six languages: ru, en, es, fr, pt, ar.
- Isolated DEMO badge with flex alignment, spacing and no-wrap to avoid overlapping lettering.
- Updated JS cache version to 50i18n.

Checks: Python compile, node --check, ZIP CRC. Browser smoke test in Chromium with mocked API for six languages, wallet, deposit, crypto details, profile, security and AI Bot, no page errors. Real Render/Telegram integration not tested.
