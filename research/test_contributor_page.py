#!/usr/bin/env python3
"""Sanity and functional browser checks for the public contribution page."""
from html.parser import HTMLParser
from pathlib import Path
import os
import re
import shutil
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
PAGE=(ROOT/"kontributor.html").read_text(encoding="utf-8")
TEMPLATE=(ROOT/".github/ISSUE_TEMPLATE/01-kontribusi-kosakata.yml").read_text(encoding="utf-8")

class Scan(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids=[];self.links=[];self.labels=[];self.form_count=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get("id"): self.ids.append(a["id"])
        if tag=="a": self.links.append(a.get("href",""))
        if tag=="label" and a.get("for"): self.labels.append(a["for"])
        if tag=="form": self.form_count+=1
scan=Scan();scan.feed(PAGE)
assert scan.form_count==1
assert len(scan.ids)==len(set(scan.ids)), "Duplicate HTML ids"
assert {"contribution-form","jenis","kata","makna","consent","status"}<=set(scan.ids)
assert {"jenis","kata","makna"}<=set(scan.labels)
assert "./" in scan.links
assert "https://github.com/kamusmandailing/kamusmandailing.github.io/issues/new?template=01-kontribusi-kosakata.yml" in scan.links
assert 'name: "Usulan kosakata dan koreksi Mandailing"' in TEMPLATE
assert "required: true" in TEMPLATE and "pernyataan" in TEMPLATE
assert "noopener noreferrer" in PAGE
assert "URLSearchParams" in PAGE and 'navigator.clipboard.writeText' in PAGE
assert not any(x in PAGE for x in ["fetch(", "XMLHttpRequest(", "sendBeacon(", "eval("])
print("HTML structure and submission boundaries: PASS")

scripts=re.findall(r"<script(?: [^>]*)?>(.*?)</script>",PAGE,re.S)
assert len(scripts)==1
node=shutil.which("node")
assert node
with tempfile.TemporaryDirectory(prefix="kontributor-test-") as temp:
    tmp=Path(temp)
    js=tmp/"page.js";js.write_text(scripts[0],encoding="utf-8")
    subprocess.run([node,"--check",str(js)],check=True)
    print("JavaScript syntax: PASS")

    chrome=next((shutil.which(name) for name in ("google-chrome","google-chrome-stable","chromium","chromium-browser") if shutil.which(name)),None)
    if not chrome:
        raise RuntimeError("Chrome missing; browser test cannot pass")

    testjs=r"""
<script>
document.addEventListener('DOMContentLoaded', () => {
  const failures = [];
  const check=(v,n)=>{if(!v) failures.push(n)};
  const form=document.getElementById('contribution-form');
  const set=(id,v)=>{document.getElementById(id).value=v};
  check(!!form,'no-form');
  check(!!document.getElementById('copy-draft'),'no-copy-button');
  check(document.querySelectorAll('#contribution-form [required]').length>=4,'missing-required-inputs');
  check(form.checkValidity()===false,'invalid-empty-form-accepted');
  set('jenis','Kosakata atau padanan baru');
  set('kata','amang');
  set('makna','Usulan pengujian saja');
  set('wilayah','Mandailing');
  document.getElementById('consent').checked=true;
  check(form.checkValidity()===true,'valid-form-rejected');
  let opened='';
  const original=HTMLAnchorElement.prototype.click;
  HTMLAnchorElement.prototype.click=function(){opened=this.href};
  form.dispatchEvent(new Event('submit',{cancelable:true,bubbles:true}));
  HTMLAnchorElement.prototype.click=original;
  check(opened.startsWith('https://github.com/kamusmandailing/kamusmandailing.github.io/issues/new?'),'wrong-destination');
  try {
    const url=new URL(opened);
    check(url.searchParams.get('title').includes('amang'),'title-not-populated');
    check(url.searchParams.get('body').includes('Usulan pengujian saja'),'meaning-not-populated');
    check(url.searchParams.get('body').includes('Mandailing'),'region-not-populated');
  } catch(e){failures.push('invalid-url')}
  check(document.getElementById('status').textContent.includes('belum mengirim'),'false-submission-status');
  document.getElementById('consent').checked=false;
  check(form.checkValidity()===false,'consent-not-required');
  check(document.documentElement.scrollWidth<=window.innerWidth+2,'horizontal-overflow');
  document.documentElement.setAttribute('data-test', failures.length ? 'FAIL-'+failures.join('-'):'PASS');
});
</script>
"""
    assert PAGE.count("</body>")==1
    fixture=tmp/"kontributor.html"
    fixture.write_text(PAGE.replace("</body>",testjs+"</body>"),encoding="utf-8")
    for viewport in ["1280,900","390,844"]:
        run=subprocess.run([chrome,"--headless=new","--no-sandbox","--disable-gpu",
            "--disable-dev-shm-usage","--user-data-dir="+str(tmp/("chrome-"+viewport.replace(",","-"))),
            "--window-size="+viewport,"--virtual-time-budget=2500","--dump-dom",fixture.as_uri()],
            capture_output=True,text=True,timeout=70)
        verdict=re.search(r'data-test="([^"]+)"',run.stdout)
        result=verdict.group(1) if verdict else "MISSING-TEST-RESULT"
        print("Chrome",viewport,":",result)
        if run.returncode!=0 or result!="PASS":
            print(run.stderr[-1500:])
            raise AssertionError("Chrome UI smoke test failed: "+result)

    assert re.search(r'<button[^>]*id="send-drive"[^>]*disabled', PAGE), "Drive must fail closed until deployed"
    assert '<meta name="kamus-drive-endpoint" content="">' in PAGE
    backend=(ROOT/"integrations/google-drive-intake/Code.gs").read_text(encoding="utf-8")
    assert 'function doPost(e)' in backend and 'function setupOnce()' in backend
    assert 'MENUNGGU TELAAH' in backend and 'KAMUS_INTAKE_FOLDER_ID' in backend
    assert '1Pa5TimoNh9ragvun2XTEkIKHA4wdUpU2' not in backend, "Private folder ID must not be embedded in public code"
    subprocess.run([node,"--check"],input=backend,text=True,check=True)
    print("Apps Script backend syntax and configuration boundaries: PASS")

    drive_js=r"""
<script>
document.addEventListener('DOMContentLoaded', () => {
  const fails=[];
  const check=(ok,name)=>{if(!ok) fails.push(name)};
  const button=document.getElementById('send-drive');
  check(!button.disabled,'configured-drive-remains-disabled');
  for(const [id,v] of Object.entries({
    jenis:'Kosakata atau padanan baru',kata:'amang',makna:'Pengujian untuk antrean',
    wilayah:'Mandailing',padanan:'-',contoh:'Contoh',sumber:'Uji'
  })) document.getElementById(id).value=v;
  document.getElementById('consent').checked=true;
  let sent;
  const original=HTMLFormElement.prototype.submit;
  HTMLFormElement.prototype.submit=function(){
    sent={
      method:this.method,action:this.action,target:this.target,
      data:Object.fromEntries(new FormData(this).entries())
    };
  };
  button.click();
  HTMLFormElement.prototype.submit=original;
  check(!!sent,'post-not-created');
  if(sent){
    check(sent.action==='https://script.google.com/macros/s/AKfycbxTEST123/exec','wrong-drive-endpoint');
    check(sent.method==='post','not-post');
    check(sent.target==='_blank','not-new-tab');
    check(sent.data.kata==='amang','missing-word');
    check(sent.data.consent==='yes','missing-consent');
    check(sent.data.makna==='Pengujian untuk antrean','missing-meaning');
  }
  check(document.getElementById('status').textContent.includes('belum dianggap tersimpan'),
    'premature-success-claim');
  document.documentElement.setAttribute('data-test',fails.length?'FAIL-'+fails.join('-'):'PASS');
});
</script>
"""
    configured=PAGE.replace(
      '<meta name="kamus-drive-endpoint" content="">',
      '<meta name="kamus-drive-endpoint" content="https://script.google.com/macros/s/AKfycbxTEST123/exec">'
    ).replace("</body>",drive_js+"</body>")
    drive_fixture=tmp/"kontributor-configured.html"
    drive_fixture.write_text(configured,encoding="utf-8")
    run=subprocess.run([chrome,"--headless=new","--no-sandbox","--disable-gpu",
      "--disable-dev-shm-usage","--user-data-dir="+str(tmp/"chrome-drive-test"),
      "--window-size=390,844","--virtual-time-budget=2500","--dump-dom",drive_fixture.as_uri()],
      capture_output=True,text=True,timeout=70)
    marker=re.search(r'data-test="([^"]+)"',run.stdout)
    verdict=marker.group(1) if marker else 'MISSING-TEST-RESULT'
    print("Configured Drive handoff (mock endpoint):",verdict)
    if run.returncode or verdict!='PASS':
      print(run.stderr[-1200:])
      raise AssertionError("Configured Drive browser handoff failed: "+verdict)
print("Contributor page checks: PASS")
