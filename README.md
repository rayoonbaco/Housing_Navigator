# Housing Navigator

**What protects my home? Start with a readable answer, then check its evidence.**

Ray Gomez's solo submission for Challenge 2: RealPage, Hack-Nation 7th Global AI Hackathon.

- [Open the working demo](https://housing-navigator.onrender.com/)
- [Current one-page method note](METHOD_NOTE_FINAL.pdf)
- [Canonical challenge JSON exports](ui/submission_json.zip)

Housing Navigator organizes rental housing rules around six everyday resident questions. **Check my homework** opens the supporting passage, citation, source URL, dates and remaining coverage uncertainty. The prototype uses saved, automated evaluation results for the supplied challenge addresses. It is not legal advice, continuous monitoring or a nationwide legal service.

## Try it

Choose a supplied address and an evaluation date. Open a deposit answer, inspect its evidence, then compare a question that needs more facts. Search only selects a home when you click the matching address; a missing match hides the previous home's answers. Fair-housing disclosures and **What should I check next?** help residents find relevant evidence and unresolved questions.

## Run the website locally

Download this repository using Code > Download ZIP, extract it, and open PowerShell in the extracted folder containing `ui`:

```powershell
py -3 -X utf8 -m http.server 8000 --bind 127.0.0.1 --directory .\ui
```

Open http://127.0.0.1:8000/ in your browser. Keep PowerShell open; Ctrl+C stops the preview. No API key, package installation or live model call is needed. If port 8000 is occupied, replace it with 8001 and use that port in the URL. Do not open index.html directly: the website loads JSON over HTTP.

The active website is the **ui/** directory, with its JSON files alongside index.html. Root-level duplicates and numbered historical uploads are retained for continuity; they are not the deployed website. Render serves `ui` as a static site and contains no browser API credentials.

## Pipeline and current evidence

Five stages connect sources to the resident view: **extract, resolve, apply, explain, track**. Automated extraction selects pinned passage IDs; code copies exact source text. Schema/evidence gates precede independent model review. Coverage predicates return true, false or unknown. Postal city stays separate from matched legal geography. Date gates separate current, future, pending and failed measures. Change cases use reviewed source-rule mappings.

The current saved release contains **310 rules, 289 model-reviewed coverage predicates, 21 unresolved scopes and 500 addresses at four dates**. Seventeen everyday explanations passed additional source audit; unapproved explanations retain labelled original summaries. A model approval alone is not publication authority. Evidence fingerprints bind prose to its unchanged rule and passages.

A city-label mismatch had skipped 117 original city records. The corrected evaluator and independent recomputation agree on the default 40,564 returned rule/address records. Lossless website transport reproduces all 162,256 records across four dates. It changes serialization, not legal meaning or status.

## Tests and limits

Recorded checks include 72 integrated offline engine tests, eight release/import checks, adversarial uncertainty and evidence gates, 12,000 topic summaries and transport round trips. Live desktop Chrome checks covered explicit address selection, unmatched search, fair-housing disclosures, next-step guidance, date switching and citations. See [the final live usability receipt](LIVE_USABILITY_FIX_CHECK_20261004.md). Final mobile layout was not retested. Simulated renter reviews are not studies with real residents, and passing code tests do not certify legal accuracy.

Five internal change-case checks pass within documented bounds. **T2 has 88 potential local notifications and zero confirmed eligible addresses** because relevant property and actor facts are absent. T4 describes hypothetical pending bills, not current protection. Baseline change narratives are labelled separately from selected-date results.

Twenty legal cities remain unresolved. Required owner, occupancy, certificate, tenancy and facility facts cannot be inferred. County geography is not county-law completeness. The supplied inventory has 87 sources and 54 usable text captures; denied/link-only sources remain gaps. Organizer byte hashes disagree with bundled texts; separately pinned snapshots do not establish original-source integrity. State/local precedence requires specific legal evidence and coverage review. English is demonstrated; validated Spanish and nationwide expansion are not.

## Code and reproducibility

The public repository includes the website, saved results, Python extraction/coverage code and review archives. The preserved original input corpus and complete paid-run logs are in the versioned local project and saved handoff packages; a fresh paid extraction requires those inputs and a private Claude API key. This repository alone is sufficient to run the saved-result demo, not to reproduce every historical paid run. Never put a key into a web file or commit.

[Strategy and evidence](STRATEGY_AND_EVIDENCE.md) documents the evidence-first design, three-valued applicability, internal red team, external Claude critique and integration choices. Review archives preserve positive reviews, withheld candidates and failed checks. [The current method text](METHOD_NOTE_FINAL.md) records the final scope; older method notes remain historical.

## Next product milestone

A focused, legally reviewed pilot with housing counselors and real resident comprehension testing. An organization subscription for reviewed evidence and change histories is a proposed business model; demand, pricing, revenue and measured resident impact are not validated.
