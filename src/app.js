(() => {
  "use strict";
  const $ = (selector) => document.querySelector(selector);
  const $$ = (selector) => [...document.querySelectorAll(selector)];
  const SEED = JSON.parse($("#seed-data").textContent);
  const INITIAL = JSON.parse($("#initial-state").textContent);
  const RESEARCH = JSON.parse($("#research-data").textContent);
  const KEY = "hata-mandailing-v1";
  const CATEGORIES = {
    all: {label:"Semua", title:"Semua kosakata", icon:"grid"},
    ganti: {label:"Kata ganti & tanya", title:"Kata ganti & kata tanya", icon:"people"},
    angka: {label:"Angka", title:"Angka sehari-hari", icon:"hash"},
    kerja: {label:"Kata kerja", title:"Kata kerja sehari-hari", icon:"sparkle"},
    rumah: {label:"Di rumah", title:"Benda & kebutuhan di rumah", icon:"home"},
    sifat: {label:"Sifat & keadaan", title:"Sifat & keadaan", icon:"sparkle"},
    alam: {label:"Alam & sekitar", title:"Alam & lingkungan sekitar", icon:"globe"},
    orang: {label:"Orang & tubuh", title:"Orang, keluarga & tubuh", icon:"people"},
    tugas: {label:"Kata tugas", title:"Kata tugas & penghubung", icon:"feather"},
    umum: {label:"Waktu & sosial", title:"Waktu & kehidupan sosial", icon:"book"}
  };
  const LANGUAGES = {idn:"Indonesia",my:"Melayu Malaysia",en:"English"};
  const SOURCES = JSON.parse($("#source-data").textContent);
  const PATHS = {
    book:'<path d="M12 5C8 2.8 4.7 3 2 4.5v15c3-1.5 6-1.5 10 .5m0-15c4-2.2 7.3-2 10-.5v15c-3-1.5-6-1.5-10 .5m0-15v15"/>',
    bookmark:'<path d="M6 4h12v17l-6-4-6 4V4Z"/>',
    layers:'<path d="m12 3 10 6-10 6L2 9l10-6Zm-10 11 10 6 10-6M2 18l10 6 10-6" transform="translate(0 -1)"/>',
    feather:'<path d="M20 3c-5-1-12 3-13 8l-1 7 7-1c5-1 9-8 7-14ZM3 21 16 8M9 15l5 1M9 10l-1 5"/>',
    globe:'<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c5 4 5 14 0 18-5-4-5-14 0-18Z"/>',
    plus:'<path d="M12 5v14M5 12h14"/>',
    arrow:'<path d="M4 12h15m-5-5 5 5-5 5"/>',
    left:'<path d="m14 5-7 7 7 7"/>',
    right:'<path d="m10 5 7 7-7 7"/>',
    down:'<path d="m6 9 6 6 6-6"/>',
    search:'<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>',
    close:'<path d="m6 6 12 12M6 18 18 6"/>',
    grid:'<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
    list:'<path d="M8 5h13M8 12h13M8 19h13M3 5h.1M3 12h.1M3 19h.1"/>',
    table:'<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 10h18M10 4v16"/>',
    download:'<path d="M12 3v12m-5-5 5 5 5-5M4 16v5h16v-5"/>',
    info:'<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7h.01"/>',
    check:'<path d="m5 12 4 4L20 5"/>',
    copy:'<rect x="8" y="8" width="12" height="13" rx="2"/><path d="M16 8V3H3v13h5"/>',
    sparkle:'<path d="m12 3 2.5 6.5L21 12l-6.5 2.5L12 21l-2.5-6.5L3 12l6.5-2.5L12 3Z"/>',
    people:'<circle cx="9" cy="7" r="3"/><path d="M3 21v-3a6 6 0 0 1 12 0v3M16 4a3 3 0 0 1 0 6m1 5a5 5 0 0 1 4 5"/>',
    hash:'<path d="M9 3 6 21M18 3l-3 18M3 9h18M2 16h18"/>',
    home:'<path d="m2 11 10-8 10 8M5 9v12h14V9M9 21v-7h6v7"/>',
    external:'<path d="M14 3h7v7m-1-6L10 14M11 3H3v18h18v-8"/>',
    bulb:'<path d="M8 17c0-2-4-4-4-8a8 8 0 0 1 16 0c0 4-4 6-4 8M8 17h8M9 21h6M12 17v-6m-3-2 3 2 3-2"/>',
    shuffle:'<path d="m3 5 4 1 10 13h4m-4-4 4 4-4 3M3 19l4-1L17 5h4m-4-3 4 3-4 4"/>'
  };
  const icon = (name) => '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'+(PATHS[name]||PATHS.book)+'</svg>';
  const esc = (value) => String(value??"").replace(/[&<>"']/g, character => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[character]));
  const normalize = (text) => String(text??"").normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLocaleLowerCase("id").trim();
  const plain = (text) => String(text??"").replace(/[\t\r\n]+/g," ").trim();
  const isAttested = word => word.status === "source_attested";
  const statusLabel = word => isAttested(word)?"Entri dirujuk":word.status==="personal"?"Kata pribadi":"Draf awal";
  const exampleLabel = word => word.status==="personal"?"Contoh pribadi · draf":word.exampleStatus==="source_quoted"?"Contoh dari rujukan":word.exampleStatus==="pending"?"Contoh belum tersedia":"Contoh latihan · draf";
  const sourcePageUrl = ref => {
    const source=SOURCES.find(s=>s.id===(ref.sourceId||ref.id));
    const base=ref.url||source?.documentUrl||source?.url||'';
    return ref.pdfPage&&source?.documentUrl&&(!ref.url||ref.url===source.documentUrl)?base.split('#')[0]+'#page='+ref.pdfPage:base;
  };
  const scopeLabel = word => !word.sourceRef?"Belum ditelaah per halaman":word.sourceRef.languageLabel==="Tapsel"?"Cakupan Tapsel":word.sourceRef.languageLabel==="Mdl"?"Label Mdl":word.sourceRef.languageLabel==="shared-pronunciation"?"Lafal Mdl tercatat":"Angkola–Mandailing";
  const statusMarkup = word => '<span class="entry-status '+(isAttested(word)?'attested':'draft')+'">'+esc(statusLabel(word))+'</span>';
  const seedIds = new Set(SEED.map(word=>word.id));
  const emptyState = () => ({fav:Array.isArray(INITIAL.fav)?INITIAL.fav:[],known:Array.isArray(INITIAL.known)?INITIAL.known:[],custom:[]});
  let local = emptyState();
  let storageAvailable = true;
  try {
    const stored = localStorage.getItem(KEY);
    if(stored) {
      const candidate=JSON.parse(stored);
      local.fav=Array.isArray(candidate.fav)?candidate.fav.filter(v=>typeof v==="string"):[];
      local.known=Array.isArray(candidate.known)?candidate.known.filter(v=>typeof v==="string"):[];
      local.custom=Array.isArray(candidate.custom)?candidate.custom.filter(word=>word&&typeof word.id==="string"&&typeof word.md==="string"&&typeof word.idn==="string"&&typeof word.my==="string"&&typeof word.en==="string"&&CATEGORIES[word.category]&&word.category!=="all"&&!seedIds.has(word.id)):[];
    }
  } catch { storageAvailable=false; }
  let fav=new Set(local.fav), known=new Set(local.known);
  let state={view:"dictionary",query:"",language:"all",category:"all",letter:"all",status:"all",sort:"az",layout:"grid",page:1,expanded:new Set()};
  let deck=[],deckIndex=0,revealed=false,sessionKnown=0,toastTimer;
  const PAGE_SIZE=12;
  function words(){
    const map=new Map(SEED.map(word=>[word.id,{...word}]));
    const spellings=new Map();
    for(const word of SEED){spellings.set(normalize(word.md),word.id);for(const alias of word.aliases||[])if(!spellings.has(normalize(alias)))spellings.set(normalize(alias),word.id);}
    for(const word of local.custom){
      const seedId=spellings.get(normalize(word.md));
      if(seedId){const entry=map.get(seedId);entry.personalAlternatives=[...(entry.personalAlternatives||[]),word];}
      else map.set(word.id,word);
    }
    return [...map.values()];
  }
  function byId(id){return words().find(word=>word.id===id||(word.personalAlternatives||[]).some(item=>item.id===id));}
  function persist(){
    local.fav=[...fav];local.known=[...known];
    try{localStorage.setItem(KEY,JSON.stringify(local));storageAvailable=true;return true;}
    catch{storageAvailable=false;toast("Penyimpanan peramban tidak tersedia. Ekspor TSV untuk menyimpan kosakata sesi ini; progres tidak ikut dicadangkan.");return false;}
  }
  function toast(message){
    clearTimeout(toastTimer);$("#toast").textContent=message;$("#toast").classList.add("show");
    toastTimer=setTimeout(()=>$("#toast").classList.remove("show"),3800);
  }
  function filtered(){
    const query=normalize(state.query);
    return words().filter(word=>{
      if(state.view==="saved"&&!fav.has(word.id))return false;
      if(state.category!=="all"&&word.category!==state.category)return false;
      if(state.letter!=="all"&&normalize(word.md).charAt(0)!==state.letter.toLowerCase())return false;
      if(state.status==="attested"&&!isAttested(word))return false;
      if(state.status==="draft"&&word.status!=="draft")return false;
      if(state.status==="personal"&&word.status!=="personal")return false;
      if(!query)return true;
      const fields=state.language==="all"?["md","idn","my","en"]:[state.language];
      return fields.some(field=>normalize(word[field]).includes(query))||
        ((state.language==="all"||state.language==="md")&&(word.aliases||[]).some(alias=>normalize(alias).includes(query)));
    }).sort((a,b)=>state.sort==="original"?0:state.sort==="za"?b.md.localeCompare(a.md,"id"):a.md.localeCompare(b.md,"id"));
  }
  function syncCounts(){
    const list=words(),validIds=new Set(list.map(word=>word.id));
    const savedCount=[...fav].filter(id=>validIds.has(id)).length;
    const learnedCount=[...known].filter(id=>validIds.has(id)).length;
    $("#nav-saved-count").textContent=savedCount;
    $("#hero-word-count").textContent=list.length;
    $("#sidebar-word-count").textContent=list.length;
    $("#known-count").textContent=learnedCount;
    $("#progress-orbit").style.background='conic-gradient(var(--wine) '+(learnedCount/list.length*360)+'deg, #e4d8c8 0deg)';
    $("#progress-copy").textContent=learnedCount?learnedCount+" dari "+list.length+" kata sudah Anda pahami.":"Mulai dari satu kata hari ini.";
  }
  function renderCategories(){
    const pool=words().filter(word=>(state.view!=="saved"||fav.has(word.id))&&(state.letter==="all"||normalize(word.md).startsWith(state.letter.toLowerCase()))&&(state.status==="all"||state.status==="attested"&&isAttested(word)||state.status==="draft"&&word.status==="draft"||state.status==="personal"&&word.status==="personal"));
    $("#category-bar").innerHTML=Object.entries(CATEGORIES).map(([key,cat])=>{
      const count=pool.filter(word=>key==="all"||word.category===key).length;
      return '<button class="category '+(state.category===key?"active":"")+'" data-category="'+key+'" aria-pressed="'+(state.category===key)+'">'+esc(cat.label)+'<span>'+count+'</span></button>';
    }).join("");
  }
  function renderAlphabet(){
    const pool=words().filter(word=>state.view!=="saved"||fav.has(word.id));
    $("#alphabet-bar").innerHTML=RESEARCH.alphabet.split("").map(letter=>{
      const count=pool.filter(word=>normalize(word.md).startsWith(letter.toLowerCase())).length;
      return '<button class="letter-button '+(state.letter===letter?'active':'')+'" data-letter="'+letter+'" aria-pressed="'+(state.letter===letter)+'" aria-label="Huruf '+letter+', '+count+' entri" title="'+count+' entri dalam koleksi; bukan ukuran kelengkapan bahasa">'+letter+'<small>'+count+'</small></button>';
    }).join("");
    $("#all-letters").classList.toggle("active",state.letter==="all");
    $("#all-letters").setAttribute("aria-pressed",String(state.letter==="all"));
    $("#editorial-filter").value=state.status;
    $("#active-filter-copy").textContent=(state.letter==='all'?'Semua huruf':'Huruf '+state.letter)+' · '+({all:'semua status',attested:'entri dirujuk',draft:'draf awal',personal:'kata pribadi'}[state.status]);
  }
  function favoriteButton(word){
    const selected=fav.has(word.id);
    return '<button class="icon-button '+(selected?"saved":"")+'" data-save="'+esc(word.id)+'" aria-label="'+(selected?"Hapus dari":"Simpan ke")+' favorit: '+esc(word.md)+'" aria-pressed="'+selected+'">'+icon("bookmark")+'</button>';
  }
  function card(word){
    const open=state.expanded.has(word.id),cat=CATEGORIES[word.category]||CATEGORIES.umum;
    return '<article class="word-card" data-word-id="'+esc(word.id)+'"><div class="word-card-main"><div class="word-card-top"><span class="category-label '+word.category+'">'+icon(cat.icon)+esc(cat.label)+'</span>'+favoriteButton(word)+'</div><div class="entry-provenance">'+statusMarkup(word)+'<span>'+esc(scopeLabel(word))+(word.sourceRef?' · hlm. '+word.sourceRef.printedPage:'')+'</span></div><button class="word-term" data-open="'+esc(word.id)+'" aria-label="Lihat detail '+esc(word.md)+'">'+esc(word.md)+'</button><div class="translations">'+Object.entries(LANGUAGES).map(([key,label])=>'<div class="translation-row"><span class="language-label">'+label+'</span><span class="translation-value">'+esc(word[key])+'</span></div>').join('')+'</div>'+(known.has(word.id)?'<div class="known-tick">'+icon('check')+'Sudah dipahami</div>':'')+'</div><div class="card-bottom"><button class="example-toggle" data-example="'+esc(word.id)+'" aria-expanded="'+open+'" aria-controls="example-'+esc(word.id)+'">'+icon('book')+esc(exampleLabel(word))+'<span class="chevron">'+icon('down')+'</span></button><button class="detail-link" data-open="'+esc(word.id)+'" aria-label="Detail kata '+esc(word.md)+'">Detail '+icon('arrow')+'</button></div><div class="card-example" id="example-'+esc(word.id)+'" '+(open?'':'hidden')+'><p class="md-example">'+esc(word.exampleMd||'Belum ada contoh terverifikasi.')+'</p><p class="id-example">'+esc(word.exampleId||'Kalimat tidak direka untuk mengisi kolom.')+'</p></div></article>';
  }
  function table(list){
    return '<div class="table-scroll" tabindex="0" aria-label="Tabel kosakata, geser untuk melihat semua kolom"><table><thead><tr><th><span class="sr-only">Favorit</span></th><th>Mandailing</th><th>Indonesia</th><th>Melayu Malaysia</th><th>English</th><th>Contoh Kalimat</th></tr></thead><tbody>'+list.map(word=>'<tr><td>'+favoriteButton(word)+'</td><td><button class="table-word" data-open="'+esc(word.id)+'">'+esc(word.md)+'</button><small>'+esc(CATEGORIES[word.category].label)+'</small><div class="table-provenance">'+statusMarkup(word)+'<small>'+esc(scopeLabel(word))+(word.sourceRef?' · hlm. '+word.sourceRef.printedPage:'')+'</small></div></td><td>'+esc(word.idn)+'</td><td>'+esc(word.my)+'</td><td>'+esc(word.en)+'</td><td class="table-example">'+esc(word.exampleMd||'Belum tersedia')+'<span>'+esc(word.exampleId||'Contoh belum diverifikasi.')+'</span><small>'+esc(exampleLabel(word))+'</small></td></tr>').join('')+'</tbody></table></div>';
  }
  function renderList(){
    renderCategories();renderAlphabet();syncCounts();
    const result=filtered(),pages=Math.max(1,Math.ceil(result.length/PAGE_SIZE));
    state.page=Math.min(Math.max(1,state.page),pages);
    $("#results-title").textContent=state.view==="saved"?(state.category==="all"?"Kosakata disimpan":CATEGORIES[state.category].title):CATEGORIES[state.category].title;
    if(state.letter!=="all")$("#results-title").textContent="Huruf "+state.letter+" · "+$("#results-title").textContent;
    $("#result-count").textContent=result.length+(state.query?" kata cocok dengan “"+state.query+"”":state.view==="saved"?" kata dalam koleksi Anda":" kata tersedia untuk dijelajahi");
    $("#grid-view").classList.toggle("selected",state.layout==="grid");
    $("#table-view").classList.toggle("selected",state.layout==="table");
    $("#grid-view").setAttribute("aria-pressed",String(state.layout==="grid"));
    $("#table-view").setAttribute("aria-pressed",String(state.layout==="table"));
    const current=result.slice((state.page-1)*PAGE_SIZE,state.page*PAGE_SIZE);
    if(!result.length){
      const emptySaved=state.view==="saved"&&!fav.size;
      $("#word-results").innerHTML='<div class="empty-state"><div class="empty-icon">'+icon(emptySaved?"bookmark":"search")+'</div><h3>'+(emptySaved?"Simpan kata pertama Anda.":"Belum ada kata yang cocok.")+'</h3><p>'+(emptySaved?"Tekan ikon penanda pada kartu untuk mengumpulkan kata yang ingin Anda ingat.":"Coba kata yang lebih singkat, bahasa lain, atau kategori yang berbeda.")+'</p><button class="button button-outline" '+(emptySaved?'data-nav="dictionary"':'data-clear-filters="true"')+'>'+(emptySaved?"Jelajahi kamus":"Reset pencarian & filter")+'</button></div>';
    }else $("#word-results").innerHTML=state.layout==="grid"?'<div class="word-grid">'+current.map(card).join("")+'</div>':table(current);
    let indices=[...new Set([1,state.page-1,state.page,state.page+1,pages])].filter(index=>index>0&&index<=pages).sort((a,b)=>a-b);
    let pageHtml="",previous=0;
    for(const index of indices){if(previous&&index-previous>1)pageHtml+='<span class="page-ellipsis">…</span>';pageHtml+='<button class="page-button '+(index===state.page?"current":"")+'" data-page="'+index+'" aria-label="Halaman '+index+'" '+(index===state.page?'aria-current="page"':"")+'>'+index+'</button>';previous=index;}
    $("#pagination").innerHTML=result.length?'<p>Menampilkan '+((state.page-1)*PAGE_SIZE+1)+'–'+Math.min(state.page*PAGE_SIZE,result.length)+' dari '+result.length+' kata</p><div class="page-buttons"><button class="page-button" data-page="'+(state.page-1)+'" '+(state.page===1?"disabled":"")+' aria-label="Halaman sebelumnya">'+icon("left")+'</button>'+pageHtml+'<button class="page-button" data-page="'+(state.page+1)+'" '+(state.page===pages?"disabled":"")+' aria-label="Halaman berikutnya">'+icon("right")+'</button></div>':"";
  }
  function navigate(view,writeHash=true){
    const same=state.view===view;
    state.view=view;
    $$("[data-view]").forEach(section=>section.hidden=section.dataset.view!==view);
    $("#dictionary-workspace").hidden=!["dictionary","saved"].includes(view);
    $$(".nav-item").forEach(button=>{const active=button.dataset.nav===view;button.classList.toggle("active",active);if(active)button.setAttribute("aria-current","page");else button.removeAttribute("aria-current");});
    if(!same){state.page=1;state.category="all";state.letter="all";state.status="all";state.query="";$("#search").value="";}
    if(view==="dictionary"||view==="saved")renderList();
    if(view==="inventory")renderBank();
    if(view==="learn"){if(!deck.length)startDeck();else renderFlashcard();syncCounts();}
    if(writeHash){const hash={dictionary:"kamus",inventory:"bank",saved:"disimpan",learn:"belajar",sources:"rujukan"}[view];history.replaceState(null,"","#"+hash);}
    if(!same)window.scrollTo({top:0,behavior:"instant"});
  }
  function toggleFavorite(id){
    if(!byId(id))return;
    if(fav.has(id))fav.delete(id);else fav.add(id);
    const saved=persist();
    renderList();
    if($("#entry-modal").open&&$("#entry-detail").dataset.current===id)renderDetail(id);
    if(state.view==="learn")renderFlashcard();
    if(saved)toast(fav.has(id)?"Kata ditambahkan ke koleksi Anda.":"Kata dihapus dari koleksi.");
  }
  function renderDetail(id){
    const word=byId(id);if(!word)return;
    const isKnown=known.has(word.id),personal=word.status==='personal',ref=word.sourceRef;
    $('#entry-detail').dataset.current=word.id;
    const refs=(word.sources||[]).map(id=>SOURCES.find(source=>source.id===id)).filter(Boolean);
    const exampleNote=word.exampleStatus==='source_quoted'?'Kalimat Mandailing dikutip singkat dari kamus gabungan; kapitalisasi dan tanda baca disesuaikan. Terjemahan Indonesia disunting. Belum ditinjau penutur asli untuk satu dialek tertentu.':word.exampleStatus==='pending'?'Belum ada contoh yang dapat ditelusuri untuk entri ini. Kolom dikosongkan sampai tersedia bukti atau penelaahan penutur.':'Contoh ini merupakan konstruksi latihan versi awal atau catatan pribadi; belum ditinjau penutur asli.';
    const evidence=ref?'<section class="evidence-panel"><h3>Jejak penelaahan</h3><dl><div><dt>Bentuk sumber</dt><dd>'+esc(ref.lemma)+' · '+esc(ref.kind)+'</dd></div><div><dt>Lokasi</dt><dd><a href="'+esc(sourcePageUrl(ref))+'" target="_blank" rel="noopener noreferrer">Halaman cetak '+ref.printedPage+' · PDF '+ref.pdfPage+' '+icon('external')+'</a></dd></div><div><dt>Label bahasa</dt><dd>'+esc(scopeLabel(word))+'</dd></div><div><dt>Ditelaah</dt><dd>26 Oktober 2026 · '+esc(word.batch)+'</dd></div></dl><p>Bentuk dan satu makna Indonesia ditelusuri ke sumber. Padanan Melayu Malaysia dan Inggris merupakan pilihan editorial, bukan hasil penelaahan penutur asli.</p>'+(word.translationRefs||[]).map(item=>'<p><a href="'+esc(item.url)+'" target="_blank" rel="noopener noreferrer">Perbandingan padanan Melayu di PRPM '+icon('external')+'</a></p>').join('')+(word.variantRefs||[]).map(item=>'<p>Variasi '+esc(item.form)+' berlabel '+esc(item.languageLabel)+' · <a href="'+esc(sourcePageUrl(item))+'" target="_blank" rel="noopener noreferrer">hlm. '+item.printedPage+'</a>.</p>').join('')+'</section>':'';
    const personalNotes=(word.personalAlternatives||[]).map(item=>'<section class="personal-preserved"><h3>Catatan pribadi yang dipertahankan</h3><p>Padanan Anda: '+esc(item.idn)+' · '+esc(item.my)+' · '+esc(item.en)+'</p>'+(item.note?'<p>'+esc(item.note)+'</p>':'')+(item.exampleMd?'<p>'+esc(item.exampleMd)+' — '+esc(item.exampleId)+'</p>':'')+'<small>Belum ditinjau. Catatan tersimpan terpisah dari data rujukan.</small></section>').join('');
    $('#entry-detail').innerHTML='<div class="modal-topline"><span class="eyebrow">'+esc(statusLabel(word).toUpperCase())+' · '+esc(scopeLabel(word))+'</span><button class="icon-button" data-close="entry-modal" aria-label="Tutup detail kata">'+icon('close')+'</button></div><div class="detail-title-row"><h2 id="detail-title">'+esc(word.md)+'</h2>'+favoriteButton(word)+'</div><p class="detail-category">'+esc(CATEGORIES[word.category].label)+(word.pos?' · '+esc(word.pos):'')+(word.aliases?.length?' · Variasi tercatat: '+word.aliases.map(esc).join(', '):'')+'</p><div class="detail-translations">'+Object.entries(LANGUAGES).map(([key,label])=>'<div><span class="language-label">'+label+'</span><strong>'+esc(word[key])+'</strong></div>').join('')+'</div><div class="detail-example"><span class="eyebrow">'+esc(exampleLabel(word).toUpperCase())+'</span><p class="md-example">'+esc(word.exampleMd||'Contoh belum tersedia.')+'</p><p class="id-example">'+esc(word.exampleId||'')+'</p><p class="example-context">'+esc(exampleNote)+'</p></div>'+(word.note?'<p class="detail-note">'+esc(word.note)+'</p>':'')+'<p class="detail-source">'+esc(word.scope||'Kata pribadi; makna dan contoh belum diverifikasi.')+(refs.length?'<br>Rujukan: '+refs.map(item=>'<a href="'+esc(item.url)+'" target="_blank" rel="noopener noreferrer">'+esc(item.title)+'</a>').join('; '):'')+'</p>'+evidence+personalNotes+'<div class="detail-footer"><button class="button button-outline" data-copy="'+esc(word.id)+'">'+icon('copy')+'Salin entri</button><button class="button button-primary '+(isKnown?'is-known':'')+'" data-known="'+esc(word.id)+'">'+icon('check')+(isKnown?'Sudah dipahami':'Tandai sudah dipahami')+'</button></div>';
  }
  function openDetail(id){renderDetail(id);if(!$("#entry-modal").open)$("#entry-modal").showModal();}
  function toggleKnown(id){
    if(known.has(id))known.delete(id);else known.add(id);
    const saved=persist();renderDetail(id);renderList();syncCounts();
    if(saved)toast(known.has(id)?"Satu kata lebih dekat. Progres disimpan.":"Kata dikembalikan ke daftar untuk dipelajari.");
  }
  function exampleCell(word){return word.exampleMd||word.exampleId?"Mandailing: "+(word.exampleMd||"")+" — Indonesia: "+(word.exampleId||""):"";}
  function tsv(list){
    return [["Mandailing","Indonesia","Melayu Malaysia","English","Contoh Kalimat"],...list.map(word=>[word.md,word.idn,word.my,word.en,exampleCell(word)])].map(row=>row.map(plain).join("\t")).join("\n");
  }
  function download(filename,content,type){
    const blob=new Blob([content],{type});const url=URL.createObjectURL(blob);const link=document.createElement("a");
    link.href=url;link.download=filename;document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),30000);
  }
  function exportTSV(all=false){
    const list=all?words():filtered();
    if(!list.length){toast("Belum ada kata untuk diekspor.");return;}
    download("hata-kamus-mandailing-"+list.length+"-kata.tsv","\uFEFF"+tsv(list),"text/tab-separated-values;charset=utf-8");
    toast(list.length+" kata diekspor dalam lima kolom TSV.");
  }
  async function copyEntry(id){
    const word=byId(id);if(!word)return;
    const content=tsv([word]);
    try{await navigator.clipboard.writeText(content);toast("Entri disalin sebagai TSV.");}
    catch{
      const input=document.createElement("textarea");input.value=content;input.style.position="fixed";input.style.opacity="0";const host=$("#entry-modal").open?$("#entry-modal"):document.body;host.append(input);input.select();
      const success=document.execCommand("copy");input.remove();toast(success?"Entri disalin sebagai TSV.":"Penyalinan tidak tersedia. Gunakan ekspor TSV.");
    }
  }
  function deckPool(){
    const category=$('#learn-category').value;
    return words().filter(word=>category==='all'||category==='saved'&&fav.has(word.id)||category==='reviewed'&&isAttested(word)||word.category===category);
  }
  function startDeck(shuffle=false){
    deck=deckPool().map(word=>word.id);
    if(shuffle)for(let i=deck.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[deck[i],deck[j]]=[deck[j],deck[i]];}
    deckIndex=0;revealed=false;sessionKnown=0;renderFlashcard();
  }
  function renderFlashcard(){
    const target=$("#learn-language").value;
    const targetPhrase={idn:"bahasa Indonesia",my:"bahasa Melayu Malaysia",en:"bahasa Inggris"}[target];
    if(!deck.length){
      $("#flashcard-area").innerHTML='<div class="empty-state learning-empty"><div class="empty-icon">'+icon("bookmark")+'</div><h3>Belum ada kartu di sini.</h3><p>Simpan kata dari kamus atau pilih kategori lain untuk mulai belajar.</p><button class="button button-outline" data-nav="dictionary">Jelajahi kamus</button></div>';return;
    }
    if(deckIndex>=deck.length){
      $("#flashcard-area").innerHTML='<div class="flashcard"><div class="flashcard-content learning-empty"><span class="eyebrow">SESI SELESAI</span><div class="flash-word">'+icon("check")+'</div><h3 style="font:30px var(--serif);color:var(--wine);margin:0 0 15px">Selangkah lebih dekat.</h3><p class="flash-prompt">'+deck.length+' kartu ditinjau; '+sessionKnown+' jawaban ditandai dipahami dalam sesi ini.</p><button class="button button-primary" data-restart-deck="true">Mulai sesi baru</button></div></div>';return;
    }
    const word=byId(deck[deckIndex]);
    if(!word){deckIndex++;renderFlashcard();return;}
    $("#flashcard-area").innerHTML='<div class="flashcard"><div class="flashcard-header"><span>Kartu '+(deckIndex+1)+' dari '+deck.length+'</span>'+favoriteButton(word)+'</div><div class="flashcard-content"><span class="eyebrow">MANDAILING</span><div class="flash-word">'+esc(word.md)+'</div>'+(revealed?'<div class="flash-answer"><span class="eyebrow">'+LANGUAGES[target].toUpperCase()+'</span><div class="answer-word">'+esc(word[target])+'</div><p>'+esc(word.exampleMd||"")+'</p><p>'+esc(word.exampleId||"")+'</p></div>':'<p class="flash-prompt">Apa padanannya dalam '+targetPhrase+'?</p><button class="button button-outline" id="reveal-answer">Buka jawaban '+icon("down")+'</button>')+'</div>'+(revealed?'<div class="flashcard-footer"><button class="button button-outline" id="review-later">Ulangi nanti</button><button class="button button-primary" id="mark-learned">'+icon("check")+'Sudah paham</button></div>':"")+'</div><div class="flash-meta"><span>'+esc(CATEGORIES[word.category].label)+' · '+esc(exampleLabel(word))+'</span><button class="text-button" id="shuffle-deck">'+icon("shuffle")+'Acak kartu</button></div>';
  }
  function advance(understood){
    const word=byId(deck[deckIndex]);if(!word)return;
    if(understood){known.add(word.id);sessionKnown++;}else known.delete(word.id);
    persist();deckIndex++;revealed=false;syncCounts();renderFlashcard();
  }
  function renderSources(){
    $("#source-list").innerHTML=SOURCES.map((source,index)=>'<article class="source-item"><span class="source-index">'+String(index+1).padStart(2,'0')+'</span><div class="source-content"><h3>'+esc(source.title)+'</h3><p>'+esc(source.meta)+'</p><p>'+esc(source.use)+'</p></div><a href="'+source.url+'" target="_blank" rel="noopener noreferrer" aria-label="Buka sumber: '+esc(source.title)+'">Buka rujukan '+icon("external")+'</a></article>').join("");
  }
  function openChoice(){
    $("#choose-word-modal").showModal();
  }
  function openAdd(){
    $("#word-form").reset();$("#form-error").textContent="";$("#edit-modal").showModal();
  }
  function saveNewWord(event){
    event.preventDefault();const form=new FormData(event.target);
    const md=plain(form.get("md")),idn=plain(form.get("idn")),my=plain(form.get("my")),en=plain(form.get("en"));
    const exampleMd=plain(form.get("exampleMd")),exampleId=plain(form.get("exampleId"));
    if(!md||!idn||!my||!en){$("#form-error").textContent="Lengkapi kata Mandailing dan ketiga padanannya.";return;}
    if(words().some(word=>normalize(word.md)===normalize(md))){$("#form-error").textContent="Kata ini sudah ada. Gunakan pencarian untuk melihat entrinya.";return;}
    if(Boolean(exampleMd)!==Boolean(exampleId)){$("#form-error").textContent="Lengkapi kedua bagian contoh kalimat, atau kosongkan keduanya.";return;}
    const id="personal-"+(globalThis.crypto?.randomUUID?crypto.randomUUID():Date.now()+"-"+Math.random().toString(36).slice(2));
    local.custom.push({id,md,idn,my,en,exampleMd,exampleId,category:form.get("category"),aliases:[],note:plain(form.get("note")),scope:"Ditambahkan pengguna. Kosakata, padanan, dan contoh belum diverifikasi melalui penelaahan bahasa.",sources:[],status:"personal"});
    const saved=persist();$("#edit-modal").close();navigate("dictionary");state.category="all";state.letter="all";state.status="all";state.language="all";state.query=md;state.page=1;$("#search").value=md;$("#search-language").value="all";renderList();deck=[];
    if(saved)toast("Kata pribadi ditambahkan. Statusnya belum diverifikasi.");
  }
  document.addEventListener("click",event=>{
    const button=event.target.closest("button");if(!button||button.disabled)return;
    if(button.dataset.nav){navigate(button.dataset.nav);return;}
    if(button.dataset.close){$("#"+button.dataset.close).close();return;}
    if(button.dataset.save){toggleFavorite(button.dataset.save);return;}
    if(button.dataset.open){openDetail(button.dataset.open);return;}
    if(button.dataset.known){toggleKnown(button.dataset.known);return;}
    if(button.dataset.copy){copyEntry(button.dataset.copy);return;}
    if(button.dataset.category){state.category=button.dataset.category;state.page=1;renderList();return;}
    if(button.dataset.letter){state.letter=button.dataset.letter;state.page=1;renderList();return;}
    if(button.dataset.curation){navigate("dictionary");state.letter="all";state.status="attested";state.query="";state.category="all";$("#search").value="";state.page=1;renderList();$("#alphabet-bar").scrollIntoView({behavior:"smooth",block:"center"});return;}
    if(button.id==="download-analysis"){download("analisis-inventaris-sumber.md",RESEARCH.reportMarkdown,"text/markdown;charset=utf-8");return;}
    if(button.dataset.page){state.page=Number(button.dataset.page);renderList();$("#results-title").scrollIntoView({behavior:"smooth",block:"start"});return;}
    if(button.dataset.example){
      const id=button.dataset.example,expanded=state.expanded.has(id);if(expanded)state.expanded.delete(id);else state.expanded.add(id);
      const element=document.getElementById("example-"+id);if(element)element.hidden=expanded;button.setAttribute("aria-expanded",String(!expanded));return;
    }
    if(button.dataset.clearFilters){state.query="";state.category="all";state.letter="all";state.status="all";state.language="all";state.page=1;$("#search").value="";$("#search-language").value="all";renderList();$("#search").focus();return;}
    if(button.dataset.restartDeck){startDeck(true);return;}
    if(button.id==="grid-view"||button.id==="table-view"){state.layout=button.id==="grid-view"?"grid":"table";renderList();return;}
    if(button.id==="export-top"){exportTSV();return;}
    if(button.id==="export-all"){exportTSV(true);return;}
    if(button.id==="add-word-top"){openChoice();return;}
    if(button.id==="add-word-private"){openAdd();return;}
    if(button.id==="choice-word-private"){$("#choose-word-modal").close();openAdd();return;}
    if(button.id==="reveal-answer"){revealed=true;renderFlashcard();return;}
    if(button.id==="review-later"){advance(false);return;}
    if(button.id==="mark-learned"){advance(true);return;}
    if(button.id==="shuffle-deck"){startDeck(true);toast("Urutan kartu diacak. Progres tetap disimpan.");return;}
  });
  $("#search").addEventListener("input",event=>{state.query=event.target.value;state.page=1;renderList();});
  $("#search-clear").addEventListener("click",()=>{state.query="";state.page=1;$("#search").value="";renderList();$("#search").focus();});
  $("#search-language").addEventListener("change",event=>{state.language=event.target.value;state.page=1;renderList();});
  $("#editorial-filter").addEventListener("change",event=>{state.status=event.target.value;state.page=1;renderList();});
  $("#sort").addEventListener("change",event=>{state.sort=event.target.value;state.page=1;renderList();});
  $("#learn-category").addEventListener("change",()=>startDeck());
  $("#learn-language").addEventListener("change",()=>renderFlashcard());
  $("#word-form").addEventListener("submit",saveNewWord);
  $$("dialog").forEach(dialog=>dialog.addEventListener("click",event=>{if(event.target===dialog){const rect=dialog.getBoundingClientRect();if(event.clientX<rect.left||event.clientX>rect.right||event.clientY<rect.top||event.clientY>rect.bottom)dialog.close();}}));
  $(".brand").addEventListener("click",event=>{event.preventDefault();navigate("dictionary");});
  document.addEventListener("keydown",event=>{
    const typing=event.target.matches("input,textarea,select,[contenteditable=true]");
    if(event.key==="/"&&!typing&&!$$("dialog").some(dialog=>dialog.open)){
      event.preventDefault();if(state.view==="inventory")$("#bank-search").focus();else{if(!["dictionary","saved"].includes(state.view))navigate("dictionary");$("#search").focus();}
    }
  });
  $$("[data-icon]").forEach(element=>{element.innerHTML=icon(element.dataset.icon);});
  if(location.protocol==="file:"){
    $("#download-app").href=location.href.split("#")[0];
    $("#download-database").href="https://kamusmandailing.github.io/data/Kamus_Mandailing_Database.zip";
    $("#download-database").title="Unduhan database memerlukan koneksi internet. Pencarian dan ekspor TSV tetap dapat digunakan tanpa koneksi.";
  }
  $("#search").value="";$("#search-language").value="all";$("#sort").value="az";
  const categoryOptions=Object.entries(CATEGORIES).filter(([key])=>key!=="all").map(([key,cat])=>'<option value="'+key+'">'+esc(cat.label)+'</option>').join("");
  $("#learn-category").innerHTML='<option value="all">Semua kategori</option><option value="reviewed">Semua entri dirujuk</option>'+categoryOptions+'<option value="saved">Kata disimpan</option>';
  $("#entry-category").innerHTML=categoryOptions;$("#entry-category").value="rumah";
  for(const item of local.custom){
    const seed=SEED.find(word=>normalize(word.md)===normalize(item.md)||(word.aliases||[]).some(alias=>normalize(alias)===normalize(item.md)));
    if(seed){if(fav.delete(item.id))fav.add(seed.id);if(known.delete(item.id))known.add(seed.id);}
  }
  const number = value => Number(value).toLocaleString("id-ID");
  $("#curation-added").textContent=number(RESEARCH.added);
  $("#curation-reviewed").textContent=number(RESEARCH.sourceAttested);
  $("#audit-summary").textContent=number(RESEARCH.sourceAttested)+" entri memiliki lokasi sumber · pilihan praktis A–Z";
  $("#research-summary").textContent=number(RESEARCH.added)+" entri ditambahkan dan 94 entri lama diaudit. Koleksi kini "+number(RESEARCH.total)+" entri unik, semuanya mempunyai lokasi rujukan. Seleksi telah melintasi semua 21 huruf pada abjad kamus; bukan seluruh lema buku atau seluruh kosakata bahasa.";
  $("#research-examples").textContent=RESEARCH.sourceExamples+" entri mempunyai contoh singkat dari sumber. "+number(RESEARCH.pendingExamples)+" entri belum mempunyai contoh terverifikasi. Contoh latihan lama yang belum terbukti telah dikosongkan; tidak ada kalimat pengisi.";
  $("#research-labels").textContent=RESEARCH.languageLabels.Mdl+" entri berlabel Mdl, "+RESEARCH.languageLabels["shared-pronunciation"]+" mencatat lafal Mandailing dan Angkola, "+number(RESEARCH.languageLabels.unmarked)+" berasal dari kamus gabungan tanpa label khusus, dan "+RESEARCH.languageLabels.Tapsel+" bilangan merujuk penelitian Tapsel. Mdl tidak berarti eksklusif Mandailing.";
  $("#research-roadmap").innerHTML=RESEARCH.letters.map(item=>'<button class="roadmap-letter '+(item.phase==='selected_reviewed'?'started':'pending')+'" data-curation-letter="'+item.letter+'"><strong>'+item.letter+'</strong><span>'+item.entries+' entri pilihan</span><small>'+(item.phase==='selected_reviewed'?'Lokasi sumber ditelaah':'Di luar abjad sumber')+'</small></button>').join("");
  document.addEventListener("click",event=>{const button=event.target.closest("[data-curation-letter]");if(!button)return;navigate("dictionary");state.letter=button.dataset.curationLetter;state.page=1;renderList();$("#alphabet-bar").scrollIntoView({behavior:"smooth",block:"center"});});
  $("#source-count").textContent=SOURCES.length+" rujukan";
  renderSources();syncCounts();
  /* INLINE_INVENTORY_APP */
  const initialView={kamus:"dictionary",bank:"inventory",disimpan:"saved",belajar:"learn",rujukan:"sources"}[location.hash.slice(1)]||"dictionary";
  navigate(initialView,false);
})();
