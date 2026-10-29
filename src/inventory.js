  const BANK = JSON.parse($('#inventory-data').textContent);
  const bankEntries = new Map(SEED.map(w=>[w.id,w]));
  const bankById = new Map(BANK.forms.map(f=>[f.id,f]));
  const bankState = {query:'',letter:'all',kind:'all',scope:'all',status:'all',source:'all',page:1};
  const BANK_SIZE=24;
  const bankKinds={headword:'Lema',subentry:'Turunan / gabungan',cross_reference:'Rujuk silang',abbreviation_expansion:'Perluasan singkatan',bound_form:'Bentuk terikat',compound:'Gabungan kata',reference_example:'Contoh ejaan',number_list:'Daftar bilangan / ukuran',historical_form:'Bentuk kamus 1977',wordlist_entry:'Entri daftar kata',study_table:'Bentuk pada penelitian',publisher_abstract:'Abstrak penerbit',idiom:'Idiom / ungkapan',cultural_term:'Istilah budaya',botanical_name:'Nama botani pada sumber'};
  const bankLabels={Mdl:'Label Mdl',Akl:'Angkola',Tb:'Toba',unmarked:'Tanpa label per bentuk',Tapsel:'Tapsel','Mdl-scope':'Cakupan studi Mandailing',MA:'Mandailing–Angkola (MA)',Sipirok:'Catatan dialek Sipirok'};
  const bankSourceName=id=>{const s=SOURCES.find(s=>s.id===id);return s?.shortTitle||s?.title||id;};
  const bankSourceLocation=ref=>ref.pdfPage?'Hlm. cetak '+ref.printedPage+' · PDF '+ref.pdfPage:ref.sourceLocator||'Halaman sumber';
  const bankSelectedReferences=f=>bankState.source==='all'?f.references:f.references.filter(ref=>ref.sourceId===bankState.source);
  const bankLetter=f=>normalize(f.form).replace(/^-+/,'').charAt(0).toUpperCase();
  const bankByNormalizedForm=new Map(BANK.forms.map(f=>[normalize(f.form),f]));
  const bankLetterCounts={};
  for(const f of BANK.forms){const l=bankLetter(f);bankLetterCounts[l]=(bankLetterCounts[l]||0)+1;}
  const bankSearchText=new Map(BANK.forms.map(f=>{
    const w=bankEntries.get(f.entryId);
    return [f.id,normalize([f.form,...f.references.flatMap(ref=>[ref.parent,ref.sourceGloss,ref.taxonAsPrinted]),...(w?[w.idn,w.my,w.en,...(w.aliases||[])]:[])].join(' '))];
  }));
  function bankFiltered(){
    const q=normalize(bankState.query);
    return BANK.forms.filter(f=>{
      const refs=bankSelectedReferences(f);
      if(!refs.length)return false;
      if(bankState.letter!=='all'&&bankLetter(f)!==bankState.letter)return false;
      if(bankState.kind!=='all'&&!(['bound_form','compound'].includes(bankState.kind)?f.kinds.includes(bankState.kind):refs.some(ref=>ref.kind===bankState.kind)))return false;
      if(bankState.scope!=='all'&&!refs.some(ref=>ref.labels.includes(bankState.scope)))return false;
      if(bankState.status==='reviewed'&&!f.entryId||bankState.status==='pending'&&f.entryId)return false;
      if(bankState.status==='source-gloss'&&!refs.some(ref=>ref.sourceGloss))return false;
      if(!q)return true;
      if(bankState.source==='all')return bankSearchText.get(f.id).includes(q);
      const w=bankEntries.get(f.entryId);
      return normalize([f.form,...refs.flatMap(ref=>[ref.parent,ref.sourceGloss,ref.taxonAsPrinted]),...(w?[w.idn,w.my,w.en,...(w.aliases||[])]:[])].join(' ')).includes(q);
    });
  }
  function renderBank(){
    const items=bankFiltered(),pages=Math.max(1,Math.ceil(items.length/BANK_SIZE));bankState.page=Math.min(Math.max(1,bankState.page),pages);
    $('#bank-count').textContent=items.length.toLocaleString('id-ID')+' bentuk cocok · '+BANK.stats.uniqueForms.toLocaleString('id-ID')+' bentuk dalam bank';
    $('#bank-letters').innerHTML='<button data-bank-letter="all" class="letter-button '+(bankState.letter==='all'?'active':'')+'" aria-pressed="'+(bankState.letter==='all')+'">Semua</button>'+RESEARCH.alphabet.split('').map(l=>'<button class="letter-button '+(bankState.letter===l?'active':'')+'" data-bank-letter="'+l+'" aria-pressed="'+(bankState.letter===l)+'" aria-label="Bank huruf '+l+'">'+l+'<small>'+(bankLetterCounts[l]||0)+'</small></button>').join('');
    const slice=items.slice((bankState.page-1)*BANK_SIZE,bankState.page*BANK_SIZE);
    $('#bank-results').innerHTML=slice.length?'<div class="bank-grid">'+slice.map(f=>{
      const w=bankEntries.get(f.entryId),refs=bankSelectedReferences(f),labels=[...new Set(refs.flatMap(ref=>ref.labels))].map(l=>bankLabels[l]||l).join(' · ');
      const mainKind=f.kinds.includes('bound_form')?'Bentuk terikat':refs.some(ref=>ref.kind==='headword')?'Lema':bankKinds[refs[0]?.kind]||'Bentuk sumber';
      const glossRef=refs.find(ref=>ref.sourceGloss&&ref.glossLanguage==='id')||refs.find(ref=>ref.sourceGloss);
      const taxonRef=refs.find(ref=>ref.taxonAsPrinted);
      const meaning=w?esc(w.idn):glossRef?'<span class="bank-gloss-label">Glos sumber ('+esc(glossRef.glossLanguage)+')</span>'+esc(glossRef.sourceGloss):taxonRef?'<span class="bank-gloss-label">Takson pada sumber</span>'+esc(taxonRef.taxonAsPrinted):'Padanan belum ditelaah';
      return '<article class="bank-card"><div class="bank-card-meta"><span>'+esc(mainKind)+'</span><span class="bank-label">'+esc(labels)+'</span></div><button class="bank-term" data-bank-open="'+f.id+'">'+esc(f.form)+'</button><p class="bank-meaning '+(!w?'pending':'')+'">'+meaning+'</p><div class="bank-card-bottom"><small>'+f.references.length+' lokasi sumber</small><button data-bank-open="'+f.id+'" aria-label="Lihat sumber bentuk '+esc(f.form)+'">Lihat sumber '+icon('arrow')+'</button></div></article>';
    }).join('')+'</div>':'<div class="empty-state"><h3>Belum ada bentuk yang cocok.</h3><p>Huruf atau gabungan filter ini tidak mempunyai hasil dalam inventaris. Huruf kosong tidak diisi dengan kata rekaan.</p><button class="button button-outline" data-bank-reset="true">Reset filter bank</button></div>';
    $('#bank-pagination').innerHTML=items.length?'<p>Halaman '+bankState.page+' dari '+pages+' · '+((bankState.page-1)*BANK_SIZE+1)+'–'+Math.min(bankState.page*BANK_SIZE,items.length)+' dari '+items.length+'</p><div><button class="button button-outline button-small" data-bank-page="'+(bankState.page-1)+'" '+(bankState.page===1?'disabled':'')+'>Sebelumnya</button><button class="button button-outline button-small" data-bank-page="'+(bankState.page+1)+'" '+(bankState.page===pages?'disabled':'')+'>Berikutnya</button></div>':'';
  }
  function openBankDetail(id){
    const f=bankById.get(id);if(!f)return;const w=bankEntries.get(f.entryId);
    const refs=f.references.map(ref=>{
      const source=SOURCES.find(s=>s.id===ref.sourceId);
      return '<section class="evidence-panel"><h3>'+esc(bankKinds[ref.kind]||ref.kind)+' · '+esc(bankSourceName(ref.sourceId))+'</h3>'+
        '<p><a href="'+esc(sourcePageUrl(ref))+'" target="_blank" rel="noopener noreferrer">'+esc(bankSourceLocation(ref))+' '+icon('external')+'</a></p>'+
        '<p>Induk: '+esc(ref.parent||'—')+(ref.homonym?' · homonim '+esc(ref.homonym):'')+'<br>Label: '+esc(ref.labels.map(l=>bankLabels[l]||l).join(', '))+(ref.labelBasis==='parent'?' · mengikuti induk lema':'')+'</p>'+
        '<p>'+esc(ref.sourceScope||source?.use||'')+'</p>'+
        (ref.sourceGloss?'<p><strong>Glos konsep sumber ('+esc(ref.glossLanguage)+'):</strong> '+esc(ref.sourceGloss)+'. Glos ini belum menjadi padanan kurasi.</p>':'')+
        (ref.taxonAsPrinted?'<p><strong>Takson pada sumber:</strong> '+esc(ref.taxonAsPrinted)+'. Nama ilmiah mengikuti cetakan sumber; identitas spesies dan ejaannya tidak otomatis disamakan dengan sumber lain.</p>':'')+
        (ref.annotation?'<p>Catatan sumber: '+esc(ref.annotation)+'</p>':'')+
        (ref.crossReference?'<p>Rujuk silang ke '+esc(ref.crossReference)+'.</p>':'')+
        (ref.printedNotation?'<p>Notasi cetak: '+esc(ref.printedNotation)+'.</p>':'')+
        (ref.normalizationNote?'<p>'+esc(ref.normalizationNote)+'</p>':'')+'</section>';
    }).join('');
    $('#bank-detail').innerHTML='<div class="modal-topline"><span class="eyebrow">INVENTARIS SUMBER · '+esc(f.status==='reviewed_translations'?'PADANAN TERSEDIA':'PADANAN BELUM DITELAAH')+'</span><button class="icon-button" data-close="bank-modal" aria-label="Tutup sumber bentuk">'+icon('close')+'</button></div><h2 id="bank-detail-title">'+esc(f.form)+'</h2><p class="detail-note">'+esc(f.kinds.map(k=>bankKinds[k]||k).join(' · '))+'</p>'+
      (w?'<div class="detail-translations">'+Object.entries(LANGUAGES).map(([k,l])=>'<div><span class="language-label">'+l+'</span><strong>'+esc(w[k])+'</strong></div>').join('')+'</div><p class="detail-note">Padanan mengikuti satu makna dalam koleksi berpadanan, bukan otomatis semua homonim di bawah ini.</p><button class="button button-outline" data-bank-reviewed="'+esc(w.id)+'">Buka entri berpadanan</button>':'<p class="bank-pending-note">Bentuk ini tercatat pada sumber. Padanan Indonesia, Melayu Malaysia, Inggris, serta contoh kalimat belum ditelaah untuk bank ini. Kolom tersebut tetap kosong dalam database.</p>')+
      '<p class="detail-note">Label per bentuk dibedakan dari cakupan bahasa suatu penelitian. Tanpa label per bentuk bukan berarti Mandailing eksklusif. Angkola, Toba, Tapsel dan catatan dialek lain tetap diberi keterangan.</p>'+
      (f.usageTags.length?'<p class="detail-note">Label pemakaian sumber: '+esc(f.usageTags.join(', '))+'. tdk berarti tidak dikenal menurut petunjuk sumber; Ark berarti arkais.</p>':'')+'<div class="bank-reference-list">'+refs+'</div>';
    $('#bank-modal').showModal();
  }
  function renderLocalNames(){
    const q=normalize($('#local-name-search').value);
    const status=$('#local-name-status').value||'all';
    const supported=r=>['cross_source_supported','combined_scope_supported','study_scope_supported'].includes(r.review?.status);
    const names=(BANK.localNames||[]).filter(r=>normalize(r.name+' '+bankSourceName(r.sourceId)+' '+(r.taxonAsPrinted||'')+' '+(r.taxonExpanded||'')).includes(q)&&
      (status==='all'||status==='supported'&&supported(r)||status==='pending'&&r.review?.status==='pending_language_and_meaning'||status==='needs-check'&&!supported(r)&&r.review?.status!=='pending_language_and_meaning'));
    $('#local-name-count').textContent=names.length+' catatan cocok';
    $('#local-name-results').innerHTML=names.length?names.map(r=>{
      const f=bankByNormalizedForm.get(normalize(r.name));
      const review=r.review;
      const reviewNote=review&&review.status!=='pending_language_and_meaning'?'<p class="plant-review-note '+(supported(r)?'supported':'caution')+'">'+esc(review.note)+'</p>':'';
      return '<article><strong>'+esc(r.name)+'</strong><p>'+esc(bankSourceName(r.sourceId))+'</p><p class="local-name-taxon">'+(r.taxonAsPrinted?'Takson pada sumber: <em>'+esc(r.taxonAsPrinted)+'</em>':'Nama ilmiah tidak diisi pada sumber')+'</p><a href="'+esc(sourcePageUrl(r))+'" target="_blank" rel="noopener noreferrer">'+esc(bankSourceLocation(r))+' '+icon('external')+'</a>'+reviewNote+(review?.evidence?.length?'<p>'+review.evidence.map((e,i)=>e.url?'<a href="'+esc(e.url)+'" target="_blank" rel="noopener noreferrer">Bukti silang '+(i+1)+' ↗</a>':'').filter(Boolean).join(' · ')+'</p>':'')+(f?'<button data-bank-open="'+f.id+'">Kecocokan ejaan dalam bank · makna perlu diperiksa</button>':'')+'</article>';
    }).join(''):'<p>Belum ada nama yang cocok.</p>';
  }
  function exportBankLabels(){
    const rows=bankFiltered().map(f=>{
      const w=bankEntries.get(f.entryId),refs=bankSelectedReferences(f);
      const labels=[...new Set(refs.flatMap(ref=>ref.labels))],kinds=[...new Set([...refs.map(ref=>ref.kind),...f.kinds.filter(kind=>['bound_form','compound'].includes(kind))])];
      return [f.form,w?.idn||'',w?.my||'',w?.en||'',labels.join(', '),kinds.join(', '),f.status,f.id,[...new Set(refs.map(r=>r.sourceId))].join(', ')];
    });
    const text=[['Bentuk sumber','Indonesia','Melayu Malaysia','English','Label sumber','Jenis','Status padanan','ID bentuk','Sumber'],...rows].map(row=>row.map(plain).join('\t')).join('\n');
    download('hata-bank-berlabel-'+rows.length+'.tsv','\uFEFF'+text,'text/tab-separated-values;charset=utf-8');
    toast(rows.length+' bentuk diekspor beserta label sumber.');
  }
  function exportLocalNames(){
    const text=[['Nama dalam tabel','Takson pada sumber','Sumber','Halaman cetak','Halaman PDF','Status bahasa asli','Status telaah','Catatan telaah','Cakupan'],...(BANK.localNames||[]).map(r=>[r.name,r.taxonAsPrinted||'',r.sourceId,r.printedPage,r.pdfPage,r.languageStatus,r.review?.status||'',r.review?.note||'',r.scope])].map(row=>row.map(plain).join('\t')).join('\n');
    download('hata-telaah-nama-tumbuhan.tsv','\uFEFF'+text,'text/tab-separated-values;charset=utf-8');
  }
  function exportBankTSV(){
    const rows=bankFiltered().map(f=>{
      const w=bankEntries.get(f.entryId);return [f.form,w?.idn||'',w?.my||'',w?.en||'',w?exampleCell(w):''];
    });
    const content=[['Mandailing','Indonesia','Melayu Malaysia','English','Contoh Kalimat'],...rows].map(row=>row.map(plain).join('\t')).join('\n');
    download('hata-bank-'+rows.length+'-bentuk.tsv','\uFEFF'+content,'text/tab-separated-values;charset=utf-8');toast(rows.length+' bentuk diekspor; padanan yang belum ditelaah tetap kosong.');
  }
  $('#bank-search').addEventListener('input',event=>{bankState.query=event.target.value;bankState.page=1;renderBank();});
  for(const [id,key] of [['bank-kind','kind'],['bank-scope','scope'],['bank-status','status'],['bank-source','source']])$('#'+id).addEventListener('change',event=>{bankState[key]=event.target.value;bankState.page=1;renderBank();});
  document.addEventListener('click',event=>{
    const b=event.target.closest('button');if(!b||b.disabled)return;
    if(b.dataset.bankLetter){bankState.letter=b.dataset.bankLetter;bankState.page=1;renderBank();}
    if(b.dataset.bankOpen)openBankDetail(b.dataset.bankOpen);
    if(b.dataset.bankReviewed){$('#bank-modal').close();openDetail(b.dataset.bankReviewed);}
    if(b.dataset.bankPage){bankState.page=Number(b.dataset.bankPage);renderBank();$('#bank-count').scrollIntoView({block:'start',behavior:'smooth'});}
    if(b.dataset.bankReset){Object.assign(bankState,{query:'',letter:'all',kind:'all',scope:'all',status:'all',source:'all',page:1});$('#bank-search').value='';for(const id of ['bank-kind','bank-scope','bank-status','bank-source'])$('#'+id).value='all';renderBank();}
    if(b.id==='bank-export')exportBankTSV();
    if(b.id==='bank-export-labels')exportBankLabels();
    if(b.id==='local-name-export')exportLocalNames();
  });
  for(const element of $$('[data-bank-total]'))element.textContent=BANK.stats.uniqueForms.toLocaleString('id-ID');
  for(const element of $$('[data-bank-pending]'))element.textContent=BANK.stats.pendingTranslations.toLocaleString('id-ID');
  $('#bank-source-records').textContent=BANK.stats.referenceRecords.toLocaleString('id-ID');
  $('#bank-source-total').textContent=BANK.stats.sourceCount;
  const researchUpdate=BANK.researchUpdate;
  $('#research-update-summary').textContent=BANK.stats.releaseAddedUniqueForms.toLocaleString('id-ID')+' bentuk baru dan '+BANK.stats.releaseAddedReferences.toLocaleString('id-ID')+' rujukan tambahan dari penelaahan sumber. Isi buku yang belum diperoleh tetap ditandai.';
  $('#source-audit-summary').textContent=researchUpdate.phase+' · '+researchUpdate.date+' · '+BANK.stats.uniqueForms.toLocaleString('id-ID')+' bentuk tersimpan. '+researchUpdate.supportedPlantNames+' dari '+researchUpdate.plantNames+' nama–takson mendapat dukungan silang dengan cakupan yang dibedakan. '+researchUpdate.plantTaxa+' nama ilmiah asal tersimpan; satu baris sumber kosong. Glos sumber dibedakan dari padanan multibahasa yang dikurasi.';
  $('#source-audit-cards').innerHTML=researchUpdate.cards.map(card=>'<article><h3>'+esc(card.title)+'</h3><strong>'+esc(card.status)+'</strong><p>'+esc(card.detail)+'</p><a href="'+esc(card.url)+'" target="_blank" rel="noopener noreferrer">Lihat bukti dan cakupan ↗</a></article>').join('');
  $('#research-update-link').href=researchUpdate.reportUrl;
  $('#bank-source').innerHTML='<option value="all">Semua sumber bentuk</option>'+Object.keys(BANK.stats.recordsBySource).map(id=>'<option value="'+esc(id)+'">'+esc(bankSourceName(id))+'</option>').join('');
  for(const el of $$('[data-local-count]'))el.textContent=BANK.stats.localNameObservations;
  $('#local-name-search').addEventListener('input',renderLocalNames);
  $('#local-name-status').addEventListener('change',renderLocalNames);
  renderLocalNames();
