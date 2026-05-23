# Apps Script Setup

Use this when you want free Google Sheets logging without Google Cloud.

## Environment values

Set these in `backend/.env`:

```env
GOOGLE_APPS_SCRIPT_WEBAPP_URL=https://script.google.com/macros/s/AKfycbwaAFp0RGR1QZDiC1qyDLv1mOodudpXGIiy8A1P1rHd3OOSiHJbg0FHnzgH_ar4NdGJAQ/exec
GOOGLE_APPS_SCRIPT_TOKEN=bh-auth-2026-super-secret-7f3c9a
```

## Apps Script steps

1. Open the Apps Script project attached to your sheet.
2. Paste the contents of `docs/google-apps-script.gs`.
3. Run `setApiToken('bh-auth-2026-super-secret-7f3c9a')` once.
4. Run `setupWorkbook()` once to create the sheet tabs and headers.
5. Deploy as a Web App.
6. Set access to `Anyone with the link` if you want backend posting without Google login.

## Test payload

```json
{
  "token": "bh-auth-2026-super-secret-7f3c9a",
  "sheet": "Authentication Logs",
  "record": {
    "timestamp": "2026-05-23T10:00:00Z",
    "user_id": "doctor.singh",
    "login_status": "success",
    "ip_address": "127.0.0.1",
    "device": "desktop",
    "session_id": "SESSION-001"
  }
}
```