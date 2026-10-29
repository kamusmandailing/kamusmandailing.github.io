from pathlib import Path
import csv
import io
import json
from urllib.parse import quote

root = Path(__file__).resolve().parent
source = root / 'src'
words = json.loads((source / 'words.json').read_text(encoding='utf-8'))
research = json.loads((root / 'research/progress.json').read_text(encoding='utf-8'))
research['reportMarkdown'] = (root / 'research/analisis_pendalaman_20261030.md').read_text(encoding='utf-8')
from prepare_inventory import prepare_inventory
inventory=prepare_inventory()
assert words and len({word['id'] for word in words}) == len(words)
assert len({word['md'].strip().casefold() for word in words}) == len(words)
categories = {'ganti','angka','kerja','rumah','sifat','alam','orang','tugas','umum'}
for word in words:
    assert all(isinstance(word.get(key),str) and word[key].strip() for key in ('md','idn','my','en'))
    assert word['category'] in categories
    assert bool(word.get('exampleMd')) == bool(word.get('exampleId'))
    if word['status'] == 'source_attested':
        ref = word['sourceRef']
        assert ref['id'] in {'dictionary','numbers'}
        if ref['id'] == 'dictionary':
            assert (ref['printedPage']=='xi' and ref['pdfPage']==13) or (isinstance(ref['printedPage'],int) and ref['pdfPage']==ref['printedPage']+16)
        else:
            assert ref['printedPage']==262 and ref['pdfPage']==11
        assert ref['languageLabel'] in {'Mdl','unmarked','shared-pronunciation','Tapsel'}
        assert word['exampleStatus'] in {'pending','source_quoted'}
    for key in ('md','idn','my','en','exampleMd','exampleId'):
        assert not any(c in word.get(key,'') for c in '\t\r\n|'), (word['md'],key)
assert research['total'] == len(words)
assert research['sourceAttested'] == sum(w['status']=='source_attested' for w in words)
template = (source / 'index.html').read_text(encoding='utf-8')
pattern = 'url("data:image/svg+xml,' + quote((source / 'ulos-pattern.svg').read_text(encoding='utf-8'),safe='') + '")'
skin = (source / 'ulos.css').read_text(encoding='utf-8').replace('INLINE_ULOS_PATTERN',pattern)
styles = (source / 'styles.css').read_text(encoding='utf-8')+'\n'+skin+'\n'+(source / 'research.css').read_text(encoding='utf-8')+'\n'+(source/'inventory.css').read_text(encoding='utf-8')
template = template.replace('/* INLINE_STYLES */',styles)
app=(source/'app.js').read_text(encoding='utf-8').replace('/* INLINE_INVENTORY_APP */',(source/'inventory.js').read_text(encoding='utf-8'))
template = template.replace('/* INLINE_APP */',app)
encode = lambda value: json.dumps(value,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
template = template.replace('"INLINE_INVENTORY"',encode(inventory))
template = template.replace('"INLINE_SOURCES"',encode(json.loads((source/'sources.json').read_text(encoding='utf-8'))))
template = template.replace('"INLINE_WORDS"',encode(words)).replace('"INLINE_RESEARCH"',encode(research))
assert 'INLINE_' not in template
for directory in (root,root/'dist'):
    directory.mkdir(exist_ok=True)
    for name in ('index.html','Hata_Kamus_Mandailing.html'):
        (directory/name).write_text(template,encoding='utf-8')
buffer=io.StringIO(newline='')
writer=csv.writer(buffer,delimiter='\t',lineterminator='\n')
writer.writerow(['Mandailing','Indonesia','Melayu Malaysia','English','Contoh Kalimat'])
for word in words:
    example=f"Mandailing: {word['exampleMd']} — Indonesia: {word['exampleId']}" if word.get('exampleMd') else ''
    writer.writerow([word['md'],word['idn'],word['my'],word['en'],example])
(root/'data').mkdir(exist_ok=True)
(root/'data/kamus.tsv').write_text('\ufeff'+buffer.getvalue(),encoding='utf-8')
audit=io.StringIO(newline='')
audit_writer=csv.writer(audit,delimiter='\t',lineterminator='\n')
audit_writer.writerow(['Mandailing','Sumber','Lema sumber','Jenis lokasi','Halaman cetak','Halaman PDF','Label bahasa','Status contoh','Catatan'])
for word in words:
    ref=word.get('sourceRef',{})
    audit_writer.writerow([word['md'],ref.get('id',''),ref.get('lemma',''),ref.get('kind',''),ref.get('printedPage',''),ref.get('pdfPage',''),ref.get('languageLabel',''),word['exampleStatus'],word.get('note','')])
(root/'data/jejak_sumber.tsv').write_text('\ufeff'+audit.getvalue(),encoding='utf-8')
print(f'Built {len(words)} unique entries, {research["sourceAttested"]} source-attested headwords.')

from export_database import export_database
export_database()

import shutil
(root/"dist/data").mkdir(exist_ok=True)
shutil.copy2(root/"data/Kamus_Mandailing_Database.zip",root/"dist/data/Kamus_Mandailing_Database.zip")
