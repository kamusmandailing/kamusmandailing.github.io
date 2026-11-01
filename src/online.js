(()=>{
"use strict";
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const SEED=JSON.parse($("#seed-data").textContent), SOURCES=JSON.parse($("#source-data").textContent), RELEASE=JSON.parse($("#release-data").textContent);
const SOURCE_MAP=new Map(SOURCES.map(s=>[s.id,s]));
const CURATED_MAP=new Map(SEED.map(w=>[w.id,w]));
const PAGE=24;
let bank=null,bankLoading=null,bankLoadingAll=null,filtersInitialized=false,mode="curated",curatedPage=1,bankPage=1,bankQueryCache=null;
const loadedChunks=new Map(),chunkLoading=new Map();
const safe=x=>String(x??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const plain=x=>String(x??"").replace(/[\t\r\n]+/g," ").trim();
const norm=x=>String(x??"").normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLocaleLowerCase("id").trim();
const format=n=>Number(n).toLocaleString("id-ID");
const uri=x=>typeof x==="string"&&/^https:\/\//i.test(x)?x:null;
const state={curated:"",language:"all",bank:"",kind:"all",scope:"all",status:"all",source:"all"};
const audit={curatedLoaded:true,bankLoaded:()=>Boolean(bank&&loadedChunks.has(0)),
 bankComplete:()=>Boolean(bank&&loadedChunks.size===bank.chunks.length),loadedChunkCount:()=>loadedChunks.size,bankPage:()=>bankPage};
$("#curated-total").textContent=format(RELEASE.counts.curatedEntries);
$("#bank-total").textContent=format(RELEASE.counts.sourceForms);
$("#pending-total").textContent=format(RELEASE.counts.pendingTranslations);
$("#reference-total").textContent=format(RELEASE.counts.referenceRecords);
const sorted=[...SEED].sort((a,b)=>a.md.localeCompare(b.md,"id"));
const exact=()=>sorted.filter(w=>{
 if(!state.curated)return true;
 const cols=state.language==="all"?["md","idn","my","en"]:[state.language];
 return cols.some(col=>norm(w[col]).includes(norm(state.curated))) ||
   (state.language==="all"||state.language==="md")&&(w.aliases||[]).some(alias=>norm(alias).includes(norm(state.curated)));
});
function pagination(node,page,total,onPage){
 const pages=Math.max(1,Math.ceil(total/PAGE));
 node.replaceChildren();
 if(!total)return;
 const text=document.createElement("span");
 text.textContent="Menampilkan "+format((page-1)*PAGE+1)+"–"+format(Math.min(page*PAGE,total))+" dari "+format(total);
 const wrap=document.createElement("div");
 for(const [caption,p,disabled] of [["Sebelumnya",page-1,page===1],["Berikutnya",page+1,page>=pages]]){
  const button=document.createElement("button");button.textContent=caption;button.disabled=disabled;
  button.addEventListener("click",()=>onPage(p));wrap.append(button);
 }
 node.append(text,wrap);
}
const wordHTML=w=>'<article class="entry"><span class="tag">'+safe(w.category||"Entri")+' · '+safe(w.status==="personal"?"pribadi":"berpadanan editorial")+'</span><h3>'+safe(w.md)+'</h3><dl>'+
 [["Indonesia",w.idn],["Melayu Malaysia",w.my],["English",w.en]].map(([name,word])=>'<dt>'+name+'</dt><dd>'+safe(word)+'</dd>').join("")+
 '</dl><p class="info">Sumber: '+safe(w.sourceRef?.id||"Data editorial")+(w.sourceRef?.printedPage?" · hlm. "+safe(w.sourceRef.printedPage):"")+'</p></article>';
function renderCurated(){
 const items=exact(),pages=Math.max(1,Math.ceil(items.length/PAGE));curatedPage=Math.min(curatedPage,pages);
 $("#curated-count").textContent=format(items.length)+" entri sesuai pencarian";
 $("#curated-results").innerHTML=items.length?items.slice((curatedPage-1)*PAGE,curatedPage*PAGE).map(wordHTML).join(""):'<p>Tidak ada kata yang cocok. Coba kata lebih singkat atau bahasa lain.</p>';
 pagination($("#curated-pagination"),curatedPage,items.length,p=>{curatedPage=p;renderCurated();$("#curated-title").scrollIntoView({block:"start"});});
}
$("#curated-search").addEventListener("input",e=>{state.curated=e.target.value;curatedPage=1;renderCurated();});
$("#curated-language").addEventListener("change",e=>{state.language=e.target.value;curatedPage=1;renderCurated();});
$("#curated-reset").addEventListener("click",()=>{state.curated="";state.language="all";curatedPage=1;$("#curated-search").value="";$("#curated-language").value="all";renderCurated();$("#curated-search").focus();});
function download(filename,rows){
 const content="\ufeff"+rows.map(row=>row.map(plain).join("\t")).join("\n");
 const a=document.createElement("a"),url=URL.createObjectURL(new Blob([content],{type:"text/tab-separated-values;charset=utf-8"}));
 a.href=url;a.download=filename;document.body.append(a);a.click();a.remove();
 setTimeout(()=>URL.revokeObjectURL(url),1500);
}
$("#curated-export").addEventListener("click",()=>download("hata-online-berpadanan.tsv",
 [["Mandailing","Indonesia","Melayu Malaysia","English","Contoh Kalimat"],...exact().map(w=>[w.md,w.idn,w.my,w.en,w.exampleMd?"Mandailing: "+w.exampleMd+" — Indonesia: "+w.exampleId:""])]));
const validateManifest=data=>{
 if(!data||!Array.isArray(data.chunks)||!data.stats||!Array.isArray(data.localNames)||!data.filterOptions)
  throw Error("Manifest Bank Kosakata tidak lengkap.");
 if(!Number.isInteger(data.chunkSize)||data.chunkSize<1)throw Error("Ukuran potongan Bank tidak valid.");
 if(data.stats.uniqueForms!==RELEASE.counts.sourceForms||data.stats.referenceRecords!==RELEASE.counts.referenceRecords||
 data.stats.reviewedTranslations!==RELEASE.counts.curatedEntries||data.stats.pendingTranslations!==RELEASE.counts.pendingTranslations||
 data.stats.sourceCount!==RELEASE.counts.sourceCount)throw Error("Versi data Bank tidak cocok dengan rilis Kamus ini.");
 let next=0;
 for(const chunk of data.chunks){
  if(chunk.start!==next||!chunk.file||!Number.isInteger(chunk.count)||chunk.count<1||!chunk.sha256)
   throw Error("Urutan potongan Bank tidak lengkap.");
  next+=chunk.count;
 }
 if(next!==data.stats.uniqueForms||data.chunks.reduce((n,c)=>n+c.referenceRecords,0)!==data.stats.referenceRecords)
  throw Error("Jumlah potongan Bank tidak cocok dengan rilis.");
 if(!Array.isArray(data.filterOptions.kinds)||!Array.isArray(data.filterOptions.scopes))
  throw Error("Pilihan filter Bank tidak lengkap.");
 return {...data,forms:[]};
};
const updateLoadedForms=()=>{
 const forms=[];
 for(let index=0;loadedChunks.has(index);index++)forms.push(...loadedChunks.get(index));
 bank.forms=forms;bankQueryCache=null;
};
async function loadChunk(index){
 if(!bank)throw Error("Manifest Bank belum tersedia.");
 if(loadedChunks.has(index))return loadedChunks.get(index);
 if(chunkLoading.has(index))return chunkLoading.get(index);
 const meta=bank.chunks[index];
 if(!meta)throw Error("Nomor potongan Bank tidak tersedia.");
 const promise=(async()=>{
  const response=await fetch("./data/bank-online-shards/"+meta.file);
  if(!response.ok)throw Error("HTTP "+response.status+" pada potongan "+(index+1));
  const bytes=await response.arrayBuffer();
  if(window.crypto?.subtle){
   const digest=await window.crypto.subtle.digest("SHA-256",bytes);
   const actual=[...new Uint8Array(digest)].map(value=>value.toString(16).padStart(2,"0")).join("");
   if(actual!==meta.sha256)throw Error("Pemeriksaan integritas potongan Bank gagal.");
  }
  const data=JSON.parse(new TextDecoder().decode(bytes));
  if(!data||!Array.isArray(data.forms)||data.forms.length!==meta.count)
   throw Error("Jumlah bentuk dalam potongan Bank tidak cocok.");
  const referenceCount=data.forms.reduce((sum,form)=>sum+(form.references||[]).length,0);
  if(referenceCount!==meta.referenceRecords)throw Error("Rujukan dalam potongan Bank tidak lengkap.");
  const ids=new Set();
  for(const forms of loadedChunks.values())for(const form of forms)ids.add(form.id);
  for(const form of data.forms){
   if(!form.id||ids.has(form.id))throw Error("ID bentuk Bank berulang atau kosong.");
   ids.add(form.id);
  }
  loadedChunks.set(index,data.forms);updateLoadedForms();
  return data.forms;
 })().finally(()=>chunkLoading.delete(index));
 chunkLoading.set(index,promise);
 return promise;
}
function showBankFailure(err,retryAction){
 const info=$("#bank-loading");
 info.hidden=false;
 info.innerHTML="Bank belum dapat dimuat ("+safe(err.message)+"). Periksa internet lalu <button id='bank-retry' type='button'>Coba lagi</button>, atau gunakan <a href='./Hata_Kamus_Mandailing.html'>versi offline lengkap</a>.";
 $("#bank-retry").addEventListener("click",()=>{
  info.textContent="Mencoba memuat Bank Kosakata…";
  retryAction().then(()=>{
   if(!$("#bank-workspace").hidden){info.hidden=true;renderBank();}
  }).catch(next=>showBankFailure(next,retryAction));
 },{once:true});
}
async function loadBank(){
 if(bank&&loadedChunks.has(0))return bank;
 if(bankLoading)return bankLoading;
 const info=$("#bank-loading");
 info.hidden=false;info.textContent="Memuat indeks Bank Kosakata dan bentuk pertama…";
 bankLoading=(async()=>{
  if(!bank){
   const response=await fetch("./data/bank-online-shards/manifest.json");
   if(!response.ok)throw Error("HTTP "+response.status+" pada manifest Bank");
   bank=validateManifest(await response.json());
  }
  if(!filtersInitialized){initBankFilters();filtersInitialized=true;}
  await loadChunk(0);
  $("#bank-workspace").hidden=false;info.hidden=true;renderBank();return bank;
 })().catch(err=>{
  showBankFailure(err,()=>{bankLoading=null;return loadBank();});
  throw err;
 }).finally(()=>{bankLoading=null;});
 return bankLoading;
}
function ensureAllBank(){
 if(!bank)return loadBank().then(()=>ensureAllBank());
 if(loadedChunks.size===bank.chunks.length)return Promise.resolve(bank);
 if(bankLoadingAll)return bankLoadingAll;
 const info=$("#bank-loading");
 info.hidden=false;
 info.textContent="Memuat semua potongan agar pencarian, filter, dan ekspor Bank lengkap…";
 bankLoadingAll=Promise.all(bank.chunks.map((_,index)=>loadChunk(index))).then(()=>{
  info.hidden=true;bankQueryCache=null;return bank;
 }).catch(err=>{
  showBankFailure(err,()=>{bankLoadingAll=null;return ensureAllBank();});
  throw err;
 }).finally(()=>{bankLoadingAll=null;});
 return bankLoadingAll;
}
function ensureBankPage(page){
 if(!bank)return Promise.resolve();
 const lastForm=Math.min(page*PAGE,bank.stats.uniqueForms)-1;
 const lastChunk=Math.floor(lastForm/bank.chunkSize);
 const missing=[];
 for(let index=0;index<=lastChunk;index++)if(!loadedChunks.has(index))missing.push(index);
 if(!missing.length)return Promise.resolve();
 const info=$("#bank-loading");
 info.hidden=false;info.textContent="Memuat potongan Bank untuk halaman "+format(page)+"…";
 let task=Promise.resolve();
 for(const index of missing)task=task.then(()=>loadChunk(index));
 return task.then(()=>{info.hidden=true;});
}
function switchMode(next){
 mode=next;$("#curated-view").hidden=next!=="curated";$("#bank-view").hidden=next!=="bank";
 $("#show-curated").setAttribute("aria-pressed",String(next==="curated"));
 $("#show-bank").setAttribute("aria-pressed",String(next==="bank"));
 if(next==="bank"){loadBank().catch(()=>{});}
}
$("#show-curated").addEventListener("click",()=>switchMode("curated"));
$("#show-bank").addEventListener("click",()=>switchMode("bank"));
function initBankFilters(){
 const kind=$("#bank-kind"),scope=$("#bank-scope"),source=$("#bank-source");
 for(const k of bank.filterOptions.kinds)kind.add(new Option(k.replaceAll("_"," "),k));
 for(const k of bank.filterOptions.scopes)scope.add(new Option(k,k));
 for(const x of SOURCES)source.add(new Option(x.shortTitle||x.title,x.id));
}
function bankSearchText(f,refs){
 const w=CURATED_MAP.get(f.entryId);
 return norm([f.form,...refs.flatMap(r=>[r.parent,r.sourceGloss,r.taxonAsPrinted]),
 ...(w?[w.idn,w.my,w.en,...(w.aliases||[])]:[])].join(" "));
}
function bankFiltered(){
 if(!bank)return [];
 const key=JSON.stringify(state);
 if(bankQueryCache?.key===key)return bankQueryCache.result;
 const q=norm(state.bank);
 const rows=bank.forms.filter(f=>{
  const refs=state.source==="all"?f.references:f.references.filter(r=>r.sourceId===state.source);
  if(!refs.length)return false;
  if(state.kind!=="all"&&!((["bound_form","compound"].includes(state.kind))?f.kinds.includes(state.kind):refs.some(r=>r.kind===state.kind)))return false;
  if(state.scope!=="all"&&!refs.some(r=>r.labels.includes(state.scope)))return false;
  if(state.status==="reviewed"&&!f.entryId)return false;
  if(state.status==="pending"&&f.entryId)return false;
  if(state.status==="source-gloss"&&!refs.some(r=>r.sourceGloss))return false;
  return !q||bankSearchText(f,refs).includes(q);
 });
 bankQueryCache={key,result:rows};return rows;
}
const bankNeedsCompleteResults=()=>Boolean(norm(state.bank)||state.kind!=="all"||state.scope!=="all"||state.status!=="all"||state.source!=="all");
function prepareCompleteResults(){
 if(!bankNeedsCompleteResults()||!bank){renderBank();return Promise.resolve(bank);}
 if(loadedChunks.size===bank.chunks.length){renderBank();return Promise.resolve(bank);}
 $("#bank-count").textContent="Memuat data lengkap agar hasil pencarian dan filter tidak terpotong…";
 $("#bank-results").replaceChildren();
 return ensureAllBank().then(()=>{renderBank();return bank;}).catch(()=>{});
}
function renderBank(){
 const incomplete=loadedChunks.size<bank.chunks.length,unfiltered=!bankNeedsCompleteResults();
 const rows=bankFiltered(),resultTotal=incomplete&&unfiltered?bank.stats.uniqueForms:rows.length;
 const pages=Math.max(1,Math.ceil(resultTotal/PAGE));bankPage=Math.min(bankPage,pages);
 $("#bank-count").textContent=incomplete&&unfiltered?
  format(bank.forms.length)+" bentuk dimuat dari "+format(bank.stats.uniqueForms)+"; buka halaman berikutnya atau cari untuk menelusuri seluruh Bank":
  format(rows.length)+" bentuk cocok dari "+format(bank.stats.uniqueForms);
 const slice=rows.slice((bankPage-1)*PAGE,bankPage*PAGE);
 $("#bank-results").innerHTML=slice.length?slice.map(f=>{
  const w=CURATED_MAP.get(f.entryId),refs=state.source==="all"?f.references:f.references.filter(r=>r.sourceId===state.source);
  const gloss=refs.find(r=>r.sourceGloss&&r.glossLanguage==="id")||refs.find(r=>r.sourceGloss);
  const taxon=refs.find(r=>r.taxonAsPrinted);
  const meaning=w?w.idn:gloss?"Glos sumber ("+gloss.glossLanguage+"): "+gloss.sourceGloss:taxon?"Takson sumber: "+taxon.taxonAsPrinted:"Padanan belum ditelaah";
  return '<article class="entry"><span class="tag">'+safe(f.kinds.join(" · "))+' · '+safe([...new Set(refs.flatMap(r=>r.labels))].join(", "))+'</span><h3>'+safe(f.form)+'</h3><p>'+safe(meaning)+'</p><p class="info">'+format(f.references.length)+' rujukan · '+(w?"Padanan editorial":"Belum berpadanan")+'</p><button class="source-button" type="button" data-form-id="'+safe(f.id)+'">Lihat sumber & bukti</button></article>';
 }).join(""):'<p>Tidak ada bentuk yang cocok. Tidak ada data tambahan yang direka.</p>';
 pagination($("#bank-pagination"),bankPage,resultTotal,p=>{
  bankPage=p;
  const load=unfiltered&&incomplete?ensureBankPage(p):Promise.resolve();
  load.then(()=>{renderBank();$("#bank-title").scrollIntoView({block:"start"});}).catch(err=>showBankFailure(err,()=>ensureBankPage(p)));
 });
}
for(const [id,key] of [["bank-search","bank"],["bank-kind","kind"],["bank-scope","scope"],["bank-status","status"],["bank-source","source"]]){
 $("#"+id).addEventListener(id==="bank-search"?"input":"change",e=>{
  state[key]=e.target.value;bankPage=1;bankQueryCache=null;
  if(bankNeedsCompleteResults())prepareCompleteResults();else renderBank();
 });
}
$("#bank-reset").addEventListener("click",()=>{
 Object.assign(state,{bank:"",kind:"all",scope:"all",status:"all",source:"all"});
 for(const id of ["bank-search","bank-kind","bank-scope","bank-status","bank-source"])$("#"+id).value="";
 for(const id of ["bank-kind","bank-scope","bank-status","bank-source"])$("#"+id).value="all";
 bankQueryCache=null;bankPage=1;renderBank();$("#bank-search").focus();
});
function bankExport(withLabels){
 const cols=withLabels?["Bentuk sumber","Indonesia","Melayu Malaysia","English","Label sumber","Jenis","Status padanan","ID bentuk","Sumber"]:["Mandailing","Indonesia","Melayu Malaysia","English","Contoh Kalimat"];
 const rows=bankFiltered().map(f=>{
  const w=CURATED_MAP.get(f.entryId), refs=state.source==="all"?f.references:f.references.filter(r=>r.sourceId===state.source);
  if(!withLabels)return [f.form,w?.idn||"",w?.my||"",w?.en||"",w?.exampleMd?"Mandailing: "+w.exampleMd+" — Indonesia: "+w.exampleId:""];
  const labels=[...new Set(refs.flatMap(r=>r.labels))],kinds=[...new Set([...refs.map(r=>r.kind),...f.kinds.filter(k=>["bound_form","compound"].includes(k))])];
  return [f.form,w?.idn||"",w?.my||"",w?.en||"",labels.join(", "),kinds.join(", "),f.status,f.id,[...new Set(refs.map(r=>r.sourceId))].join(", ")];
 });
 download(withLabels?"hata-bank-online-berlabel.tsv":"hata-bank-online.tsv",[cols,...rows]);
}
$("#bank-export").addEventListener("click",()=>ensureAllBank().then(()=>bankExport(false)).catch(()=>{}));
$("#bank-export-labels").addEventListener("click",()=>ensureAllBank().then(()=>bankExport(true)).catch(()=>{}));
const sourcePageUrl=(ref,source)=>{
 const direct=uri(ref.url);
 if(direct)return direct;
 const document=uri(source?.documentUrl)||uri(source?.url);
 return document?(ref.pdfPage?document.split("#")[0]+"#page="+encodeURIComponent(ref.pdfPage):document):null;
};
$("#bank-results").addEventListener("click",e=>{
 const button=e.target.closest("[data-form-id]");if(!button||!bank)return;
 const f=bank.forms.find(row=>row.id===button.dataset.formId);if(!f)return;
 const refs=state.source==="all"?f.references:f.references.filter(ref=>ref.sourceId===state.source);
 $("#source-dialog-body").innerHTML='<h2 id="source-dialog-title">'+safe(f.form)+'</h2>'+
 '<p>'+refs.length+' rujukan sumber dipilih. Glos sumber bukan padanan editorial otomatis.</p>'+
 refs.map(ref=>{
  const src=SOURCE_MAP.get(ref.sourceId),link=sourcePageUrl(ref,src);
  return '<section class="evidence"><strong>'+safe(src?.title||ref.sourceId)+'</strong><p>Jenis: '+safe(ref.kind)+' · Label: '+safe(ref.labels.join(", "))+
  ' · Induk: '+safe(ref.parent||"—")+'</p><p>Hlm. cetak: '+safe(ref.printedPage??"—")+' · PDF: '+safe(ref.pdfPage??"—")+
  '</p>'+(ref.sourceGloss?'<p>Glos sumber: '+safe(ref.sourceGloss)+'</p>':"")+
  (ref.taxonAsPrinted?'<p>Takson tercetak: '+safe(ref.taxonAsPrinted)+'</p>':"")+
  (link?'<a href="'+safe(link)+'" target="_blank" rel="noopener noreferrer">Buka rujukan asli</a>':"<p>Tautan sumber tidak tersedia.</p>")+'</section>';
 }).join("");
 $("#source-dialog").showModal();
});
$("#source-close").addEventListener("click",()=>$("#source-dialog").close());
window.HataOnlineAudit=audit;
renderCurated();
})();
