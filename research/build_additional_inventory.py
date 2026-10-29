"""Rebuild the supplemental *form index*, without importing definitions.

The 1977 decisions refer to visually inspected scan crops. The other inputs
are factual word-list/table observations, with their source scope preserved.
This script uses only Python's standard library; no live network is needed.
"""
from pathlib import Path
import json, re, html, hashlib, collections

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

def clean(s):
    return ' '.join(html.unescape(re.sub(r'<[^>]+>', '', s)).split())

def build():
    records = []
    def add(form, source, page=None, pdf=None, kind='study_table', labels=None, **extra):
        form = ' '.join(form.split())
        assert form and not any(c in form for c in '\t\n\r|[]'), form
        layout = {'visual_scan_crop':'visual_scan_checked','structured_dataset':'structured_dataset',
                  'native_text_bold_index':'native_text_indexed','publisher_abstract':'publisher_abstract_checked'}.get(extra.get('layoutEvidence'),'table_visually_checked')
        records.append(dict(form=form, sourceId=source, printedPage=page if page is not None else '',
                            pdfPage=pdf, kind=kind, labels=labels or ['Mdl-scope'],
                            labelBasis=extra.pop('labelBasis','source_scope'), layoutStatus=layout, **extra))

    geometry = json.loads((HERE/'1977_extraction_geometry.json').read_text())
    locations = {r['id']:r for r in geometry['records']}
    decisions = {}
    for line in (HERE/'1977_review_decisions.txt').read_text().splitlines():
        if not line.strip() or line.startswith('#'): continue
        key, text = line.split('=',1); key = int(key)
        assert key not in decisions
        decisions[key] = text.split(';')
    # Hyphens here indicate the explicitly described bound usage, not a new
    # claim about the printed orthography. Independent 'na' is not changed.
    bound = {3757:('hu','hu-'),4078:('ki','-ki'),4093:('kon','-kon'),
             4451:('mi','-mi'),4478:('mu','-mu'),4576:('nami','-nami'),
             4686:('nia','-nia'),4694:('niba','-niba')}
    for key, forms in decisions.items():
        r = locations[key]
        for printed in forms:
            form = bound[key][1] if key in bound and printed==bound[key][0] else printed
            add(form,'dictionary1977',r['printedPage'],r['pdfPage'],'historical_form',['unmarked'],
                recordId='1977-'+str(key), column=r['column'],x=r['bbox'][0],y=r['bbox'][1],
                bbox=r['bbox'],labelBasisNote='Label dialek tidak ditranskripsikan dari pindai ini.',
                sourceScope='Kamus gabungan Angkola/Mandailing, edisi 1977; bukan label Mandailing eksklusif.',
                printedNotation=printed if form!=printed else '',
                normalizationNote='Tanda hubung analitis menandai pemakaian terikat yang dijelaskan sumber; bukan klaim ejaan resmi.' if form!=printed else '',
                layoutEvidence='visual_scan_crop',labelBasis='unmarked',sourceLocator='Kandidat pindai '+str(key))

    abvd = json.loads((HERE/'abvd1655_factual_records.json').read_text())
    assert len(abvd['aaData']) == abvd['iTotalRecords'] == 241
    for order, row in enumerate(abvd['aaData']):
        concept, gloss, form, annotation = map(clean,row[:4])
        url = html.unescape(re.search(r'href="([^"]+)"', row[2]).group(1))
        labels = ['Mdl'] if annotation=='Mandailing' else ['Sipirok'] if annotation=='Sipirok dialect' else ['unmarked']
        add(form,'abvd1655',kind='wordlist_entry',labels=labels,recordId='abvd-'+str(order+1),
            url=url,sourceLocator='ABVD 1655 · konsep '+concept+' · '+gloss,
            sourceGloss=gloss,glossLanguage='en',annotation=annotation,loanFlag=clean(row[5]),
            sourceScope='ABVD: Mandailing (A. Bazar Harahap); rujukan kamus 2007 mencakup Angkola/Mandailing. Anotasi dialek dipertahankan.',
            labelBasis='direct_annotation' if labels!=['unmarked'] else 'combined_source',
            layoutEvidence='structured_dataset')

    for order,r in enumerate(json.loads((HERE/'zenodo2024_lexical_index.json').read_text())):
        add(r['form'],'zenodo2024',r['printedPage'],r['pdfPage'],r['kind'],['unmarked'],
            recordId='zenodo-'+str(order+1),parent=r['parent'],x=r['x'],y=r['y'],
            sourceScope='Deposit mandiri 2024; pengantar menyebut Angkola–Mandailing. Bukan verifikasi penutur per dialek.',
            layoutEvidence='native_text_bold_index',labelBasis='unmarked')

    grain_verbs = 'manyuan eme;manyabi;mambon dar;mangga du;marlupak;mambarati;mambujuri;manahalak;pamasuk aek;manapui;mangkipas;mamaspa;mardege;marlungguk;marandilo;manggonion;mangkarung kon;marincir'.split(';')
    grain_nouns = 'bondar;bondar karihir;bondar tonga;bondar buangan;bondar jae;bondar julu;gadu;lupak;lubang;muara;ombik;pintu ni aek;saba;saba holbung;saba jae;saba julu;saba pasir;saba udan;sibarati;sitapangi;sibatangi;sibujuri;tahalak;ulu ni aek;aek;alak-alak;baju salin;batu;bustak;burir;buntu-buntu;duhut;irta;karetel;lapung;lungguk;orsik;porngis;rintop;sagean;singgulu;sopo;tano;tano na lom-lom;tapu-tapu;tano na rara;marsialapari;amak;andilo;goni;harung;induri;indalu;incirlosa ka;jait goni;kadangan;losung;losung aek;napu;pangkipas;paspasan;paradegean;panggilingan;timbangan;ubat nihama'.split(';')
    grain_adj = 'marmua ra;marsita pa ngi;maraek;marbatu;marbustak;marduhut;marirta;markarekel;marlapung;marorsik;marintop;maramak'.split(';')
    for group, forms, pdf, page in [('verba',grain_verbs,4,146),('nomina',grain_nouns,4,146),('adjektiva',grain_adj,7,149)]:
        for order,form in enumerate(forms):
            # 'amak' is clear in detailed Table 3, rather than 'smak' in Table 1.
            rp, pp = (6,148) if form=='amak' else (pdf,page)
            add(form,'grain2021',pp,rp,sourceLocator=('Tabel 3' if form=='amak' else 'Tabel 4' if group=='adjektiva' else 'Tabel 1')+' · '+group+' '+str(order+1),
                sourceScope='Kajian Mandailing di Desa Manisak, Batang Natal; label cakupan penelitian, bukan label dialek per lema.',
                annotation='Bentuk mengikuti tabel, termasuk spasi internal yang tidak lazim. Penelaahan ejaan dan makna masih diperlukan.',
                normalizationNote='Amak terbaca jelas pada tabel rinci; bentuk smak pada tabel ringkasan tidak dipromosikan.' if form=='amak' else '')

    for form in 'manatap;mamandang;manonton;manungkir;mangonjap;manjagoi;mamparrohahon;malirik;malotot;mamareso;manjangok;mangalayat'.split(';'):
        add(form,'sight2022',180,5,sourceLocator='Tabel 1: verba penglihatan',
            sourceScope='Kajian verba penglihatan yang menyebut bahasa Mandailing; belum pemeriksaan penutur per dialek.',
            normalizationNote='Sambungan baris Mamparroha hon pada tabel dibaca mamparrohahon, didukung bentuk utuh dalam teks sumber.' if form=='mamparrohahon' else '')

    for form in 'ama;amang;ina;inang;anak;angkang;anggi;amangtua;amanguda;namboru;inangtua;inanguda;tulang;nantulang;paman;oppung;oppung doli;oppung boru;etek;uda;kakang;amangnaposo'.split(';'):
        page,pdf = (550,5) if form in ['uda','kakang','amangnaposo'] else (549,4)
        add(form,'kinship2026',page,pdf,sourceLocator='Tabel 1: kekerabatan',
            sourceScope='Bentuk yang dilaporkan penelitian kekerabatan masyarakat Mandailing. Tabel memiliki ketidakkonsistenan glos; glos tidak diadopsi.')
    for form, pdf,page,table in [('anak boru',5,550,2),('mora',5,550,2),('pahompu',6,551,3),('kahanggi',6,551,3)]:
        add(form,'kinship2026',page,pdf,sourceLocator='Tabel '+str(table),sourceScope='Penelitian kekerabatan Mandailing; hanya bentuk yang benar-benar tampil, bukan 45 istilah yang diklaim artikel.')

    number_pages = [
        (11,262,'sada;dua;tolu;opat;lima;onom;pitu;lapan;sambilan;sapulu;sabolas;dua bolas;tolu bolas;opat bolas;lima bolas;onom bolas;pitu bolas;lapan bolas;sambilan bolas;dua pulu;tolu pulu;opat pulu;lima pulu;onom pulu;pitu pulu;lapan pulu;sambilan pulu'),
        (12,263,'saratus;dua ratus;tolu ratus;opat ratus;lima ratus;onom ratus;pitu ratus;lapan ratus;sambilan ratus;saribu;dua ribu;tolu ribu;opat ribu;lima ribu;onom ribu;pitu ribu;lapan ribu;sambilan ribu;sapulu ribu;saratus ribu;dua ratus ribu;tolu ratus ribu;opat ratus ribu;lima ratus ribu;onom ratus ribu;pitu ratus ribu;lapan ratus ribu;sambilan ratus ribu;sajuta;dua juta;tolu juta;opat juta;lima juta;onom juta;pitu juta;lapan juta;sambilan juta;satonga;sapartolu;saparopat;saparlima;saparonom;saparpitu;saparlapan;saparsambilan;sajongkal;lungguk;sadengkul;sadada;satetes;sagenggam;sajanjang;sagang hari;tonga ari')]
    for pdf,page,text in number_pages:
        for form in text.split(';'):
            add(form,'numbers',page,pdf,'number_list',['Tapsel'],sourceLocator='Daftar dan contoh bilangan/ukuran pada halaman '+str(page),
                sourceScope='Kajian pembelajaran bahasa matematis Tapsel, bukan cakupan Mandailing eksklusif.',
                annotation='Hanya bentuk yang tertulis; kombinasi bilangan baru tidak dibangkitkan. Beberapa pemetaan angka pada contoh sumber keliru dan tidak diadopsi.')

    # The publisher abstract is accessible; the advertised full PDF failed.
    # The ambiguous spelling abingsoabibg is deliberately not admitted.
    for form in ['abara','abincaran','abinsoabin','abuan','abubusan','adat manjujur']:
        add(form,'idiom2023',kind='publisher_abstract',sourceLocator='Abstrak penerbit; contoh lema awal A',
            sourceScope='Kamus Idiom: Leksikon Mandailing; hanya bentuk yang terbaca pada abstrak penerbit, bukan isi buku penuh.',
            layoutEvidence='publisher_abstract')

    # Remove identical observations; retain distinct pages and homonyms.
    seen=set(); result=[]
    for r in records:
        key=(r['form'].casefold(),r['sourceId'],str(r['printedPage']),r['kind'],r.get('sourceLocator',''))
        if key not in seen: result.append(r);seen.add(key)
    extension=json.loads((HERE/'extension_20261027.json').read_text())
    result.extend(extension['records'])
    result.extend(json.loads((HERE/'extension_20261027b.json').read_text())['records'])
    result.extend(json.loads((HERE/'extension_20261030.json').read_text())['records'])
    counts=dict(collections.Counter(r['sourceId'] for r in result))
    output={'schemaVersion':1,'method':'Source forms only; no inferred derivations or bulk definitions.',
            'sourceRecordCounts':counts,'records':result,
            'review1977':{'candidateCount':5671,'newCandidateCropsReviewed':3403,
                          'acceptedCropRecords':len(decisions),'acceptedUniqueForms':len({r['form'].casefold() for r in result if r['sourceId']=='dictionary1977'}),
                          'coverage':'All candidate contact sheets reviewed; lexical detection and transcription are not a guarantee of full dictionary coverage.'}}
    (HERE/'additional_inventory.json').write_text(json.dumps(output,ensure_ascii=False,separators=(',',':'))+'\n')
    print(json.dumps({'records':len(result),'sources':counts,'review1977':output['review1977']},ensure_ascii=False))
    return output

if __name__=='__main__': build()
