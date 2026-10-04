"""Model-compiled, independently reviewed coverage predicates from original evidence."""
import argparse,datetime as dt,json,uuid,zipfile,os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import api_support as support
from evaluate import validate_predicate,lookup,FIELDS
support.VERSION='coverage-2.4-targeted-definition-context'
SCHEMA={'type':'object','required':['rules'],'properties':{'rules':{'type':'array','items':{'type':'object','required':['team_rule_id','coverage','coverage_note','effective_date','evidence_ids'],'properties':{'team_rule_id':{'type':'string'},'coverage':{'type':'object'},'coverage_note':{'type':'string'},'effective_date':{'type':['string','null']},'evidence_ids':{'type':'array','minItems':1,'items':{'type':'string'}}}}}}}
REVIEW={'type':'object','required':['reviews'],'properties':{'reviews':{'type':'array','items':{'type':'object','required':['team_rule_id','verdict','reason','evidence_ids'],'properties':{'team_rule_id':{'type':'string'},'verdict':{'enum':['supported','unsupported','uncertain']},'reason':{'type':'string'},'evidence_ids':{'type':'array','items':{'type':'string'}}}}}}}

def batch(number,rows,prov,api):
    folder=api.run/f'batch-{number:03d}';folder.mkdir();evidence={};material=[]; allowed={};contexts={}
    for r in rows:
        entry=prov[r['team_rule_id']];keys=[]
        doc=r.get('source_doc_id'); allowed[r['team_rule_id']]=set()
        # Full definitions from explicitly linked sources must be available, not
        # only snippets selected during extraction. Links are rule-specific.
        linked = entry.get('authorized_companion_sources', [])
        if not isinstance(linked, list) or any(not isinstance(x, str) for x in linked):
            raise ValueError('Invalid authorized companion source list')
        source_ids = ([doc] if doc else []) + linked
        for owner in dict.fromkeys(source_ids):
            if owner not in getattr(api,'sources',{}):
                if owner != doc:
                    raise ValueError('Authorized companion source is unavailable')
                continue
            if owner not in contexts:
                spans=support.passages(api.sources[owner])
                contexts[owner]=[{'id':owner+':C'+str(i+1),'text':x['text'],
                    'source_doc_id':owner} for i,x in enumerate(spans)]
                evidence.update({x['id']:x['text'] for x in contexts[owner]})
            allowed[r['team_rule_id']].update(x['id'] for x in contexts[owner])
        for i,span in enumerate(entry['supporting_spans']+entry.get('authorized_companion_spans',[])):
            owner=span.get('source_doc_id') or doc
            text=span['text']
            if owner and owner != doc:
                if owner not in getattr(api,'sources',{}) or text not in api.sources[owner]:
                    raise ValueError('Companion evidence is not an exact linked source substring')
                if span not in entry.get('authorized_companion_spans',[]) and owner not in entry.get('authorized_companion_sources',[]):
                    raise ValueError('Unapproved companion evidence')
            key=r['team_rule_id']+':E'+str(i+1);evidence[key]=text;keys.append(key)
        allowed[r['team_rule_id']].update(keys)
        all_spans=entry['supporting_spans']+entry.get('authorized_companion_spans',[])
        material.append({'rule':r,'evidence':[{ 'id':k,'text':evidence[k],
            'source_doc_id':all_spans[i].get('source_doc_id') or doc,
            'source_url':all_spans[i].get('source_url') or r.get('source_url'),
            'role':'linked_companion' if (all_spans[i].get('source_doc_id') or doc)!=doc else 'main_source'} for i,k in enumerate(keys)]})
    source=json.dumps({'rules':material,'full_source_context':contexts,
        'allowed_evidence_by_rule':{k:sorted(v) for k,v in allowed.items()},
        'previous_review_feedback':{r['team_rule_id']:getattr(api,'repair_feedback',{}).get(r['team_rule_id'],[]) for r in rows}},ensure_ascii=False)
    prompt='''Compile PROPERTY COVERAGE from these automated rule records and their original evidence. No code generation or new legal rules.
Return exactly one entry per supplied rule ID. Keep coverage_note under100 words and review reasons under100 words. Prefer one explicit unknown node describing an unrepresentable legal exemption over inaccurate broad boolean comparisons; never substitute a generic subsidized or owner_occupied boolean for a narrower statutory exception. Distinguish property eligibility from events that trigger an obligation: ordinary landlord/tenant transactions are described in coverage_note, not silently assumed to have happened. A specific PROPERTY exemption or eligibility prerequisite requiring unavailable owner/tenant facts MUST remain unknown. Generic landlord/tenant roles and a future regulated transaction are conditional duties, not missing property eligibility. The question is WHICH LAW GOVERNS IF its stated action occurs, never whether that action has already occurred. Do not turn the absence of an owner name or evidence of actual algorithm use into a property unknown for laws covering all rental apartment properties. A specific small-landlord, owner-occupied, restricted-subsidy, or certificate-date exemption is different and must remain unknown if necessary facts are missing.
Do not infer certificate-of-occupancy dates from year_built. For cutoff certificate years, certificate fields are unavailable. Do not infer owners, registrations, notices, new-construction filings, rent amounts or tenant facts.
Predicates: {op:true}, {op:false}, {op:unknown,reason:string}, {op:all,args:[predicates]}, {op:any,args:[predicates]}, {op:not,arg:predicate}, {op:cmp,field:name,comparison:eq|ne|lt|le|gt|ge|starts_with,value:literal}. (Use JSON strings for op values.)
The previous reviewer feedback identifies defects to reconsider, not legal evidence. Rebuild each candidate from the original source evidence. Explicitly retain an unknown for primary-residence intent and medical/inpatient/long-term-care/detention exclusions where those definitions apply and the supplied facts cannot establish them. Do not use dataset_residential_scope as a substitute for those definitions. Include definition evidence for each relied-on exemption; if a same-owner exemption definition occurs in an authorized companion, cite its allowed C passage instead of copying a rule-record summary. A faithful predicate retaining unknown prerequisites can be supported even when its actual property result stays unknown.
Available facts: dataset_residential_scope is true ONLY for these organizer-supplied sample apartment addresses (Participant Guide section 1 and 4.1); it establishes residential property scope, never owner identity, tenancy, exemption, or a transaction. units and year_built numeric; use_code and use_description strings. All other permitted fields are unavailable, so their comparisons evaluate unknown. Permitted fields: '''+','.join(sorted(FIELDS))+'''.
Use true ONLY when property scope is unconditional in the supplied evidence; if incomplete source context prevents an exemption test, use unknown with reason. Never create false simply because sample data lacks a fact. Evidence IDs must belong to that rule's allowed_evidence_by_rule list. Own-source and explicitly authorized linked-source C passages are available; another rule's unlinked C or E passages are forbidden. An E passage explicitly labeled linked_companion is authorized evidence from a separately identified source, verified against its pinned text. Use linked commencement guidance together with chaptered metadata and check all exceptions; do not reject it merely for having a different document ID. Select ALL evidence needed for scope and date, including linked guidance. Full source context is supplied to find definitions and exemptions; do not invent them. Owner/buyer occupancy and conversion exceptions require their explicit unknown facts even for small buildings. Government publication/court administration duties may have residential scope, but coverage_note must identify that actor rather than describe a landlord obligation. Explicitly keep exceptions and alternative coverage paths in predicates. Empty all/any is forbidden. No new jurisdiction/precedence decisions.
Return effective_date YYYY-MM-DD or null. Only exact evidence-backed start dates or unambiguous calendar derivations; no invented January1 dates, passage/effective confusion, or application of dates to unrelated rules. Preserve original effective_date unless original evidence proves otherwise. A reviewer must approve any derived date. Missing date does not establish historical validity.
Coverage_note explains scope and unresolved assumptions. No legal certification. Query baseline 2026-10-01.
DATA\n'''+source
    result=api.call(folder,'compile',prompt,SCHEMA,9000);support.save(folder/'candidate-predicates.json',result)
    rows_out=result['rules'];expected={r['team_rule_id'] for r in rows};valid=[];rejected=[]
    for r in rows_out:
        try:
            ident=r['team_rule_id']
            if ident not in expected or sum(x.get('team_rule_id')==ident for x in rows_out)!=1:raise ValueError('Unexpected or duplicate ID')
            validate_predicate(r['coverage'])
            keys=r['evidence_ids']
            if not keys or any(k not in evidence or k not in allowed[ident] for k in keys):raise ValueError('Invalid/cross-rule evidence ID')
            if not r['coverage_note'].strip():raise ValueError('Missing scope explanation')
            if r['effective_date'] is not None:dt.date.fromisoformat(r['effective_date'])
            original=next(x for x in rows if x['team_rule_id']==ident)
            if original.get('effective_date') and len(original['effective_date'])==10 and r['effective_date']!=original['effective_date']:raise ValueError('Cannot alter an existing exact extracted effective date')
            valid.append(r)
        except Exception as exc:rejected.append({'candidate':r,'reason':str(exc)})
    accepted=[]
    if valid:
        review=api.call(folder,'review','''Independently audit these coverage predicates against the original rule and source evidence. supported only if ALL scope, exemptions, actors, thresholds and effective dates are faithful. Missing PROPERTY eligibility/exemption facts must remain unknown. Ordinary actions (using a qualifying pricing service, receiving an application, charging a fee) and the generic actor role of landlord are conditional triggers, not evidence that a covered property is ineligible. The organizer explicitly supplies apartment/multifamily addresses. Validate conditional property coverage, never infer an actual transaction. Keep genuine property-specific owner/CO/subsidy exceptions. Review reasons under100 words. Year built cannot substitute for certificate-of-occupancy date. An unconditional true predicate needs proof of property-wide scope; incomplete scope must be unknown. Do not reward optimistic coverage. Reject another rule's E passages or any source not present in that rule's allowed_evidence_by_rule list. C passages from an explicitly authorized linked source are allowed and supply full definitions; a different document ID alone is not grounds for rejection. Previous feedback is not source evidence. A faithful predicate with explicit unknown prerequisites may be supported even though actual property eligibility remains unknown. This rule's E passages labeled linked_companion are expressly authorized separate sources, with source_doc_id and URL. They have been checked as exact substrings of pinned source text. Evaluate their legal support jointly with main bill metadata; a different document ID alone is not a reason to reject. An independently extracted date still needs evidence review; cite both chapter metadata and linked commencement guidance. For general laws with no property restriction, true is preferable to a residential-only scope gate. For residential definitions excluding care/detention facilities, dataset_residential_scope alone does not prove primary residence or those exclusions; retain explicit unknown prerequisites when organizer facts cannot establish them. Check owner/buyer occupancy conditions explicitly; a small unit count cannot prove occupancy or intent. A compared field must represent the fact named in the source. No silent repairs. For each candidate return verdict, nonempty reason, and IDs supporting your decision.\nCANDIDATES\n'''+json.dumps(valid)+'\nORIGINAL DATA\n'+source,REVIEW,6500)
        support.save(folder/'predicate-review.json',review)
        for r in valid:
            ident=r['team_rule_id'];verdict=[x for x in review['reviews'] if x['team_rule_id']==ident]
            if len(verdict)==1 and verdict[0]['verdict']=='supported' and verdict[0]['reason'].strip() and verdict[0]['evidence_ids'] and all(k in evidence and k in allowed[ident] for k in verdict[0]['evidence_ids']):
                r['independent_review']=verdict[0];accepted.append(r)
            else:rejected.append({'candidate':r,'reason':'Independent review missing, unsupported, uncertain, or invalid evidence','review':verdict})
    support.save(folder/'accepted-predicates.json',accepted);support.save(folder/'rejections.json',rejected)
    print(f'Coverage batch {number}: {len(accepted)}/{len(rows)} approved',flush=True)
    return accepted,rejected

