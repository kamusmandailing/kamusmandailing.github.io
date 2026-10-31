#!/usr/bin/env python3
"""Measure static/offline dictionary payload without requesting any external service.

The standalone HTML is independently usable from file://; references and ZIP
downloads may need an internet connection. This is a transfer-size baseline,
not a Core Web Vitals benchmark or a real-device network measurement.
"""
from __future__ import annotations
import gzip
import json
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FILE=ROOT/"index.html"

class Audit(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts=[]
        self.active=None
        self.inline_styles=[]
        self.style=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="script":
            self.active={"type":a.get("type","text/javascript"),"id":a.get("id","")}
            self.scripts.append(self.active)
        elif tag=="style":
            self.style=True
    def handle_data(self,data):
        if self.active is not None:
            self.active["bytes"]=self.active.get("bytes",0)+len(data.encode("utf-8"))
        if self.style:
            self.inline_styles.append(data)
    def handle_endtag(self,tag):
        if tag=="script":
            self.active=None
        elif tag=="style":
            self.style=False

def main():
    data=FILE.read_bytes()
    p=Audit();p.feed(data.decode("utf-8"))
    sizes={
        "standaloneHtmlBytes":len(data),
        "standaloneHtmlGzipBytes":len(gzip.compress(data,compresslevel=9,mtime=0)),
        "inlineJsonBytes":sum(i.get("bytes",0) for i in p.scripts if i["type"]=="application/json"),
        "inlineJavaScriptBytes":sum(i.get("bytes",0) for i in p.scripts if i["type"]!="application/json"),
        "inlineCssBytes":sum(len(x.encode("utf-8")) for x in p.inline_styles),
        "externalScripts":0,
        "externalStylesheets":0
    }
    html=data.decode("utf-8")
    if "<script src=" in html or '<link rel="stylesheet"' in html:
        raise SystemExit("Standalone HTML relies on external scripts or stylesheets.")
    if not all(f'id="{i}"' in html for i in ("seed-data","inventory-data","source-data","search","bank-search")):
        raise SystemExit("Offline main search or bank source data missing.")
    report={
        "schemaVersion":1,
        "testType":"Static delivery footprint and self-contained file audit (NOT a real network timing benchmark)",
        "source":"Generated root index.html from checked-in source",
        "metrics":sizes,
        "offlineBoundary":"Standalone dictionary, bank search and learning UI can render from file://; some source links and database ZIP download require internet."
    }
    output=Path(sys.argv[1]) if len(sys.argv)>1 else None
    if output:
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False))
if __name__=="__main__":
    main()
