# Scoped evidence drawer density patch

Baseline inspected: work/release-kit/Housing_Release_v1/publication/ui. Original baseline/data untouched. Patch files app.js and styles.css; index.html copied unchanged and does not need replacement.

Changes:
- Reviewed prose remains exact. Explanations over the existing 60-word display threshold expand under Read the full reviewed explanation; no legal truncation/rewrite. The renderer has no 900-character text limit and accepts genuine newly approved longer prose once the external artifact gate/producer permits it.
- Complete claim supporting passages, original quote, supporting/companion source spans, coverage/exemptions and model review notes use native details/summary disclosures. They remain complete textContent nodes; nothing is discarded. Detailed hashes/provenance are expandable.
- Personal eligibility qualifier, legal citation, effective date, query as-of, source retrieval date and safe source link stay visible. Source hash mismatch and missing provenance warnings remain visible rather than buried.
- Snapshot call/cost metrics explicitly say this snapshot run; a visible note excludes earlier project runs. No cumulative project cost is invented.

Checks actually performed:
- node --check app.js PASS.
- node test_disclosures.js PASS: lightweight DOM harness executes actual patched openEvidence function; complete long prose/quotes/exceptions remain under disclosures; citation/unknown qualifier/source URL/integrity visible; malicious companion URL omitted; modal opens; data texts unmodified; no innerHTML; metric labels scope checked.

Limits:
- DOM harness is not a browser accessibility/visual test. Parent's prior live desktop verification covers the baseline, not this new patch.
- Native details are keyboard-operable, and existing native dialog/close controls remain; no event/focus code changed. Nested disclosures require real browser check for layout/focus/scroll after integration.
- Long prose appears under an expandable full explanation, so personal status remains visible but every material clause still requires reading the full text. Do not imply display condensation is legal condensation.
- Repetition across different disclosure sections is preserved intentionally for audit completeness; it no longer floods the initial drawer view.

Copy only work/resident-v2-patch/app.js and styles.css into final UI. Optional test_disclosures.js/PATCH_NOTES.md as audit artifacts. Do not overwrite engine data or approved claim artifacts. Rerun full integration verifier and actual browser smoke after merge.
