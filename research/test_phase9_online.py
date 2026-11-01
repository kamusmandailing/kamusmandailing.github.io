#!/usr/bin/env python3
"""Phase 9: canonical online/offline parity, lazy bank fetch, error fallback and responsive browser smoke."""
from __future__ import annotations
from functools import partial
from html.parser import HTMLParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import gzip,json,re,shutil,subprocess,tempfile
import hashlib

ROOT=Path(__file__).resolve().parents[1]
full=(ROOT/"index.html").read_text(encoding="utf-8")
lite=(ROOT/"online.html").read_text(encoding="utf-8")
bank=json.loads((ROOT/"data/bank-online.json").read_text(encoding="utf-8"))
curated=json.loads((ROOT/"src/words.json").read_text(encoding="utf-8"))
canonical=json.loads((ROOT/"src/inventory.json").read_text(encoding="utf-8"))
manifest=json.loads((ROOT/"data/bank-online-shards/manifest.json").read_text(encoding="utf-8"))
snapshot=json.loads((ROOT/"research/release_snapshot.json").read_text(encoding="utf-8"))
assert bank==canonical,"Public lazy bank must match canonical inventory exactly."
shard_forms=[];next_start=0
for chunk in manifest["chunks"]:
    chunk_bytes=(ROOT/"data/bank-online-shards"/chunk["file"]).read_bytes()
    assert hashlib.sha256(chunk_bytes).hexdigest()==chunk["sha256"],"Bank chunk checksum mismatch."
    chunk_data=json.loads(chunk_bytes)
    assert chunk["start"]==next_start and len(chunk_data["forms"])==chunk["count"]
    assert sum(len(form["references"]) for form in chunk_data["forms"])==chunk["referenceRecords"]
    shard_forms.extend(chunk_data["forms"]);next_start+=chunk["count"]
manifest_metadata={key:value for key,value in manifest.items() if key not in ("chunks","chunkSize","filterOptions")}
assert {**manifest_metadata,"forms":shard_forms}==canonical,"Sharded data must reconstruct the canonical Bank exactly."
assert len(bank["forms"])==snapshot["counts"]["sourceForms"]==10821
assert len(curated)==snapshot["counts"]["curatedEntries"]==1404
assert sum(len(f["references"]) for f in bank["forms"])==snapshot["counts"]["referenceRecords"]==13745
assert sum(f["entryId"] is None for f in bank["forms"])==snapshot["counts"]["pendingTranslations"]==9417
expected_form_hash=hashlib.sha256("\n".join(form["form"] for form in bank["forms"]).encode("utf-8")).hexdigest()
manifest_bytes=(ROOT/"data/bank-online-shards/manifest.json").read_bytes()
first_chunk_bytes=(ROOT/"data/bank-online-shards"/manifest["chunks"][0]["file"]).read_bytes()
first_view_gzip_bytes=len(gzip.compress(manifest_bytes,compresslevel=9,mtime=0))+len(gzip.compress(first_chunk_bytes,compresslevel=9,mtime=0))
first_view_raw_bytes=len(manifest_bytes)+len(first_chunk_bytes)
assert first_view_raw_bytes<600_000 and first_view_gzip_bytes<55_000, "First Bank view exceeds the initial payload budget."
assert '<script id="inventory-data"' not in lite, "Online HTML must not embed full bank."
assert 'Hata_Kamus_Mandailing.html' in lite and 'data/bank-online-shards/manifest.json' in lite
assert 'id="inventory-data"' in full, "Offline copy must remain self-contained."
assert "Coba versi online ringan" in full

class AccessibilityMarkup(HTMLParser):
    """Small dependency-free checks for named controls and accessible landmarks."""
    def __init__(self):
        super().__init__()
        self.labels_for=set();self.label_depth=0
        self.controls=[];self.buttons=[];self.links=[];self.live_statuses=[];self.dialogs=[];self.landmarks=[]
        self._button_stack=[];self._link_stack=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="label":
            self.label_depth+=1
            if a.get("for"): self.labels_for.add(a["for"])
        if tag in ("input","select","textarea"):
            self.controls.append({"tag":tag,"attrs":a,"wrapped":self.label_depth>0})
        if tag=="button":
            item={"attrs":a,"text":""};self.buttons.append(item);self._button_stack.append(item)
        if tag=="a" and a.get("href"):
            item={"attrs":a,"text":""};self.links.append(item);self._link_stack.append(item)
        if a.get("role")=="status": self.live_statuses.append(a)
        if tag=="dialog": self.dialogs.append(a)
        if tag in ("nav","main"): self.landmarks.append((tag,a))
    def handle_endtag(self,tag):
        if tag=="label": self.label_depth=max(0,self.label_depth-1)
        if tag=="button" and self._button_stack: self._button_stack.pop()
        if tag=="a" and self._link_stack: self._link_stack.pop()
    def handle_data(self,data):
        for item in self._button_stack+self._link_stack: item["text"]+=data

