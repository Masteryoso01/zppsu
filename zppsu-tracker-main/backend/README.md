# GeoTrack backend

FastAPI (Python) API with **Google Sheets** as the database, reached through a **Google Apps Script** web app.

```
Vue app  ──HTTPS+JWT──▶  FastAPI (this folder)  ──HTTPS+secret──▶  Apps Script  ──▶  Google Sheet
```

Browsers/phones only ever talk to FastAPI. The Apps Script URL and its secret stay on the server.

## 1. Set up the spreadsheet + Apps Script

1. Create a new Google Sheet (name it e.g. `GeoTrack DB`).
2. **Extensions → Apps Script**. Delete the default code and paste all of [`apps-script/Code.gs`](apps-script/Code.gs). Save.
3. **Project Settings (gear icon) → Script properties → Add script property**
   - Property: `API_SECRET`
   - Value: a long random string (e.g. generate one with `python -c "import secrets; print(secrets.token_urlsafe(32))"`). You'll reuse it in `.env`.
4. Back in the editor, choose the function **`setup`** in the dropdown and click **Run**. Approve the permission prompt
   (*Advanced → Go to project → Allow*). This creates one tab per table with header rows.
5. **Deploy → New deployment → ⚙ Select type → Web app**
   - Execute as: **Me**
   - Who has access: **Anyone** (requests are still rejected without the secret)
   - Deploy, then copy the **Web app URL** (ends in `/exec`).
6. Whenever you edit `Code.gs` later: **Deploy → Manage deployments → ✏ Edit → Version: New version → Deploy** (the URL stays the same).

## 2. Run the API

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate            # Windows  (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env            # then edit .env (see below)
python -m app.seed                # creates the first Super Admin
python -m app.seed --demo         # optional: demo orgs/admins/trainees (password: Demo12345!)
uvicorn app.main:app --reload --port 8000
```

`.env` essentials: `STORE=sheets`, `APPS_SCRIPT_URL` (from step 5), `APPS_SCRIPT_SECRET` (same as `API_SECRET`),
a random `JWT_SECRET`, and your `SUPERADMIN_EMAIL` / `SUPERADMIN_PASSWORD`.

Check it: open <http://localhost:8000/api/health> (`storeReachable: true` means the sheet connection works)
and <http://localhost:8000/docs> for the interactive API docs.

No Google account handy? Use `STORE=memory` — same API, data lives in RAM and resets on restart.

## Tests

```bash
pytest
```

Runs against the in-memory store (no Google needed).

## API overview

| Area | Endpoints |
|---|---|
| Auth | `POST /api/auth/login`, `POST /api/auth/register`, `GET /api/auth/me` |
| OJT trainee | `GET /api/intern/profile`, `GET/POST /api/intern/attendance`, `GET /api/intern/failed-attempts`, `GET/POST /api/intern/daily-logs`, `GET /api/intern/evaluations`, `GET /api/intern/notifications`, `POST /api/intern/notifications/read` |
| Admin (own org only) | `GET /api/admin/dashboard`, `interns`, `interns/{id}`, `attendance`, `failed-attempts`, `daily-logs` (+ `POST daily-logs/{id}/review`), `evaluations` (+ create / `release`), `locations` CRUD, `reports/summary` |
| Super Admin | `GET /api/super-admin/overview`, `applications` (+ `approve` / `deploy` / `reject`), `organizations`, `admins`, `audit-logs`, `reports/summary` |

Attendance: the client sends `locationId`, `latitude`, `longitude` and the biometric `method`; the **server** decides Time In vs
Time Out, validates the geofence (Haversine), flags Late (after `LATE_AFTER`), and adds the real hours worked on Time Out.

## Notes / limits

- Google Sheets is fine for a capstone/pilot (hundreds of trainees), but every Apps Script call takes ~1-3 s. To keep the app fast the
  API keeps all tables **in memory** (loaded in parallel at startup): reads are instant, and writes appear in the app immediately and are
  saved to the sheet by a background worker (inserts are merged into one call; failed saves are retried 3 times). Manual edits made
  directly in the spreadsheet are picked up every `SHEETS_REFRESH_SECONDS` (default 60). `GET /api/health` shows `pendingWrites`
  and `failedWrites`. Trade-offs: run **one** API process (it owns the data), and stop it normally (Ctrl+C) so pending writes are
  flushed; a hard kill can lose writes that were still waiting. Expect Apps Script quotas (~20k calls/day on free accounts).
- The device biometric (fingerprint/Face ID via WebAuthn) never leaves the phone; the API only records which `method` was used.
  This is a convenience check, not tamper-proof — a hardened version would verify WebAuthn assertions server-side.
- Passwords are bcrypt-hashed in the `users` tab. Treat the spreadsheet itself as sensitive: share it with nobody you wouldn't
  trust with trainee data.
- `apps-script/Code.gs` and `app/schema.py` must keep the same tables/columns. If you add a column, change both and re-run `setup`.
