"""Merge source-form observations while preserving dialect and evidence scope."""
from pathlib import Path
import json,hashlib,collections,csv,io

ROOT=Path(__file__).resolve().parent

def prepare_inventory():
    source=json.loads((ROOT/'research/source_inventory.json').read_text())
    words=json.loads((ROOT/'src/words.json').read_text());known={w['md'].casefold():w for w in words}
    forms={}
    for order,r in enumerate(source['records']):
        key=r['form'].casefold()
        assert key and not any(c in key for c in '\t\r\n|[]'),r
        assert r['layoutStatus'] in ['intact','joined_confirmed','visually_reviewed'],r
        f=forms.setdefault(key,{'id':'form-'+hashlib.sha256(key.encode()).hexdigest()[:16],'form':r['form'],'kinds':[], 'labels':[], 'usageTags':[], 'references':[],'entryId':known[key]['id'] if key in known else None})
        own=[t for t in r['tags'] if t in ['Mdl','Akl','Tb']]
        inherited=[t for t in r.get('parentTags',[]) if t in ['Mdl','Akl','Tb']]
        labels=own or inherited
        if r['form']=='sarop' and r['printedPage']==199:labels=['Mdl','Akl']
        usage=list(dict.fromkeys([t for t in r['tags']+r.get('parentTags',[]) if t not in ['Mdl','Akl','Tb']]))
        f['kinds'].append(r['kind'])
        if r.get('boundForm'):f['kinds'].append('bound_form')
        if ' ' in r['form']:f['kinds'].append('compound')
        f['labels'].extend(labels or ['unmarked']);f['usageTags'].extend(usage)
        f['references'].append({'sourceId':'dictionary','printedPage':r['printedPage'],'pdfPage':r['pdfPage'],
          'kind':r['kind'],'parent':r.get('parentForm',''),'homonym':r.get('homonym',''),
          'labels':labels or ['unmarked'],'labelBasis':'direct' if own else 'parent' if inherited else 'unmarked',
          'layoutStatus':r['layoutStatus'],'column':r['column'],'x':r['x'],'y':r['y'],
          'crossReference':r.get('crossReference',''),'printedNotation':r.get('printedNotation',''),
          'normalizationNote':r.get('normalizationNote','')})
    # Existing reviewed forms in the preface or the separate numeral study are retained.
    for key,w in known.items():
        if key in forms:continue
        ref=w['sourceRef'];labels=[ref['languageLabel']]
        if labels==['shared-pronunciation']:labels=['Akl','Mdl']
        forms[key]={'id':'form-'+hashlib.sha256(key.encode()).hexdigest()[:16],'form':w['md'],'kinds':['reference_example' if ref['printedPage']=='xi' else 'number_list'],'labels':list(labels),'usageTags':[], 'entryId':w['id'],
          'references':[{'sourceId':ref['id'],'printedPage':ref['printedPage'],'pdfPage':ref['pdfPage'],'kind':ref['kind'],'parent':ref['lemma'],'homonym':ref.get('homonym',''),'labels':labels,'labelBasis':'reviewed_reference','layoutStatus':'reviewed_reference','column':None,'x':None,'y':None,'crossReference':'','printedNotation':'','normalizationNote':''}]}
    baseline_count=len(forms)
    from research.build_additional_inventory import build as build_additional
    additional=build_additional()
    for r in additional['records']:
        key=r['form'].casefold()
        assert key and not any(c in key for c in '\t\r\n|[]'),r
        f=forms.setdefault(key,{'id':'form-'+hashlib.sha256(key.encode()).hexdigest()[:16],
          'form':r['form'],'kinds':[],'labels':[],'usageTags':[], 'references':[],
          'entryId':known[key]['id'] if key in known else None})
        f['kinds'].append(r['kind'])
        if r['form'].startswith('-') or r['form'].endswith('-'):f['kinds'].append('bound_form')
        if ' ' in r['form']:f['kinds'].append('compound')
        f['labels'].extend(r['labels']);f['usageTags'].extend(r.get('usageTags',[]))
        defaults={'parent':'','homonym':'','column':None,'x':None,'y':None,
          'crossReference':'','printedNotation':'','normalizationNote':''}
        defaults.update({k:v for k,v in r.items() if k!='form'})
        same_number=next((ref for ref in f['references'] if r['sourceId']=='numbers' and ref['sourceId']=='numbers' and ref['pdfPage']==r['pdfPage']),None)
        if same_number:
            same_number.update(defaults)
        else:f['references'].append(defaults)
    result=sorted(forms.values(),key=lambda f:f['form'].casefold().lstrip('-'))
    for f in result:
        for k in ['kinds','labels','usageTags']:f[k]=list(dict.fromkeys(f[k]))
        f['status']='reviewed_translations' if f['entryId'] else 'source_inventory'
    stats={'uniqueForms':len(result),'bodySourceForms':len({r['form'].casefold() for r in source['records']}),
           'sourceRecords':len(source['records']),'referenceRecords':sum(len(f['references']) for f in result),
           'reviewedTranslations':len(words),'pendingTranslations':sum(not f['entryId'] for f in result),
           'headwordRecords':sum(r['kind']=='headword' for r in source['records']),
           'subentryRecords':sum(r['kind']=='subentry' for r in source['records']),
           'crossReferenceRecords':sum(r['kind']=='cross_reference' for r in source['records']),
           'abbreviationRecords':sum(r['kind']=='abbreviation_expansion' for r in source['records']),
           'boundForms':sum('bound_form' in f['kinds'] for f in result),'indexedPages':len(source['pages']),
           'normalizationsReviewed':sum(r['layoutStatus']=='visually_reviewed' for r in source['records']),
           'previousUniqueForms':baseline_count,'addedUniqueForms':len(result)-baseline_count,
           'supplementalRecords':len(additional['records']),
           'sourceCount':len({ref['sourceId'] for f in result for ref in f['references']}),
           'recordsBySource':dict(collections.Counter(ref['sourceId'] for f in result for ref in f['references'])),
           'localNameObservations':len(json.loads((ROOT/'research/local_name_observations.json').read_text()))}
    extension=json.loads((ROOT/'research/extension_20261027b.json').read_text())
    old_forms={r['form'].casefold() for r in additional['records'] if r.get('extensionBatch')!=extension['releaseId']}|{r['form'].casefold() for r in source['records']}|set(known)
    stats['releasePreviousUniqueForms']=len(old_forms)
    stats['releaseAddedUniqueForms']=len({f['form'].casefold() for f in result}-old_forms)
    stats['releaseAddedReferences']=stats['referenceRecords']-extension['baselineReferences']
    stats['sourceGlossForms']=sum(any(r.get('sourceGloss') for r in f['references']) for f in result)
    stats['indonesianSourceGlossForms']=sum(any(r.get('sourceGloss') and r.get('glossLanguage')=='id' for r in f['references']) for f in result)
    stats['botanicalReferences']=sum(bool(r.get('taxonAsPrinted')) for f in result for r in f['references'])
    stats['localNameTaxa']=sum(bool(r.get('taxonAsPrinted')) for r in json.loads((ROOT/'research/local_name_observations.json').read_text()))
    stats['localNameReviewCounts']=dict(collections.Counter(r['review']['status'] for r in json.loads((ROOT/'research/local_name_observations.json').read_text())))
    bank={'schemaVersion':5,'version':'2026-10-27-DEEP02','stats':stats,'forms':result,
          'coverage':source['pages'],'sourceSha256':source['sourceSha256'],
          'additionalCoverage':additional['review1977'],
          'researchUpdate':json.loads((ROOT/'research/research_update_20261027.json').read_text()),
          'localNames':json.loads((ROOT/'research/local_name_observations.json').read_text()),
          'notes':['Bentuk leksikal bertanda pada halaman 1–248 kamus 2021 diinventarisasi; kata dasar, turunan, gabungan, bentuk terikat dan rujuk silang dibedakan.',
          'Kamus 1977 ditambah melalui pemeriksaan visual calon dari OCR; seluruh lembar calon baru ditinjau, tetapi deteksi tersebut bukan jaminan seluruh isi kamus sudah ditranskripsikan.',
          'ABVD 1655 dan indeks leksikal PDF mandiri 2024 ditambahkan, bersama tabel penelitian yang dapat dibaca serta abstrak penerbit 2023. Cakupan dan mutu tiap sumber berbeda.',
          'Jumlah bentuk unik bukan jumlah semua kata dasar bahasa Mandailing. Variasi ejaan, gabungan, kata serapan dan nama yang terdaftar dalam sumber ikut terhitung.',
          'Label Akl dan Tb dipertahankan sebagai pembanding. Mdl-scope berarti cakupan penelitian, berbeda dari label Mdl per bentuk. unmarked bukan berarti Mandailing eksklusif.',
          'Hanya koleksi berpadanan yang telah disunting memiliki terjemahan. Glos konsep dan makna ringkas dari sumber disimpan sebagai glos sumber, bukan terjemahan kurasi.',
          'Nama tumbuhan dengan bahasa yang tidak disebutkan per nama disimpan terpisah sebagai observasi pembanding, tidak menambah jumlah lexical_forms.']}
    (ROOT/'src/inventory.json').write_text(json.dumps(bank,ensure_ascii=False,separators=(',',':'))+'\n')
    for filename,header,rows in [
      ('kosakata_semua.tsv',['Mandailing','Indonesia','Melayu Malaysia','English','Contoh Kalimat'],
       [[f['form']]+([known[f['form'].casefold()][k] for k in ['idn','my','en']]+[('Mandailing: '+known[f['form'].casefold()]['exampleMd']+' — Indonesia: '+known[f['form'].casefold()]['exampleId']) if known[f['form'].casefold()].get('exampleMd') else ''] if f['entryId'] else ['','','','']) for f in result]),
      ('kosakata_berlabel.tsv',['Bentuk sumber','Indonesia','Melayu Malaysia','English','Label sumber','Jenis','Status padanan','ID bentuk','Sumber'],
       [[f['form']]+([known[f['form'].casefold()][k] for k in ['idn','my','en']] if f['entryId'] else ['','',''])+[', '.join(f['labels']),', '.join(f['kinds']),f['status'],f['id'],', '.join(dict.fromkeys(ref['sourceId'] for ref in f['references']))] for f in result]),
      ('inventaris_sumber.tsv',['ID bentuk','Bentuk','Jenis','Label bahasa','Label pemakaian','Status padanan','Sumber','Halaman cetak','Halaman PDF','Induk lema','Homonim','Dasar label','Rujuk silang','Notasi sumber','Catatan normalisasi','Lokasi sumber','URL khusus','Cakupan sumber','Glos sumber','Bahasa glos','Anotasi'],
       [[f['id'],f['form'],ref['kind'],', '.join(ref['labels']),', '.join(f['usageTags']),f['status'],ref['sourceId'],ref['printedPage'],ref['pdfPage'],ref['parent'],ref['homonym'],ref['labelBasis'],ref['crossReference'],ref['printedNotation'],ref['normalizationNote'],ref.get('sourceLocator',''),ref.get('url',''),ref.get('sourceScope',''),ref.get('sourceGloss',''),ref.get('glossLanguage',''),ref.get('annotation','')] for f in result for ref in f['references']])]:
        buff=io.StringIO(newline='');writer=csv.writer(buff,delimiter='\t',lineterminator='\n');writer.writerow(header);writer.writerows(rows)
        (ROOT/'data'/filename).write_text('\ufeff'+buff.getvalue())
    buff=io.StringIO(newline='');writer=csv.writer(buff,delimiter='\t',lineterminator='\n')
    writer.writerow(['Nama dalam tabel','Sumber','Halaman cetak','Halaman PDF','Status bahasa','Cakupan'])
    writer.writerows([[r['name'],r['sourceId'],r['printedPage'],r['pdfPage'],r['languageStatus'],r['scope']] for r in bank['localNames']])
    (ROOT/'data/nama_tumbuhan_pembanding.tsv').write_text('\ufeff'+buff.getvalue())
    buff=io.StringIO(newline='');writer=csv.writer(buff,delimiter='\t',lineterminator='\n')
    writer.writerow(['ID observasi','Nama tabel','Status bahasa sumber asli','Status telaah silang','Takson sebagaimana sumber','Kecocokan ID bentuk','Catatan telaah','Sumber bukti'])
    form_ids={f['form'].casefold():f['id'] for f in result}
    writer.writerows([[r['id'],r['name'],r['languageStatus'],r['review']['status'],r.get('taxonAsPrinted',''),form_ids.get(r['name'].casefold(),''),r['review']['note'],'; '.join(e.get('url','') for e in r['review'].get('evidence',[]))] for r in bank['localNames']])
    (ROOT/'data/telaah_nama_tumbuhan.tsv').write_text('\ufeff'+buff.getvalue())
    buff=io.StringIO(newline='');writer=csv.writer(buff,delimiter='\t',lineterminator='\n')
    writer.writerow(['ID bentuk','Bentuk','Takson sebagaimana sumber','Sumber','Halaman cetak','Halaman PDF','Label sumber','Lokasi','Catatan'])
    writer.writerows([[f['id'],f['form'],r['taxonAsPrinted'],r['sourceId'],r['printedPage'],r['pdfPage'],', '.join(r['labels']),r.get('sourceLocator',''),r.get('annotation','')] for f in result for r in f['references'] if r.get('taxonAsPrinted')])
    (ROOT/'data/nama_botani_sumber.tsv').write_text('\ufeff'+buff.getvalue())
    return bank

if __name__=='__main__':print(json.dumps(prepare_inventory()['stats']))
