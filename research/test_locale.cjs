'use strict';
/* Regression tests for the phase-one locale selector; no browser packages needed. */
const fs = require('node:fs');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'src/index.html'), 'utf8');
const source = fs.readFileSync(path.join(root, 'src/language-selector.js'), 'utf8');

function element(attributes = {}, content = '') {
  return {
    attributes: { ...attributes }, textContent: content,
    hidden: false, value: '', children: [], listeners: {},
    getAttribute(key) { return this.attributes[key] ?? null; },
    setAttribute(key, value) { this.attributes[key] = value; },
    append(...nodes) { this.children.push(...nodes); },
    appendChild(node) { this.children.push(node); },
    prepend(node) { this.children.unshift(node); },
    addEventListener(event, callback) { this.listeners[event] = callback; }
  };
}
const nodes = [...html.matchAll(/<[^>]+data-i18n="([^"]+)"[^>]*>([^<]*)/g)]
  .map(match => element({ 'data-i18n': match[1] }, match[2]));
const placeholders = [...html.matchAll(/<input[^>]+data-i18n-placeholder="([^"]+)"[^>]*placeholder="([^"]*)"/g)]
  .map(match => element({ 'data-i18n-placeholder': match[1], placeholder: match[2] }));
assert(nodes.length >= 40, 'Not enough static labels marked for translation');
assert.equal(new Set(nodes.map(node => node.getAttribute('data-i18n'))).size, nodes.length,
  'Duplicate translation keys in HTML');

const originals = new Map(nodes.map(node => [node.getAttribute('data-i18n'), node.textContent]));
const initialPlaceholders = new Map(placeholders.map(node => [node.getAttribute('data-i18n-placeholder'), node.getAttribute('placeholder')]));
const host = element(), note = element(), rootElement = element();
const control = element();
const memory = new Map([['kamus-interface-language', 'en']]);
const document = {
  readyState: 'complete',
  documentElement: rootElement,
  querySelectorAll(selector) {
    return selector === '[data-i18n]' ? nodes :
      selector === '[data-i18n-placeholder]' ? placeholders : [];
  },
  querySelector(selector) { return selector === '.topbar-actions' ? host : null; },
  getElementById(id) { return id === 'interface-language-note' ? note : id === 'interface-language' ? control : null; },
  createElement: () => element()
};
const localStorage = {
  getItem: key => memory.get(key) || null,
  setItem: (key, value) => memory.set(key, value)
};
const window = {};
vm.runInNewContext(source, { document, localStorage, window });
const locale = window.KamusLocale;
assert(locale, 'Missing public localization interface');
const keys = [...originals.keys(), ...initialPlaceholders.keys()];
for (const lang of ['en', 'ms']) {
  for (const key of keys) {
    assert(typeof locale.messages[lang][key] === 'string' && locale.messages[lang][key].length,
      'Missing ' + lang + ' translation for ' + key);
  }
}
assert.equal(locale.currentLanguage(), 'en', 'Stored language should be used at load');
assert.equal(rootElement.getAttribute('lang'), 'en');
assert.equal(nodes.find(n => n.getAttribute('data-i18n') === 'navDictionary').textContent, 'Dictionary');
assert.equal(placeholders.find(p => p.getAttribute('data-i18n-placeholder') === 'searchPlaceholder').getAttribute('placeholder'), locale.messages.en.searchPlaceholder);
assert.equal(note.hidden, true, 'English does not use Mandailing fallback');

locale.applyLanguage('ms');
assert.equal(rootElement.getAttribute('lang'), 'ms');
assert.equal(memory.get('kamus-interface-language'), 'ms');
assert.equal(nodes.find(n => n.getAttribute('data-i18n') === 'navInventory').textContent, 'Bank kosa kata');

locale.applyLanguage('md');
assert.equal(rootElement.getAttribute('lang'), 'id', 'Unreviewed Mandailing UI must be declared Indonesian');
assert.equal(rootElement.getAttribute('data-ui-language'), 'md');
assert.equal(note.hidden, false, 'Mandailing fallback notice must be visible');
for (const node of nodes) {
  assert.equal(node.textContent, originals.get(node.getAttribute('data-i18n')),
    'Mandailing fallback must restore exact Indonesian text');
}
for (const input of placeholders) {
  assert.equal(input.getAttribute('placeholder'), initialPlaceholders.get(input.getAttribute('data-i18n-placeholder')));
}

locale.applyLanguage('id');
assert.equal(note.hidden, true);
assert.equal(rootElement.getAttribute('lang'), 'id');
locale.applyLanguage('bogus');
assert.equal(locale.currentLanguage(), 'id', 'Unknown language must default to Indonesian');
assert.equal(memory.get('kamus-interface-language'), 'id');

// Built-in static fallback must not mutate the embedded dictionary data.
assert(!source.includes("seed-data") && !source.includes('inventory-data') &&
       !source.includes('words.json'), 'Locale script may not rewrite lexicographic data');
console.log(JSON.stringify({ passed: true, labeledNodes: nodes.length, placeholderNodes: placeholders.length, languages: ['id', 'md (Indonesian fallback)', 'ms', 'en'] }));
