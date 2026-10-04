# Release v1 validation

Completed in the build environment before packaging; no new live API calls were made here.

- Existing Windows finish return: 72 engine tests and 8 release/import tests passed; 13 genuine calls in that run, estimated $0.855802 (not an invoice).
- New targeted-review preflight: 2 orchestration tests, 15 prose tests, 12 pair tests and 5 publication gate tests passed. Source pins and full-context anchors passed. A simulated failed prose stage still ran the pair stage, preserved old files, and returned both new outputs.
- Lossless UI transport: all 162,256 evaluated records round-trip across four dates; malformed payloads rejected.
- Resident logic: 16 adversarial assertions plus 12,000 actual-data topic summaries passed.
- Resident claim gates: 24 assertions passed; all 13 released claims have matching rule fingerprints, exact source passages, and distinct model-response review receipts. Six semantically incomplete rewrites remain withheld.
- Static/fixture UI verification: 43 checks passed. Local HTTP returned 200 for the index, codec, manifest, compact lookups and canonical submission JSON archive.
- Publication is 70 files; every file is below 25 MiB. Method note is one rendered and inspected PDF page.

Visual browser interaction, mobile readability, deployed URL and submission receipts still need verification. Tests do not establish legal accuracy or completeness. The next six-call review produces a return for audit and does not automatically alter the publication or existing canonical snapshot.
