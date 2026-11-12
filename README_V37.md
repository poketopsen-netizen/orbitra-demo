# Orbitra V37 — DEMO withdrawals and levels

This build adds a virtual withdrawal request flow after the 3h30m scripted simulation, a 5 DEMO USDT per-request limit at Level 1, a Level 2 virtual upgrade request (120 DEMO USDT credited to the test wallet after approval), a cryptocurrency/network/address form, wallet history, and Telegram approval/rejection buttons. No real money or blockchain transfers are made. The term "completed" in withdrawal history means a simulated operation, not an actual payment.

**Operational note:** Existing SQLite database is still ephemeral on many Render plans. Use persistent storage before relying on history across deployments. Admin approval updates the database only once per request.

**Tests:** Python compile and Node JS syntax checks completed. Full Flask integration testing and device browser testing were not available in the build environment.
