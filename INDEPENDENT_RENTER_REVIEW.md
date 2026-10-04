# Independent simulated renter walkthrough — live site

Reviewed live https://housing-navigator.onrender.com/ using the connected Chrome browser on 2026-10-04 UTC. This is an AI-simulated persona usability review, not a test with a real renter and not legal validation. Persona: tired renter with no legal or technical literacy. No private tenant facts, voucher status, disability, tenancy events or building ownership facts were invented. Actions only selected public sample addresses and opened disclosures. No application changes or deployment.

## Tasks actually attempted and observed

1. Opened the live site and inspected default A0001 Los Angeles after data loaded. Six ordinary question headings, explicit saved date 2026-10-01, saved-results label, and personal uncertainty were visible. Main view contained 105 returned rules, including 16 rent and 41 eviction records behind disclosures.
2. Selected public sample A0140, 459 BEACON ST, Boston, using the actual address list. The screening card prominently displayed a reviewed explanation that Boston rental-assistance discrimination is illegal and identified refusal to accept Section 8 as an example. This was a useful practical answer for a simulated person seeking fair-housing information; it was clearly labelled one rule rather than a complete verdict.
3. Opened that answer's Check my homework drawer. Observed visible citation, source link, retrieval date 10/01/2026, query date 2026-10-01, In force source status and Not verified effective date. Eligibility qualification and source-integrity mismatch warning remained visible. Expanded Read the exact passages behind this explanation. The complete supplied Boston passage contained protected classes and commission contact information, including Fair Housing and Equity 617-635-2500, but these practical contact/help details were hidden inside a long exact-source passage rather than offered as a clear next action.
4. Selected public sample A0002, 1031-1035 CLINTON ST, Hoboken. Main screening answer selected the credit-report denial disclosure rule. No obvious fair-housing/discrimination heading appeared among the six topic titles. A resident seeking voucher/race/family/disability protections must infer that "What can a landlord check about me?" contains them or expand 12 records. Main rent answer explained statewide versus local authority rather than telling the person the actual governing cap.
5. Expanded Hoboken's reviewed software/rent explanation. It preserved primary-residence/care-detention limits, precise nonpublic-information conditions, enforcement actors, penalties and unverified effective date. However, the result reads as a long ordinance explanation (roughly 200 words), not two neighbors talking. The closed card merely says important conditions exist and eligibility is unconfirmed. A simulated tired renter still cannot tell what fact to check next or whom to ask.

## Ranked improvements supported by this walkthrough

### 1. Make fair housing discoverable by name

Rename or supplement the screening topic with explicit "Fair housing and screening" / "Can they reject me or discriminate against me?" navigation. Do not automatically claim every protected class applies to every home. Boston proves a practical reviewed answer can already be shown; Hoboken shows a generic credit-report claim may hide the discrimination purpose. Claim selection should respond to the person's chosen concern rather than first available record.

### 2. Replace repeated process language with a precise next question where justified

"Some legal checks did not pass review; a building detail alone will not resolve that" is honest, but it tells the renter about our work rather than what they can do. Retain the reason distinction and add a plain next action only when source/engine logic supports it: a specific needed fact, a cited housing-agency contact, or a clearly labelled unresolved-law review. Never ask household questions to repair an unreviewed legal interpretation. Boston's source already offers a relevant agency contact; a linked factual contact card would be useful without giving legal advice.

### 3. A short answer must still say something practical

The main software card is small because its whole reviewed meaning is collapsed, but it contains no useful legal meaning until expanded. An independently reviewed narrow headline could summarize the prohibition while conditions stay visible next to it. The long exact meaning and receipts should remain intact beneath it. Do not hand-shorten the existing 200-word Hoboken claim: new short claim requires its own recorded evidence review.

### 4. Explain saved dates and unknown effective dates in resident terms

The saved 2026-10-01 date is visible and the site does not explicitly claim live monitoring. But a tired renter landing on October 4 could assume the selected date means today. Use an unmistakable "Last checked for [date]" explanation and distinguish query date, source retrieval date, adoption date and unverified effective date. Showing In force next to Effective date Not verified may be technically valid for a snapshot but needs a short explanation of that limitation. I did not personally run future-date selection in this independent pass; no claims about its correctness follow from these observations.

### 5. Keep evidence readable without pretending integrity is resolved

The updated drawer succeeds: plain meaning, citation/date/status, source link and integrity warning are visible; exact complete passages are expandable. The Boston example is good evidence of traceability, not certification. Long citations containing raw URLs and repeated process disclaimers still demand reading. Source title/section can be visible with URL in the hyperlink, leaving hash details expandable as implemented.

## What worked

- Address selection changed the visible city/date/results correctly for the two samples tested.
- Boston's reviewed voucher/discrimination example was concrete, ordinary and source-linked.
- Current versus proposal distinctions were explicit: Boston's algorithm topic said Proposed, not law; main application-fee absence said no verified answer rather than no protection.
- Missing property facts and failed model/legal review were not turned into a confident yes.
- Drawer preserved actual exact text and dates with visible integrity limits.
- The longer Hoboken reviewed explanation restored critical definitions/exceptions and plainly said a separate effective date was not supplied.

## Boundaries

No real-human comprehension score or accessibility certification. No external source page opened, no official source-currentness verification, no personalized housing eligibility determined, no source/code mutations. Live DOM/accessibility content is the basis for these findings. Parent's separate search-mismatch/future-T3 observations should be tracked under its own walkthrough, not attributed to this one. A Playwright role locator did not target a summary disclosure, but retargeting the observed native summary succeeded; this automation issue is not evidence that a human cannot click it.
