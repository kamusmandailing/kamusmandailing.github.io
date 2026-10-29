"""Generate PRIVATE OCR candidates, never an automatically accepted word list.

Usage: python3 research/detect_1977_candidates.py SOURCE.pdf PRIVATE_OUTPUT.json
Requires PyMuPDF, NumPy and SciPy. The accepted form bank uses separately
reviewed decisions and does not import this raw output.
"""
from pathlib import Path
import fitz,numpy as np,json,re,collections,sys,hashlib
from scipy.ndimage import distance_transform_edt
source=Path(sys.argv[1]);target=Path(sys.argv[2]);
assert hashlib.sha256(source.read_bytes()).hexdigest()=='cac94f74d5f004ce1da3cbd35fbeaaa3bdddd2062b50610aa6c89f985609147c','Wrong source PDF'
doc=fitz.open(source);out=[];pages=[]
for pi in range(10,144):
 page=doc[pi];pix=page.get_pixmap(matrix=fitz.Matrix(3,3),colorspace=fitz.csGRAY);a=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width);dt=distance_transform_edt(a<165)
 words=[]
 for w in page.get_text('words'):
  x0,y0,x1,y1,t,*_=w
  if not (25<y0<page.rect.height-25) or not re.search('[A-Za-z]',t):continue
  z=dt[max(0,int(y0*3)):int(y1*3),max(0,int(x0*3)):int(x1*3)];v=z[z>0]
  words.append({'text':t,'bbox':[x0,y0,x1,y1],'col':0 if x0<page.rect.width/2 else 1,'score':float(np.mean(v)) if len(v) else 0})
 words.sort(key=lambda w:(w['col'],w['bbox'][1],w['bbox'][0]));lines=[]
 for col in [0,1]:
  column=[w for w in words if w['col']==col];ys=[]
  for w in column:
   y=w['bbox'][1]
   near=next((ln for ln in reversed(ys[-3:]) if abs(ln['y']-y)<2.5),None)
   if near:near['words'].append(w)
   else:ys.append({'y':y,'words':[w],'col':col})
  for ln in ys:ln['words'].sort(key=lambda w:w['bbox'][0])
  if not ys:continue
  starts=[ln['words'][0]['bbox'][0] for ln in ys];margin=float(np.quantile(starts,.08))
  head=[ln['words'][0]['score'] for ln in ys if ln['words'][0]['bbox'][0]<margin+5]
  normal=[w['score'] for ln in ys for w in ln['words'][2:] if len(w['text'])>3]
  medh=float(np.median(head));medn=float(np.median(normal));threshold=(medh+medn)/2+.01
  for ln in ys:
   first=ln['words'][0];ishead=first['bbox'][0]<margin+5;score=first['score']
   if not ishead and score<threshold:continue
   ts=[];bs=[]
   for j,w in enumerate(ln['words']):
    if j and (w['score']<threshold or w['bbox'][0]-ln['words'][j-1]['bbox'][2]>25):break
    t=w['text'].strip('.,;:()!?')
    if not re.fullmatch(r'[a-zA-ZÀ-ÖØ-öø-ÿ·\-]+',t):break
    ts.append(t);bs.append(w['bbox'])
   if not ts:continue
   form=' '.join(ts);bbox=[min(b[0] for b in bs),min(b[1] for b in bs),max(b[2] for b in bs),max(b[3] for b in bs)]
   out.append({'id':len(out),'rawForm':form,'pdfPage':pi+1,'printedPage':pi+1,'column':col+1,'bbox':[round(z,2) for z in bbox],'score':round(score,3),'threshold':round(threshold,3),'kind':'headword' if ishead else 'subentry','reviewStatus':'ocr_candidate'})
  pages.append({'pdfPage':pi+1,'column':col+1,'margin':round(margin,2),'threshold':round(threshold,3),'headScore':round(medh,3),'normalScore':round(medn,3)})
target.write_text(json.dumps({'records':out,'pages':pages},ensure_ascii=False,indent=2))
print('candidates',len(out),'unique',len({r['rawForm'].casefold() for r in out}))
