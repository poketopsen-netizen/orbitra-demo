# Orbitra V23 — Telegram DEMO Admin

## What works
- Registered user requests 50 **virtual DEMO USDT** activation in AI Bot.
- Admin receives Telegram message with Approve / Reject buttons.
- Approval atomically changes the user's `bot_demo.funded` flag to true, making 50 DEMO USDT available for the bot. It **does not** add real USDT or money to any wallet. No real payment is requested or verified.
- Repeat approvals are blocked, and decisions are recorded in `demo_deposit_requests` with admin ID and timestamp.
- Telegram commands: `/start`, `/users`, `/pending`, `/stats`.
- Webhook requires Telegram secret header and admin Telegram ID allowlist.

## Render environment variables (Dashboard > Service > Environment)
- `SECRET_KEY`: stable, random secret; **must persist across deploys**.
- `TELEGRAM_BOT_TOKEN`: token issued by @BotFather, never share it.
- `TELEGRAM_ADMIN_IDS`: your numeric Telegram user ID (comma separated for multiple admins).
- `TELEGRAM_WEBHOOK_SECRET`: random alphanumeric secret (letters, digits, `_`, `-`, 1–256 characters).
- `DATABASE_PATH`: absolute path on **persistent disk** (SQLite). Render Free ephemeral filesystem may erase data on redeploy. For production migrate to managed PostgreSQL and use transactions.

## Telegram webhook setup (once)
Once Render reports Live, register webhook with Telegram Bot API `setWebhook` using HTTPS URL:
`https://orbitra-demo.onrender.com/telegram/webhook`
Provide `secret_token` equal to `TELEGRAM_WEBHOOK_SECRET` and `allowed_updates=["message","callback_query"]`.
Use an authenticated API client or local PowerShell to call Telegram; **do not paste tokens in chat**. Example PowerShell (run on your computer, replace locally):

```powershell
$token = Read-Host 'BotFather token'
$secret = Read-Host 'TELEGRAM_WEBHOOK_SECRET'
$body = @{ url='https://orbitra-demo.onrender.com/telegram/webhook'; secret_token=$secret; allowed_updates=@('message','callback_query') } | ConvertTo-Json
Invoke-RestMethod -Uri "https://api.telegram.org/bot$token/setWebhook" -Method Post -ContentType 'application/json' -Body $body
```

## Test
1. Set env vars and deploy.
2. Open bot chat in Telegram, press Start, send `/start`.
3. Register on Orbitra and open AI Bot.
4. Click "Отправить заявку на 50 DEMO USDT".
5. In Telegram press Approve.
6. Reload AI Bot. The DEMO activation should be enabled.
7. Check `/pending`, `/stats`; attempt duplicate approval (must not credit again).

## Important limitations
- Demo-only, not a payment system. No real money is accepted, verified, transferred or credited.
- The pre-existing trading bot uses a scripted simulation and fixed virtual target; this is not market performance.
- Telegram is only for admin actions; no public admin dashboard yet, no per-geo payment method editing yet.
- Webhook requests are processed synchronously; for scale use background jobs, webhook idempotency by `update_id`, and a managed database.
- Existing V22 bot activations are preserved; they will not generate retroactive Telegram requests.
