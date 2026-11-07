#!/usr/bin/env python3
"""Guard public README statistics against canonical release evidence.

This is a *claims consistency* check, not a linguistic review or a declaration
that every form, translation, or example is speaker-verified.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check(root: Path = ROOT) -> None:
    audit = json.loads((root / "research/coverage_audit.json").read_text(encoding="utf-8"))
    snapshot = json.loads((root / "research/release_snapshot.json").read_text(encoding="utf-8"))
    readme = (root / "README.md").read_text(encoding="utf-8")
    intro = readme.split("## Menggunakan aplikasi", 1)[0]
    counts = snapshot["counts"]
    stats = audit["stats"]

    expected = {
        "sourceForms": stats["uniqueForms"],
        "curatedEntries": stats["reviewedTranslations"],
        "pendingTranslations": stats["pendingTranslations"],
        "referenceRecords": stats["referenceRecords"],
        "sourceCount": stats["sourceCount"],
    }
    for name, value in expected.items():
        if counts[name] != value:
            raise AssertionError(f"Release snapshot disagrees with audit: {name}")

    if counts["sourceForms"] != counts["curatedEntries"] + counts["pendingTranslations"]:
        raise AssertionError("Curated and pending counts do not partition source forms")
    if counts["examplesWithSource"] + counts["curatedEntriesWithoutSourceExample"] != counts["curatedEntries"]:
        raise AssertionError("Example coverage does not partition curated entries")
    if snapshot["releaseVersion"] != audit["version"]:
        raise AssertionError("Snapshot release version does not match audit")

    # Scope must explicitly avoid converting source attestation into speaker approval.
    if snapshot["scope"].get("speakerVerifiedSenseCount") is not None:
        raise AssertionError("Speaker-verified count needs independent review evidence and an updated policy")
    if "bukan pengesahan" not in snapshot["scope"]["curatedEntries"].casefold():
        raise AssertionError("Curated entries must not be presented as speaker-validated")

    normalized_intro = intro.casefold()
    for label, count in counts.items():
        if label not in expected:
            continue
        formatted = f"{count:,}".replace(",", ".")
        if not re.search(r"(?<!\\d)" + re.escape(formatted) + r"(?!\\d)", intro):
            raise AssertionError(f"Public README intro missing current {label} count: {formatted}")
    for phrase in ("menunggu penelaahan", "bukan klaim", "label angkola"):
        if phrase not in normalized_intro:
            raise AssertionError(f"Public README intro is missing a scope warning: {phrase}")


if __name__ == "__main__":
    check()
    print("PASS: README release statistics and source/speaker scope match canonical snapshot")
