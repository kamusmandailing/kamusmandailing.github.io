#!/usr/bin/env python3
"""Regression tests for current-vs-historical Kamus Mandailing release counts."""
import copy
import json
from unittest.mock import patch
from research import release_snapshot as rs

snapshot=rs.make_snapshot()
tracked=json.loads((rs.ROOT/rs.SNAPSHOT_PATH).read_text(encoding="utf-8"))
assert snapshot==tracked
assert snapshot["counts"]["sourceForms"]==10821
assert snapshot["counts"]["curatedEntries"]==1404
assert snapshot["counts"]["pendingTranslations"]==9417
assert snapshot["counts"]["referenceRecords"]==13745
assert snapshot["historicalProgress"]["sourceForms"]==10250
assert snapshot["historicalProgress"]["referenceRecords"]==12679
assert snapshot["scope"]["speakerVerifiedSenseCount"] is None

original=rs.read
def corrupted(field,value,filename):
 def read(root,relative):
  result=copy.deepcopy(original(root,relative))
  if relative==filename:
   node=result
   for key in field[:-1]:
    node=node[key]
   node[field[-1]]=value
  return result
 return read

mutations=[
 (["stats","uniqueForms"],10820,"research/coverage_audit.json"),
 (["stats","referenceRecords"],13744,"research/coverage_audit.json"),
 (["inventory","uniqueForms"],10821,"research/progress.json"),
 (["stats","reviewedTranslations"],1405,"research/coverage_audit.json")
]
for keys,value,file in mutations:
 with patch.object(rs,"read",corrupted(keys,value,file)):
  try:
   rs.make_snapshot()
  except ValueError:
   continue
  raise AssertionError(f"Stale snapshot condition was not detected: {keys}")
print("Current release snapshot and four stale/mutated baseline guards: PASS")
