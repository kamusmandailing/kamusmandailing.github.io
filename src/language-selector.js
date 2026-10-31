/* Language selector: interface labels only; dictionary source entries remain unchanged. */
(function(){
  'use strict';
  const choices={id:'Bahasa Indonesia',md:'Bahasa Mandailing',ms:'Bahasa Melayu (Malaysia)',en:'English'};
  const labels={
    id:['Kamus','Bank kosakata','Disimpan','Belajar','Catatan & sumber','Tambah kata','Pilih bahasa'],
    ms:['Kamus','Bank kosa kata','Disimpan','Belajar','Catatan & sumber','Tambah perkataan','Pilih bahasa'],
    en:['Dictionary','Vocabulary bank','Saved','Learn','Notes & sources','Add word','Choose language'],
    // Unverified Mandailing interface strings fall back to Indonesian pending review.
    md:['Kamus','Bank kosakata','Disimpan','Belajar','Catatan & sumber','Tambah kata','Pilih bahasa']
  };
  const nodes=['[data-nav="dictionary"] > span:nth-child(2)','[data-nav="inventory"] > span:nth-child(2)','[data-nav="saved"] > span:nth-child(2)','[data-nav="learn"] > span:nth-child(2)','[data-nav="sources"] > span:nth-child(2)','#add-word-top > span:last-child'];
  function apply(code){
    const lang=Object.prototype.hasOwnProperty.call(choices,code)?code:'id';
    const copy=labels[lang];
    nodes.forEach((selector,i)=>{const el=document.querySelector(selector);if(el)el.textContent=copy[i];});
    const select=document.getElementById('interface-language');
    if(select){select.value=lang;select.setAttribute('aria-label',copy[6]);}
    // Mandailing has the BCP 47 language tag btm; keep md as the stored UI choice.
    document.documentElement.lang=lang==='md'?'btm':lang;
    try{localStorage.setItem('kamus-interface-language',lang);}catch(e){}
  }
  function init(){
    const host=document.querySelector('.topbar-actions');
    if(!host)return;
    const wrap=document.createElement('label');wrap.className='interface-language-wrap';
    const text=document.createElement('span');text.className='sr-only';text.textContent='Pilih bahasa antarmuka';
    const select=document.createElement('select');select.id='interface-language';select.className='interface-language-select';
    for(const [code,label] of Object.entries(choices)){const opt=document.createElement('option');opt.value=code;opt.textContent=label;select.appendChild(opt);}
    wrap.append(text,select);host.prepend(wrap);
    // Cross-navigation: add an accessible link without changing dictionary data.
    if(!host.querySelector('[data-cross-site="encyclopedia"]')){
      const link=document.createElement('a');
      link.href='https://ensiklopediamandailing.github.io/';
      link.textContent='Ensiklopedia Mandailing';
      link.setAttribute('data-cross-site','encyclopedia');
      link.setAttribute('aria-label','Buka Ensiklopedia Mandailing');
      link.style.cssText='display:inline-flex;align-items:center;min-height:36px;padding:4px 9px;font-size:12px;text-decoration:underline;text-underline-offset:3px';
      host.append(link);
    }
    let initial='id';try{initial=localStorage.getItem('kamus-interface-language')||'id';}catch(e){}
    apply(initial);select.addEventListener('change',()=>apply(select.value));
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();