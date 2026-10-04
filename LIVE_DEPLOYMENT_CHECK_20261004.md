# Live deployment verification — October 4, 2026

Public site: https://housing-navigator.onrender.com/
Repository: rayoonbaco/Housing_Navigator
Initial deployed commit: 4e2343c810d0782c1827423b1a57319f2e3f351c0

## Actual browser checks
Performed against the public Render deployment in a desktop Chrome browser, not a local fixture.

- Initial project data loaded and offered 500 supplied addresses.
- Desktop screenshot inspected: readable heading, address selection, saved-date selector and three main views.
- A0001 Los Angeles displayed 105 evaluated records and six resident questions.
- A0430 Berkeley address search narrowed to one match; selection showed Alameda County with missing year/unit facts explicit and 107 records.
- Each of the six Berkeley topic disclosures was opened and closed; all six expanded successfully.
- Check this answer's homework opened the California nonrefundable-deposit explanation, exact supporting passage, statute citation, source link, retrieval date, source hash and unresolved manifest hash warning.
- Escape closed the evidence drawer.
- The date selector loaded and displayed 2025-12-31, 2026-01-02, 2026-10-01 and 2027-07-02. The selected date and loaded-answer date were checked after each asynchronous load completed.
- What changed displayed T1–T5 and kept T2 potential notifications and T4 hypothetical pending status explicit.
- How we checked displayed 310 rule/provenance records, 289 reviewed scopes, 480 matched legal geographies, 20 unresolved geographies, source gaps and the evaluated JSON archive link.
- ArrowLeft from the audit tab selected What changed through keyboard navigation.
- A0168's supplied Hoboken postal label did not become confirmed legal-city membership; the screen explicitly said the legal city was not confirmed.
- A deliberately unmatched search returned no address options; the previously selected home's result was retained until another match was selected.
- Restored A0430 with the current 2026-10-01 snapshot after testing.

## Test-harness distinctions
An initial Playwright role=button selector did not match native summary disclosures. Native accessibility/text locators were used and the actual controls opened correctly. This was a locator mismatch, not evidence of a broken product button. The browser log sample contained extension metadata errors; this record does not treat those as application failures or claim a clean complete console log.

## Limits and next checks
Desktop interaction and one initial desktop layout are verified. Mobile viewport, a complete keyboard/focus audit, downloaded archive bytes from the public site, legal accuracy/completeness, translations, continual monitoring and final submission receipts are not established by these checks. The six withheld prose claims and specific state/local priority review await their separate evidence return. T2 still has zero confirmed eligible addresses. No underlying rule, eligibility result, or legal finding was changed during these browser checks.
