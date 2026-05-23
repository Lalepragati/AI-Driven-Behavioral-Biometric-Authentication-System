# Google Sheets Schema

Module 1 uses Google Sheets as the operational log surface. Password hashes remain local only and are never written to Sheets.

## Sheets

### Users

Columns:
- user_id
- role
- full_name
- email
- created_at
- active

### Authentication Logs

Columns:
- user_id
- session_id
- decision
- risk_score
- anomaly_confidence
- model_kind
# Google Sheets Schema

Module 1 uses the provided workbook as the operational log surface. Password hashes remain local only and are never written to Sheets.

Workbook URL:

- https://docs.google.com/spreadsheets/d/19OK7N-XH_PDRZZLSl5PojkQwbKITWzbozCed6bCzuy8/edit?usp=sharing

## Sheets

### Users

Columns:
- user_id
- name
- email
- role
- created_at
- status

### AI Agent Actions

Columns:
- agent_name
- timestamp
- action
- target_user
- result

### Security Alerts

Columns:
- alert_id
- timestamp
- severity
- message
- status

### Authentication Logs

Columns:
- timestamp
- user_id
- login_status
- ip_address
- device
- session_id

### Session Analytics

Columns:
- session_id
- user_id
- avg_dwell_time
- typing_speed
- consistency_score

### Risk Events

Columns:
- timestamp
- user_id
- risk_score
- anomaly_score
- decision
- reason

## Notes

- Use a service account when Google Sheets is enabled.
- Keep `GOOGLE_SHEETS_SPREADSHEET_ID` pointed at the shared workbook.
- When offline or unconfigured, the platform spools rows locally as JSONL files under `backend/data/sheets_spool/`.
