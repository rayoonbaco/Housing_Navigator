# Final-pass challenge and precedence audit

Offline audit of latest `latest-finish-v4` return. No new paid calls or canonical mutations were made by this audit. This supplements, rather than replaces, `review/red-team/challenge.md`.

## Current inspected baseline

`20261004T040310-8b18182d/report.json`: 310 rules, 289 model-reviewed coverage predicates, 21 unresolved, 500 addresses. This recomputation reports zero API calls and preserves the existing change mapping. Jurisdiction matching correction now admits qualified `City, ST` labels; this is a substantive engine correction, not mere copy editing. Prior snapshots produced before that fix must not be described as having established all local applicability.

T1-T5 still report pass with the same material qualifications: T2 has88potential,0confirmed,93unknown; T1/T3 also retain unknown records; T4 hypothetical pending; T5 failed/no operative ballot cap. Forty prior Windows engine tests do not automatically establish correctness of the newly corrected engine; coordinator's new regression checks must be included separately.

`20261004T040331-52ec5399/report.json`:19selected plain-language claims,19model-approved,0rejected,8genuine calls, estimated$0.30605. This is model review of wording against evidence, not measured legal correctness. It does not mean every remaining record now has reviewed resident prose. The unapproved records need honest original-text or unresolved fallback, not invented short answers.

`20261004T040314-9493b073/report.json` and `proposed-edges.json`: one proposal call,191,302input tokens, estimated$0.396194, zero edges. Therefore no independent-review call occurred and no priority relationship was approved. Label “no executable edges proposed,” not “independent precedence review passed.”

## Audit of model's no-edge explanation

The rejection of automatic state/city precedence is substantively conservative and appropriate. Some supporting rationale is factually overbroad:

- Model says supplied sources give no adoption dates for San Diego. **False as written.** `corpus/text/D073.txt` lines15-16 identifies the2023retitling/amendment ordinance O-21647 and effective6-24-2023; lines29-31 repeat the amendment/effective date; lines471-472 date the just-cause section itself. These are clear supplied legislative dates. Fulltext also references original2004Tenants'RightToKnow regulations, which must not be confused with the operative2023justcause amendment.
- The actual missing question is whether the San Diego local ordinance satisfies every California1946.2(i)(1)(B)criterion, including **binding local finding**. D073purpose/intent says consistency, added relocation/protections and rights in addition to existing law (lines18-27), but this audit did not find an explicit binding finding in that captured text. Do not equate a broad purpose clause with the statutory binding-finding criterion.
- Model says no source establishes then-current priority on2026-10-01. This is too categorical as a global statement. D023contains an express legal precedence provision; existing dated snapshots support then-current text. What remains unestablished is the fully supported **specific state-rule/local-rule/property/date relationship** that can execute under this initial edge contract.
- SF's annual cap period IS documented: D080lines8-17 states1.6% forMarch1,2026-February28,2027 and1.4% for the previous year. This dates the annual cap, not the original adoption/amendment date of the justcause ordinance and not every SF provision.

Keep the actual model output intact as evidence. Annotate these corrections in the audit rather than altering its limitations silently. The zero-edge result remains safe, but the explanatory opinion is not authoritative legal evidence.

## Highest-stakes unresolved preemption/precedence problem

The original challenge specifically requests state/local cap precedence and supplies `superseded` output. Current source-gated edge contract supports only `both_rules_apply`. That is a deliberately safe execution boundary, but it is too narrow to solve many real state carveouts:

- D0231946.2(i) explicitly says qualifying local law applies instead and a property shall not be subject to both. Thus merely waiting for independent current state+local lookups both to sayapplies may conflict with statutory semantics.
- D0241947.12(d)(3) excludes housing subject to valid local control restricting increases to less than the state cap. This requires a reviewed comparative relationship plus confirmed local eligibility; generic same-category overlap and headline numbers cannot establish it.
- Missing local property coverage must not suppress potential state coverage. Unknown owner/CO/tenancy/exemption facts cannot be bypassed to make a neat summary.

### Minimal targeted next solution, without manual legal rules