a11y=AccessibilityMarkup();a11y.feed(lite)
online_js=(ROOT/"src/online.js").read_text(encoding="utf-8")
unnamed_controls=[c for c in a11y.controls if not c["wrapped"] and
    c["attrs"].get("id") not in a11y.labels_for and
    not c["attrs"].get("aria-label") and not c["attrs"].get("aria-labelledby")]
assert not unnamed_controls, f"Controls need an accessible label: {unnamed_controls}"
unnamed_buttons=[b for b in a11y.buttons if not b["text"].strip() and
    not b["attrs"].get("aria-label") and not b["attrs"].get("title")]
assert not unnamed_buttons, f"Buttons need an accessible name: {unnamed_buttons}"
unnamed_links=[a for a in a11y.links if not a["text"].strip() and
    not a["attrs"].get("aria-label") and not a["attrs"].get("title")]
assert not unnamed_links, f"Links need an accessible name: {unnamed_links}"
assert any(a.get("href")=="#main" for a in (link["attrs"] for link in a11y.links)), "Skip-to-content link missing."
assert any(tag=="nav" and a.get("aria-label") for tag,a in a11y.landmarks), "Navigation landmark needs a name."
assert any(tag=="main" for tag,_ in a11y.landmarks), "Main landmark missing."
assert len(a11y.live_statuses)>=3 and all(s.get("aria-live")=="polite" for s in a11y.live_statuses)
assert any(d.get("aria-labelledby")=="source-dialog-title" for d in a11y.dialogs)
assert 'id="source-dialog-title"' in online_js, "Dialog title needs an accessible name."
assert 'class="source-button" type="button"' in online_js, "Generated source controls must be buttons."
print(json.dumps({"accessibilityControlsNamed":len(a11y.controls),"buttonsNamed":len(a11y.buttons),
"linksNamed":len(a11y.links),"liveStatuses":len(a11y.live_statuses)},ensure_ascii=False),flush=True)

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
"initialHtmlReductionPercent":round(100*(1-online_bytes/full_bytes),1),
"bankFirstViewRawBytes":first_view_raw_bytes,"bankFirstViewGzipBytes":first_view_gzip_bytes},ensure_ascii=False),flush=True)

