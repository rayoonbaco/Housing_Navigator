# Renter usability fixes

2026-10-04. Prepared for deployment; updated fixes have not yet been tested on the live deployment.

Two website assets changed: app.js and resident_logic.js. No legal JSON, saved lookup, claim, citation, or provenance data changed.

- Unmatched or not-yet-selected search hides previous-home answers and change impacts. Explicit address selection restores them. Clearing search restores the selected address.
- Screening question now asks about unfair treatment; its first disclosure surfaces returned discrimination/family protections, with original eligibility limits and evidence buttons. Six categories remain.
- Uncertain topics provide next steps tied to missing facts, geography, dates, or unfinished legal review. No new legal rights or help contacts invented.
- Original change notes are retained and labelled as baseline narrative; selected-date results remain in My home.
- Earlier reviewed-claim version loading fix retained.

Actual offline checks passed: targeted DOM regressions for search, selection, fairness discovery, next steps, and baseline labelling; 16 adversarial summary assertions and 12,000 actual-data topic summaries; 24 evidence/security assertions; all 17 real approved claim evidence/fingerprint checks; citation/disclosure DOM checks preserving full quotes and exceptions; lossless lookup codec across 162,256 records; JavaScript syntax.

Independent simulated renter review: INDEPENDENT_RENTER_REVIEW.md. This is not a real-person study or legal certification. Long legal explanations and comprehensive rights coverage remain limitations.
