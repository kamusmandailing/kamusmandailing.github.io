"""Index lexical forms printed in bold in the 2021 source, without copying definitions.

Requires PyMuPDF for extraction only. Normal app/database builds do not require it.
Usage: python3 research/extract_source_inventory.py /path/to/source.pdf /path/to/output.json
"""
from pathlib import Path
import sys,re,json,hashlib,collections
import fitz

LETTER=re.compile(r'[A-Za-zÀ-ÖØ-öø-ÿ]')
FORM=re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ][A-Za-zÀ-ÖØ-öø-ÿ '\-]*[A-Za-zÀ-ÖØ-öø-ÿ]$|^[A-Za-z]$")
POS=re.compile(r'\b(adv|pron|num|n|v|a|p)\b')
LABELS=re.compile(r'\b(Mdl|Akl|Tb|tdk|Ark|ark|cak|kas|ksr|ki|kla|Adt|pb|kp)\b')

def extract(pdf_path):
    doc=fitz.open(pdf_path);all_spans=[];raw=[];fragments=[];pages=[]
    for pi in range(16,264):
        spans=[]
        for block in doc[pi].get_text('dict')['blocks']:
            if block['type']!=0:continue
            for line in block['lines']:
                for s in line['spans']:
                    x,y=s['origin'];text=s['text']
                    if not (54<y<611) or s['size']>12 or not text.strip():continue
                    s=dict(s);s['column']=0 if x<215 else 1;s['page']=pi-15;s['pdfPage']=pi+1
                    spans.append(s)
        spans.sort(key=lambda s:(s['column'],round(s['origin'][1],1),s['bbox'][0]))
        # Preserve actual read order, including definitions, solely for boundary/tag detection.
        all_spans.extend(spans)
        pages.append({'printedPage':pi-15,'pdfPage':pi+1,'bodySpanCount':len(spans)})
    # Lexical spans: bold type is specified for lemmas, sublemmas, compounds and references.
    candidates=[]
    for i,s in enumerate(all_spans):
        if 'Bold' not in s['font'] or 'Italic' in s['font'] or not (8.5<=s['size']<=11.5) or not LETTER.search(s['text']):continue
        t=s['text'].strip()
        if t in ['Akl','Mdl','Tb','Adt','Ark']:continue
        candidates.append({'spanIndex':i,'s':s,'text':t})
    consumed=set()
    for ci,c in enumerate(candidates):
        if ci in consumed:continue
        s=c['s'];text=c['text'];parts=[text];end_i=c['spanIndex'];join_state='intact'
        # Line-wrapped bold words. Join candidates but retain fragments and review status.
        while parts[-1].endswith('-') and ci+len(parts)<len(candidates):
            ni=ci+len(parts);n=candidates[ni];ns=n['s'];last=candidates[ni-1]['s']
            next_line=ns['page']==last['page'] and ns['column']==last['column'] and 8<ns['origin'][1]-last['origin'][1]<16
            if not next_line or not re.match(r'^[a-z]',n['text']):break
            parts.append(n['text']);consumed.add(ni);end_i=n['spanIndex'];join_state='joined_needs_review'
        if len(parts)>1:
            text=''.join(p[:-1] if p.endswith('-') else p for p in parts)
        # Adjacent same-line bold runs can be a single lexical form split by font changes.
        if ci+len(parts)<len(candidates):
            ni=ci+len(parts);n=candidates[ni];ns=n['s']
            intervening=all_spans[end_i+1:n['spanIndex']]
            if ni not in consumed and ns['page']==s['page'] and ns['column']==s['column'] and abs(ns['origin'][1]-s['origin'][1])<1 and not any(ss['text'].strip() for ss in intervening) and not text.endswith((',',':',';')):
                text+=' '+n['text'];consumed.add(ni);end_i=n['spanIndex']
        # Gather following text in source reading order for structural classification only.
        following=[]
        for ss in all_spans[end_i+1:end_i+25]:
            if ss['page']!=s['page'] or ss['column']!=s['column']:break
            if 'Bold' in ss['font'] and LETTER.search(ss['text']) and 'Italic' not in ss['font']:break
            following.append(ss['text'])
        tail=' '.join(following);tail=re.sub(r'\s+',' ',tail).strip()
        at_margin=(s['bbox'][0]-(42.6 if s['column']==0 else 230.64))<7
        kind='headword' if tail.startswith('[') or '[' in text else ('cross_reference' if '→' in text or tail.startswith('→') else 'subentry')
        if '[' in text:text=text.split('[',1)[0].strip()
        superscript=''
        if kind=='headword':
            for prev in all_spans[max(0,c['spanIndex']-3):c['spanIndex']]:
                if prev['page']==s['page'] and prev['column']==s['column'] and prev['text'].strip().isdigit() and prev['size']<8 and abs(prev['bbox'][2]-s['bbox'][0])<5 and 0<=s['origin'][1]-prev['origin'][1]<7:superscript=prev['text'].strip()
        target=''
        if '→' in text:text,target=text.split('→',1);kind='cross_reference'
        elif '→' in tail:target=tail.split('→',1)[1]
        text=text.strip(' ,;:.()\t')
        # References/alternatives separated by commas are distinct printed forms.
        chunks=[x.strip(' ,;:.()') for x in re.split(r'[,;]',text) if x.strip(' ,;:.()')]
        for form in chunks:
            form=re.sub(r'\s+',' ',form).strip()
            form=re.sub(r'\s+\d+$','',form)
            if not form or not LETTER.search(form):continue
            record={'form':form,'printedPage':s['page'],'pdfPage':s['pdfPage'],'column':s['column']+1,
                    'x':round(s['bbox'][0],2),'y':round(s['bbox'][1],2),'kind':kind,'homonym':superscript,
                    'layoutStatus':join_state,'printedFragments':parts if len(parts)>1 else [],
                    'atMargin':at_margin,'sourceIndex':len(raw),'tags':[], 'partOfSpeech':'','crossReference':target.strip(' ;,.')[:100]}
            # Only labels before the definition; never import a label from an example.
            structural=tail.split(':',1)[0].split(';',1)[0]
            if kind=='headword':
                structural=re.sub(r'^\[[^\]]{0,90}[\])]?','',structural).strip()
            m=POS.search(structural)
            record['tags']=list(dict.fromkeys(LABELS.findall(structural[:150])))
            record['partOfSpeech']=m[1] if m else ''
            if (not FORM.fullmatch(form) and not re.fullmatch(r'-?[A-Za-z]+-?',form)) or len(form)>100 or any(w in form.split() for w in ['n','v','adv','pron','num']):
                record['layoutStatus']='needs_review'
            if form.startswith('-') or form.endswith('-'):record['boundForm']=True
            raw.append(record)
    overrides=json.loads((Path(__file__).parent/'inventory_overrides.json').read_text())
    for fix in overrides['normalizations']:
        matches=[r for r in raw if r['printedPage']==fix['page'] and r['form']==fix['from']]
        assert len(matches)==1,fix
        r=matches[0];r['printedNotation']=fix.get('printedNotation','');r['form']=fix['to'];r['layoutStatus']='visually_reviewed';r['normalizationNote']=fix['reason']
    for fix in overrides['headwordCorrections']:
        matches=[r for r in raw if r['printedPage']==fix['page'] and r['form']==fix['form']]
        if fix['form']=='jolo':matches=matches[:1]
        assert len(matches)==1,fix
        matches[0]['kind']=fix['kind'];matches[0]['normalizationNote']=fix['reason']
    for fix in overrides['crossReferences']:
        for r in raw:
            if r['printedPage']==fix['page'] and r['form']==fix['form'] and r['kind']=='cross_reference':r['crossReference']=fix['target']
    # The unbolded expansion is explicitly given in a headword abbreviation, not inferred.
    doba=next(r for r in raw if r['form']=='doba' and r['printedPage']==93)
    expansion=dict(doba);expansion.update(form='dohoba',kind='abbreviation_expansion',homonym='',sourceIndex=doba['sourceIndex']+0.5)
    raw.append(expansion);raw.sort(key=lambda r:r['sourceIndex'])
    # A line join is considered confirmed only if the entire spelling is also printed intact.
    intact={r['form'].casefold() for r in raw if r['layoutStatus']=='intact'}
    for r in raw:
        if r['layoutStatus']=='joined_needs_review' and r['form'].casefold() in intact:r['layoutStatus']='joined_confirmed'
    # Link subentries to the preceding main entry, including across columns and pages.
    parent=None
    for r in raw:
        if r['kind']=='headword':parent=r
        r['parentForm']=parent['form'] if parent else ''
        r['parentPage']=parent['printedPage'] if parent else None
        r['parentHomonym']=parent['homonym'] if parent else ''
        r['parentTags']=parent['tags'] if parent else []
    counts=collections.Counter(r['printedPage'] for r in raw)
    for p in pages:p['records']=counts[p['printedPage']]
    return {'sourceId':'dictionary','sourceSha256':hashlib.sha256(Path(pdf_path).read_bytes()).hexdigest(),
            'version':'inventory-2021-v1','records':raw,'pages':pages,
            'notes':['Printed lexical forms only; definitions and examples are not bulk-copied.','Extraction is a source inventory, not speaker validation. Layout exceptions remain explicitly flagged.']}

if __name__=='__main__':
    result=extract(sys.argv[1]);Path(sys.argv[2]).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    rs=result['records'];print(json.dumps({'records':len(rs),'uniqueForms':len({r['form'].casefold() for r in rs}),
       'kinds':dict(collections.Counter(r['kind'] for r in rs)),'layout':dict(collections.Counter(r['layoutStatus'] for r in rs)),
       'pagesWithRecords':sum(p['records']>0 for p in result['pages'])},ensure_ascii=False))
