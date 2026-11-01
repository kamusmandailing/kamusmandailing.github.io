#!/usr/bin/env python3
"""Phase 9: canonical online/offline parity, lazy bank fetch, error fallback and responsive browser smoke."""
from __future__ import annotations
from functools import partial
from html.parser import HTMLParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import gzip,json,re,shutil,subprocess,tempfile

ROOT=Path(__file__).resolve().parents[1]
full=(ROOT/"index.html").read_text(encoding="utf-8")
lite=(ROOT/"online.html").read_text(encoding="utf-8")
bank=json.loads((ROOT/"data/bank-online.json").read_text(encoding="utf-8"))
curated=json.loads((ROOT/"src/words.json").read_text(encoding="utf-8"))
canonical=json.loads((ROOT/"src/inventory.json").read_text(encoding="utf-8"))
snapshot=json.loads((ROOT/"research/release_snapshot.json").read_text(encoding="utf-8"))
assert bank==canonical,"Public lazy bank must match canonical inventory exactly."
assert len(bank["forms"])==snapshot["counts"]["sourceForms"]==10821
assert len(curated)==snapshot["counts"]["curatedEntries"]==1404
assert sum(len(f["references"]) for f in bank["forms"])==snapshot["counts"]["referenceRecords"]==13745
assert sum(f["entryId"] is None for f in bank["forms"])==snapshot["counts"]["pendingTranslations"]==9417
assert '<script id="inventory-data"' not in lite, "Online HTML must not embed full bank."
assert 'Hata_Kamus_Mandailing.html' in lite and 'data/bank-online.json' in lite
assert 'id="inventory-data"' in full, "Offline copy must remain self-contained."
assert "Coba versi online ringan" in full

class JSONScripts(HTMLParser):
    def __init__(self): super().__init__();self.stack=[];self.json={}
    def handle_starttag(self,tag,attrs):
        if tag=="script":
            a=dict(attrs);self.stack.append(a.get("id") if a.get("type")=="application/json" else None)
    def handle_endtag(self,tag):
        if tag=="script" and self.stack:self.stack.pop()
    def handle_data(self,data):
        if self.stack and self.stack[-1]:self.json[self.stack[-1]]=json.loads(data)
page=JSONScripts();page.feed(lite)
offline=JSONScripts();offline.feed(full)
assert page.json["seed-data"]==curated==offline.json["seed-data"]
assert page.json["source-data"]==json.loads((ROOT/"src/sources.json").read_text(encoding="utf-8"))
assert page.json["release-data"]==snapshot
assert offline.json["inventory-data"]==bank
full_bytes=len(full.encode("utf-8"))
online_bytes=len(lite.encode("utf-8"))
gzip_online=len(gzip.compress(lite.encode("utf-8"),compresslevel=9,mtime=0))
assert online_bytes < full_bytes * .35, f"Online HTML not substantially lighter: {online_bytes}/{full_bytes}"
print(json.dumps({"canonicalForms":len(bank["forms"]),"curated":len(curated),
"references":snapshot["counts"]["referenceRecords"],"onlineHtmlBytes":online_bytes,
"offlineHtmlBytes":full_bytes,"onlineHtmlGzipBytes":gzip_online,
"initialHtmlReductionPercent":round(100*(1-online_bytes/full_bytes),1)},ensure_ascii=False),flush=True)

