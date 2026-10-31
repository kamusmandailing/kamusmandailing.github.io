/* Phase 6: translated core controls; lexical entries, meaning and evidence NEVER translated by UI code.
 * 'md' is explicitly Indonesian fallback pending Mandailing speaker review.
 * Coverage: selected navigation and search controls only, not the full application.
 */
(function(){
  'use strict';
  const has=(obj,key)=>Object.prototype.hasOwnProperty.call(obj,key);
  const choices={id:'Bahasa Indonesia',md:'Bahasa Mandailing (fallback ID)',ms:'Bahasa Melayu (Malaysia)',en:'English'};
  const strings={
    id:{
      navDictionary:'Kamus',navBank:'Bank kosakata',navSaved:'Disimpan',navLearn:'Belajar',navSources:'Catatan & sumber',
      add:'Tambah / usulkan',choose:'Pilih bahasa antarmuka',
      search:'Cari kosakata',searchHint:'Cari kata, misalnya rumah, bagas, atau house…',
      searchLang:'Bahasa pencarian',allLang:'Semua bahasa',allLetters:'Semua huruf',
      reviewStatus:'Status penelaahan',reviewAll:'Semua status',reviewAttested:'Entri dirujuk',
      reviewDraft:'Draf awal',reviewPersonal:'Kata pribadi',
      results:'Semua kosakata',export:'Ekspor TSV',sort:'Urutkan kosakata',
      searchBank:'Cari dalam seluruh bank',searchBankHint:'Bentuk, takson, induk lema, atau padanan…',
      kind:'Jenis bentuk',scope:'Label bahasa sumber',bankStatus:'Status padanan',bankSource:'Sumber bentuk',
      clear:'Hapus',clearMain:'Hapus pencarian kamus',clearBank:'Hapus pencarian bank',
      viewCards:'Tampilan kartu',viewTable:'Tampilan tabel'
    },
    ms:{
      navDictionary:'Kamus',navBank:'Bank kosa kata',navSaved:'Disimpan',navLearn:'Belajar',navSources:'Nota & sumber',
      add:'Tambah / cadangkan',choose:'Pilih bahasa antara muka',
      search:'Cari kosa kata',searchHint:'Cari perkataan seperti rumah, bagas atau house…',
      searchLang:'Bahasa carian',allLang:'Semua bahasa',allLetters:'Semua huruf',
      reviewStatus:'Status semakan',reviewAll:'Semua status',reviewAttested:'Entri bersumber',
      reviewDraft:'Draf awal',reviewPersonal:'Perkataan peribadi',
      results:'Semua kosa kata',export:'Eksport TSV',sort:'Susun kosa kata',
      searchBank:'Cari dalam seluruh bank',searchBankHint:'Bentuk, takson, kata induk atau padanan…',
      kind:'Jenis bentuk',scope:'Label bahasa sumber',bankStatus:'Status padanan',bankSource:'Sumber bentuk',
      clear:'Padam',clearMain:'Padam carian kamus',clearBank:'Padam carian bank',
      viewCards:'Paparan kad',viewTable:'Paparan jadual'
    },
    en:{
      navDictionary:'Dictionary',navBank:'Vocabulary bank',navSaved:'Saved',navLearn:'Learn',navSources:'Notes & sources',
      add:'Add / suggest',choose:'Choose interface language',
      search:'Search vocabulary',searchHint:'Search a word, for example rumah, bagas, or house…',
      searchLang:'Search language',allLang:'All languages',allLetters:'All letters',
      reviewStatus:'Review status',reviewAll:'All statuses',reviewAttested:'Source-attested entry',
      reviewDraft:'Early draft',reviewPersonal:'Personal word',
      results:'All vocabulary',export:'Export TSV',sort:'Sort vocabulary',
      searchBank:'Search the full bank',searchBankHint:'Form, taxon, headword, or translation…',
      kind:'Form type',scope:'Source language label',bankStatus:'Translation status',bankSource:'Source',
      clear:'Clear',clearMain:'Clear dictionary search',clearBank:'Clear bank search',
      viewCards:'Card view',viewTable:'Table view'
    }
  };
  // Leaf nodes only. Never overwrite icons or dynamic search results with textContent.
  const labels={
    navDictionary:'[data-nav="dictionary"] > span:nth-child(2)',
    navBank:'[data-nav="inventory"] > span:nth-child(2)',
    navSaved:'[data-nav="saved"] > span:nth-child(2)',
    navLearn:'[data-nav="learn"] > span:nth-child(2)',
    navSources:'[data-nav="sources"] > span:nth-child(2)',
    add:'#add-word-top > span:last-child',
    allLetters:'#all-letters',
    reviewStatus:'label[for="editorial-filter"]',
    results:'#results-title',
    search:'label[for="search"]',
    searchLang:'label[for="search-language"]',
    sort:'label[for="sort"]',
    searchBank:'label[for="bank-search"]',
    kind:'label[for="bank-kind"]',
    scope:'label[for="bank-scope"]',
    bankStatus:'label[for="bank-status"]',
    bankSource:'label[for="bank-source"]',
    clear:'#search-clear',
    clearMain:null,
    clearBank:null
  };
  const options={
    allLang:'#search-language option[value="all"]',
    reviewAll:'#editorial-filter option[value="all"]',
    reviewAttested:'#editorial-filter option[value="attested"]',
    reviewDraft:'#editorial-filter option[value="draft"]',
    reviewPersonal:'#editorial-filter option[value="personal"]'
  };
  function updateText(selector,value,lang){
    if(!selector)return;
    const el=document.querySelector(selector);
    if(el){el.textContent=value;el.lang=lang;}
  }
  function apply(code){
    const selected=has(choices,code)?code:'id';
    const fallback=selected==='md';
    const language=(selected==='en' || selected==='ms')?selected:'id';
    const copy=strings[fallback?'id':selected];
    for(const [key,selector] of Object.entries(labels)) if(selector) updateText(selector,copy[key],language);
    for(const [key,selector] of Object.entries(options)) updateText(selector,copy[key],language);
    for(const [id,value] of [['search','searchHint'],['bank-search','searchBankHint']]){
      const el=document.getElementById(id);if(el){el.placeholder=copy[value];el.setAttribute('aria-label',copy[id==='search'?'search':'searchBank']);}
    }
    const select=document.getElementById('interface-language');
    if(select){select.value=selected;select.setAttribute('aria-label',copy.choose);}
    const clearMain=document.getElementById('search-clear'), clearBank=document.getElementById('bank-search-clear');
    if(clearMain){clearMain.textContent=copy.clear;clearMain.setAttribute('aria-label',copy.clearMain);clearMain.lang=language;}
    if(clearBank){clearBank.textContent=copy.clear;clearBank.setAttribute('aria-label',copy.clearBank);clearBank.lang=language;}
    for(const [key,id] of [['export','export-top'],['viewCards','grid-view'],['viewTable','table-view']]){
      const el=document.getElementById(id);if(el){el.setAttribute('aria-label',copy[key]);}
    }
    // Much of the application (evidence, dynamic results, learning UI) remains Indonesian.
    // Keep the document language honest; individually translated controls are tagged above.
    document.documentElement.lang='id';
    document.documentElement.dataset.interfaceLanguage=selected;
    const note=document.getElementById('interface-language-note');
    if(note){
      note.hidden=selected==='id';
      note.lang=language;
      note.textContent=selected==='md'
        ? 'Bahasa Mandailing dipilih. Teks antarmuka masih menggunakan Bahasa Indonesia sampai ditelaah penutur Mandailing; isi kamus tidak diubah.'
        : selected==='en'
          ? 'Partial English interface: results, source notes, and some controls remain in Indonesian. Dictionary translations are unchanged.'
          : 'Antara muka Bahasa Melayu masih separa: hasil, nota sumber dan sebahagian kawalan kekal dalam Bahasa Indonesia. Padanan kamus tidak diubah.';
    }
    try{localStorage.setItem('kamus-interface-language',selected);}catch(e){}
  }
  function init(){
    const host=document.querySelector('.topbar-actions');
    if(!host || document.getElementById('interface-language'))return;
    const wrap=document.createElement('label');wrap.className='interface-language-wrap';
    const caption=document.createElement('span');caption.className='sr-only';caption.textContent='Pilih bahasa antarmuka';
    const select=document.createElement('select');select.id='interface-language';select.className='interface-language-select';
    for(const [code,label] of Object.entries(choices)){
      const option=document.createElement('option');option.value=code;option.textContent=label;select.appendChild(option);
    }
    wrap.append(caption,select);host.prepend(wrap);
    const note=document.createElement('p');
    note.id='interface-language-note';note.className='interface-language-note';note.setAttribute('role','status');note.setAttribute('aria-live','polite');note.hidden=true;
    const ribbon=document.querySelector('.ulos-ribbon');if(ribbon)ribbon.insertAdjacentElement('afterend',note);
    let initial='id';
    try{initial=localStorage.getItem('kamus-interface-language')||'id';}catch(e){}
    apply(initial);
    select.addEventListener('change',()=>apply(select.value));
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
