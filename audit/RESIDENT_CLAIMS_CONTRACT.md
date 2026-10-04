# Reviewed everyday explanations: optional additive contract

The engine contracts are unchanged. `data/resident-claims.json` is optional, with shape:

```json
{"version":"resident-claims-1","claims":[{
 "team_rule_id":"existing rule ID",
 "rule_fingerprint":"sha256 of canonical full rule",
 "claim_id":"unique stable claim ID",
 "scope":"rule_meaning",
 "text":"independently reviewed plain explanation, preserving material conditions",
 "evidence":[{"span_id":"rule-quote","text":"exact supporting source substring of at least 20 characters"}],
 "extractor":{"approved":true,"model":"actual model","request_id":"actual extraction response/message ID"},
 "reviewer":{"approved":true,"model":"actual model","request_id":"different actual review response/message ID"}
}]}
```

Fingerprint = SHA256 of UTF-8 full rule canonical JSON. Recursively sort object keys; preserve list order; no separators whitespace; preserve Unicode. Python equivalent `hashlib.sha256(json.dumps(rule,sort_keys=True,separators=(',', ':'),ensure_ascii=False).encode('utf-8')).hexdigest()` for the supplied finite JSON rule fields. All rule fields are bound, including exemptions/coverage/status/date. Browser computes fingerprints using WebCrypto on HTTPS or localhost.

Each evidence `span_id` is `rule-quote` (exact substring of quoted_span), `support:0`, `support:1`, etc. for this rule’s supporting_spans index; `companion:0`, etc. for authorized_companion_spans index; or an existing saved span id for this exact rule. Include source_doc_id/source_url in producer evidence for companion provenance. Every evidence text must occur exactly in its saved span. A stale fingerprint, unsupported span, missing approvals, shared request ID or malformed artifact blocks prose and falls back to unaltered requirement text. The validator is a structural/evidence-mapping gate: it cannot itself prove semantic entailment, reviewer honesty or completeness. Those require real independent paid/recorded model review and audit artifacts. Never fabricate approved flags or request IDs.

Text describes what a rule means, not a personalized entitlement. Personal applicability always remains the saved engine result, displayed with visible date/status and qualification. The raw eligibility explanation remains expandable. Current/future/pending status never comes from the prose. A category summary may say some rules apply while others remain unresolved; it never selects a governing law without an engine decision.

Unknown cause labels are conservative presentation classifications from existing explanation text. They do not create additional eligibility facts. A structured reason taxonomy in the engine would be preferable; raw reasoning stays visible.

No model is called by the browser. Missing artifact leaves the interface functional. All prose/evidence uses textContent; source URLs retain HTTP(S)-only safeUrl filtering. Main stage artifact contains no approved claims until genuine reviews are supplied.
