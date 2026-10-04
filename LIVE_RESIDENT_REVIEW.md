# Actual reviewed resident prose integration

## Inputs and preservation

Isolated copy `work/live-resident-review`, based on current finish kit UI. Existing refresh_viewer.py refreshed from saved engine run `20261004T040310-8b18182d`. Copied actual prose artifact from `20261004T040331-52ec5399`. No production originals changed, no API calls.

19 of 19 actual approved claims pass JavaScript full-rule SHA256 fingerprint and exact evidence-span mapping. Each has distinct extraction/review response message IDs. Those are recorded model reviews, not legal certification.

## Main-screen density fix

A reviewed explanation longer than 60 words moves intact into **Read the full reviewed explanation**. The main card explains that important conditions must be read; it does not show an abbreviated legal sentence. Exact sources remain one click away. This especially prevents the 94-word Hoboken algorithm/penalty claim from crowding the main screen. No sentence, condition, exception or numeric threshold was manually removed from approved prose. Eligibility status/qualification remains outside the dropdown, visible on the card.

Long approved explanation word counts: Hoboken algorithm 94; JC subscriber prohibition 69; JC provider noncompetition 70; California coercive pricing-algorithm prohibition 69; San Francisco algorithm rule 62; Hoboken >10% disclosure rule 71. These six explanations are expanded rather than truncated. Generic main copy is an interface explanation, not a new housing-law assertion.

## Coverage qualifiers requiring care

The actual T2 explanations are rule-meaning summaries, not complete eligibility summaries. The lookup reasoning separately records unknown primary-residence and care/detention facts for Hoboken and JC, and same-owner/licensed-agent exclusions for JC. Approved prose does not enumerate all those definition-based limits. Therefore **never move the plain prose into a current-personal-protection headline** or remove the visible unknown qualification. All raw coverage reasoning remains under Does this cover my situation? Future improvement should expose specific verified missing facts directly, through a structured uncertainty contract, rather than unreviewed hand-authored law paraphrases.

The NJ statewide rent claim says state law does not set rents; it must not become "No rent cap." It explicitly points to municipal rules and exceptions, and state/city interaction warnings remain. "A rule that applies" labels the selected claim, not a whole category's governing outcome. Source snapshots are not live monitoring.

## Actual reviewed-prose distribution

19 claims: algorithmic rent 5; screening restrictions 4; deposits 3; application/screening fees 3; rent increase 2; eviction 2. No single address has approved prose for every one of the six topics. Avoid claiming six complete concise legal answers were independently reviewed for each of 500 homes.

Recommended matched demo addresses:

- **A0320, 408 MADISON ST, Hoboken:** reviewed prose in five topics; four topics have reviewed Applies examples, algorithmic rent remains Unknown. Good for showing honest uncertainty plus local rent disclosure, which is not a rent cap.
- **A0495, 230 VAN HORNE ST., Jersey City:** five topics, four with reviewed Applies examples; both local algorithm claims remain Unknown. Good for exact-source/exception checks.
- **A0430, 1950 ADDISON ST, Berkeley:** six approved individual claims across four topics (fees, deposit, screening, algorithms), all of those returned Applies. Good plain-language California deposit/fee examples and visible state/city review warning.
- **A0140, 459 BEACON ST, Boston:** four reviewed claims across three topics (eviction, screening, deposit). Good for pending MA bill contrast and failed-cap empty change case.

Do not choose unresolved-geography addresses simply because they show more reviewed municipal records: Unknown-city candidates include multiple cities' rules to preserve uncertainty and are a poor primary resident demo.

## Tests and limits

PASS: 43 existing static/fixture/HTTP checks; 24 claim-gate/security/status/long-density assertions; 16 topic/uncertainty/layer assertions; 12,000 actual-data topic summaries across 500 addresses x four snapshots x six topics; 19 genuine claim artifact gates. The display remains additive and does not mutate any lookup result.

Actual browser launch attempted through installed Playwright. Chromium executable is absent; no actual browser rendering, screenshot or keyboard success claimed for this revision. No human comprehension experiment performed. Before final video, visually check real data for A0320/A0430, open one homework receipt, expand a long explanation, switch date, and verify mobile/keyboard behavior. Existing prior fixture browser evidence cannot certify this new presentation.

## Integration

Copy updated `app.js`, `resident_logic.js`, and `tests/test_resident_claims.js`; optionally add `tests/test_live_claim_artifact.js` and this report. Parent should refresh/copy actual approved artifact and engine data using its final source-of-truth snapshot; do not overwrite current source data with stale worker copies. Styles already support details and paragraphs; add spacing for `.full-reviewed-explanation .reviewed-answer` if desired. No further paid call required for these UI changes.
