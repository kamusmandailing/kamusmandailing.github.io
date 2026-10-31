/* Interface localization (phase 1). Source words and lexicographic data remain unchanged. */
(function () {
  'use strict';
  const choices = Object.freeze({
    id: 'Bahasa Indonesia',
    md: 'Bahasa Mandailing (antarmuka dalam semakan)',
    ms: 'Bahasa Melayu (Malaysia)',
    en: 'English'
  });
  // The Mandailing interface has NOT been linguistically verified.
  // It intentionally falls back to the original Indonesian copy.
  const messages = Object.freeze({
    en: Object.freeze({
  "sidebarTitle": "LEARNING SPACE",
  "navDictionary": "Dictionary",
  "navInventory": "Vocabulary bank",
  "navSaved": "Saved",
  "navLearn": "Learn",
  "navSources": "Notes & sources",
  "addWord": "Add word",
  "heroKicker": "PRACTICAL MULTILINGUAL DICTIONARY",
  "heroTitle": "Find a word.",
  "heroEm": "Discover its meaning.",
  "heroDescription": "Explore Mandailing through Indonesian, Malaysian Malay, and English equivalents.",
  "featuredLink": "Explore this word",
  "bankKicker": "COMPLETE SOURCE-FORM INVENTORY",
  "bankTitle": "More documented forms.",
  "bankEm": "Trace every source.",
  "bankSearchLabel": "Search the entire vocabulary bank",
  "bankKindLabel": "Form type",
  "bankScopeLabel": "Source language label",
  "bankStatusLabel": "Translation status",
  "bankSourceLabel": "Source",
  "bankLatest": "New forms",
  "savedKicker": "PERSONAL COLLECTION",
  "savedTitle": "Words you",
  "savedEm": "want to remember.",
  "savedDescription": "Save useful words and find them again here.",
  "searchLabel": "Search vocabulary",
  "searchLanguage": "Search language",
  "allLetters": "All letters",
  "reviewFilter": "Review status",
  "allVocabulary": "All vocabulary",
  "sortLabel": "Sort vocabulary",
  "learnKicker": "ONE STEP AT A TIME",
  "learnTitle": "One card.",
  "learnEm": "One word closer.",
  "learnDescription": "Recall the meaning, reveal the answer, then mark words you understand.",
  "categoryLabel": "Category",
  "guessLanguage": "Guess the equivalent",
  "everyWord": "Every word matters.",
  "progressNotice": "Progress is saved in this browser.",
  "sourcesKicker": "LEARN WITH SOURCES",
  "sourcesTitle": "Language has context.",
  "sourcesEm": "So does this dictionary.",
  "sourcesDescription": "Explore word origins, variations, and verification limits before using an entry.",
  "exploreBank": "Explore the source bank",
  "searchPlaceholder": "Search, e.g. rumah, bagas, or house…",
  "bankSearchPlaceholder": "Form, taxon, root entry, or equivalent…"
}),
    ms: Object.freeze({
  "sidebarTitle": "RUANG PEMBELAJARAN",
  "navDictionary": "Kamus",
  "navInventory": "Bank kosa kata",
  "navSaved": "Disimpan",
  "navLearn": "Belajar",
  "navSources": "Catatan & sumber",
  "addWord": "Tambah perkataan",
  "heroKicker": "KAMUS PRAKTIKAL PELBAGAI BAHASA",
  "heroTitle": "Cari perkataan.",
  "heroEm": "Kenali maknanya.",
  "heroDescription": "Terokai bahasa Mandailing melalui padanan Indonesia, Melayu Malaysia dan Inggeris.",
  "featuredLink": "Kenali perkataan ini",
  "bankKicker": "INVENTORI BENTUK DARIPADA SUMBER",
  "bankTitle": "Lebih banyak perkataan.",
  "bankEm": "Sumbernya dapat dijejaki.",
  "bankSearchLabel": "Cari dalam seluruh bank kosa kata",
  "bankKindLabel": "Jenis bentuk",
  "bankScopeLabel": "Label bahasa sumber",
  "bankStatusLabel": "Status padanan",
  "bankSourceLabel": "Sumber bentuk",
  "bankLatest": "Bentuk baharu",
  "savedKicker": "KOLEKSI PERIBADI",
  "savedTitle": "Perkataan yang",
  "savedEm": "ingin diingati.",
  "savedDescription": "Simpan perkataan yang menarik dan temukannya semula di sini.",
  "searchLabel": "Cari kosa kata",
  "searchLanguage": "Bahasa carian",
  "allLetters": "Semua huruf",
  "reviewFilter": "Status semakan",
  "allVocabulary": "Semua kosa kata",
  "sortLabel": "Susun kosa kata",
  "learnKicker": "SEDIKIT DEMI SEDIKIT",
  "learnTitle": "Satu kad.",
  "learnEm": "Satu perkataan lebih dekat.",
  "learnDescription": "Ingat maknanya, lihat jawapan dan tandakan perkataan yang sudah difahami.",
  "categoryLabel": "Kategori",
  "guessLanguage": "Teka padanan",
  "everyWord": "Setiap perkataan bermakna.",
  "progressNotice": "Kemajuan disimpan dalam pelayar ini.",
  "sourcesKicker": "BELAJAR BERSAMA SUMBER",
  "sourcesTitle": "Bahasa ada konteksnya.",
  "sourcesEm": "Begitu juga kamus ini.",
  "sourcesDescription": "Kenali asal perkataan, variasi bentuk dan batas pengesahan sebelum menggunakannya.",
  "exploreBank": "Terokai bank sumber",
  "searchPlaceholder": "Cari, contohnya rumah, bagas atau house…",
  "bankSearchPlaceholder": "Bentuk, takson, lema induk atau padanan…"
})
  });
  const originals = new Map();
  let current = 'id';

  function rememberDefaults() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = 'text:' + el.getAttribute('data-i18n');
      if (!originals.has(key)) originals.set(key, el.textContent);
    });
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
      const key = 'placeholder:' + el.getAttribute('data-i18n-placeholder');
      if (!originals.has(key)) originals.set(key, el.getAttribute('placeholder') || '');
    });
  }

  function applyLanguage(code) {
    const lang = Object.prototype.hasOwnProperty.call(choices, code) ? code : 'id';
    const locale = messages[lang] || {};
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      const translated = locale[key];
      const value = typeof translated === 'string' ? translated : originals.get('text:' + key);
      if (typeof value === 'string' && el.textContent !== value) el.textContent = value;
    });
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
      const key = el.getAttribute('data-i18n-placeholder');
      const value = typeof locale[key] === 'string' ? locale[key] : originals.get('placeholder:' + key);
      if (typeof value === 'string') el.setAttribute('placeholder', value);
    });
    // The actual text is Indonesian for md until community review.
    document.documentElement.lang = lang === 'md' ? 'id' : lang;
    document.documentElement.setAttribute('data-ui-language', lang);
    const note = document.getElementById('interface-language-note');
    if (note) note.hidden = lang !== 'md';
    const control = document.getElementById('interface-language');
    if (control) {
      control.value = lang;
      control.setAttribute('aria-label', lang === 'en' ? 'Choose interface language' :
        lang === 'ms' ? 'Pilih bahasa antara muka' : 'Pilih bahasa antarmuka');
    }
    current = lang;
    try { localStorage.setItem('kamus-interface-language', lang); } catch (_) {}
    return lang;
  }

  function init() {
    const host = document.querySelector('.topbar-actions');
    if (!host) return;
    rememberDefaults();
    const wrap = document.createElement('label');
    wrap.className = 'interface-language-wrap';
    const helper = document.createElement('span');
    helper.className = 'sr-only';
    helper.textContent = 'Pilih bahasa antarmuka';
    const select = document.createElement('select');
    select.id = 'interface-language';
    select.className = 'interface-language-select';
    for (const [code, label] of Object.entries(choices)) {
      const option = document.createElement('option');
      option.value = code;
      option.textContent = label;
      select.appendChild(option);
    }
    wrap.append(helper, select);
    host.prepend(wrap);
    let stored = 'id';
    try { stored = localStorage.getItem('kamus-interface-language') || 'id'; } catch (_) {}
    applyLanguage(stored);
    select.addEventListener('change', () => applyLanguage(select.value));
  }

  window.KamusLocale = Object.freeze({
    messages,
    choices,
    applyLanguage,
    currentLanguage: () => current
  });
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
