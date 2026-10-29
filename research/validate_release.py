"""Validate exported evidence, preserved identities, schema and app payloads."""
from pathlib import Path
from html.parser import HTMLParser
import json,sqlite3,csv,io,hashlib,zipfile,subprocess,collections

ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads((ROOT/p).read_text())
bank=read('src/inventory.json');words=read('src/words.json');sources=read('src/sources.json')
manifest=read('data/database/kamusmandailing.json');stats=bank['stats'];checks={}
def passed(name,condition):
    assert condition,name
    checks[name]=True

extension=read('research/extension_20261027.json')
passed('expectedCounts',stats['uniqueForms']==10821 and stats['releasePreviousUniqueForms']==10703 and stats['releaseAddedUniqueForms']==118 and stats['referenceRecords']==13745 and stats['releaseAddedReferences']==174)
passed('uniqueForms',len({f['form'].casefold() for f in bank['forms']})==len(bank['forms'])==10821)
old={r['form'].casefold() for r in read('research/source_inventory.json')['records']}|{w['md'].casefold() for w in words}
forms={f['form'].casefold():f for f in bank['forms']}
passed('legacyFormsPreserved',len(old)==8177 and old<=forms.keys())
previous=old|{r['form'].casefold() for r in read('research/additional_inventory.json')['records'] if r.get('extensionBatch')!='2026-10-30-DEEP03'}
passed('previousReleaseFormsPreserved',len(previous)==10703 and previous<=forms.keys())
passed('stableFormIds',all(f['id']=='form-'+hashlib.sha256(k.encode()).hexdigest()[:16] for k,f in forms.items()))
passed('curatedIdsPreserved',len({w['id'] for w in words})==1404 and {f['entryId'] for f in bank['forms'] if f['entryId']}=={w['id'] for w in words})
source_ids={s['id'] for s in sources}
passed('referenceSourcesPresent',all(ref['sourceId'] in source_ids for f in bank['forms'] for ref in f['references']))
passed('referenceLabelsIndependent',all(ref['labels'] and len(set(ref['labels']))==len(ref['labels']) for f in bank['forms'] for ref in f['references']))
passed('webLocationsNullable',all(ref['pdfPage'] is None and ref.get('url','').startswith('https://abvd.clld.org/valuesets/') for f in bank['forms'] for ref in f['references'] if ref['sourceId']=='abvd1655'))
passed('2021PageCoverage',len(bank['coverage'])==248 and {p['printedPage'] for p in bank['coverage']}==set(range(1,249)))
passed('jsonMatchesAppData',manifest['forms']==bank['forms'] and manifest['entries']==words and manifest['localNameObservations']==bank['localNames'])
passed('pendingCount',sum(f['entryId'] is None for f in bank['forms'])==9417)
passed('extensionProvenance',len(extension['records'])==793 and collections.Counter(r['sourceId'] for r in extension['records'])=={'dictionary1977':54,'idiom2012':75,'culture2021':650,'flora2015':13,'betle2020':1})
passed('duplicateScanLocationsMerged',len(extension['duplicateBaselineLocations'])==8)
passed('sourceGlossSeparated',sum(any(r.get('sourceGloss') for r in f['references']) for f in bank['forms'])==stats['sourceGlossForms'])
passed('researchUpdateMatches',manifest['researchUpdate']==bank['researchUpdate'] and bank['researchUpdate']['addedForms']==118 and bank['researchUpdate']['addedReferences']==174)
followup=read('research/extension_20261027b.json')
passed('followupProvenance',len(followup['records'])==99 and followup['counts']['newForms']==54 and collections.Counter(r['sourceId'] for r in followup['records'])=={'plants2018':17,'wedding2022':43,'ginger2023':8,'patuaekkon2024':13,'pasak2015':1,'parinduri2009':17})
passed('curatedBytesPreserved',hashlib.sha256((ROOT/'src/words.json').read_bytes()).hexdigest()=='4ce1fee295abcd66ba5eb72a9315e611a93f42eb3707322c89595e1ac29aeac5')
passed('MAIsCombinedCode',all(r['labels']==['MA'] and r['labelBasis']=='direct_language_code' for r in followup['records'] if r['sourceId']=='plants2018'))
passed('translatedLabelsNotPromoted',not any(r['form'].casefold() in {'pedestal','unique','curcuma','incor','the lamp'} for r in followup['records'] if r['sourceId']=='ginger2023') and not any(r['form'].startswith('banana ') or r['form']=='pohon bargot' for r in followup['records'] if r['sourceId']=='wedding2022'))

