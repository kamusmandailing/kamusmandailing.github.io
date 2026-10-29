PRAGMA page_size=8192;
PRAGMA foreign_keys=ON;
CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE sources (id TEXT PRIMARY KEY, title TEXT NOT NULL, description TEXT NOT NULL, url TEXT NOT NULL, document_url TEXT NOT NULL, short_title TEXT NOT NULL);
CREATE TABLE entries (
 id TEXT PRIMARY KEY, mandailing TEXT NOT NULL COLLATE NOCASE UNIQUE,
 category TEXT NOT NULL, part_of_speech TEXT NOT NULL DEFAULT '',
 status TEXT NOT NULL CHECK(status IN ('source_attested','draft','personal')),
 batch TEXT, reviewed_at TEXT, scope TEXT NOT NULL, note TEXT NOT NULL,
 example_status TEXT NOT NULL CHECK(example_status IN ('source_quoted','pending','draft'))
);
CREATE TABLE translations (
 entry_id TEXT NOT NULL REFERENCES entries(id), language TEXT NOT NULL CHECK(language IN ('id','ms-MY','en')),
 value TEXT NOT NULL CHECK(length(trim(value))>0), status TEXT NOT NULL,
 PRIMARY KEY(entry_id,language)
);
CREATE TABLE aliases (entry_id TEXT NOT NULL REFERENCES entries(id), alias TEXT NOT NULL, PRIMARY KEY(entry_id,alias));
CREATE TABLE entry_references (
 entry_id TEXT PRIMARY KEY REFERENCES entries(id), source_id TEXT NOT NULL REFERENCES sources(id),
 source_lemma TEXT NOT NULL, location_kind TEXT NOT NULL, printed_page TEXT NOT NULL,
 pdf_page INTEGER NOT NULL CHECK(pdf_page>0), language_label TEXT NOT NULL, homonym TEXT
);
CREATE TABLE translation_references (
 entry_id TEXT NOT NULL REFERENCES entries(id), language TEXT NOT NULL,
 source_id TEXT NOT NULL REFERENCES sources(id), url TEXT NOT NULL, note TEXT NOT NULL
);
CREATE TABLE examples (
 entry_id TEXT PRIMARY KEY REFERENCES entries(id), mandailing TEXT NOT NULL,
 indonesia TEXT NOT NULL, source_id TEXT NOT NULL REFERENCES sources(id),
 printed_page TEXT NOT NULL, pdf_page INTEGER NOT NULL, note TEXT NOT NULL
);
CREATE INDEX entries_category_idx ON entries(category);
CREATE INDEX translations_value_idx ON translations(value COLLATE NOCASE);
CREATE INDEX aliases_lookup_idx ON aliases(alias COLLATE NOCASE);
CREATE VIEW dictionary AS
 SELECT e.id, e.mandailing AS Mandailing,
 ti.value AS Indonesia, tm.value AS "Melayu Malaysia", te.value AS English,
 CASE WHEN x.mandailing IS NOT NULL THEN 'Mandailing: '||x.mandailing||' — Indonesia: '||x.indonesia ELSE '' END AS "Contoh Kalimat"
 FROM entries e JOIN translations ti ON ti.entry_id=e.id AND ti.language='id'
 JOIN translations tm ON tm.entry_id=e.id AND tm.language='ms-MY'
 JOIN translations te ON te.entry_id=e.id AND te.language='en'
 LEFT JOIN examples x ON x.entry_id=e.id;