def main():
    p=argparse.ArgumentParser();p.add_argument('--project',type=Path,required=True);p.add_argument('--max-usd',type=float,default=40);p.add_argument('--workers',type=int,default=3);a=p.parse_args()
    data=Path(__file__).parent/'data'
    pins=json.loads((data/'input_hashes.json').read_text())
    for name,expected_hash in pins.items():
        if support.sha((data/name).read_bytes())!=expected_hash:raise ValueError('Input integrity check failed: '+name)
    rules=json.loads((data/'rules.json').read_text());prov={x['team_rule_id']:x for x in json.loads((data/'provenance.json').read_text())};addresses=json.loads((data/'addresses.json').read_text());geos={x['address_id']:x for x in json.loads((data/'jurisdictions.json').read_text())}
    run=a.project/'outputs'/'applicability-v1'/(dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S')+'-'+uuid.uuid4().hex[:8]);run.mkdir(parents=True)
    api=support.Api(run,a.project/'evidence'/'coverage-v1-cache',a.max_usd,160);compiled=[];reject=[];errors=[]
    groups=[rules[i:i+5] for i in range(0,len(rules),5)]
    with ThreadPoolExecutor(max_workers=min(max(a.workers,1),4)) as pool:
        jobs={pool.submit(batch,i+1,rows,prov,api):i+1 for i,rows in enumerate(groups)}
        for job in as_completed(jobs):
            try:
                accepted,rejected=job.result();compiled.extend(accepted);reject.extend(rejected)
            except Exception as exc:
                errors.append({'batch':jobs[job],'error':str(exc).replace(api.key,'[REDACTED]') if api.key else str(exc)});print('Batch '+str(jobs[job])+' failed; unreviewed scope remains unknown',flush=True)
            support.save(run/'coverage.json',compiled);support.save(run/'coverage-errors.json',errors);support.save(run/'coverage-rejections.json',reject)
    normalized={x['team_rule_id']:x for x in compiled};lookups={'as_of':'2026-10-01','lookups':{row['address_id']:lookup(row,geos.get(row['address_id']),rules,normalized,'2026-10-01') for row in addresses}}
    support.save(run/'rules.json',rules);support.save(run/'lookups.json',lookups);support.save(run/'provenance.json',list(prov.values()));support.save(run/'jurisdictions.json',list(geos.values()));support.save(run/'merge-audit.json',json.loads((data/'merge-audit.json').read_text()))
    support.save(run/'report.json',{'version':'applicability-1.0','rules':len(rules),'coverage_approved':len(compiled),'coverage_unresolved':len(rules)-len(compiled),'addresses':len(addresses),'genuine_api_calls':api.calls,'estimated_usd':round(api.spent,6),'batch_errors':errors,'usage':api.usage,'result_counts':{status:sum(x['result']==status for matches in lookups['lookups'].values() for x in matches) for status in ['applies','unknown','pending','not_yet_effective','superseded']},'limitations':['Preliminary applicability; not legal certification.','No cross-source duplicate consolidation or stricter-rule supersession yet.','T1-T5 and supplemental-source integration remain untested.','City resolution unknown for20 addresses; state uses supplied assessor state.','Source manifest hash integrity unresolved.','Coverage review is model-assisted, not human counsel review.']})
    downloads=Path(os.environ.get('USERPROFILE',str(Path.home())))/'Downloads';downloads.mkdir(exist_ok=True);output=downloads/('Housing_Applicability_Return-'+run.name+'.zip')
    with zipfile.ZipFile(output,'x',zipfile.ZIP_DEFLATED) as z:
        for f in run.rglob('*'):
            if f.is_file():z.write(f,str(f.relative_to(run.parent)))
    print('\nRETURN ZIP: '+str(output),flush=True);print('Send ZIP to coordinating canvas. Preliminary lookups generated; change cases and source reconciliation are next.',flush=True)
if __name__=='__main__':main()
