"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const src = fs.readFileSync(path.join(__dirname,"..","integrations/google-drive-intake/Code.gs"),"utf8");
const headers = [
 "id","tanggal_utc","status","jenis","kata","makna",
 "wilayah","padanan","contoh","sumber","persetujuan","asal","catatan_editor"
];
const sheetData = [headers.slice()];
let calls = {appends:0,sends:0};
const store = new Map([
 ["KAMUS_INTAKE_FOLDER_ID", "test-private-folder"],
 ["KAMUS_INTAKE_SHEET_ID", "test-private-sheet"]
]);
const sheet = {
 getLastRow:()=>sheetData.length,
 getRange:(row,col,count,width)=>({
   getValues:()=>[sheetData[row-1].slice(col-1,col-1+width)],
   setFontWeight:()=>({setBackground:()=>({setFontColor:()=>{}})})
 }),
 appendRow:row=>{sheetData.push(row);calls.appends++;},
 getName:()=>"Masuk"
};
const book={
 getSheetByName:n=>n==="Masuk"?sheet:null,
 getSheets:()=>[sheet],
 getId:()=>"test-private-sheet",
 getUrl:()=>"https://docs.google.com/spreadsheets/d/test-private-sheet/edit"
};
const props={
 getProperty:name=>store.get(name)||null,
 setProperty:(name,value)=>store.set(name,value)
};
const cache=new Map();
const sandbox={
 PropertiesService:{getScriptProperties:()=>props},
 SpreadsheetApp:{openById:id=>{assert.equal(id,"test-private-sheet");return book;}},
 DriveApp:{getFolderById:id=>{assert.equal(id,"test-private-folder");return {};} },
 HtmlService:{createHtmlOutput:markup=>({markup,setTitle(title){this.title=title;return this;}})},
 LockService:{getScriptLock:()=>({tryLock:()=>true,releaseLock:()=>{}})},
 CacheService:{getScriptCache:()=>({
   get:key=>cache.get(key),
   put:(key,v)=>cache.set(key,v)
 })},
 Utilities:{
   getUuid:()=>"unit-test-uuid",
   formatDate:()=> "202610310000"
 },
 Logger:{log:()=>{}},
 console:{error:()=>{}},
 Date, String, Number, Error
};
vm.createContext(sandbox);
vm.runInContext(src,sandbox,{filename:"Code.gs"});
assert.equal(sandbox.setupOnce(),book.getUrl(),"Setup must reuse configured private sheet");
assert.equal(sheetData.length,1,"Setup cannot create extra rows");

const valid={
 jenis:"Kosakata atau padanan baru",
 kata:"amang",
 makna:"Contoh pengujian, bukan entri ilmiah",
 wilayah:"Mandailing",
 padanan:"Indonesia: ...",
 contoh:"",
 sumber:"",
 consent:"yes",
 hpt:""
};
let response=sandbox.doPost({parameter:valid});
assert.equal(calls.appends,1);
assert.equal(sheetData.length,2);
assert.equal(sheetData[1][2],"MENUNGGU TELAAH");
assert.equal(sheetData[1][4],"amang");
assert.match(response.markup,/Usulan diterima untuk ditelaah/);
assert.doesNotMatch(response.markup,/otomatis terbit/i);

for(const bad of [
 {...valid,kata:""},
 {...valid,consent:"no"},
 {...valid,hpt:"bot-filled"},
 {...valid,jenis:"Tidak sesuai"},
 {...valid,makna:"x".repeat(501)}
]){
 const before=calls.appends;
 const r=sandbox.doPost({parameter:bad});
 assert.equal(calls.appends,before,"Invalid submission was appended to private sheet");
 assert.match(r.markup,/Usulan belum tersimpan/);
}

response=sandbox.doPost({parameter:{...valid,kata:"=IMPORTXML(A1,B1)"}});
assert.equal(calls.appends,2);
assert.equal(sheetData[2][4],"'=IMPORTXML(A1,B1)","Spreadsheet formula injection must be disabled");
assert.equal(sheetData[2][2],"MENUNGGU TELAAH");

store.delete("KAMUS_INTAKE_SHEET_ID");
const before=calls.appends;
response=sandbox.doPost({parameter:valid});
assert.equal(calls.appends,before);
assert.match(response.markup,/Usulan belum tersimpan/);
assert(!src.includes("GITHUB_TOKEN"),"No GitHub token is needed for account-free submission");

console.log(JSON.stringify({status:"PASS",checks:["admin-sheet reuse","valid private queue write","pending review status","required fields","consent","honeypot","max length","spreadsheet injection prevention","unconfigured fail closed"]}));