1. **Create an automated relation proposal on a bounded source pair**, rather than resending111records/191k tokens. Start with one substantive state provision and one local rent-cap provision plus their actual exemption/commencement source chunks. Preserve exact evidence IDs, source hashes and model receipt. Do not compare notice/admin/penalty records as competing caps.
2. **Separate intrinsic eligibility from precedence eligibility.** A reviewed relation needs the base property/event predicates for each law and a separately reviewed carveout/precedence predicate. Existing canonical records stay immutable; a supplemental, source-backed relation artifact can specify which existing record yields and under what precise facts. Do not infer a legal exclusion by testing only the final already-excluded output.
3. **Represent the legal priority test as a bounded reviewed condition.** For1947.12(d)(3), needed inputs include valid local ordinance/current cap period, covered unit, statutory state formula for the correct CPI region/date, and permitted comparison method/exception handling. The review must explicitly approve these inputs and relation. Numeric min of arbitrary displayed caps is prohibited. For1946.2(i), needed inputs include operative adoption/amendment branch and, for post2019amendments, consistency/additional protections/binding finding with exact text. Date of original code alone is insufficient.
4. **Use existing public facts only; leave additional facts unknown.** Yearbuilt cannot establishCOdate or tenancy/exemption; generic residential scope cannot prove local coverage. A failed relation condition is not automatically “state wins.” It can mean local lawcomplements state, the relationship is unresolved, or a provision is inapplicable; evidence determines which.
5. **Review the proposed relation independently** against both full provisions and all selected conditions. Rejected/uncertain condition never executes. A narrow result can be “priority unresolved due toX” and that is useful.
6. **Test four meaningful scenarios**: confirmed local coverage and supported priority; local exemption with state potentiallyapplicable; unknown local coverage; date outside supported cap period. Add a complementary-notice case to ensure no blanket supersession. No real property result changes until these pass and the actual accepted artifact is inspected.

Under current deadline, retain “State and city rules both appear here; which governs still needs review” if the complete relation cannot be established. That is an explicit gap, not challenge completion. Do not use another large proposal call to conceal this contract limitation.

## Current challenge requirement matrix

| Requirement / authority | Actual current evidence | Remaining gate |
|---|---|---|
| Automated extraction, PDFp2/README§3 |310canonical records from logged automatic pipeline; originals preserved |87source disposition completeness; unavailable sources and all54organizer hash mismatches remain explicit |
| Six categories/ten corpus cities, PDFp3 |Allsix categories; SantaAna extraction-only records exist |Do not drop SantaAna because zero sample addresses;9sample cities versus10corpus cities explained |
| Coverage/exemptions, PDFp2/README§4 |289reviewed predicates,21unresolved; missingfactsunknown |Model review is notlegal certification;21unresolved staydistinct from approved-but-missingfactunknown |
| Legal address stack, PDFp2/README§4 |500retained,480matchedcity/county,20unknown; qualified labelbugcorrected |New local-city regression/recomputed snapshot checks; county geography notcounty-lawcoverage |
| State/local precedence, PDFp1/3/README§5 |Evidence-gated module+tests;0real edges approved |Stillnotclosed; bounded sourcepairrelation needed or visible unresolvedpriority |
| Plain-language explanations/citations, PDFp2/schema |19approved conciseclaim rewrites;existingcitation/evidencedrawers |Final UI every materialclaim has receipt; conditions/date/actorpreserved; fallback for otherrecords notunsupportedsummary |
| T1/T3datechanges, PDFp4/devtests |Savedbefore/aftersnapshots;250CA/140NJaffectedsets |Retain unknownrules and evidence-backed mappedrecordmembership;as-ofscopeclear |
| T2localbans, PDFp4/devtests |88potentialcity-boundnotifications;0confirmedlocalcoverage |Boundarynotificationpassisnotfullindividualeligibilitypass;primaryresidence/exclusions missing |
| T4pending, PDFp4/devtests |110MAhypotheticalaffected,pending |No currentlaw/protectionclaim |
| T5failed, PDFp4/devtests |Failedmeasureemptyaffectedset |DoesnotproveabsenceofallMAhousingprotections |
| Publicsources/notlegaladvice/audit, PDFp5 |Loggedcalls,snapshotpins,exactevidenceandknownlimits |Actual release everyinterface saysnotlegaladvice;sourcecapture/raw/thirdparty distinctions preserved |
| ThreeJSONs+methodnote+livedemo, PDFp6 |JSONsexist;localpreview |Updatefinalmethodnoteandallpresentationclaims to correctedrelease;deployedURLtest |
| HackOSdelivery, observedscreens |3<=60secvideos,photo,validGitHublink,HackOS+GoogleForm requirementsknown |Actualrecordingswatch/duration,repositoryaccess,appaccess,twoforms+receipts before9AMEastern |
| Spanish/confidence/newjurisdiction, PDFp2stretch |No completed validatedSpanish/newjurisdiction demonstrated |Stretchonly;confidencecannot masqueradeaslegalaccuracyprobability |

## Recommended final framing

“We turn public housing-law sources into cited address results, show exactly what is supported, and explain what is still missing.” This can be demonstrated now. “Every rule is resolved,” “all legal tests passed,” and “we know the single governing cap for every property” cannot.
