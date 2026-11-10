# Orbitra V19 — varied simulated trade amounts

- Each new 3h30m demo run precomputes a randomized ledger: WIN, LOSS, WIN, LOSS, LOSS, WIN, WIN.
- All wins and losses differ; losses are larger than the fixed -50 USDT in V18.
- Exactly 50 + sum(P/L) = 3000 **virtual** USDT after the seventh stage. This is a predetermined simulation target, not an achievable guaranteed trading return.
- The ledger is persisted server-side on start; reloads do not reroll results. Unsettled entries are not returned to the browser.
- Existing active V18 demos continue on their original schedule. To get new varied amounts, start a new demo after the prior one finishes and reset it.
- No real trading, deposits, or withdrawals. All transactions are marked SIMULATED.

## Deployment

Commit `app.py` and `README_V19.md` on top of the existing `main` branch, then push. Preserve Render environment variables and back up the database before deployment.