browser_candidates=[shutil.which(name) for name in ("google-chrome","chromium","chromium-browser")]
mac_chrome=Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
if mac_chrome.is_file(): browser_candidates.append(str(mac_chrome))
browser=next((candidate for candidate in browser_candidates if candidate),None)
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
 const exports=[];
 URL.createObjectURL=blob=>{exports.push(blob);return "blob:phase9-test-"+exports.length;};
 const hashText=async text=>[...new Uint8Array(await crypto.subtle.digest("SHA-256",new TextEncoder().encode(text)))].map(value=>value.toString(16).padStart(2,"0")).join("");
 const hashForms=async lines=>hashText(lines.slice(1).map(row=>row.split("\t")[0]).join("\n"));
 const wait=async condition=>{
   for(let i=0;i<85;i++){if(condition())return true;await new Promise(r=>setTimeout(r,60));}
   return false;
 };
 try{
   check(!!window.HataOnlineAudit && !window.HataOnlineAudit.bankLoaded(),"bank-requested-on-start");
   check(!performance.getEntriesByType("resource").some(entry=>entry.name.includes("/data/bank-online-shards/")),"no-bank-assets-before-request");
   check($("#show-curated").getAttribute("aria-pressed")==="true"&&$("#show-bank").getAttribute("aria-pressed")==="false","initial-mode-state");
   check($("#curated-count").textContent.includes("1.404"),"curated-count");
   $("#curated-search").value="amak";
   $("#curated-search").dispatchEvent(new Event("input",{bubbles:true}));
   check($("#curated-results").textContent.toLowerCase().includes("amak"),"curated-search");
   $("#curated-reset").click();
   check($("#curated-search").value===""&&$("#curated-count").textContent.includes("1.404"),"reset-curated");
   $("#curated-export").click();
   check(await wait(()=>exports.length===1),"curated-export-created");
   const curatedLines=(await exports[0].text()).split("\n");
   const expectedCurated=JSON.parse($("#seed-data").textContent).sort((a,b)=>a.md.localeCompare(b.md,"id")).map(word=>word.md).join("\n");
   check(curatedLines.length===1405&&curatedLines[0].replace(/^\uFEFF/,"").split("\t").length===5&&await hashForms(curatedLines)===await hashText(expectedCurated),"curated-export-complete");
   $("#show-bank").click();
   check($("#show-curated").getAttribute("aria-pressed")==="false"&&$("#show-bank").getAttribute("aria-pressed")==="true","selected-mode-state");
   check(await wait(()=>window.HataOnlineAudit.bankLoaded()),"fetch-bank");
   check(!window.HataOnlineAudit.bankComplete()&&window.HataOnlineAudit.loadedChunkCount()===1,"first-chunk-only");
   const firstBankAssets=performance.getEntriesByType("resource").filter(entry=>entry.name.includes("/data/bank-online-shards/"));
   const firstBankFiles=firstBankAssets.map(entry=>new URL(entry.name).pathname.split("/").pop());
   check(firstBankAssets.length===2&&firstBankFiles.includes("manifest.json")&&firstBankFiles.includes("chunk-000.json"),"first-view-fetches-only-manifest-and-first-chunk");
   check(firstBankAssets.reduce((sum,entry)=>sum+entry.encodedBodySize,0)>0&&firstBankAssets.reduce((sum,entry)=>sum+entry.encodedBodySize,0)<600000,"first-bank-view-byte-budget");
   check($("#bank-count").textContent.includes("10.821"),"full-bank-count");
   check($("#bank-workspace").hidden===false,"bank-panel");
   const number=new Intl.NumberFormat("id-ID");
   for(let page=2;page<=22;page++){
    $("#bank-pagination button:last-child").click();
    const range="Menampilkan "+number.format((page-1)*24+1)+"–"+number.format(page*24);
    check(await wait(()=>$("#bank-pagination").textContent.includes(range)),"pagination-page-"+page);
   }
   check(window.HataOnlineAudit.loadedChunkCount()===2,"pagination-loads-next-chunk");
   $("#bank-export").click();
   check(await wait(()=>window.HataOnlineAudit.bankComplete()&&exports.length===2),"five-column-export-loads-all");
   const fiveColumns=await exports[1].text(),fiveLines=fiveColumns.split("\n");
   check(fiveLines.length===10822&&fiveLines[0].replace(/^\uFEFF/,"").split("\t").length===5&&await hashForms(fiveLines)==="__EXPECTED_FORM_HASH__","five-column-export-complete");
   $("#bank-export-labels").click();
   check(await wait(()=>exports.length===3),"labeled-export-created");
   const labeled=await exports[2].text(),labeledLines=labeled.split("\n");
   check(labeledLines.length===10822&&labeledLines[0].replace(/^\uFEFF/,"").split("\t").length===9&&await hashForms(labeledLines)==="__EXPECTED_FORM_HASH__","labeled-export-complete");
   const input=$("#bank-search");
   input.value="Piper betle";input.dispatchEvent(new Event("input",{bubbles:true}));
   check(await wait(()=>window.HataOnlineAudit.bankComplete()),"complete-search-load");
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
   if(btn){btn.focus();btn.click();check($("#source-dialog").open && $("#source-dialog-body").textContent.includes("rujukan"),"source-dialog");check($("#source-dialog").getAttribute("aria-labelledby")===$("#source-dialog-title").id,"dialog-name");check(document.activeElement===$("#source-close"),"dialog-focus-on-open");$("#source-close").click();check(document.activeElement===btn,"dialog-focus-restored");}
   check(document.documentElement.scrollWidth<=window.innerWidth+2,"mobile-overflow");
 }catch(err){failures.push("runtime-"+err.message);}
 document.documentElement.dataset.phase9=failures.length?"FAIL-"+failures.join(","):"PASS";
});
</script>
"""
js=js.replace("__EXPECTED_FORM_HASH__",expected_form_hash)
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
      "--virtual-time-budget=15000","--dump-dom",host+"/phase9-browser-check.html"],
      capture_output=True,text=True,timeout=90)
    m=re.search(r'data-phase9="([^"]+)"',run.stdout)
    verdict=m.group(1) if m else "MISSING"
    print("Chrome",size,verdict,flush=True)
    if run.returncode or verdict!="PASS":
     print(run.stdout[-1200:],flush=True)
     print(run.stderr[-1200:],flush=True)
     raise AssertionError("Online browser test failed: "+verdict)
  finally:
   test_file.unlink(missing_ok=True)
  # Deliberately simulate unavailable Bank JSON to verify retry+offline fallback.
  error_page=ROOT/"phase9-network-error-check.html"
  error_test=r"""