browser=next((shutil.which(x) for x in ("google-chrome","chromium","chromium-browser") if shutil.which(x)),None)
assert browser,"Chromium unavailable"
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass
server=ThreadingHTTPServer(("127.0.0.1",0),partial(Quiet,directory=str(ROOT)))
thread=Thread(target=server.serve_forever,daemon=True);thread.start()
host="http://127.0.0.1:"+str(server.server_port)
js=r"""
<script>
document.addEventListener('DOMContentLoaded',async()=>{
 const failures=[],check=(x,name)=>{if(!x)failures.push(name)};
 const $=x=>document.querySelector(x);
 const wait=async condition=>{
   for(let i=0;i<85;i++){if(condition())return true;await new Promise(r=>setTimeout(r,60));}
   return false;
 };
 try{
   check(!!window.HataOnlineAudit && !window.HataOnlineAudit.bankLoaded(),"bank-requested-on-start");
   check($("#curated-count").textContent.includes("1.404"),"curated-count");
   $("#curated-search").value="amak";
   $("#curated-search").dispatchEvent(new Event("input",{bubbles:true}));
   check($("#curated-results").textContent.toLowerCase().includes("amak"),"curated-search");
   $("#curated-reset").click();
   check($("#curated-search").value===""&&$("#curated-count").textContent.includes("1.404"),"reset-curated");
   $("#show-bank").click();
   check(await wait(()=>window.HataOnlineAudit.bankLoaded()),"fetch-bank");
   check($("#bank-count").textContent.includes("10.821"),"full-bank-count");
   check($("#bank-workspace").hidden===false,"bank-panel");
   const input=$("#bank-search");
   input.value="Piper betle";input.dispatchEvent(new Event("input",{bubbles:true}));
   check($("#bank-results").textContent.includes("simanat"),"taxon-search");
   const source=$("#bank-source");source.value="plants2019";source.dispatchEvent(new Event("change",{bubbles:true}));
   check($("#bank-results").textContent.includes("simanat"),"scoped-source-search");
   source.value="dictionary";source.dispatchEvent(new Event("change",{bubbles:true}));
   check(!$("#bank-results").textContent.includes("simanat"),"source-gloss-isolation");
   $("#bank-reset").click();
   const status=$("#bank-status");status.value="pending";status.dispatchEvent(new Event("change",{bubbles:true}));
   check($("#bank-count").textContent.includes("9.417"),"pending-count");
   status.value="reviewed";status.dispatchEvent(new Event("change",{bubbles:true}));
   check($("#bank-count").textContent.includes("1.404"),"reviewed-count");
   $("#bank-reset").click();
   const btn=$("#bank-results [data-form-id]");
   check(!!btn,"detail-button");
   if(btn){btn.click();check($("#source-dialog").open && $("#source-dialog-body").textContent.includes("rujukan"),"source-dialog");$("#source-close").click();}
   check(document.documentElement.scrollWidth<=window.innerWidth+2,"mobile-overflow");
 }catch(err){failures.push("runtime-"+err.message);}
 document.documentElement.dataset.phase9=failures.length?"FAIL-"+failures.join(","):"PASS";
});
</script>
"""
try:
 with tempfile.TemporaryDirectory(prefix="kamus-phase9-") as directory:
  # Test html files are served from repository root so relative asset paths resolve.
  test_folder=ROOT/"qa"/"phase9"
  test_folder.mkdir(parents=True,exist_ok=True)
  test_file=test_folder/"phase9-browser-check.html"
  # Use a root temporary file; its links to data/bank-online.json must resolve to root.
  test_file=ROOT/"phase9-browser-check.html"
  try:
   test_file.write_text(lite.replace("</body>",js+"</body>"),encoding="utf-8")
   for size in ("1280,900","390,844"):
    run=subprocess.run([browser,"--headless=new","--no-sandbox","--disable-gpu",
      "--disable-dev-shm-usage","--window-size="+size,
      "--user-data-dir="+str(Path(directory)/("state-"+size.replace(",","-"))),
      "--virtual-time-budget=7500","--dump-dom",host+"/phase9-browser-check.html"],
      capture_output=True,text=True,timeout=90)
    m=re.search(r'data-phase9="([^"]+)"',run.stdout)
    verdict=m.group(1) if m else "MISSING"
    print("Chrome",size,verdict,flush=True)
    if run.returncode or verdict!="PASS":
     print(run.stderr[-1200:],flush=True)
     raise AssertionError("Online browser test failed: "+verdict)
  finally:
   test_file.unlink(missing_ok=True)
finally:
 server.shutdown();server.server_close()
print("Phase 9 online/offline parity and lazy-fetch browser smoke: PASS")
