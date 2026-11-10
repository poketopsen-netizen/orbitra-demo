# Orbitra V16 — mobile / trading / wallet / profile

Built on the V15 project. Keep the current GitHub repo and Render service.

## Changes
- Mobile: safe-area bottom navigation, narrow-screen layout, keyboard focus states, reduced-motion support.
- Trading: lower polling load; do not substitute the entry quote when live prices are unavailable.
- Settlement: protect against simultaneous close requests by using a conditional status update under a SQLite write transaction.
- Wallet: new demo trading summary (closed positions, wins, net demo P/L).
- Profile and session: retains V15 password checks and existing account layout.
- Replaced misleading fixed BTC/ETH/market-cap figures in the top ticker with clearly labeled demo information.

## Deploy from this folder (Windows CMD)
The ZIP does not contain a `.git` folder. For a fresh extracted directory, use your existing workflow to attach to the remote history first; do not force push.

    git init
    git remote add origin https://github.com/poketopsen-netizen/orbitra-demo.git
    git fetch origin main
    git reset --mixed origin/main
    git add app.py static/app.js static/styles.css templates/index.html README_V16.md
    git commit -m "Orbitra V16 mobile and demo improvements"
    git push origin HEAD:main

If already in a connected Git folder, skip init/remote/fetch/reset and run the final three commands only.

## Important
- `SECRET_KEY` must be configured on Render and remain stable between deploys.
- SQLite on ephemeral storage can lose data after redeploy; configure durable storage or a hosted DB before storing valuable accounts.
- Demo trades are simulations, not real exchange orders.
- Validate on a staging deployment before production use.
