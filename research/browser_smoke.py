#!/usr/bin/env python3
"""Dependency-free headless Chrome smoke test for the generated Kamus Mandailing site."""
from pathlib import Path
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
chrome = next((shutil.which(name) for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser") if shutil.which(name)), None)
if not chrome:
    sys.exit("Browser smoke test unavailable: Chrome/Chromium not found; do not approve release.")
site = (ROOT / "index.html").read_text(encoding="utf-8")
assert site.lower().endswith("</html>\n") or site.lower().rstrip().endswith("</html>")
assert "id=\"interface-language-note\"" in site, "Missing Mandailing fallback notice"
script = r"""
<script>
(function(){
  const failures = [];
  const check = (value, label) => {if (!value) failures.push(label)};
  window.addEventListener('error', event => failures.push('script-error'));
  document.addEventListener('DOMContentLoaded', () => {
    try {
      const select = document.getElementById('interface-language');
      check(!!select, 'selector-missing');
      check(!!window.KamusLocale, 'locale-api-missing');
      check(select && select.options.length === 4, 'four-languages-missing');
      const nav = key => document.querySelector('[data-nav="' + key + '"] [data-i18n]')?.textContent || '';
      function choose(lang) {
        if (!select) return;
        select.value = lang;
        select.dispatchEvent(new Event('change', {bubbles:true}));
      }
      choose('en');
      check(nav('dictionary') === 'Dictionary', 'english-label');
      check(document.documentElement.lang === 'en', 'english-lang');
      choose('ms');
      check(nav('inventory') === 'Bank kosa kata', 'malay-label');
      choose('md');
      check(document.getElementById('interface-language-note')?.hidden === false, 'mandailing-warning');
      check(document.documentElement.lang === 'id', 'mandailing-fallback-lang');
      choose('id');
      check(nav('dictionary') === 'Kamus', 'indonesian-restored');
      check(document.getElementById('interface-language-note')?.hidden === true, 'warning-hidden');
      const bank = JSON.parse(document.getElementById('inventory-data').textContent);
      const seed = JSON.parse(document.getElementById('seed-data').textContent);
      check(bank.forms.length === 10821, 'bank-count');
      check(seed.length === 1404, 'curated-count');
      const input = document.getElementById('search');
      check(!!input, 'search-missing');
      if (input) {
        input.value = 'amak';
        input.dispatchEvent(new Event('input', {bubbles:true}));
      }
      setTimeout(() => {
        try {
          const result = document.getElementById('word-results')?.textContent || '';
          check(result.toLowerCase().includes('amak'), 'search-result-missing');
          document.documentElement.setAttribute('data-browser-smoke', failures.length ? 'FAIL-' + failures.join('-') : 'PASS');
        } catch(e) {
          document.documentElement.setAttribute('data-browser-smoke', 'FAIL-result-error');
        }
      }, 1200);
    } catch(e) {
      document.documentElement.setAttribute('data-browser-smoke','FAIL-test-exception');
    }
  });
})();
</script>
"""
if site.count("</body>") != 1:
    sys.exit("Unexpected HTML body closing count: cannot create smoke test")
with tempfile.TemporaryDirectory(prefix="mandailing-browser-") as temp:
    base = Path(temp)
    fixture = base / "index.html"
    fixture.write_text(site.replace("</body>", script + "\n</body>"), encoding="utf-8")
    cmd = [
        chrome, "--headless=new", "--no-sandbox", "--disable-gpu",
        "--disable-dev-shm-usage", "--no-first-run", "--no-default-browser-check",
        "--disable-background-networking", "--user-data-dir=" + str(base / "profile"),
        "--virtual-time-budget=12000", "--dump-dom", fixture.as_uri()
    ]
    run = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    marker = re.search(r'data-browser-smoke="([^"]+)"', run.stdout)
    result = marker.group(1) if marker else "MISSING-RESULT"
    print("Chrome browser smoke:", result)
    print("Browser:", chrome)
    if result != "PASS":
        print("Chrome return code:", run.returncode)
        print("Diagnostic stderr:", run.stderr[-2500:])
        sys.exit(1)
    if run.returncode:
        print("Chrome returned nonzero code:", run.returncode)
        sys.exit(run.returncode)
