#!/usr/bin/env python3
"""Stage 6 browser regression: partial locale coverage, truthful fallback, search clear, mobile.
Only tests existing public lexicon; never alters curated dictionary entries.
"""
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
html=(ROOT/"index.html").read_text(encoding="utf-8")
source=(ROOT/"src/index.html").read_text(encoding="utf-8")
selector=(ROOT/"src/language-selector.js").read_text(encoding="utf-8")
assert '<button type="button" id="search-clear"' in source
assert '<button type="button" id="bank-search-clear"' in source
assert "const choices={id:" in selector
assert "document.documentElement.lang='id'" in selector
assert "releaseSnapshot" in html
assert "10.821" in html or "10821" in html
assert selector in html, "Built HTML must contain the exact locale implementation"

node=shutil.which("node")
assert node
subprocess.run([node,"--check"],input=selector,text=True,check=True)
print("Locale selector syntax and release snapshot presence: PASS",flush=True)
chrome=next((shutil.which(x) for x in ("google-chrome","chromium","chromium-browser") if shutil.which(x)),None)
assert chrome, "Chromium needed for browser smoke test"

smoke=r"""
<script>
document.addEventListener('DOMContentLoaded',function(){
  const faults=[];
  const check=(test,name)=>{if(!test)faults.push(name)};
  const $=(id)=>document.getElementById(id);
  const select=$('interface-language');
  check(!!select,'missing-locale-control');
  check(!!$('search-clear') && !!$('bank-search-clear'),'missing-search-clear');
  if(!select){document.documentElement.dataset.phase6='FAIL-MISSING-CONTROL';return;}
  const setLang=(code)=>{
    select.value=code;
    select.dispatchEvent(new Event('change',{bubbles:true}));
  };
  setLang('en');
  check(document.querySelector('[data-nav="dictionary"] > span:nth-child(2)').textContent==='Dictionary','english-navigation');
  check($('search-clear').textContent==='Clear','english-clear');
  check($('search').placeholder.includes('Search a word'),'english-placeholder');
  check(!$('interface-language-note').hidden,'missing-english-limits');
  check(document.documentElement.lang==='id','wrong-document-language');
  check($('search').getAttribute('aria-label')==='Search vocabulary','english-accessible-search');
  setLang('ms');
  check($('search-clear').textContent==='Padam','malay-clear');
  check($('interface-language-note').textContent.includes('separa'),'malay-coverage-disclaimer');
  setLang('md');
  check($('search-clear').textContent==='Hapus','mandailing-unverified-fallback');
  check($('interface-language-note').textContent.includes('belum') || $('interface-language-note').textContent.includes('sampai ditelaah'),'mandailing-disclaimer');
  check(document.documentElement.dataset.interfaceLanguage==='md','mandailing-choice-not-retained');
  check(document.documentElement.lang==='id','mandailing-incorrect-lang');
  setLang('id');
  check($('interface-language-note').hidden,'indonesian-note-not-hidden');
  check($('results-title').textContent==='Semua kosakata','indonesian-restored');

  // Search clear must preserve the user's chosen filters while clearing only query.
  const main=$('search');main.value='zzzyyxxunknownword';
  main.dispatchEvent(new Event('input',{bubbles:true}));
  check($('result-count').textContent.includes('0') || $('word-results').textContent.includes('tidak'),'dictionary-missing-result');
  $('search-clear').click();
  check(main.value===''&&document.activeElement===main,'dictionary-clear-and-focus');
  check(!$('result-count').textContent.startsWith('0 '),'dictionary-count-not-reset');

  // Bank has its own view; navigate there before asserting programmatic focus.
  document.querySelector('.sidebar [data-nav="inventory"]').click();
  check(!document.querySelector('[data-view="inventory"]').hidden,'bank-view-not-open');
  const bank=$('bank-search');bank.value='zzzyyxxunknownword';
  bank.dispatchEvent(new Event('input',{bubbles:true}));
  check($('bank-count').textContent.startsWith('0 '),'bank-no-match-result');
  $('bank-search-clear').click();
  check(bank.value===''&&document.activeElement===bank,'bank-clear-and-focus');
  check($('bank-count').textContent.includes('10.821'),'bank-original-count');

  check(document.documentElement.scrollWidth<=window.innerWidth+2,'mobile-horizontal-overflow');
  document.documentElement.dataset.phase6=faults.length?'FAIL-'+faults.join(','):'PASS';
});
</script>
"""
with tempfile.TemporaryDirectory(prefix="mandailing-phase6-") as temp:
  testpage=Path(temp)/"phase6.html"
  testpage.write_text(html.replace("</body>",smoke+"</body>"),encoding="utf-8")
  for size in ("1280,900","390,844","360,760"):
    cmd=[chrome,"--headless=new","--no-sandbox","--disable-gpu","--disable-dev-shm-usage",
      "--user-data-dir="+str(Path(temp)/("chrome-"+size.replace(",","-"))),
      "--window-size="+size,"--virtual-time-budget=3000","--dump-dom",testpage.as_uri()]
    out=subprocess.run(cmd,timeout=90,capture_output=True,text=True)
    match=re.search(r'data-phase6="([^"]+)"',out.stdout)
    result=match.group(1) if match else "MISSING-TEST-RESULT"
    print(f"Chrome {size} -> {result}",flush=True)
    if out.returncode or result!="PASS":
      print(out.stderr[-1300:])
      raise AssertionError("Stage 6 UI regression failed: "+result)
print("Phase 6 locale and search accessibility regression: PASS")
