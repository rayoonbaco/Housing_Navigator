const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');const {decode}=require('../lookup_codec.js');
const fixture={format:'lookup-table-1',as_of:'2026-10-01',rule_ids:['R1'],statuses:['unknown'],explanations:['Missing property fact.'],rows:{A1:[[0,0,0,false]]}};
assert.deepEqual(JSON.parse(JSON.stringify(decode(fixture))),{as_of:'2026-10-01',lookups:{A1:[{team_rule_id:'R1',result:'unknown',explanation:'Missing property fact.',conflict_flag:false}]}});
for(const change of [x=>x.rows.A1[0][0]=99,x=>x.rows.A1[0][1]=-1,x=>x.rows.A1[0][2]=0.5,x=>x.rows.A1[0][3]='false',x=>x.statuses[0]='eligible',x=>x.rows.A1='broken']){const item=structuredClone(fixture);change(item);assert.throws(()=>decode(item));}
assert.equal(decode(null),null);const original={as_of:'date',lookups:{}};assert.equal(decode(original),original);
let count=0;for(const name of fs.readdirSync(path.join(__dirname,'../data')).filter(n=>/^lookups-.*\.json$/.test(n))){const value=decode(JSON.parse(fs.readFileSync(path.join(__dirname,'../data',name),'utf8')));assert.equal(Object.keys(value.lookups).length,500);count+=Object.values(value.lookups).reduce((n,r)=>n+r.length,0);}
console.log('PASS: lossless codec fixture, 6 malformed payload rejections, backward compatibility and '+count+' actual date/address records.');
