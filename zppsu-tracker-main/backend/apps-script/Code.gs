/**
 * GeoTrack — Google Sheets data layer.
 *
 * A small JSON-over-HTTP "database" that lives inside a Google Spreadsheet.
 * Only the Python API talks to it; browsers/phones never see this URL.
 *
 * SETUP (see backend/README.md for the step-by-step):
 *   1. Create a Google Sheet, then Extensions > Apps Script and paste this file.
 *   2. Put your secret in SECRET_TO_STORE below, run `setSecret` once, then blank the constant again.
 *      (Or add it by hand: Project Settings > Script properties > API_SECRET.)
 *      Run `checkSecret` to confirm it is stored (it logs only the length).
 *   3. Run the `setup` function once (creates every tab + header row).
 *   4. Deploy > New deployment > Web app
 *        Execute as: Me      Who has access: Anyone
 *      Copy the /exec URL into backend/.env as APPS_SCRIPT_URL.
 *   5. Whenever you change this file: Deploy > Manage deployments > Edit > New version.
 *
 * Column types:  s = text   n = number   b = boolean   j = JSON (stored as text)
 * Keep SCHEMA in sync with backend/app/schema.py (same tables, same column order).
 */

const SCHEMA = {
  organizations: { id: 's', name: 's', address: 's', status: 's', createdAt: 's' },
  users: { id: 's', email: 's', passwordHash: 's', role: 's', name: 's', orgId: 's', status: 's', createdAt: 's' },
  admins: { id: 's', name: 's', email: 's', orgId: 's', status: 's', lastLogin: 's' },
  programs: { id: 's', orgId: 's', name: 's', description: 's', requiredHours: 'n', status: 's' },
  locations: { id: 's', orgId: 's', name: 's', latitude: 'n', longitude: 'n', radius: 'n', status: 's' },
  interns: {
    id: 's', orgId: 's', programId: 's', name: 's', email: 's', studentId: 's', school: 's', course: 's',
    yearLevel: 's', contact: 's', address: 's', avatarColor: 's', applicationStatus: 's', requiredHours: 'n',
    renderedHours: 'n', faceStatus: 's', internshipStatus: 's', startDate: 's', endDate: 's',
  },
  attendance: {
    id: 's', internId: 's', locationId: 's', type: 's', date: 's', timestamp: 's', status: 's', distance: 'n',
    faceVerified: 'b', livenessVerified: 'b', gpsVerified: 'b', method: 's',
  },
  failed_attempts: { id: 's', internId: 's', date: 's', timestamp: 's', reason: 's', stage: 's' },
  daily_logs: {
    id: 's', internId: 's', date: 's', activities: 's', learnings: 's', challenges: 's', status: 's',
    reviewerComment: 's', reviewedAt: 's',
  },
  evaluations: {
    id: 's', internId: 's', evaluatorId: 's', evaluatorName: 's', period: 's', rating: 'n', status: 's',
    comments: 's', createdAt: 's', criteria: 'j',
  },
  audit_logs: { id: 's', user: 's', action: 's', resource: 's', result: 's', timestamp: 's' },
  notifications: { id: 's', userId: 's', title: 's', body: 's', time: 's', read: 'b', tone: 's' },
};

/* ------------------------------------------------------------------ */
/* HTTP entry points                                                   */
/* ------------------------------------------------------------------ */

function doGet() {
  // `secretConfigured` lets you check the deployment from a browser without exposing the secret.
  return json_({ ok: true, service: 'geotrack-sheets', hint: 'POST only', secretConfigured: !!getSecret_() });
}

/* ---------------------------- Secret handling ---------------------------- */

// Paste your secret here, run `setSecret` once from the editor, then replace it with '' again.
const SECRET_TO_STORE = 'PASTE_YOUR_SECRET_HERE';

function setSecret() {
  const value = String(SECRET_TO_STORE || '').trim();
  if (!value || value === 'PASTE_YOUR_SECRET_HERE') throw new Error('Put your secret in SECRET_TO_STORE first.');
  PropertiesService.getScriptProperties().setProperty('API_SECRET', value);
  console.log('API_SECRET stored. length=' + value.length + ' — now blank out SECRET_TO_STORE.');
}

function checkSecret() {
  const s = getSecret_();
  console.log(s ? 'API_SECRET is set. length=' + s.length : 'API_SECRET is NOT set.');
}

function getSecret_() {
  const s = PropertiesService.getScriptProperties().getProperty('API_SECRET');
  return s ? String(s).trim() : '';
}

