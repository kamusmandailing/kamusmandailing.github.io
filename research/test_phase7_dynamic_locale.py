#!/usr/bin/env python3
"""Stage 7: test dynamic UI language changes without altering lexical records."""
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
html=(ROOT/"index.html").read_text(encoding="utf-8")
src=(ROOT/"src/language-selector.js").read_text(encoding="utf-8")
assert src in html, "Locale module must be compiled in public HTML."
assert 'document.addEventListener("kamus:locale"' in (ROOT/"src/app.js").read_text(encoding="utf-8")
assert "bankUi('bankPage'" in (ROOT/"src/inventory.js").read_text(encoding="utf-8")
node=shutil.which("node")
subprocess.run([node,"--check"],input=src,check=True,text=True)
chrome=next((shutil.which(x) for x in ("google-chrome","chromium","chromium-browser") if shutil.which(x)),None)
assert chrome,"Chromium required"

smoke=r"""
<script>
document.addEventListener('DOMContentLoaded',()=>{
  const errors=[], assert=(ok,k)=>{if(!ok) errors.push(k)};
  const $=id=>document.getElementById(id);
  const locale=$('interface-language');
  const set=code=>{locale.value=code;locale.dispatchEvent(new Event('change',{bubbles:true}));};
  const nav=id=>document.querySelector('.sidebar [data-nav="'+id+'"]').click();

  set('en');
  assert($('results-title').textContent==='All vocabulary','dynamic-results-title-en');
  assert($('result-count').textContent.includes('words available to explore'),'dynamic-count-en');
  assert($('pagination').textContent.includes('Showing ') && $('pagination').textContent.includes(' of '),'dynamic-pagination-en');
  $('search').value='zzzyyxxthiswillnotmatch';
  $('search').dispatchEvent(new Event('input',{bubbles:true}));
  assert($('result-count').textContent.includes('matching words'),'dynamic-query-en');
  assert($('word-results').textContent.includes('No matching words.'),'empty-en');
  $('search-clear').click();
  assert($('results-title').textContent==='All vocabulary','clear-after-locale-en');
  nav('inventory');
  assert($('bank-count').textContent.includes('matching forms'),'bank-count-en');
  assert($('bank-pagination').textContent.includes('Page 1 of '),'bank-pagination-en');
  assert($('bank-pagination').textContent.includes('Previous'),'bank-prev-en');
  nav('learn');
  assert($('flashcard-area').textContent.includes('Card 1 of '),'flash-card-progress-en');
  assert($('flashcard-area').textContent.includes('What is its meaning'),'flash-card-prompt-en');
  assert($('flashcard-area').textContent.includes('Show answer'),'flash-card-button-en');
  $('reveal-answer').click();
  assert($('flashcard-area').textContent.includes('Review later'),'flash-card-review-en');
  assert($('flashcard-area').textContent.includes('I understand'),'flash-card-understood-en');

  set('ms');
  assert($('flashcard-area').textContent.includes('Kad 1 daripada'),'flash-card-progress-ms');
  assert($('flashcard-area').textContent.includes('Ulang kemudian'),'flash-card-review-ms');
  nav('inventory');
  assert($('bank-count').textContent.includes('bentuk sepadan'),'bank-count-ms');
  assert($('bank-pagination').textContent.includes('Halaman 1 daripada'),'bank-pagination-ms');
  nav('dictionary');
  assert($('results-title').textContent==='Semua kosa kata','dynamic-title-ms');
  assert($('pagination').textContent.includes('Memaparkan'),'pagination-ms');

  set('md');
  assert($('results-title').textContent==='Semua kosakata','md-fallback-indonesian-title');
  assert($('interface-language-note').textContent.includes('belum')||$('interface-language-note').textContent.includes('sampai ditelaah'),'md-fallback-banner');
  assert(document.documentElement.lang==='id','document-lang-must-match-untranslated-majority');
  set('id');
  assert($('results-title').textContent==='Semua kosakata','indonesian-restored');
  assert($('pagination').textContent.includes('Menampilkan'),'pagination-id');
  assert(document.documentElement.scrollWidth<=window.innerWidth+2,'horizontal-overflow');

  const choice=$('choose-word-modal'),trigger=$('add-word-top');
  trigger.focus();trigger.click();
  assert(choice.open,'dialog-open');
  assert(choice.contains(document.activeElement),'dialog-initial-focus');
  choice.close();
  // Browser's native <dialog> should restore focus for ordinary activation.
  assert(document.activeElement===trigger,'dialog-focus-restored');

  document.documentElement.dataset.phase7=errors.length?'FAIL-'+errors.join(','):'PASS';
});
</script>
"""
with tempfile.TemporaryDirectory(prefix="kamus-phase7-") as root:
    p=Path(root)/"test.html"
    assert html.count("</body>")==1
    p.write_text(html.replace("</body>",smoke+"</body>"),encoding="utf-8")
    for viewport in ("1280,900","390,844","360,760"):
        result=subprocess.run([chrome,"--headless=new","--no-sandbox","--disable-gpu",
          "--disable-dev-shm-usage","--window-size="+viewport,
          "--user-data-dir="+str(Path(root)/("state-"+viewport.replace(",","-"))),
          "--virtual-time-budget=3500","--dump-dom",p.as_uri()],
          capture_output=True,text=True,timeout=90)
        marker=re.search(r'data-phase7="([^"]+)"',result.stdout)
        verdict=marker.group(1) if marker else "NO-RESULT"
        print("Chrome",viewport,verdict,flush=True)
        if result.returncode or verdict!="PASS":
            print(result.stderr[-1100:],flush=True)
            raise AssertionError("Stage 7 failed: "+verdict)
print("Stage 7 dynamic UI and focus smoke: PASS",flush=True)