CREATE TABLE lexical_forms (
 id TEXT PRIMARY KEY, form TEXT NOT NULL COLLATE NOCASE UNIQUE,
 curated_entry_id TEXT REFERENCES entries(id), status TEXT NOT NULL,
 kinds_json TEXT NOT NULL, labels_json TEXT NOT NULL, usage_tags_json TEXT NOT NULL
);
CREATE TABLE lexical_occurrences (
 id INTEGER PRIMARY KEY, form_id TEXT NOT NULL REFERENCES lexical_forms(id),
 source_id TEXT NOT NULL REFERENCES sources(id), printed_page TEXT NOT NULL,
 pdf_page INTEGER CHECK(pdf_page IS NULL OR pdf_page>0), kind TEXT NOT NULL, parent_form TEXT NOT NULL,
 homonym TEXT NOT NULL, labels_json TEXT NOT NULL, label_basis TEXT NOT NULL,
 layout_status TEXT NOT NULL, source_column INTEGER, source_x REAL, source_y REAL,
 cross_reference TEXT NOT NULL, printed_notation TEXT NOT NULL, normalization_note TEXT NOT NULL,
 source_url TEXT NOT NULL, source_locator TEXT NOT NULL, source_scope TEXT NOT NULL,
 source_gloss TEXT NOT NULL, gloss_language TEXT NOT NULL, annotation TEXT NOT NULL, reference_json TEXT NOT NULL,
 taxon_as_printed TEXT NOT NULL
);
CREATE TABLE source_coverage (
 source_id TEXT NOT NULL REFERENCES sources(id), printed_page INTEGER NOT NULL,
 pdf_page INTEGER NOT NULL, body_span_count INTEGER NOT NULL, lexical_record_count INTEGER NOT NULL,
 PRIMARY KEY(source_id,printed_page)
);
CREATE TABLE source_catalog (id TEXT PRIMARY KEY, title TEXT NOT NULL, url TEXT NOT NULL, inventory_status TEXT NOT NULL, note TEXT NOT NULL, sha256 TEXT NOT NULL);
CREATE TABLE extraction_audit (
 source_id TEXT NOT NULL REFERENCES sources(id), candidate_id INTEGER NOT NULL,
 pdf_page INTEGER NOT NULL, printed_page INTEGER NOT NULL, source_column INTEGER NOT NULL,
 bbox_json TEXT NOT NULL, candidate_kind TEXT NOT NULL, review_status TEXT NOT NULL,
 accepted_printed_forms_json TEXT NOT NULL, PRIMARY KEY(source_id,candidate_id)
);
CREATE TABLE additional_coverage (source_id TEXT PRIMARY KEY REFERENCES sources(id), details_json TEXT NOT NULL);
CREATE TABLE local_name_observations (
 id TEXT PRIMARY KEY, name TEXT NOT NULL, source_id TEXT NOT NULL REFERENCES sources(id),
 printed_page TEXT NOT NULL, pdf_page INTEGER NOT NULL, source_locator TEXT NOT NULL,
 language_status TEXT NOT NULL, scope TEXT NOT NULL, normalization_note TEXT NOT NULL,
 matched_form_id TEXT REFERENCES lexical_forms(id),
 taxon_as_printed TEXT NOT NULL, taxon_expanded TEXT NOT NULL, taxon_note TEXT NOT NULL
);
CREATE TABLE local_name_reviews (
 observation_id TEXT PRIMARY KEY REFERENCES local_name_observations(id),
 review_status TEXT NOT NULL, note TEXT NOT NULL, taxon_as_printed TEXT NOT NULL,
 evidence_json TEXT NOT NULL
);
CREATE TABLE second_pass_extraction_audit (
 source_id TEXT NOT NULL REFERENCES sources(id), candidate_id INTEGER NOT NULL,
 pdf_page INTEGER NOT NULL, source_column INTEGER NOT NULL,
 bbox_json TEXT NOT NULL, review_status TEXT NOT NULL, accepted_forms_json TEXT NOT NULL,
 PRIMARY KEY(source_id,candidate_id)
);
CREATE INDEX lexical_occurrences_form_idx ON lexical_occurrences(form_id);
CREATE INDEX lexical_occurrences_parent_idx ON lexical_occurrences(parent_form);
CREATE VIEW vocabulary_all AS
 SELECT f.id, f.form AS Mandailing, d.Indonesia, d."Melayu Malaysia", d.English,
 d."Contoh Kalimat", f.status, f.curated_entry_id, f.kinds_json, f.labels_json
 FROM lexical_forms f LEFT JOIN dictionary d ON d.id=f.curated_entry_id;
PRAGMA user_version=5;
