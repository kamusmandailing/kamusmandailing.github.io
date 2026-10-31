#!/usr/bin/env python3
"""Stage 8 browser checks: no eager plant panel DOM; opening reveals 183 source records."""
from pathlib import Path
import re,shutil,subprocess,tempfile

ROOT=Path(__file__).resolve().parents[1]
html=(ROOT/"index.html").read_text("utf-8")
chrome=next((shutil.which(x) for x in ("google-chrome","chromium","chromium-browser") if shutil.which(x)),None)
assert chrome
test=r"""
<script>
document.addEventListener('DOMContentLoaded',()=>{
 const fail=[];
 const check=(ok,n)=>{if(!ok)fail.push(n)};
 const names=document.querySelector('#local-name-results');
 check(names.children.length===0,'plant-panel-eagerly-rendered');
 const nav=document.querySelector('.sidebar [data-nav="inventory"]');
 nav.click();
 check(!document.querySelector('[data-view="inventory"]').hidden,'bank-view-not-open');
 const panel=document.querySelector('.local-name-panel');
 check(!panel.open,'plant-panel-started-open');
 panel.open=true;
 panel.dispatchEvent(new Event('toggle'));
 check((names.innerHTML.match(/<article/g)||[]).length===183,'plant-panel-did-not-load-on-demand');
 const search=document.querySelector('#bank-search');
 search.value='Piper betle';
 search.dispatchEvent(new Event('input',{bubbles:true}));
 check(document.querySelector('#bank-results').textContent.includes('simanat'),'bank-global-search');
 const source=document.querySelector('#bank-source');
 source.value='plants2019';
 source.dispatchEvent(new Event('change',{bubbles:true}));
 check(document.querySelector('#bank-results').textContent.includes('simanat'),'source-scoped-search');
 source.value='dictionary';
 source.dispatchEvent(new Event('change',{bubbles:true}));
 check(!document.querySelector('#bank-results').textContent.includes('simanat'),'source-gloss-leak');
 document.documentElement.dataset.phase8=fail.length?'FAIL-'+fail.join(','):'PASS';
});
</script>
"""
with tempfile.TemporaryDirectory(prefix="kamus-lazy-bank-") as folder:
 file=Path(folder)/"index.html"
 file.write_text(html.replace("</body>",test+"</body>"),"utf-8")
 for viewport in ("1280,900","390,844"):
  res=subprocess.run([chrome,"--headless=new","--no-sandbox","--disable-gpu","--disable-dev-shm-usage",
      "--window-size="+viewport,"--user-data-dir="+str(Path(folder)/("state-"+viewport.replace(",","-"))),
      "--virtual-time-budget=3200","--dump-dom",file.as_uri()],capture_output=True,text=True,timeout=90)
  match=re.search(r'data-phase8="([^"]+)"',res.stdout)
  status=match.group(1) if match else "MISSING"
  print("Chrome",viewport,status,flush=True)
  if res.returncode or status!="PASS":
   print(res.stderr[-800:])
   raise AssertionError("Lazy bank browser regression: "+status)
print("Lazy plant panel and source-isolated search: PASS")
