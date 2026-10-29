"""Render private review sheets for the 1977 OCR candidates.

Usage: python3 research/render_1977_candidates.py SOURCE.pdf PRIVATE_CANDIDATES.json OUTPUT_DIRECTORY
Requires PyMuPDF, Pillow and the DejaVuSans font. IDs identify source crops,
not accepted words. The baseline is reconstructed from the original 2021 index.
"""
from pathlib import Path
import fitz,json,math,sys
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1]
base=json.loads((R/'research/source_inventory.json').read_text());words=json.loads((R/'src/words.json').read_text())
old={x['form'].casefold() for x in base['records']}|{w['md'].casefold() for w in words}
data=json.loads(Path(sys.argv[2]).read_text());rs=[r for r in data['records'] if r['rawForm'].casefold() not in old]
doc=fitz.open(sys.argv[1]);out=Path(sys.argv[3]);out.mkdir(parents=True,exist_ok=True)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',11);titlefont=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20)
for batch in range(math.ceil(len(rs)/100)):
 subset=rs[batch*100:(batch+1)*100];img=Image.new('RGB',(2000,1290),'#f5f3ed');dr=ImageDraw.Draw(img);dr.text((10,6),f'1977 NEW-TO-BANK OCR REVIEW {batch+1} — IDs identify source crops, not accepted words',font=titlefont,fill='black')
 for j,r in enumerate(subset):
  col=j//25;row=j%25;x=col*500;y=40+row*50
  page=doc[r['pdfPage']-1];x0,y0,x1,y1=r['bbox'];right=page.rect.width/2 if r['column']==1 else page.rect.width-15
  clip=fitz.Rect(x0-1,y0-2,min(right,x0+145),y0+13)
  pix=page.get_pixmap(matrix=fitz.Matrix(3,3),clip=clip,colorspace=fitz.csRGB);crop=Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
  img.paste(crop,(x+57,y));dr.text((x+2,y+4),str(r['id']),font=font,fill='black');dr.text((x+2,y+19),'p'+str(r['pdfPage']),font=font,fill='#66523f');dr.line((x,y+48,x+498,y+48),fill='#d9d1c5')
 img.save(out/f'batch-{batch+1:02d}.png')
print('sheets',math.ceil(len(rs)/100),'new raw records',len(rs),'path',out)
