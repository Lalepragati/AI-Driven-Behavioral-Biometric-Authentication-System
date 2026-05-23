const SPREADSHEET_ID = '19OK7N-XH_PDRZZLSl5PojkQwbKITWzbozCed6bCzuy8';
const DEFAULT_API_TOKEN = 'bh-auth-2026-super-secret-7f3c9a';

const SHEETS = {
  Users: ['user_id', 'name', 'email', 'role', 'created_at', 'status'],
  'AI Agent Actions': ['agent_name', 'timestamp', 'action', 'target_user', 'result'],
  'Security Alerts': ['alert_id', 'timestamp', 'severity', 'message', 'status'],
  'Authentication Logs': ['timestamp', 'user_id', 'login_status', 'ip_address', 'device', 'session_id'],
  'Session Analytics': ['session_id', 'user_id', 'avg_dwell_time', 'typing_speed', 'consistency_score'],
  'Risk Events': ['timestamp', 'user_id', 'risk_score', 'anomaly_score', 'decision', 'reason'],
};

function doPost(e) {
  try {
    const body = JSON.parse(e.postData.contents || '{}');
    if (!isAuthorized(body.token)) {
      return jsonResponse({ ok: false, error: 'unauthorized' }, 401);
    }

    if (!body.sheet || !SHEETS[body.sheet]) {
      return jsonResponse({ ok: false, error: 'invalid_sheet' }, 400);
    }

    if (Array.isArray(body.values)) {
      appendRawRow(body.sheet, body.values);
    } else {
      const row = mapRecordToRow(body.sheet, body.record || {});
      appendRow(body.sheet, row);
    }

    return jsonResponse({ ok: true, sheet: body.sheet });
  } catch (error) {
    return jsonResponse({ ok: false, error: error.message }, 500);
  }
}

function doGet() {
  return jsonResponse({ ok: true, service: 'behavioral-auth-sheets-hook' }, 200);
}

function setupWorkbook() {
  const sheet = getSpreadsheet_();
  Object.keys(SHEETS).forEach((name) => {
    const columns = SHEETS[name];
    const tab = getOrCreateSheet(sheet, name);
    if (tab.getLastRow() === 0) {
      tab.appendRow(columns);
    }
  });
}

function appendRow(sheetName, rowValues) {
  const sheet = getSpreadsheet_();
  const tab = getOrCreateSheet(sheet, sheetName);

  if (tab.getLastRow() === 0) {
    tab.appendRow(SHEETS[sheetName]);
  }

  tab.appendRow(rowValues);
}

function appendRawRow(sheetName, rowValues) {
  const sheet = getSpreadsheet_();
  const tab = getOrCreateSheet(sheet, sheetName);
  tab.appendRow(rowValues);
}

function mapRecordToRow(sheetName, record) {
  return SHEETS[sheetName].map((column) => record[column] ?? '');
}

function getOrCreateSheet(spreadsheet, sheetName) {
  let tab = spreadsheet.getSheetByName(sheetName);
  if (!tab) {
    tab = spreadsheet.insertSheet(sheetName);
  }
  return tab;
}

function getSpreadsheet_() {
  const active = SpreadsheetApp.getActiveSpreadsheet();
  if (active) {
    return active;
  }

  if (!SPREADSHEET_ID) {
    throw new Error('SPREADSHEET_ID is missing and no active spreadsheet is available');
  }

  return SpreadsheetApp.openById(SPREADSHEET_ID);
}

function isAuthorized(token) {
  return token && token === getApiToken();
}

function getApiToken() {
  return PropertiesService.getScriptProperties().getProperty('API_TOKEN') || DEFAULT_API_TOKEN;
}

function jsonResponse(payload, statusCode) {
  return ContentService
    .createTextOutput(JSON.stringify({ statusCode, ...payload }))
    .setMimeType(ContentService.MimeType.JSON);
}

function setApiToken(value) {
  PropertiesService.getScriptProperties().setProperty('API_TOKEN', value);
}

function seedExampleRows() {
  appendRow('Users', ['doctor.singh', 'Dr. Singh', 'dr.singh@hospital.test', 'doctor', new Date().toISOString(), 'active']);
  appendRow('AI Agent Actions', ['workflow-agent', new Date().toISOString(), 'sheet_initialized', 'system', 'success']);
  appendRow('Security Alerts', ['ALERT-001', new Date().toISOString(), 'low', 'Workbook initialized', 'closed']);
  appendRow('Authentication Logs', [new Date().toISOString(), 'doctor.singh', 'success', '127.0.0.1', 'desktop', 'SESSION-001']);
  appendRow('Session Analytics', ['SESSION-001', 'doctor.singh', 0.12, 48.7, 92.4]);
  appendRow('Risk Events', [new Date().toISOString(), 'doctor.singh', 12.5, 8.1, 'allow', 'Baseline session']);
}
