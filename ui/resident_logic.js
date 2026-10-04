/* Presentation only: never changes saved eligibility or chooses a governing law. */
(function(root){
  const QUESTIONS={rent_increase_limits:'Can my rent go up?',just_cause_eviction:'Can my landlord make me leave?',security_deposits:'What can I be charged for a deposit?',application_screening_fees:'What can I be charged to apply?',screening_restrictions:'Can I be treated unfairly when I apply?',algorithmic_rent_setting:'Can software be used to set my rent?'};
  function uncertainty(entry){
    const text=String(entry.explanation||'');
    if(/did not pass independent review|compilation.*(?:failed|not pass)|not independently reviewed/i.test(text))return 'review';
    if(/jurisdiction.*(?:unresolved|unknown)|legal city.*(?:unknown|unresolved)|geography.*(?:unknown|unresolved)/i.test(text))return 'geography';
    if(/effective.date.*(?:unknown|unverified|unresolved)|operative.date.*(?:unknown|unverified|unresolved)/i.test(text))return 'date';
    if(/missing|unavailable facts|facts.*(?:unavailable|unknown)|cannot.*test|exemption.*unresolved/i.test(text))return 'facts';
    return 'unresolved';
  }
  function summarize(items){
    if(!items.length)return {label:'No verified answer',tone:'unknown',answer:'We do not have a verified answer for this topic in the sources checked. That does not mean there are no protections.'};
    const counts={};for(const x of items)counts[x.entry.result]=(counts[x.entry.result]||0)+1;
    const conflict=items.some(x=>x.entry.conflict_flag||x.rule?.conflict_flag);
    const unknown=items.filter(x=>x.entry.result==='unknown');
    const reasons=new Set(unknown.map(x=>uncertainty(x.entry)));
    let answer,label,tone='unknown';
    if(conflict){label='Rules need checking';answer='More than one rule may matter here. We have not confirmed how all of them fit together.';}
    else if(counts.applies){label=unknown.length?'Some answers need checking':'Rules apply';tone=unknown.length?'unknown':'applies';answer=unknown.length?'Some rules apply to this address. Other rules still need checking before we can give you a complete answer.':'The saved check found rules that apply to this address. Read what each rule says below.';}
    else if(unknown.length){
      label=reasons.size===1&&reasons.has('facts')?'More details needed':'Answer not confirmed';
      answer=label==='More details needed'?'We need more details about your home or situation to tell whether these rules cover you.':'We found rules about this, but we cannot confirm the answer for this address yet.';
    } else if(counts.not_yet_effective){label=counts.pending?'Future and proposed rules':'Starts later';tone='not_yet_effective';answer='These rules are not in effect on the date you selected. Check the verified start date before relying on them.';}
    else if(counts.pending){label='Proposed, not law';tone='pending';answer='These are proposals. They do not give you a current protection, but you can see what would change if they became law.';}
    else if(counts.superseded){label='Another rule controls';tone='superseded';answer='The saved check marks these rules as replaced by another governing rule. Open the evidence to check which one and why.';}
    else {label='Answer not confirmed';answer='We cannot give a verified answer for this topic yet.';}
    const extra=[];
    const layers=new Set(items.map(x=>x.rule?.level));
    const interactionReviewNeeded=layers.has('state')&&layers.has('city');
    if(interactionReviewNeeded)extra.push('State and city rules appear here. Which rule governs still needs review.');
    if(counts.applies&&counts.not_yet_effective)extra.push('Other rules start later.');
    if(counts.applies&&counts.pending)extra.push('Proposals are listed separately from current rules.');
    if(reasons.has('review'))extra.push('Some legal checks did not pass review; a building detail alone will not resolve that.');
    if(reasons.has('geography'))extra.push('We still need to confirm the legal location.');
    return {label,tone,answer,extra:extra.join(' '),counts,reasons:Array.from(reasons),interactionReviewNeeded};
  }
  function canonical(value){
    if(Array.isArray(value))return '['+value.map(canonical).join(',')+']';
    if(value&&typeof value==='object')return '{'+Object.keys(value).sort().map(k=>JSON.stringify(k)+':'+canonical(value[k])).join(',')+'}';
    return JSON.stringify(value);
  }
  async function fingerprint(rule){
    const encoded=new TextEncoder().encode(canonical(rule));
    const cryptoApi=typeof window==='undefined'?require('node:crypto').webcrypto:window.crypto;
    const hash=await cryptoApi.subtle.digest('SHA-256',encoded);
    return Array.from(new Uint8Array(hash),b=>b.toString(16).padStart(2,'0')).join('');
  }
  function validateClaim(claim,rule,provenance,expectedFingerprint){
    if(!claim||claim.team_rule_id!==rule?.team_rule_id||claim.rule_fingerprint!==expectedFingerprint)return false;
    if(claim.scope!=='rule_meaning'||typeof claim.claim_id!=='string'||!claim.claim_id||typeof claim.text!=='string'||!claim.text.trim())return false;
    for(const stage of ['extractor','reviewer']){
      const x=claim[stage];if(x?.approved!==true||typeof x.model!=='string'||!x.model||typeof x.request_id!=='string'||!x.request_id)return false;
    }
    if(claim.extractor.request_id===claim.reviewer.request_id)return false;
    if(!Array.isArray(claim.evidence)||!claim.evidence.length)return false;
    const spans=new Map([['rule-quote',rule.quoted_span]]);
    for(const [i,x] of (provenance?.supporting_spans||[]).entries()){if(x.text)spans.set(`support:${i}`,x.text);if(x.id&&x.text)spans.set(x.id,x.text);}
    for(const [i,x] of (provenance?.authorized_companion_spans||[]).entries()){if(x.text)spans.set(`companion:${i}`,x.text);if(x.id&&x.text)spans.set(x.id,x.text);}
    return claim.evidence.every(x=>typeof x.span_id==='string'&&typeof x.text==='string'&&x.text.length>=20&&typeof spans.get(x.span_id)==='string'&&spans.get(x.span_id).includes(x.text));
  }
  function selectClaim(claims,rule,provenance,expectedFingerprint){
    return claims.find(x=>validateClaim(x,rule,provenance,expectedFingerprint))||null;
  }
  function eligibilityCopy(entry){
    if(entry.result==='applies')return 'The saved check says this rule covers this address. The rule still depends on its stated conditions.';
    if(entry.result==='pending')return 'This is a proposal, not a current protection.';
    if(entry.result==='not_yet_effective')return 'This rule is not in effect on the selected date.';
    if(entry.result==='superseded')return 'Another governing rule controls according to the saved check.';
    if(entry.result==='unknown'){
      return ({review:'We have not completed a reliable legal eligibility check for this rule.',facts:'We need more facts about your home or situation to confirm coverage.',geography:'We have not confirmed the legal location needed for this rule.',date:'We have not confirmed when this rule takes effect.',unresolved:'We cannot confirm whether this rule covers this address yet.'})[uncertainty(entry)];
    }
    return 'Eligibility has not been confirmed.';
  }
  function compactClaim(claim){
    const words=String(claim?.text||'').trim().split(/\s+/).filter(Boolean).length;
    return {words,showInline:words<=60,explanation:words>60?'This rule has important conditions. Read the full explanation before relying on it.':null};
  }
  const api={QUESTIONS,uncertainty,summarize,canonical,fingerprint,validateClaim,selectClaim,eligibilityCopy,compactClaim};root.ResidentLogic=api;
  if(typeof module!=='undefined'&&module.exports)module.exports=api;
})(typeof window==='undefined'?globalThis:window);
