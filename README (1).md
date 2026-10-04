# Housing Navigator UI

Static, dependency-free UI for the Housing Navigator integration contract v1. It does **not** compute legal applicability. It reads the coordinator-provided manifest and renders engine outputs, source evidence, change cases, and validation state.

## Production integration

The coordinator serves `ui/` from the project root and populates `ui/data/` with production files. This UI expects `data/manifest.json` with the exact fields in `CONTRACT.md` and relative URLs for addresses, rules, provenance, jurisdictions, report (optional), and generated snapshots.

Do not put fixture data in `ui/data/`. This integrated publication includes genuine saved production engine results in `ui/data/`; fixture files remain separate and display a visible fixture banner.

## Fixture preview on Windows PowerShell

From the returned `ui` directory:

```powershell
py -3 -X utf8 -m http.server 8000
```

Then open:

```text
http://localhost:8000/?fixture=1
```

Useful fixture cases:

- `A-DEMO1`: applies + unknown + superseded + not-yet-effective + conflict.
- `A-DEMO2`: pending result and missing provenance.
- `A-DEMO3`: unresolved jurisdiction.
- `A-DEMO4`: empty lookup result (must not read as “no restrictions”).
- `A-DEMO5`: lookup points to a missing rule record.
- `A-DEMO6`: malformed lookup payload to exercise the error state.

Select the second fixture snapshot to exercise date switching. The fixture banner remains visible at all times.

## Behavior and safety boundaries

- Original postal fields and matched geography are displayed separately.
- Only dates present in `manifest.snapshots` are selectable. JavaScript does not synthesize historical/future law results.
- Six challenge categories are always shown. A missing category says no result was returned and explicitly warns against treating that as “no restrictions.”
- Source rule status and per-address applicability are displayed as separate badges.
- Missing fields are labeled unknown/unavailable rather than guessed.
- Supplied explanations, quotations, notes and source metadata are inserted with DOM `textContent`, never trusted as HTML.
- Evidence drawer displays exact rule quotation, supplied source URL, retrieval date, hashes, supporting spans and skeptic note when present.
- T1-T5 change cards render only supplied `changes.json` outputs.
- Audit metrics render only supplied `report.json`; absent metrics remain unavailable.
- `Not legal advice` is persistent in the header/footer.

## Files

- `index.html` - accessible page shell and evidence dialog.
- `styles.css` - responsive visual system; no external fonts/CDNs.
- `app.js` - contract loader and rendering logic.
- `fixtures/` - clearly synthetic test-only data.

## Verification

From the returned project root, run:

```text
python ui/tests/verify_ui.py
```

The verification script uses only Python's standard library plus `node --check` when Node is available. It validates the synthetic fixture contract, snapshot/date consistency, T1-T5 fixture shape, rendering-safety guardrails, relative-resource policy and static HTTP serving. It does **not** establish legal accuracy or production correctness.

This browser-verified revision also guards against stale overlapping snapshot requests, adds a standard keyboard tab pattern (arrow keys/Home/End), and makes the skip-link target programmatically focusable.

V2 also loads lookup and change snapshot files independently. A failure in one is displayed as unavailable without suppressing a valid sibling output. A lookup file whose `as_of` does not match the selected manifest snapshot is rejected rather than shown under the wrong date.

## Resident entry revision

The default screen presents six ordinary housing questions, brief conservative category statuses, and collapsed raw rule lists. It distinguishes incomplete legal review from missing property information. No category-level governing law is selected by this UI. A category may contain both applicable and unknown rules.

An optional independently reviewed `data/resident-claims.json` adds everyday rule explanations. It is fingerprint-bound to unchanged engine rules and supported exact spans. Invalid/stale/unapproved claims are never displayed; the original extracted requirement remains available. See `RESIDENT_CLAIMS_CONTRACT.md`. This revision ships an empty artifact until genuine model reviews are produced. With approved claims, a compact preview shows one supported rule, visibly labeled as one rule rather than a complete category conclusion.

Additional checks (Node):
```
node tests/test_resident_logic.js
node tests/test_resident_claims.js
```
These exercise real saved output across all 500 addresses/four snapshots and adversarial evidence/uncertainty/status cases. They do not establish semantic legal accuracy or human readability.
