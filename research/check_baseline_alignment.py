"""Fail the build if the published research summary drifts from the release audit."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
def load(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))

audit = load("research/coverage_audit.json")
progress = load("research/progress.json")
stats = audit["stats"]
summary = progress["inventory"]

fields = (
    "uniqueForms", "bodySourceForms", "sourceRecords",
    "referenceRecords", "reviewedTranslations", "pendingTranslations",
    "headwordRecords", "subentryRecords", "crossReferenceRecords",
    "abbreviationRecords", "boundForms", "indexedPages",
    "normalizationsReviewed", "supplementalRecords",
    "sourceCount", "recordsBySource", "localNameObservations",
)
for field in fields:
    assert summary[field] == stats[field], (
        f"Research summary differs from release audit for {field}: "
        f"{summary[field]!r} != {stats[field]!r}"
    )

assert progress["inventoryBaselineRelease"] == audit["version"]
assert progress["sourceFormsTotal"] == stats["uniqueForms"]
assert progress["sourceFormsAdded"] == stats["uniqueForms"] - summary["previousUniqueForms"]
assert progress["total"] == stats["reviewedTranslations"]
assert summary["reviewedTranslations"] + summary["pendingTranslations"] == summary["uniqueForms"]
assert len(summary["recordsBySource"]) == summary["sourceCount"]
assert sum(summary["recordsBySource"].values()) == summary["referenceRecords"]

print(json.dumps({
    "result": "passed",
    "release": audit["version"],
    "uniqueForms": stats["uniqueForms"],
    "curated": stats["reviewedTranslations"],
    "pending": stats["pendingTranslations"],
    "references": stats["referenceRecords"],
    "sources": stats["sourceCount"],
}, ensure_ascii=False))
