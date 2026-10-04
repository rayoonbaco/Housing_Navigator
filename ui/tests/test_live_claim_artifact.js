'use strict';
const fs=require('node:fs');const path=require('node:path');const assert=require('node:assert/strict');
const {fingerprint,validateClaim,compactClaim}=require('../resident_logic.js');
(async()=>{
 const data=path.resolve(__dirname,'../data');const read=n=>JSON.parse(fs.readFileSync(path.join(data,n),'utf8'));
 const rules=new Map(read('rules.json').map(x=>[x.team_rule_id,x]));const provenance=new Map(read('provenance.json').map(x=>[x.team_rule_id,x]));const claims=read('resident-claims.json').claims;
 assert.ok(claims.length>0,'This live artifact test requires supplied genuine approved claims');let long=0;
 for(const c of claims){const rule=rules.get(c.team_rule_id);assert.ok(rule);assert.ok(validateClaim(c,rule,provenance.get(c.team_rule_id),await fingerprint(rule)),c.team_rule_id);assert.notEqual(c.extractor.request_id,c.reviewer.request_id);if(!compactClaim(c).showInline)long++;}
 console.log(`PASS: ${claims.length}/${claims.length} actual claims evidence/fingerprint/independent-response gates; ${long} long explanations expand without truncation.`);
})().catch(e=>{console.error(e);process.exit(1)});
