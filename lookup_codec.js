/* Lossless transport only. All saved statuses and explanations are unchanged. */
(function(root){
  function decode(payload){
    if(payload?.format!=='lookup-table-1')return payload;
    const {rule_ids,statuses,explanations,rows,as_of}=payload;
    if(typeof as_of!=='string'||!Array.isArray(rule_ids)||!Array.isArray(statuses)||!Array.isArray(explanations)||!rows||typeof rows!=='object'||Array.isArray(rows))throw Error('Malformed compact lookup');
    const allowed=new Set(['applies','unknown','pending','not_yet_effective','superseded']);
    if(rule_ids.some(x=>typeof x!=='string')||statuses.some(x=>!allowed.has(x))||explanations.some(x=>typeof x!=='string'))throw Error('Invalid lookup dictionaries');
    const lookups=Object.create(null);
    for(const [id,records] of Object.entries(rows)){
      if(!Array.isArray(records))throw Error('Malformed address rows');
      lookups[id]=records.map(record=>{
        if(!Array.isArray(record)||record.length!==4||typeof record[3]!=='boolean')throw Error('Malformed lookup record');
        for(const [i,dict] of [[0,rule_ids],[1,statuses],[2,explanations]])if(!Number.isInteger(record[i])||record[i]<0||record[i]>=dict.length)throw Error('Invalid lookup dictionary index');
        return {team_rule_id:rule_ids[record[0]],result:statuses[record[1]],explanation:explanations[record[2]],conflict_flag:record[3]};
      });
    }
    return {as_of,lookups};
  }
  const api={decode};root.LookupCodec=api;if(typeof module!=='undefined'&&module.exports)module.exports=api;
})(typeof window==='undefined'?globalThis:window);
