# Housing Navigator

**The law that protects a home should be readable by the people living in it.**

Housing Navigator is Ray Gomez's solo entry for the RealPage Rental Housing Law Navigator challenge. It combines automated legal extraction, geographic resolution, conditional applicability and date-aware change tracking with six resident questions and **Check my homework** evidence drawers.

This is a saved-result prototype, not legal advice, verified nationwide coverage or continuous monitoring.

## What is demonstrated

- 310 extracted rules; 289 model-reviewed coverage predicates and 21 unresolved scopes.
- 500 supplied addresses at four evaluated dates; postal city stays separate from matched legal geography.
- Current, future, pending and unknown answers stay distinct; failed measures do not become current protections.
- Seventeen everyday explanations released after source audit. Two final candidates remain withheld after coordinator source audit. Two independently supported repairs retain their full wording in expandable details. Positive model review alone is not publication authority.
- Exact supporting passages, source links, dates and eligibility reasoning remain inspectable.
- Lossless transport reduces each approximately 36 MB snapshot to approximately 1 MB. All 162,256 records across four dates reproduce the original evaluated JSON exactly.

The corrected evaluator admits 117 original city records that a qualified-label mismatch previously skipped. The fix, original failures and independent recomputation are documented rather than concealed.

## Evaluate and run locally

No API key is needed to view this release. From this directory:

```powershell
py -3 -X utf8 verify_release.py --root .
py -3 -X utf8 preview.py
```

The preview binds localhost on a free port and prints its exact URL. Windows users may also double-click `Start_Preview.bat`.

Read `DEPLOYMENT.md` for GitHub and Render. The Render publication directory is `ui`; it has no backend or browser API credentials.

## Evidence and limits

The original three challenge JSON exports, plus coverage/provenance/geography receipts, are preserved in [submission_json.zip](ui/data/submission_json.zip). UI transport compression changes serialization only; it does not shorten a legal explanation or change a status.

Five internal change checks pass with their specific qualifications. **T2 has 88 potential local notifications and zero confirmed eligible addresses.** Required primary-residence, facility and actor/ownership facts remain unavailable. **T4 describes hypothetical pending bills**, not current law. State/city precedence remains unresolved unless a specific relationship is separately source-reviewed and property conditions pass. Twenty legal cities are unresolved. County geography is not county-law completeness. Organizer source-byte hashes remain inconsistent with bundled text; separately pinned snapshots do not establish original-source integrity.

See [initial-release method PDF](METHOD_NOTE.pdf) and [current method text](METHOD_NOTE.md), [strategy](STRATEGY_AND_EVIDENCE.md), [source audit](audit/evidence.md) and [challenge audit](audit/challenge.md). Complete independent strategy critique, reconciliation and raw review receipts are in the audit archives. Exact citations and passing code tests do not establish legal completeness or accuracy.

## Business proposal

Residents get readable explanations; housing organizations may pay for reviewed evidence and change histories across address portfolios. Demand, pricing and revenue are unvalidated. The next commercial step is a focused user pilot, described in [BUSINESS_CASE.md](BUSINESS_CASE.md).

## Validation

The integrated local engine passed 72 offline tests; release/import checks passed 8. UI verification covers static/fixture checks, actual claim fingerprints and exact passages, adversarial uncertainty/security cases, 12,000 topic summaries and lossless snapshot round trips. HTTP serving was checked. The initial Render deployment passed actual desktop browser checks, documented in audit/LIVE_DEPLOYMENT_CHECK_20261004.md. The new drawer-density revision awaits deployed browser verification; mobile and final submission/video receipts are still pending.