function doPost(e) {
  try {
    const req = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    const secret = getSecret_();
    if (!secret || String(req.secret || '').trim() !== secret) return json_({ ok: false, error: 'unauthorized' });

    const handler = ACTIONS[req.action];
    if (!handler) return json_({ ok: false, error: 'unknown action: ' + req.action });
    if (req.table !== undefined && !SCHEMA[req.table]) return json_({ ok: false, error: 'unknown table: ' + req.table });

    const writes = ['insert', 'insert_many', 'update', 'delete', 'setup'];
    if (writes.indexOf(req.action) === -1) return json_({ ok: true, data: handler(req) });

    const lock = LockService.getScriptLock();
    lock.waitLock(20000);
    try {
      return json_({ ok: true, data: handler(req) });
    } finally {
      lock.releaseLock();
    }
  } catch (err) {
    return json_({ ok: false, error: String(err && err.message ? err.message : err) });
  }
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

/* ------------------------------------------------------------------ */
/* Actions                                                             */
/* ------------------------------------------------------------------ */

const ACTIONS = {
  ping: function () { return 'pong'; },

  setup: function () { return setup(); },

  // { table, where?: {col: value, ...} }  ->  rows[]
  list: function (r) {
    const rows = readAll_(r.table);
    const where = r.where || {};
    const keys = Object.keys(where);
    if (!keys.length) return rows;
    return rows.filter(function (row) {
      return keys.every(function (k) { return row[k] === where[k]; });
    });
  },

  // { table, id }  ->  row | null
  get: function (r) {
    const found = findRow_(r.table, r.id);
    return found ? found.row : null;
  },

  // { table, row }  ->  row
  insert: function (r) {
    return insertMany_(r.table, [r.row])[0];
  },

  // { table, rows }  ->  rows[]
  insert_many: function (r) {
    return insertMany_(r.table, r.rows || []);
  },

  // { table, id, patch }  ->  updated row | null
  update: function (r) {
    const found = findRow_(r.table, r.id);
    if (!found) return null;
    const cols = Object.keys(SCHEMA[r.table]);
    const merged = {};
    cols.forEach(function (c) {
      merged[c] = Object.prototype.hasOwnProperty.call(r.patch, c) && c !== 'id' ? r.patch[c] : found.row[c];
    });
    const sheet = sheet_(r.table);
    sheet.getRange(found.index, 1, 1, cols.length).setValues([serializeRow_(r.table, merged)]);
    return fromSheetRow_(r.table, serializeRow_(r.table, merged));
  },

  // { table, id }  ->  true | false
  delete: function (r) {
    const found = findRow_(r.table, r.id);
    if (!found) return false;
    sheet_(r.table).deleteRow(found.index);
    return true;
  },
};

/** Run this once from the editor (select `setup` > Run) to create all tabs. */
function setup() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const created = [];
  Object.keys(SCHEMA).forEach(function (table) {
    let sheet = ss.getSheetByName(table);
    const cols = Object.keys(SCHEMA[table]);
    if (!sheet) {
      sheet = ss.insertSheet(table);
      created.push(table);
    }
    sheet.getRange(1, 1, 1, cols.length).setValues([cols]).setFontWeight('bold').setBackground('#f3f3f3');
    sheet.setFrozenRows(1);
    // Plain-text columns stop Sheets from turning "2026-10-17" or "0917…" into dates/numbers.
    cols.forEach(function (c, i) {
      const type = SCHEMA[table][c];
      if (type === 's' || type === 'j') sheet.getRange(2, i + 1, Math.max(sheet.getMaxRows() - 1, 1), 1).setNumberFormat('@');
    });
  });
  const blank = ss.getSheetByName('Sheet1');
  if (blank && ss.getSheets().length > 1 && blank.getLastRow() === 0) ss.deleteSheet(blank);
  return { created: created, tables: Object.keys(SCHEMA) };
}

/* ------------------------------------------------------------------ */
/* Helpers                                                             */
/* ------------------------------------------------------------------ */

function sheet_(table) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(table);
  if (!sheet) throw new Error('Missing tab "' + table + '". Run setup() first.');
  return sheet;
}

function readAll_(table) {
  const sheet = sheet_(table);
  const last = sheet.getLastRow();
  if (last < 2) return [];
  const width = Object.keys(SCHEMA[table]).length;
  return sheet.getRange(2, 1, last - 1, width).getValues().map(function (v) { return fromSheetRow_(table, v); });
}

function findRow_(table, id) {
  const sheet = sheet_(table);
  const last = sheet.getLastRow();
  if (last < 2) return null;
  const ids = sheet.getRange(2, 1, last - 1, 1).getValues();
  for (let i = 0; i < ids.length; i++) {
    if (String(ids[i][0]) === String(id)) {
      const width = Object.keys(SCHEMA[table]).length;
      const values = sheet.getRange(i + 2, 1, 1, width).getValues()[0];
      return { index: i + 2, row: fromSheetRow_(table, values) };
    }
  }
  return null;
}

function insertMany_(table, rows) {
  if (!rows.length) return [];
  const sheet = sheet_(table);
  const values = rows.map(function (row) { return serializeRow_(table, row); });
  const start = sheet.getLastRow() + 1;
  sheet.getRange(start, 1, values.length, values[0].length).setValues(values);
  return values.map(function (v) { return fromSheetRow_(table, v); });
}

function serializeRow_(table, row) {
  const schema = SCHEMA[table];
  return Object.keys(schema).map(function (col) {
    const v = row[col];
    switch (schema[col]) {
      case 'n': return v === null || v === undefined || v === '' ? '' : Number(v);
      case 'b': return v === true || v === 'true' || v === 'TRUE';
      case 'j': return v === null || v === undefined ? '' : JSON.stringify(v);
      default: return v === null || v === undefined ? '' : String(v);
    }
  });
}

function fromSheetRow_(table, values) {
  const schema = SCHEMA[table];
  const tz = SpreadsheetApp.getActiveSpreadsheet().getSpreadsheetTimeZone();
  const out = {};
  Object.keys(schema).forEach(function (col, i) {
    let v = values[i];
    if (v instanceof Date) v = Utilities.formatDate(v, tz, 'yyyy-MM-dd HH:mm');
    switch (schema[col]) {
      case 'n': out[col] = v === '' || v === null ? null : Number(v); break;
      case 'b': out[col] = v === true || String(v).toUpperCase() === 'TRUE'; break;
      case 'j':
        try { out[col] = v === '' || v === null ? null : JSON.parse(v); } catch (err) { out[col] = null; }
        break;
      default: out[col] = v === '' || v === null ? null : String(v);
    }
  });
  return out;
}