latest=read('research/extension_20261030.json')
passed('latestProvenance',len(latest['records'])==174 and latest['counts']['newForms']==118 and collections.Counter(r['sourceId'] for r in latest['records'])=={'cultural2018':102,'plants2019':27,'gordang2022':17,'upah2021':12,'culinary2021':16})
passed('latestIdsExactlyNew',set(latest['newFormIds'])=={f['id'] for k,f in forms.items() if k not in previous} and len(latest['newFormIds'])==118)
passed('latestMAOnlyCombined',all(r['labels']==['MA'] and r['labelBasis']=='direct_language_code' for r in latest['records'] if r['sourceId']=='plants2019'))
passed('latestStudyScopeNotDirectMdl',all(r['labels']==['Mdl-scope'] for r in latest['records'] if r['sourceId']!='plants2019'))
passed('displacedGlossesHeld',all(not r['sourceGloss'] for r in latest['records'] if r['sourceId']=='cultural2018' and r['sourceLocator'].startswith('Tabel 1') and int(r['sourceLocator'].split()[-1])>=26))
passed('wrappedPhraseNotSpuriousIdiom',any(r['form']=='anak ni manuk na langka-langka indalu' for r in latest['records']) and not any(r['form']=='indalu' for r in latest['records']))
passed('simanatTaxaKeptSeparate',{r['taxonAsPrinted'] for r in latest['records'] if r['sourceId']=='plants2019' and r['form']=='simanat'}=={'Piper attenuatum','Piper betle'})
passed('webCulinaryEvidenceHonest',all(r['pdfPage'] is None and r['layoutStatus']=='published_fulltext_web_checked' and 'researchgate.net/' in r['url'] for r in latest['records'] if r['sourceId']=='culinary2021'))
passed('translatedArtifactsExcluded',not any(r['form'] in {'sabah ginger','redfish'} for r in latest['records']))

def tsv(name,width,rows):
    data=list(csv.reader(io.StringIO((ROOT/'data'/name).read_text(encoding='utf-8-sig')),delimiter='\t'))
    passed('tsv-'+name,len(data)==rows+1 and all(len(row)==width for row in data))
    return data
data=tsv('kosakata_semua.tsv',5,10821)
passed('fiveColumnHeader',data[0]==['Mandailing','Indonesia','Melayu Malaysia','English','Contoh Kalimat'])
passed('pendingTranslationsBlank',all(all(not cell for cell in row[1:]) for row in data[1:] if forms[row[0].casefold()]['entryId'] is None))
tsv('kosakata_berlabel.tsv',9,10821);tsv('inventaris_sumber.tsv',21,13745);tsv('nama_tumbuhan_pembanding.tsv',6,183)
tsv('telaah_nama_tumbuhan.tsv',8,183)
tsv('nama_botani_sumber.tsv',9,102)
latest_tsv=tsv('tambahan_20261030.tsv',11,sum(r['form'] in set(latest['newForms']) for r in latest['records']))
passed('latestTSVIds',set(row[0] for row in latest_tsv[1:])==set(latest['newFormIds']))
tsv('kamus.tsv',5,1404)
con=sqlite3.connect(ROOT/'data/database/kamusmandailing.sqlite')
passed('sqliteIntegrity',con.execute('PRAGMA integrity_check').fetchone()[0]=='ok')
passed('sqliteForeignKeys',not con.execute('PRAGMA foreign_key_check').fetchall())
passed('schemaVersion5',con.execute('PRAGMA user_version').fetchone()[0]==5 and manifest['schemaVersion']==5)
counts={t:con.execute('SELECT count(*) FROM '+t).fetchone()[0] for t in ['entries','dictionary','translations','lexical_forms','lexical_occurrences','vocabulary_all','source_coverage','extraction_audit','local_name_observations','local_name_reviews','second_pass_extraction_audit']}
passed('sqliteCounts',counts=={'entries':1404,'dictionary':1404,'translations':4212,'lexical_forms':10821,'lexical_occurrences':13745,'vocabulary_all':10821,'source_coverage':248,'extraction_audit':5671,'local_name_observations':183,'local_name_reviews':183,'second_pass_extraction_audit':1395})
passed('sourceURLsCorrect',con.execute("SELECT count(*) FROM lexical_occurrences WHERE source_id!='dictionary' AND source_url LIKE '%/34696/%'").fetchone()[0]==0)
passed('allReferenceURLsPresent',con.execute("SELECT count(*) FROM lexical_occurrences WHERE source_url NOT LIKE 'https://%'").fetchone()[0]==0)
passed('webSourcesNoFakePDFPage',con.execute("SELECT count(*) FROM lexical_occurrences WHERE source_id IN ('abvd1655','idiom2023') AND pdf_page IS NOT NULL").fetchone()[0]==0)
passed('localNamesSeparated',con.execute("SELECT count(*) FROM local_name_observations WHERE language_status='local_name_language_unspecified'").fetchone()[0]==183)
passed('localNameReviewsScoped',dict(con.execute('SELECT review_status,count(*) FROM local_name_reviews GROUP BY review_status'))==stats['localNameReviewCounts'])
passed('langgeMeaningNotConflated',con.execute("SELECT r.review_status FROM local_name_reviews r JOIN local_name_observations o ON o.id=r.observation_id WHERE lower(o.name)='langge'").fetchone()[0]=='homonym_risk')
passed('palagaTaxaNotConflated',con.execute("SELECT r.review_status FROM local_name_reviews r JOIN local_name_observations o ON o.id=r.observation_id WHERE lower(o.name)='palaga'").fetchone()[0]=='taxon_conflict')
passed('taxaColumnCounts',con.execute("SELECT count(*) FROM lexical_occurrences WHERE taxon_as_printed!=''").fetchone()[0]==102 and con.execute("SELECT count(*) FROM local_name_observations WHERE taxon_as_printed!=''").fetchone()[0]==182)
passed('sourceBlankTaxonPreserved',con.execute("SELECT taxon_as_printed FROM local_name_observations WHERE id='plant2022-91'").fetchone()[0]=='')
passed('scopeOfPlantSupport',con.execute("SELECT count(*) FROM local_name_reviews WHERE review_status IN ('cross_source_supported','combined_scope_supported','study_scope_supported')").fetchone()[0]==21)
passed('observationIdentitiesPreserved',{r['id'] for r in bank['localNames']}=={'plant2022-'+str(i) for i in range(1,164)}|{'wild2026-'+str(i) for i in range(1,21)})
con.close()
audit=read('research/1977_extraction_geometry.json')
accepted=[r for r in audit['records'] if r['reviewStatus']=='accepted_visual']
passed('1977AcceptedCropsTraced',len(accepted)==2641 and all(any(ref.get('recordId')=='1977-'+str(r['id']) for f in bank['forms'] for ref in f['references']) for r in accepted))
passed('rejectedCropsNotWords',all(not r.get('acceptedPrintedForms') for r in audit['records'] if r['reviewStatus']!='accepted_visual'))
passed('correctedScanReading',any(ref.get('recordId')=='1977-4590' for ref in forms['narian']['references']) and not any(ref.get('recordId')=='1977-3093' for f in bank['forms'] for ref in f['references']))
second=read('research/1977_second_pass_audit.json')
passed('secondPassDecisionsTraced',len(second['records'])==1395 and sum(r['reviewStatus']=='accepted_visual' for r in second['records'])==59 and manifest['secondPassExtractionAudit']==second)
passed('secondPassRejectedNotPromoted',all(not r['acceptedForms'] for r in second['records'] if r['reviewStatus']!='accepted_visual'))

