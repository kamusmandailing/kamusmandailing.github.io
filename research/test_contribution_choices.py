#!/usr/bin/env python3
"""Check the two word-entry paths, moderation boundary and responsive DOM behavior."""
from html.parser import HTMLParser
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / "src/index.html").read_text(encoding="utf-8")
app = (ROOT / "src/app.js").read_text(encoding="utf-8")
css = (ROOT / "src/styles.css").read_text(encoding="utf-8")
published = (ROOT / "index.html").read_text(encoding="utf-8")

class Inspect(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids=[]
        self.links=[]
        self.buttons=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get("id"): self.ids.append(a["id"])
        if tag=="a": self.links.append((a.get("href"),a.get("class")))
        if tag=="button": self.buttons.append(a)
scan=Inspect()
scan.feed(source)
assert len(scan.ids)==len(set(scan.ids)), "Duplicate DOM IDs"
required={"add-word-top","add-word-private","choose-word-modal","choice-word-private",
          "edit-modal","word-form","contribution-choices-title"}
assert required<=set(scan.ids), f"Missing controls: {required-set(scan.ids)}"
assert source.count('href="./kontributor.html"')>=3, "Community route missing"
assert "Tambah Kata Pribadi" in source and "Usulkan Kata ke Kamus Mandailing" in source
assert "localStorage.setItem" in app and "local.custom.push" in app
assert "function openChoice()" in app and 'button.id==="add-word-top"){openChoice()' in app
assert 'button.id==="choice-word-private"' in app
assert "contribution-choices-grid" in css and "choice-modal-grid" in css
assert "Tambah Kata Pribadi" in published and "choice-word-private" in published
assert "Usulkan Kata ke Kamus Mandailing" in published
assert "kontributor.html" in published
assert "Kata disimpan di peramban perangkat ini" in source
assert not re.search(r'https?://(?:script\.google\.com|docs\.google\.com)',source), "Homepage should not directly submit to privileged Google services"
print("HTML routes, personal/local storage and moderation boundaries: PASS",flush=True)

node=shutil.which("node")
assert node
subprocess.run([node,"--check"],input=app,text=True,check=True)
print("Main app JavaScript syntax: PASS",flush=True)
chrome=next((shutil.which(n) for n in ("google-chrome","chromium","chromium-browser") if shutil.which(n)),None)
assert chrome, "Chromium required"

testjs=r"""
<script>
document.addEventListener('DOMContentLoaded', () => {
 const failures=[];
 const check=(ok,name)=>{if(!ok)failures.push(name)};
 const main=document.getElementById('add-word-top');
 const chooser=document.getElementById('choose-word-modal');
 const edit=document.getElementById('edit-modal');
 check(!!main && !!chooser && !!edit,'missing-controls');
 check(!chooser.open && !edit.open,'modal-unexpectedly-open');
 main.click();
 check(chooser.open,'chooser-failed-to-open');
 check(!edit.open,'private-modal-opened-before-choice');
 const link=chooser.querySelector('a[href="./kontributor.html"]');
 check(!!link && /formulir usulan/i.test(link.textContent),'community-destination');
 document.getElementById('choice-word-private').click();
 check(!chooser.open && edit.open,'personal-choice-does-not-open-form');
 check(/Hanya untuk koleksi Anda/.test(edit.textContent),'missing-personal-notice');
 edit.close();
 document.getElementById('add-word-private').click();
 check(edit.open,'direct-personal-button-not-working');
 const form=document.getElementById('word-form');
 const fields={md:'teskata2026',idn:'kata uji',my:'kata ujian',en:'test word'};
 for(const [name,value] of Object.entries(fields)){
  const item=form.querySelector('[name="'+name+'"]');
  if(item) item.value=value;
  else failures.push('missing-'+name);
 }
 form.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));
 let stored=null;
 try{stored=JSON.parse(localStorage.getItem('hata-mandailing-v1')||'null')}catch(e){}
 check(!!stored && Array.isArray(stored.custom),'private-storage-unavailable');
 check(!!stored && stored.custom.some(w=>w.md==='teskata2026'&&w.status==='personal'),'local-entry-not-stored');
 check(!edit.open,'form-not-closed');
 check(document.documentElement.scrollWidth<=window.innerWidth+2,'horizontal-overflow');
 document.documentElement.setAttribute('data-choices-test',failures.length?'FAIL-'+failures.join('-'):'PASS');
});
</script>
"""
assert published.count("</body>")==1
with tempfile.TemporaryDirectory(prefix="mandailing-choices-") as d:
 p=Path(d)/"index.html"
 p.write_text(published.replace("</body>",testjs+"</body>"),encoding="utf-8")
 for viewport in ["1280,900","390,844"]:
  run=subprocess.run([chrome,"--headless=new","--no-sandbox","--disable-gpu",
      "--disable-dev-shm-usage","--user-data-dir="+str(Path(d)/("chrome-"+viewport.replace(",","-"))),
      "--window-size="+viewport,"--virtual-time-budget=3500","--dump-dom",p.as_uri()],
      capture_output=True,text=True,timeout=90)
  match=re.search(r'data-choices-test="([^"]+)"',run.stdout)
  result=match.group(1) if match else "MISSING-TEST-RESULT"
  print(f"Chrome {viewport}: {result}",flush=True)
  if run.returncode!=0 or result!="PASS":
   print(run.stderr[-1400:])
   raise AssertionError("UI choice smoke test failed: "+result)
print("Two-path contributor navigation & personal storage: PASS")
