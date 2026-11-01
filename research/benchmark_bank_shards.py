#!/usr/bin/env python3
"""Estimate the byte cost and exact-search implications of alphabetic Bank shards."""
from __future__ import annotations

from collections import defaultdict
import gzip
import json
from pathlib import Path
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
bank = json.loads((ROOT / "src/inventory.json").read_text(encoding="utf-8"))
published = json.loads((ROOT / "data/bank-online.json").read_text(encoding="utf-8"))
curated = json.loads((ROOT / "src/words.json").read_text(encoding="utf-8"))
assert bank == published, "Published Bank must match the canonical inventory."


def normalized(value: object) -> str:
    text = unicodedata.normalize("NFD", str(value or "")).casefold()
    return "".join(char for char in text if unicodedata.category(char) != "Mn")


def bucket(form: dict) -> str:
    first = normalized(form.get("form", ""))[:1]
    return first if first.isalpha() else "_"


def encode(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def gzip_size(payload: bytes) -> int:
    return len(gzip.compress(payload, compresslevel=9, mtime=0))


groups: dict[str, list[dict]] = defaultdict(list)
for form in bank["forms"]:
    groups[bucket(form)].append(form)

shard_payloads = {key: encode({"forms": rows}) for key, rows in groups.items()}
metadata = {key: value for key, value in bank.items() if key != "forms"}
manifest = encode({**metadata, "shards": {key: len(rows) for key, rows in sorted(groups.items())}})
full_payload = (ROOT / "data/bank-online.json").read_bytes()
full_compact = encode(bank)

# Estimate an alphabetic initial view using all shards required by its first page.
first_page_keys = list(dict.fromkeys(bucket(form) for form in bank["forms"][:24]))
first_page_payload = manifest + b"".join(shard_payloads[key] for key in first_page_keys)

page_chunks = {}
for chunk_size in (128, 256, 512, 1024):
    chunks = [bank["forms"][offset:offset + chunk_size] for offset in range(0, len(bank["forms"]), chunk_size)]
    payloads = [encode({"forms": chunk}) for chunk in chunks]
    assert [form for chunk in chunks for form in chunk] == bank["forms"]
    first_chunk = manifest + payloads[0]
    page_chunks[str(chunk_size)] = {
        "chunkCount": len(chunks),
        "firstChunkForms": len(chunks[0]),
        "firstChunkRawBytesWithManifest": len(first_chunk),
        "firstChunkGzipBytesWithManifest": gzip_size(manifest) + gzip_size(payloads[0]),
        "allChunksGzipPlusManifestBytes": sum(gzip_size(payload) for payload in payloads) + gzip_size(manifest),
    }

# Recreate the current browser's search fields to show which buckets a cross-field
# query would need. This is a scope example, not a proposed partial-search result.
curated_by_id = {word["id"]: word for word in curated}


def matching_buckets(query: str) -> set[str]:
    needle = normalized(query)
    matched = set()
    for form in bank["forms"]:
        values = [form.get("form", "")]
        for ref in form.get("references", []):
            values.extend((ref.get("parent", ""), ref.get("sourceGloss", ""), ref.get("taxonAsPrinted", "")))
        word = curated_by_id.get(form.get("entryId"))
        if word:
            values.extend((word.get("idn", ""), word.get("my", ""), word.get("en", "")))
            values.extend(word.get("aliases", []))
        if needle in normalized(" ".join(map(str, values))):
            matched.add(bucket(form))
    return matched


form_ids = [form["id"] for form in bank["forms"]]
assert len(form_ids) == len(set(form_ids)) == bank["stats"]["uniqueForms"]
assert sum(len(form["references"]) for form in bank["forms"]) == bank["stats"]["referenceRecords"]

print(json.dumps({
    "canonicalForms": len(form_ids),
    "sourceBytes": len(full_payload),
    "sourceGzipBytes": gzip_size(full_payload),
    "sourceCompactBytes": len(full_compact),
    "sourceCompactGzipBytes": gzip_size(full_compact),
    "shardCount": len(groups),
    "manifestBytes": len(manifest),
    "allShardsRawPlusManifestBytes": sum(map(len, shard_payloads.values())) + len(manifest),
    "allShardsGzipPlusManifestBytes": sum(gzip_size(payload) for payload in shard_payloads.values()) + gzip_size(manifest),
    "firstPageForms": 24,
    "firstPageShardKeys": first_page_keys,
    "firstPagePayloadRawBytes": len(first_page_payload),
    "firstPagePayloadGzipBytes": gzip_size(manifest) + sum(gzip_size(shard_payloads[key]) for key in first_page_keys),
    "contiguousChunkCandidates": page_chunks,
    "largestShards": [
        {"key": key, "forms": len(groups[key]), "rawBytes": len(shard_payloads[key]), "gzipBytes": gzip_size(shard_payloads[key])}
        for key in sorted(groups, key=lambda item: len(groups[item]), reverse=True)[:5]
    ],
    "crossShardSearchExamples": {
        query: sorted(matching_buckets(query)) for query in ("Piper betle", "simanat", "fish")
    },
}, ensure_ascii=False, indent=2))
