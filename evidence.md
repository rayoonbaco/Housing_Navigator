# Actual finish-v4 evidence audit

Scope: inspected the uploaded `latest-finish-v4` saved artifacts, without new paid calls, source acquisition or parent-file changes. This is a source-grounded engineering review, not legal advice/counsel certification.

## T2 target review outcome is valid conservative progress

Target run `20261004T040237-83de816c` contains 289 coverage predicates. Independently compared every one of the original 286 predicates against the original v2.3 return: **all 286 are exactly preserved**. The only additions are Hoboken `HN-SUP-P005-002` and Jersey City `HN-SUP-V4S002-001/002`.

All three new predicates have explicit unknown nodes for primary-residence status/intent and excluded facility types. Both Jersey City predicates additionally preserve unknowns for same-owner multi-property actions and licensed-agent status. All effective dates remain null. Both compile and review can access full authorized original definition context, and the JC service-provider review now specifically cites `V4S001:C1/C2` rather than treating a rule-record summary as definition evidence.

The target result totals are **0 applies, 152 unknown**: Hoboken 44 and each JC record 54. This is consistent with 39 resolved Hoboken plus 5 unresolved NJ legal-city addresses, and 49 resolved JC plus the same 5 unresolved NJ city addresses per record. Those five have unknown local candidates, not confirmed city membership. Existing actor/conduct triggers remain conditional; actual algorithmic use was not inferred.

This resolves a compiler evidence/context defect. It does not resolve missing factual coverage. The 289 count is a model-reviewed predicate count, not 289 confirmed applicable protections. T2 still must be presented as 88 potential local notifications and zero confirmed property eligibility.

## Resident prose audit

Artifact: `20261004T040331-52ec5399/resident-claims.json`, 19 unique claim IDs. Every attached evidence string matches an existing supporting provenance span exactly. This establishes exact attachment integrity; it does **not** establish semantic completeness. Model approval did not catch the omissions below.

### Withhold the two JC everyday explanations

- **HN-SUP-V4S002-001:** The text defines a Service Provider and expressly gives the licensed-agent exclusion, but omits the same-owner multi-property exception present in its own attached `support:2` text. It also omits the primary-residence/care/detention dwelling definition. Giving one exclusion while hiding another makes the apparent scope broader than the actual linked definition. Generic “we need more facts” eligibility copy does not identify this missing exception.
- **HN-SUP-V4S002-002:** The text asserts the coordination function means collecting nonpublic data, analyzing it and recommending rents, but its attached evidence does not contain the original coordinating definition. Its `support:1` says service provider performs a cross-referenced coordination function, and its prose expands that reference without carrying the definition. This was the same source-context weakness the targeted compiler repair addressed. The same-owner exception and primary-residence/facility scope are also omitted.

**Disposition:** Do not render these two as approved everyday explanations until the producer can access full authorized `V4S001` definition context and a semantic review checks all relied-on definitions/exemptions. Preserve original claims and audit receipts; add a separate withholding ledger. Do not silently rewrite manually and retain the old model approval. Show a neutral explanation-unavailable status with exact law/coverage evidence instead. If regeneration is deferred, their availability gap is explicit and their underlying unknown coverage remains.

### Hoboken ban needs its dwelling scope visible

**HN-SUP-P005-002:** The prose says “residential dwelling units” without explaining this means primary residences excluding medical/long-term-care and detention facilities. The attached source states it, and the newly reviewed predicate treats those details as decisive unknowns. Existing generic eligibility copy merely says more facts are needed; the actual reasons are in a collapsed panel.

**Disposition:** Require an immediately visible scope qualifier sourced from the coverage record, or withhold this prose alongside the two JC records until rewritten/reviewed. Do not imply all apartments necessarily meet the definition. Its enforcement and penalty statements do match the supplied excerpt; this issue is omitted coverage scope, not invented penalties.

### Additional targeted improvements

- **HN-SUP-P001-002:** “It requires coercion” is faithful to subsection (b) alone but could sound like all AB325 liability requires coercion. The same evidence also contains subsection (a), concerning contract/combination/conspiracy. Keep the label explicitly about this coercion provision; never summarize the entire AB325 regime with this one sentence.
- **HN-R2-D067-006-004:** The phrase “The guide states no specific dollar cap” is an absence claim about the entire guide, while attached evidence is one excerpt. Prefer an explicit selected-excerpt boundary if retained. Neither that excerpt nor this review establishes absence of all state/local caps. No claim that application fees are unlimited is justified.
- **HN-SUP-P005-001:** The ordinance requires the disclosure of the right to sue when the proposed increase is believed unconscionable or otherwise unlawful. The everyday text truncates that to “right to sue at their own expense,” and omits first-page-renewal/form placement. These details matter if the text is used as a complete compliance checklist. A short resident explanation can be narrower, but a four-item checklist should retain the trigger and required delivery format.

## Claim-by-claim disposition

“No additional defect observed” means compared the displayed prose to its supplied evidence in this pass; it is not a complete corpus/exception/date legal validation.

| Rule ID | Disposition |
|---|---|
| HN-SUP-P005-002 | Conditional hold: show exact dwelling-scope limitation visibly or withhold prose |
| HN-SUP-V4S002-001 | Withhold: missing same-owner and dwelling scope despite definition summary |
| HN-SUP-V4S002-002 | Withhold: expanded coordination definition not attached; omitted exceptions |
| HN-R2-D025-003-008 | No additional defect observed; “nonrefundable” lease-label prohibition is not a promise of full deposit return |
| HN-D026-001-002 | No additional defect observed in the supplied current excerpt |
| HN-D027-001-005 | No additional defect observed |
| HN-SUP-P001-002 | Keep subsection-specific scope; avoid coercion as whole-AB325 condition |
| HN-R2-D067-007-001 | Keep general rent-control/local-ordinance scope; no universal claim that state law never regulates rent-related conduct |
| HN-R2-D067-006-004 | Qualify excerpt absence claim; no claim of unlimited application fees |
| HN-R2-D067-006-003 | No additional defect observed; this lists a notice obligation, not every adverse-action obligation |
| HN-R2-D067-011-006 | No additional defect observed |
| HN-R2-D052-003-006 | No additional defect observed; vacation/recreation <=100-day exception retained |
| HN-D058-001-003 | No additional defect observed; actor is court, condition residential nonpayment filing |
| HN-D049-002-006 | No additional defect observed |
| HN-D081-001-001 | No additional defect observed against official Rent Board excerpt; no extra software scope inferred |
| HN-D012-001-001 | No additional defect observed against supplied Boston explanatory source |
| HN-D007-001-007 | No additional defect observed; date attributed to Rent Board source |
| HN-D005-001-006 | No additional defect observed |
| HN-SUP-P005-001 | Avoid presenting truncated disclosure list as complete compliance checklist |

## Required integration repair

Every explanation producer and reviewer needs the same authorized definition context as coverage compilation. Claim evidence IDs should include any full linked C passage needed to support definitions and exceptions, checked against pinned text and per-rule links. A generic caveat cannot cure an overbroad claim. Add a semantic review checklist for omitted exceptions, actor, defined terms, action and date, while retaining deterministic quote/fingerprint guards.

Retain the original 19 generated claims as historical output. Record withheld claims and specific reasons in a new artifact, and ensure the UI's approvedClaim selection observes that withholding list. Do not retain an “approved” display merely because the old model verdict said supported. No legal rule or fact needs to be changed to do this.
