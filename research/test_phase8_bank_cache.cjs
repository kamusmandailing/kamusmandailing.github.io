/* Phase 8: deterministic cache invariants. Measures repeated work, not device timings. */
const fs=require('node:fs'), path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),read=p=>fs.readFileSync(path.join(root,p),'utf8');
const bank=JSON.parse(read('src/inventory.json')),seed=JSON.parse(read('src/words.json')),sources=JSON.parse(read('src/sources.json'));
const dom=new Map(),listeners={};
function $(selector){
  if(!dom.has(selector))dom.set(selector,{
    value:'',textContent:'',innerHTML:'',style:{},dataset:{},listeners:{},
    addEventListener(event,cb){this.listeners[event]=cb;},
    setAttribute(){},scrollIntoView(){},showModal(){this.open=true;},close(){this.open=false;}
  });
  return dom.get(selector);
}
$('#inventory-data').textContent=JSON.stringify(bank);
const ctx=vm.createContext({
  SEED:seed,SOURCES:sources,RESEARCH:JSON.parse(read('research/progress.json')),
  LANGUAGES:{idn:'Indonesia',my:'Melayu Malaysia',en:'English'},$: $, $$:()=>[],
  document:{addEventListener(e,fn){listeners[e]=fn;}},
  normalize:v=>String(v??'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('id').trim(),
  esc:v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])),
  plain:v=>String(v??'').replace(/[\t\r\n]+/g,' ').trim(),
  icon:()=>'',toast:()=>{},openDetail:()=>{},download:()=>{},exampleCell:()=>''
});
const sourceURL=read('src/app.js').match(/  const sourcePageUrl = ref => \{[\s\S]*?\n  \};/)[0];
vm.runInContext(sourceURL+'\n'+read('src/inventory.js')+
  '\nglobalThis.api={bankFiltered,bankState,bankPerfStats,renderBank};',ctx);
const api=ctx.api, state=api.bankState, start=api.bankPerfStats();
assert.equal(start.searchStringsCached,0,'Full-bank search strings must not build at page startup');
assert.equal(start.sourceListsCached,0,'Source-specific subsets must be lazy');
let rows=api.bankFiltered();
assert.equal(rows.length,10821);
const scans=api.bankPerfStats().filterScans;
for(let i=0;i<40;i++){state.page=i+1;assert.equal(api.bankFiltered(),rows,'Paginators must reuse the same filter result');}
assert.equal(api.bankPerfStats().filterScans,scans,'Repeated pages must not rescan forms');
assert.equal(api.bankPerfStats().searchStringsCached,0,'Paging must not build full-bank text index');

state.source='abvd1655';rows=api.bankFiltered();
const sourceCount=rows.length;
assert(sourceCount>0 && sourceCount<10821);
assert.equal(api.bankPerfStats().sourceListsCached,1,'First selected source should create one subset');
const sourceScans=api.bankPerfStats().filterScans;
for(let i=0;i<30;i++)assert.equal(api.bankFiltered(),rows);
assert.equal(api.bankPerfStats().filterScans,sourceScans,'Selected source filter must be cached');
assert.equal(api.bankPerfStats().searchStringsCached,0,'Selected source must not build whole-bank index');

state.query='sama-sekali-tidak-ada';
assert.equal(api.bankFiltered().length,0);
assert.equal(api.bankPerfStats().searchStringsCached,0,'Selected source searching must not allocate global index');
state.source='all';state.query='salin batu';
assert(api.bankFiltered().some(f=>f.form==='salin batu'));
assert(api.bankPerfStats().searchStringsCached>0,'Whole-bank index should fill only on demand');
const count=api.bankPerfStats().searchStringsCached;
const totalScans=api.bankPerfStats().filterScans;
api.bankFiltered();assert.equal(api.bankPerfStats().searchStringsCached,count);
assert.equal(api.bankPerfStats().filterScans,totalScans);
state.query='Acorus calamus';assert(api.bankFiltered().some(f=>f.form==='salin batu'));
state.query='';state.status='pending';
assert.equal(api.bankFiltered().length,9417);
state.status='reviewed';assert.equal(api.bankFiltered().length,1404);
console.log(JSON.stringify({
  status:'PASS',forms:bank.forms.length,initialSearchStrings:start.searchStringsCached,
  sourceCount,sourceSubsetCaches:api.bankPerfStats().sourceListsCached,
  searchStringsAfterQueries:api.bankPerfStats().searchStringsCached,
  repeatedPageScansAvoided:39,sourceRescansAvoided:30
}));
