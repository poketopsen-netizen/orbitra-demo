# Orbitra V15 — security and demo trading fixes

Changes:
- Password required for new registrations; login rejects passwordless legacy accounts.
- Current password required to change an existing password.
- Failed market quote no longer silently settles an expired demo trade at its entry price. The trade remains open until a quote becomes available.
- Reject non-finite trade amounts; use a database write lock when reserving a registered user's demo balance.
- Refill is blocked while any open demo positions remain.
- Optional `DATABASE_PATH` environment variable allows pointing SQLite to a persistent mounted disk.
- Random session secret if `SECRET_KEY` is absent; **set a fixed strong `SECRET_KEY` in Render Environment**, otherwise sessions are invalidated on restarts and across workers.

## Deploy on Render
Build command: `pip install -r requirements.txt`
Start command: `gunicorn app:app`
Set `SECRET_KEY` to a long random secret in Render Environment. For durable SQLite storage, set `DATABASE_PATH` to a file on a persistent disk (not available on Render Free), or migrate to a managed database. Existing legacy accounts without passwords cannot log in; they require an administrator-controlled recovery/migration process. Back up the current database before deploying.

This is a training/demo application, not a production financial trading service. Test on staging before replacing the live deployment.
