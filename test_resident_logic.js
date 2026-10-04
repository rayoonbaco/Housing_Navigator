'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {summarize,uncertainty,QUESTIONS}=require('../resident_logic.js');
const item=(result,explanation='',rule={})=>({entry:{result,explanation},rule});
assert.match(summarize([]).answer,/does not mean/);
assert.equal(summarize([item('pending')]).label,'Proposed, not law');
assert.equal(summarize([item('not_yet_effective')]).label,'Starts later');
assert.equal(summarize([item('applies'),item('unknown','missing owner occupancy')]).label,'Some answers need checking');
assert.equal(summarize([item('unknown','Coverage compilation did not pass independent review.')]).label,'Answer not confirmed');
assert.match(summarize([item('unknown','Coverage compilation did not pass independent review.')]).extra,/building detail alone/);
assert.equal(summarize([item('unknown','Missing year_built')]).label,'More details needed');
assert.equal(uncertainty({explanation:'Legal city unknown'}),'geography');
assert.equal(uncertainty({explanation:'Effective date unverified'}),'date');
assert.equal(summarize([item('applies','',{conflict_flag:true})]).label,'Rules need checking');
assert.equal(summarize([item('applies'),item('pending')]).tone,'applies');
assert.match(summarize([item('applies'),item('pending')]).extra,/Proposals/);
const layered=summarize([item('applies','',{level:'state'}),item('applies','',{level:'city'})]);
assert.equal(layered.interactionReviewNeeded,true);assert.match(layered.extra,/Which rule governs still needs review/);assert.equal(layered.label,'Rules apply');
assert.equal(summarize([item('applies','',{level:'state'})]).interactionReviewNeeded,false);
const root=process.env.RESIDENT_DATA_DIR?path.resolve(process.env.RESIDENT_DATA_DIR):path.resolve(__dirname,'../data');
const rules=JSON.parse(fs.readFileSync(path.join(root,'rules.json'),'utf8'));
assert.equal(rules.length,310);
const byId=new Map(rules.map(r=>[r.team_rule_id,r]));
const categories=Object.keys(QUESTIONS);
let summaries=0;
for(const date of ['2025-12-31','2026-01-02','2026-10-01','2027-07-02']){
 const lookups=require('../lookup_codec.js').decode(JSON.parse(fs.readFileSync(path.join(root,`lookups-${date}.json`),'utf8')));
 assert.equal(lookups.as_of,date);assert.equal(Object.keys(lookups.lookups).length,500);
 for(const entries of Object.values(lookups.lookups)){
  const original=JSON.stringify(entries);
  for(const category of categories){
   const selected=entries.map(entry=>({entry,rule:byId.get(entry.team_rule_id)})).filter(x=>x.rule?.category===category);
   const result=summarize(selected);assert.equal(typeof result.answer,'string');assert.ok(result.answer.length);summaries++;
   if(result.tone==='applies')assert.ok(selected.some(x=>x.entry.result==='applies'));
   if(result.label==='More details needed')assert.ok(selected.filter(x=>x.entry.result==='unknown').every(x=>uncertainty(x.entry)==='facts'));
  }
  assert.equal(JSON.stringify(entries),original);
 }
}
console.log('PASS: 16 adversarial assertions; 12,000 actual-data topic summaries; all 500 addresses/four snapshots; no eligibility mutation.');
