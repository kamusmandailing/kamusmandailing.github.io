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
print("Contributor page checks: PASS")
