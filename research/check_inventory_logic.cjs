/* DOM-adapter checks for the bank logic. This is not visual browser testing. */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),read=p=>fs.readFileSync(path.join(root,p),'utf8');
const bank=JSON.parse(read('src/inventory.json')),seed=JSON.parse(read('src/words.json')),sources=JSON.parse(read('src/sources.json'));
const elements=new Map(),documentListeners={},downloads=[];
function element(id){
  if(!elements.has(id))elements.set(id,{value:'',textContent:'',innerHTML:'',listeners:{},
    addEventListener(type,fn){this.listeners[type]=fn;},setAttribute(key,value){this[key]=value;},showModal(){this.open=true;},close(){this.open=false;},scrollIntoView(){}});
  return elements.get(id);
}
element('#inventory-data').textContent=JSON.stringify(bank);
const ctx=vm.createContext({SEED:seed,SOURCES:sources,RESEARCH:JSON.parse(read('research/progress.json')),
  LANGUAGES:{idn:'Indonesia',my:'Melayu Malaysia',en:'English'},
  $:element,$$:()=>[],document:{addEventListener(type,fn){documentListeners[type]=fn;}},
  normalize:v=>String(v??'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('id').trim(),
  esc:v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])),
  plain:v=>String(v??'').replace(/[\t\r\n]+/g,' ').trim(),icon:()=>'',toast:()=>{},openDetail:()=>{},
  download:(filename,content,type)=>downloads.push({filename,content,type}),
  exampleCell:w=>w.exampleMd?'Mandailing: '+w.exampleMd+' — Indonesia: '+w.exampleId:''});