class Scripts(HTMLParser):
    def __init__(self):super().__init__();self.active=None;self.scripts={}
    def handle_starttag(self,tag,attrs):
        if tag=='script':
            a=dict(attrs);self.active=a.get('id','app');self.scripts[self.active]=''
    def handle_data(self,data):
        if self.active:self.scripts[self.active]+=data
    def handle_endtag(self,tag):
        if tag=='script':self.active=None

htmls=[ROOT/p for p in ['index.html','Hata_Kamus_Mandailing.html','dist/index.html','dist/Hata_Kamus_Mandailing.html']]
passed('allHTMLBuildsIdentical',len({hashlib.sha256(p.read_bytes()).hexdigest() for p in htmls})==1)
p=Scripts();p.feed(htmls[0].read_text())
passed('inlineBankMatchesDatabase',json.loads(p.scripts['inventory-data'])==bank)
passed('inlineCuratedAndSourcesMatch',json.loads(p.scripts['seed-data'])==words and json.loads(p.scripts['source-data'])==sources)
passed('noBuildPlaceholders','INLINE_' not in htmls[0].read_text())
import tempfile
with tempfile.TemporaryDirectory() as temp:
    js=Path(temp)/'app.cjs';js.write_text(p.scripts['app']);subprocess.run(['node','--check',str(js)],check=True)
passed('compiledJavaScriptSyntax',True)
logic=subprocess.run(['node',str(ROOT/'research/check_inventory_logic.cjs')],capture_output=True,text=True,check=True)
passed('bankLogicAndExports',json.loads(logic.stdout)['bankLogic']=='passed')
def verify_zip(file):
    with zipfile.ZipFile(file) as z:
        assert z.testzip() is None
        for line in z.read('SHA256SUMS.txt').decode().splitlines():
            digest,name=line.split('  ',1);assert hashlib.sha256(z.read(name)).hexdigest()==digest,name
verify_zip(ROOT/'data/Kamus_Mandailing_Database.zip');passed('databaseZipChecksums',True)
result={'version':bank['version'],'scope':'Merged evidence index; not all vocabulary of all Mandailing dialects.',
        'stats':stats,'sqliteCounts':counts,'checks':checks,
        'labelCountsOverlapping':dict(collections.Counter(l for f in bank['forms'] for l in f['labels'])),
        'browserVerification':'Bank logic checked with a DOM adapter. Visual deployment checks are recorded separately after publication.',
        'baselineAudit':'baseline_coverage_audit.json'}
(ROOT/'research/coverage_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'checksPassed':len(checks),'forms':stats['uniqueForms'],'references':stats['referenceRecords'],'sqlite':counts,'browserVisualTest':False}))