<script>
document.addEventListener('DOMContentLoaded',()=>{
 const bank=document.querySelector('#show-bank');bank.click();
 setTimeout(()=>{
  const msg=document.querySelector('#bank-loading');
  const retry=document.querySelector('#bank-retry');
  const offline=msg?.querySelector('a[href="./Hata_Kamus_Mandailing.html"]');
  const ok=!!retry && !!offline && msg.getAttribute('role')==='status' && msg.getAttribute('aria-live')==='polite' && !window.HataOnlineAudit.bankLoaded() && msg.textContent.includes('TEST-NETWORK-OFFLINE');
  document.documentElement.dataset.phase9failure=ok?'PASS':'FAIL';
 },130);
});
</script>
"""
  try:
   mock=lite.replace("</head>",'<script>window.fetch=()=>Promise.reject(new Error("TEST-NETWORK-OFFLINE"));</script></head>')
   error_page.write_text(mock.replace("</body>",error_test+"</body>"),encoding="utf-8")
   out=subprocess.run([browser,"--headless=new","--no-sandbox","--disable-gpu",
      "--disable-dev-shm-usage","--window-size=390,844",
      "--user-data-dir="+str(Path(directory)/"state-network-failure"),
      "--virtual-time-budget=2500","--dump-dom",host+"/phase9-network-error-check.html"],
      capture_output=True,text=True,timeout=90)
   verdict=re.search(r'data-phase9failure="([^"]+)"',out.stdout)
   verdict=verdict.group(1) if verdict else "MISSING"
   print("Chrome network failure fallback",verdict,flush=True)
   if out.returncode or verdict!="PASS":
    print(out.stderr[-1000:],flush=True)
    raise AssertionError("Network error must show retry and full offline fallback")
  finally:
   error_page.unlink(missing_ok=True)
  chunk_error_page=ROOT/"phase9-chunk-error-check.html"
  chunk_error_test=r"""
<script>
document.addEventListener('DOMContentLoaded',async()=>{
 const $=s=>document.querySelector(s),wait=async f=>{for(let i=0;i<85;i++){if(f())return true;await new Promise(r=>setTimeout(r,60));}return false;};
 const original=window.fetch.bind(window);
 window.fetch=(url,...args)=>String(url).includes('chunk-001.json')?Promise.reject(new Error('TEST-CHUNK-NETWORK-OFFLINE')):original(url,...args);
 $('#show-bank').click();
 await wait(()=>window.HataOnlineAudit.bankLoaded());
 $('#bank-search').value='fish';$('#bank-search').dispatchEvent(new Event('input',{bubbles:true}));
 const ready=await wait(()=>!!$('#bank-retry'));
 const status=$('#bank-loading'),offline=status?.querySelector('a[href="./Hata_Kamus_Mandailing.html"]');
 const ok=ready&&!!offline&&status.getAttribute('role')==='status'&&status.getAttribute('aria-live')==='polite'&&!window.HataOnlineAudit.bankComplete()&&status.textContent.includes('TEST-CHUNK-NETWORK-OFFLINE');
 document.documentElement.dataset.phase9chunkfailure=ok?'PASS':'FAIL';
});
</script>
"""
  try:
   chunk_error_page.write_text(lite.replace("</body>",chunk_error_test+"</body>"),encoding="utf-8")
   out=subprocess.run([browser,"--headless=new","--no-sandbox","--disable-gpu",
      "--disable-dev-shm-usage","--window-size=390,844",
      "--user-data-dir="+str(Path(directory)/"state-chunk-network-failure"),
      "--virtual-time-budget=5000","--dump-dom",host+"/phase9-chunk-error-check.html"],
      capture_output=True,text=True,timeout=90)
   verdict=re.search(r'data-phase9chunkfailure="([^"]+)"',out.stdout)
   verdict=verdict.group(1) if verdict else "MISSING"
   print("Chrome later-chunk failure fallback",verdict,flush=True)
   if out.returncode or verdict!="PASS":
    print(out.stderr[-1000:],flush=True)
    raise AssertionError("Later Bank chunk failure must show retry and full offline fallback")
  finally:
   chunk_error_page.unlink(missing_ok=True)
finally:
 server.shutdown();server.server_close()
print("Phase 9 online/offline parity and lazy-fetch browser smoke: PASS")
