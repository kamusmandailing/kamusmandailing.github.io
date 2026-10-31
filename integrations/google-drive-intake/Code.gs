/**
 * Kamus Mandailing — administratively controlled Google Drive intake.
 * Deploy as a Google Apps Script web app (execute as owner, access: anyone).
 * DO NOT store OAuth tokens, email addresses, or Drive folder IDs in public HTML.
 * Owner must configure Script Property KAMUS_INTAKE_FOLDER_ID and run setupOnce().
 */
const HEADERS = [
  'id', 'tanggal_utc', 'status', 'jenis', 'kata', 'makna',
  'wilayah', 'padanan', 'contoh', 'sumber', 'persetujuan',
  'asal', 'catatan_editor'
];
const ALLOWED_TYPES = [
  'Kosakata atau padanan baru', 'Koreksi arti atau ejaan',
  'Variasi dialek atau pengucapan', 'Contoh kalimat',
  'Istilah budaya', 'Rujukan atau sumber tertulis'
];
const SCRIPT_FOLDER_KEY = 'KAMUS_INTAKE_FOLDER_ID';
const SCRIPT_SHEET_KEY = 'KAMUS_INTAKE_SHEET_ID';

function setupOnce() {
  const props = PropertiesService.getScriptProperties();
  const folderId = props.getProperty(SCRIPT_FOLDER_KEY);
  if (!folderId) {
    throw new Error('Atur Script Property KAMUS_INTAKE_FOLDER_ID terlebih dahulu.');
  }
  // Only an authorized account may run the setup and access the destination.
  const folder = DriveApp.getFolderById(folderId);
  let id = props.getProperty(SCRIPT_SHEET_KEY);
  let book;
  if (id) {
    book = SpreadsheetApp.openById(id);
  } else {
    book = SpreadsheetApp.create('Kamus Mandailing — Antrean Usulan Kontributor');
    DriveApp.getFileById(book.getId()).moveTo(folder);
    id = book.getId();
    props.setProperty(SCRIPT_SHEET_KEY, id);
  }
  let sheet = book.getSheetByName('Masuk');
  if (!sheet) {
    sheet = book.getSheets()[0];
    sheet.setName('Masuk');
  }
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(HEADERS);
    sheet.setFrozenRows(1);
    sheet.getRange(1, 1, 1, HEADERS.length)
      .setFontWeight('bold').setBackground('#642b36').setFontColor('#ffffff');
  } else {
    const current = sheet.getRange(1, 1, 1, HEADERS.length).getValues()[0];
    if (current.join('|') !== HEADERS.join('|')) {
      throw new Error('Header sheet berbeda dari versi kode. Jangan menimpa data.');
    }
  }
  Logger.log('Sheet antrean (hanya admin): ' + book.getUrl());
  return book.getUrl();
}

function clean(value, maxLength) {
  const s = String(value === undefined || value === null ? '' : value);
  const trimmed = s.replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, '').trim();
  if (trimmed.length > maxLength) throw new Error('Isian melebihi batas panjang.');
  // Never execute spreadsheet formulas supplied by contributors.
  return /^[=+\-@]/.test(trimmed) ? "'" + trimmed : trimmed;
}
function checkConsent(p) {
  if (p.consent !== 'yes') throw new Error('Persetujuan publikasi wajib diberikan.');
  if (p.hpt) throw new Error('Usulan tidak dapat diproses.');
}
function receipt(message, success) {
  const title = success ? 'Usulan diterima untuk ditelaah' : 'Usulan belum tersimpan';
  const html = '<!doctype html><html lang="id"><meta charset="utf-8">' +
    '<meta name="viewport" content="width=device-width,initial-scale=1">' +
    '<title>' + title + '</title>' +
    '<style>body{font:16px/1.6 system-ui,sans-serif;max-width:620px;margin:10vh auto;' +
    'padding:0 20px;color:#2b2828}h1{color:#642b36}a{color:#642b36}</style>' +
    '<h1>' + title + '</h1><p>' + message + '</p>' +
    '<p>Data belum dipublikasikan ke Kamus Mandailing. Hanya editor berizin yang dapat meninjaunya.</p>' +
    '<p><a href="https://kamusmandailing.github.io/kontributor.html">Kembali ke halaman Kontributor</a></p></html>';
  return HtmlService.createHtmlOutput(html).setTitle(title);
}
function doGet() {
  return receipt('Penerima usulan aktif. Pengiriman dilakukan melalui formulir Kamus Mandailing.', true);
}
function doPost(e) {
  const p = e && e.parameter || {};
  try {
    if (p.hpt) return receipt('Usulan tidak dapat diproses.', false);
    const props = PropertiesService.getScriptProperties();
    const id = props.getProperty(SCRIPT_SHEET_KEY);
    if (!id) throw new Error('Sistem penerimaan belum dikonfigurasi.');
    checkConsent(p);
    const type = clean(p.jenis, 90);
    const word = clean(p.kata, 100);
    const meaning = clean(p.makna, 500);
    if (!ALLOWED_TYPES.includes(type) || !word || meaning.length < 3) {
      throw new Error('Jenis, kata, atau makna tidak lengkap.');
    }
    const row = [
      Utilities.getUuid(), new Date().toISOString(), 'MENUNGGU TELAAH',
      type, word, meaning, clean(p.wilayah, 120),
      clean(p.padanan, 250), clean(p.contoh, 500),
      clean(p.sumber, 500), 'YA', 'halaman-kontributor', ''
    ];
    const lock = LockService.getScriptLock();
    if (!lock.tryLock(10000)) throw new Error('Sedang banyak usulan. Silakan ulangi.');
    try {
      // Global cap limits accidental floods; it is NOT a replacement for CAPTCHA.
      const cache = CacheService.getScriptCache();
      const minute = Utilities.formatDate(new Date(), 'GMT', 'yyyyMMddHHmm');
      const key = 'submissions-' + minute;
      const current = Number(cache.get(key) || 0);
      if (current >= 15) throw new Error('Batas pengiriman sementara tercapai. Coba lagi nanti.');
      const book = SpreadsheetApp.openById(id);
      const sheet = book.getSheetByName('Masuk');
      if (!sheet) throw new Error('Tab Masuk belum tersedia.');
      const header = sheet.getRange(1, 1, 1, HEADERS.length).getValues()[0].join('|');
      if (header !== HEADERS.join('|')) throw new Error('Konfigurasi antrean berubah.');
      sheet.appendRow(row);
      cache.put(key, String(current + 1), 120);
    } finally {
      lock.releaseLock();
    }
    return receipt('Terima kasih. Usulan telah disimpan ke antrean privat di Google Drive dan menunggu pemeriksaan editor.', true);
  } catch (err) {
    console.error('Kamus Mandailing intake: ' + String(err));
    return receipt('Pengiriman tidak berhasil. Periksa isian, lalu coba kembali atau gunakan usulan GitHub. Jika masalah berulang, hubungi pengelola.', false);
  }
}