const sourceURL=read('src/app.js').match(/  const sourcePageUrl = ref => \{[\s\S]*?\n  \};/)[0];
vm.runInContext(sourceURL+'\n'+read('src/inventory.js')+'\nglobalThis.api={bankState,bankFiltered,renderBank,openBankDetail,renderLocalNames,exportBankTSV,exportBankLabels,exportLocalNames,sourcePageUrl};',ctx);
const a=ctx.api;
const reset=()=>Object.assign(a.bankState,{query:'',letter:'all',kind:'all',scope:'all',status:'all',source:'all',page:1,latestOnly:false});
assert.equal(a.bankFiltered().length,10821);
for(const id of Object.keys(bank.stats.recordsBySource)){
  reset();a.bankState.source=id;
  const expected=bank.forms.filter(f=>f.references.some(r=>r.sourceId===id)).length;
  assert.equal(a.bankFiltered().length,expected,id);
}
reset();a.bankState.status='pending';assert.equal(a.bankFiltered().length,9417);
reset();a.bankState.status='reviewed';assert.equal(a.bankFiltered().length,1404);
reset();a.bankState.status='source-gloss';assert.equal(a.bankFiltered().length,bank.stats.sourceGlossForms);
reset();a.bankState.source='idiom2012';a.bankState.kind='idiom';assert.equal(a.bankFiltered().length,75);
reset();a.bankState.source='culture2021';a.bankState.status='source-gloss';
assert(a.bankFiltered().length>0);assert(a.bankFiltered().every(f=>f.references.some(r=>r.sourceId==='culture2021'&&r.sourceGloss)));
reset();a.bankState.source='idiom2012';a.bankState.status='source-gloss';assert.equal(a.bankFiltered().length,0,'A source must not inherit another source gloss');
reset();a.bankState.source='plants2018';a.bankState.scope='MA';assert.equal(a.bankFiltered().length,16);
reset();a.bankState.source='wedding2022';a.bankState.scope='MA';assert.equal(a.bankFiltered().length,0,'Combined MA labels must be supported by the selected source');
reset();a.bankState.query='alat musik pukul dari bambu';assert(a.bankFiltered().some(f=>f.form==='etek'));
a.bankState.source='dictionary';assert(!a.bankFiltered().some(f=>f.form==='etek'),'Selected-source search must not borrow the gloss from the 2009 preview');
reset();a.bankState.query='Acorus calamus';assert(a.bankFiltered().some(f=>f.form==='salin batu'));
reset();a.bankState.query='manghiang';a.renderBank();assert(element('#bank-results').innerHTML.includes('Glos sumber (id)'));
reset();a.bankState.source='abvd1655';a.bankState.scope='Sipirok';
assert.equal(a.bankFiltered().length,1);assert.equal(a.bankFiltered()[0].form,'ihan');
reset();a.bankState.source='abvd1655';a.bankState.scope='Mdl';
assert.equal(a.bankFiltered().length,7,'The selected source must itself support the language label');
reset();a.bankState.source='abvd1655';a.bankState.kind='headword';
assert.equal(a.bankFiltered().length,0,'A source word-list entry must not inherit another source headword classification');
reset();a.bankState.query='niabahon';assert(a.bankFiltered().some(f=>f.form==='niabahon'));
reset();a.bankState.letter='F';a.renderBank();assert(element('#bank-results').innerHTML.includes('Belum ada bentuk'));
documentListeners.click({target:{closest:()=>({disabled:false,dataset:{bankReset:'true'}})}});
assert.equal(a.bankFiltered().length,10821);assert.equal(element('#bank-source').value,'all');
element('#bank-source').listeners.change({target:{value:'sight2022'}});
assert.equal(a.bankFiltered().length,12);
reset();a.renderBank();assert.equal((element('#bank-results').innerHTML.match(/<article/g)||[]).length,24);
a.bankState.page=9999;a.renderBank();assert.equal(a.bankState.page,451);
const narian=bank.forms.find(f=>f.form==='narian');a.openBankDetail(narian.id);
assert(element('#bank-detail').innerHTML.includes('27303/2/Kamus%20Bahasa%20Angkola'));
assert(!element('#bank-detail').innerHTML.includes('34696/1/'));
assert(element('#bank-modal').open);
const abvdRef=bank.forms.flatMap(f=>f.references).find(r=>r.sourceId==='abvd1655');
assert(a.sourcePageUrl(abvdRef).startsWith('https://abvd.clld.org/valuesets/'));
assert(!a.sourcePageUrl(abvdRef).includes('#page='));
for(const r of bank.forms.flatMap(f=>f.references)){
  const u=a.sourcePageUrl(r);assert(u.startsWith('https://'));
  if(r.pdfPage)assert(u.endsWith('#page='+r.pdfPage));
  if(r.sourceId!=='dictionary')assert(!u.includes('/34696/'));
}
reset();a.exportBankTSV();let rows=downloads.at(-1).content.replace(/^\uFEFF/,'').split('\n').map(r=>r.split('\t'));
assert.equal(rows.length,10822);assert(rows.every(r=>r.length===5));
const lookup=new Map(bank.forms.map(f=>[f.form,f]));
for(const row of rows.slice(1))if(!lookup.get(row[0]).entryId)assert(row.slice(1).every(v=>v===''));
a.exportBankLabels();rows=downloads.at(-1).content.replace(/^\uFEFF/,'').split('\n').map(r=>r.split('\t'));
assert.equal(rows.length,10822);assert(rows.every(r=>r.length===9));
reset();a.bankState.source='abvd1655';a.bankState.scope='Mdl';a.exportBankLabels();
rows=downloads.at(-1).content.replace(/^\uFEFF/,'').split('\n').map(r=>r.split('\t'));
assert.equal(rows.length,8);assert(rows.slice(1).every(r=>r[4]==='Mdl'&&r[8]==='abvd1655'));
reset();
element('#local-name-search').value='';a.renderLocalNames();
assert.equal((element('#local-name-results').innerHTML.match(/<article/g)||[]).length,183);
assert.equal((element('#local-name-results').innerHTML.match(/plant-review-note supported/g)||[]).length,21);
assert.equal((element('#local-name-results').innerHTML.match(/plant-review-note caution/g)||[]).length,10);
assert(element('#source-audit-cards').innerHTML.includes('edisi 2019 belum diperoleh'));
assert.equal((element('#source-audit-cards').innerHTML.match(/<article/g)||[]).length,6);
element('#local-name-search').value='spearmint';a.renderLocalNames();assert(element('#local-name-count').textContent.startsWith('1 '));
a.exportLocalNames();assert.equal(downloads.at(-1).content.split('\n').length,184);
assert(downloads.at(-1).content.split('\n').every(row=>row.split('\t').length===9));
element('#local-name-search').value='';element('#local-name-status').value='supported';a.renderLocalNames();assert(element('#local-name-count').textContent.startsWith('21 '));
element('#local-name-status').value='pending';a.renderLocalNames();assert(element('#local-name-count').textContent.startsWith('152 '));
element('#local-name-status').value='needs-check';a.renderLocalNames();assert(element('#local-name-count').textContent.startsWith('10 '));
element('#local-name-status').value='all';element('#local-name-search').value='Scaphium';a.renderLocalNames();assert(element('#local-name-count').textContent.startsWith('1 '));assert(element('#local-name-results').innerHTML.includes('Dua takson berbeda'));
reset();
documentListeners.click({target:{closest:()=>({id:'bank-latest',disabled:false,dataset:{}})}});
assert.equal(a.bankFiltered().length,118);assert.equal(element('#bank-latest')['aria-pressed'],'true');
a.bankState.source='plants2019';a.bankState.scope='MA';assert.equal(a.bankFiltered().length,21);
a.bankState.scope='Mdl';assert.equal(a.bankFiltered().length,0);
reset();a.bankState.latestOnly=true;a.exportBankLabels();
rows=downloads.at(-1).content.replace(/^\uFEFF/,'').split('\n').map(r=>r.split('\t'));
assert.equal(rows.length,119);assert(rows.slice(1).every(r=>bank.researchUpdate.newFormIds.includes(r[7])));
documentListeners.click({target:{closest:()=>({disabled:false,dataset:{bankReset:'true'}})}});
assert.equal(a.bankFiltered().length,10821);assert.equal(element('#bank-latest')['aria-pressed'],'false');
reset();a.bankState.query='Piper attenuatum';a.bankState.source='plants2019';assert(a.bankFiltered().some(f=>f.form==='simanat'));
a.bankState.query='Piper betle';assert(a.bankFiltered().some(f=>f.form==='simanat'));
reset();a.bankState.kind='culinary_term';assert.equal(a.bankFiltered().length,15);
reset();a.bankState.query='pastak-pastak ni paradaton';a.renderBank();assert(element('#bank-results').innerHTML.includes('rambu-rambu adat'));

console.log(JSON.stringify({bankLogic:'passed',forms:10821,sourceFilters:24,pendingBlankExports:9417,localNameObservations:183,visualBrowserTest:false}));
