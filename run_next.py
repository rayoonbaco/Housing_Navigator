"""Versioned extraction/coverage/change receipts. No setup or original-file mutation."""
import argparse,copy,datetime as dt,hashlib,json,os,re,uuid,zipfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import api_support as support
import extract_support as extraction
from compile_coverage import batch
from evaluate import lookup
from validation_core import validate_rules

HERE=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def safe_error(e,api):return str(e).replace(api.key,'[REDACTED]') if api.key else str(e)

def verbatim_sections(text):
    """Copy only explicitly delimited verbatim blocks; never normalize quotation bytes."""
    lines=text.splitlines(keepends=True);out=[];active=False;offset=0;start=None
    for line in lines:
        label=line.strip()
        if label.startswith('VERBATIM '):
            if active and start is not None:out.append(text[start:offset])
            active=True;start=offset+len(line)
        elif label in ('SUMMARY','INTERPRETATION / CLAIM LIMIT'):
            if active and start is not None:out.append(text[start:offset])
            active=False;start=None
        offset+=len(line)
    if active and start is not None:out.append(text[start:])
    return out


def authorize_companions(prov,sources,manifest):
    """Recover independently reviewed helper passages omitted by prior evidence assembly.
    Only exact IDs named in the existing skeptic review can be linked. No legal edits.
    """
    metadata={x['source_id']:x for x in manifest};audit=[]
    for entry in prov:
        ident=entry['team_rule_id']
        if not ident.startswith(('HN-SUP-P001-','HN-SUP-P002-')):continue
        linked=[]
        for key in entry.get('skeptic',{}).get('evidence_ids',[]):
            if not key.startswith('P003:E'):continue
            i=int(key.split(':E')[1])-1
            spans=support.passages(sources['P003'])
            if i<0 or i>=len(spans):raise ValueError('Reviewed companion passage ID out of range')
            span=copy.deepcopy(spans[i]);span.update(id=key,source_doc_id='P003',source_url=metadata['P003']['source_url'])
            if span['text'] != sources['P003'][span['start']:span['end']]:raise ValueError('Companion offsets do not match original')
            if span not in linked:linked.append(span)
        entry['authorized_companion_spans']=linked
        entry['authorized_companion_sources']=['P003'] if linked else []
        audit.append({'team_rule_id':ident,'linked_ids':[x['id'] for x in linked],
            'helper_source_sha256':support.sha(sources['P003'].encode('utf-8')),
            'basis':'Exact helper IDs already named by existing independent extraction review; linked to pinned helper source. Original main quotations unchanged.'})
    return audit

def supplemental(meta,schema,api):
    ident=meta['source_id'];folder=api.run/('supplement-'+ident);folder.mkdir()
    capture=(HERE/'supplemental_sources'/meta['text_file']).read_text(encoding='utf-8')
    blocks=verbatim_sections(capture)
    if not blocks:raise ValueError('No delimited verbatim legal text; digest cannot become production evidence')
    source='\n'.join(blocks)
    if '...' in source or '\u2026' in source:raise ValueError('Ellipsis in verbatim capture; no quote repairs')
    passages=support.passages(source);index={x['id']:x for x in passages}
    for span in passages:span.update(source_url=meta['source_url'],source_doc_id=ident)
    companions=[]
    if ident in ('P001','P002','V4S002','V4S003'):
        helper_ids={'P003'} if ident in ('P001','P002') else {'V4S001','V4S004','V4S005','V4S003' if ident=='V4S002' else 'V4S002'}
        helpers=[x for x in read(HERE/'supplemental_sources/source_manifest.json') if x['source_id'] in helper_ids]
        for helper in helpers:
            txt=(HERE/'supplemental_sources'/helper['text_file']).read_text(encoding='utf-8')
            for i,span in enumerate(support.passages('\n'.join(verbatim_sections(txt)))):
                span.update(id=helper['source_id']+':E'+str(i+1),source_url=helper['source_url'],source_doc_id=helper['source_id']);index[span['id']]=span;companions.append(span)
    api.sources[ident]=source
    (folder/'source.txt').write_text(source,encoding='utf-8')
    support.save(folder/'source-passages.json',passages)
    support.save(folder/'capture-metadata.json',meta)
    (folder/'original-capture.txt').write_text(capture,encoding='utf-8')
    if meta.get('raw_file'):
        raw=(HERE/meta['raw_file']); (folder/('raw-source'+raw.suffix)).write_bytes(raw.read_bytes())
    # Identification/status is disclosed context, never a quoted passage.
    context=capture.split('VERBATIM ',1)[0]
    ext=copy.deepcopy(schema)
    for name in ['team_rule_id','source_doc_id','source_url','jurisdiction','level','quoted_span']:
        ext['properties'].pop(name,None)
        if name in ext['required']:ext['required'].remove(name)
    ext['required'].append('evidence_ids');ext['properties']['evidence_ids']={'type':'array','minItems':1,'items':{'type':'string'}}
    tool={'type':'object','required':['rules','notes'],'properties':{'rules':{'type':'array','items':ext},'notes':{'type':'string'}}}
    material=json.dumps(passages+companions,ensure_ascii=False)
    result=api.call(folder,'extract',
        'Automatically extract distinct housing-related rules in the six schema categories. '
        'Capture metadata identifies whether raw source bytes were saved; accurately preserve that distinction. '
        'Use existing evidence_ids; never type or repair quotations. The FIRST evidence passage must contain the operative obligation, not just recitals or definitions. Definitions/penalties should accompany substantive obligations. '
        'Preserve all actors, exceptions, thresholds and dates. General antitrust rules can cover rental services, but do not claim a categorical software ban. '
        'Unenacted bill text is pending; a CHAPTERED bill is enacted. Source identification is contextual metadata, not operative text. '
        'Do not treat adoption as an exact effective date. For uncertainty return fewer rules with notes. '
        'For Jersey City use the separately identified original definitions, official adopted amendments and later official NO CHANGES confirmation jointly. The operative amended obligation must be the first/main quotation. Do not silently treat original superseded wording as current. Municipal waiting-period guidance establishes only a minimum, NOT an exact operative date. Keep effective_date null where publication/emergency facts are absent. Distinguish adopted/enacted from pending proposals, and decide baseline status from the supplied official adoption/amendment chain; any unresolved publication/current-status issue must be disclosed or rejected by independent review. No guessed start dates. For P001/P002 the P003 Secretary of State commencement guidance is separate companion evidence. Derive a calendar date only when chaptered metadata, vote/urgency information and the complete text support the regular-session rule without an exception. Keep AB325 general common-pricing scope, applying conditionally to rental services, not a categorical rental-software ban. SB763 penalties are supplementary Cartwright remedies, not their own new algorithm prohibition. A judicial opinion mirrored at Justia remains a court-authored primary document with third-party hosting explicitly disclosed; do not call it official-hosted. Current published municipal code supports default-snapshot status, not a guessed historical exact effective date. Status baseline 2026-10-01. Return at most 8 distinct rules.\nIDENTIFICATION\n'+context+'\nEVIDENCE\n'+material,tool,10000)
    support.save(folder/'extraction-result.json',result)
    mapping={'doc_id':ident,'url':meta['source_url'],'jurisdictions':meta['jurisdiction'].split(', ')[0]}
    candidates=[];spans_by_id={};rejections=[]
    for i,row in enumerate(result['rules'],1):
        try:
            if not row.get('evidence_ids') or row['evidence_ids'][0] not in {x['id'] for x in passages}:raise ValueError('First quote must come from the main legal source, not a companion')
            rule,spans=extraction.attach_evidence(row,index,mapping,'HN-SUP-'+ident+'-'+str(i).zfill(3))
            good,bad=validate_rules([rule],schema,source,mapping)
            if bad:rejections.extend(bad);continue
            candidates.extend(good);spans_by_id[rule['team_rule_id']]=spans
        except Exception as e:rejections.append({'candidate':row,'reason':safe_error(e,api)})
    support.save(folder/'candidate-rules.json',candidates)
    accepted=[];provenance=[]
    if candidates:
        reviews=api.call(folder,'skeptic',
            'Independently review ALL claims in each candidate, including status, actor, exceptions and effective date. '
            'A quote alone does not establish correctness. General antitrust legislation is not an unconditional rental-software ban. '
            'For Jersey City jointly evaluate official original definitions, amended operative language, later adopted NO CHANGES confirmation, publisher lag and state minimum waiting-period guidance. A minimum waiting period cannot establish an exact date; null is required without exact evidence. Do not treat uncodified as unenacted. Reject if the combined evidence still fails to establish enacted/baseline status. An exact commencement may be derived from the separately supplied P003 official guidance only if full chaptered source and metadata support the default rule; check all exceptions. Current published municipal code can support baseline in-force status without an exact start date, not validity for all past dates. Pending bills remain pending. A court-authored opinion mirrored on a legal repository can support failed status while its third-party hosting/raw-byte limitation remains explicit. '
            'Reject unsupported, uncertain, or overbroad records without repairs. Cite passage IDs.\nIDENTIFICATION\n'+context+
            '\nCANDIDATES\n'+json.dumps(candidates,ensure_ascii=False)+'\nEVIDENCE\n'+material,
            {'type':'object','required':['reviews'],'properties':{'reviews':{'type':'array','items':{'type':'object','required':['team_rule_id','verdict','reason','evidence_ids'],'properties':{'team_rule_id':{'type':'string'},'verdict':{'enum':['supported','unsupported','uncertain']},'reason':{'type':'string'},'evidence_ids':{'type':'array','items':{'type':'string'}}}}}}},6500)
        support.save(folder/'skeptic-result.json',reviews)
        for rule in candidates:
            matches=[x for x in reviews['reviews'] if x['team_rule_id']==rule['team_rule_id']]
            if len(matches)!=1 or matches[0]['verdict']!='supported' or not matches[0]['reason'].strip() or not matches[0]['evidence_ids'] or any(k not in index for k in matches[0]['evidence_ids']):
                rejections.append({'record':rule,'reason':'Independent source review did not approve','review':matches});continue
            accepted.append(rule)
            provenance.append({'team_rule_id':rule['team_rule_id'],'as_of':'2026-10-01','retrieved_at':meta['retrieved_at_utc'],
                'source_sha256':support.sha(source.encode('utf-8')),'capture_sha256':meta['text_sha256'],
                'manifest_hash_match':None,'raw_sha256':meta.get('raw_sha256'),'raw_file':meta.get('raw_file'),'integrity_note':'Hash pins captured source text. Raw official/publisher bytes present only where raw_sha256 is given; otherwise browser transcription/third-party mirror disclosed.',
                'supporting_spans':spans_by_id[rule['team_rule_id']], 'authorized_companion_sources':sorted({span.get('source_doc_id') for span in spans_by_id[rule['team_rule_id']] if span.get('source_doc_id') and span['source_doc_id']!=ident}), 'skeptic':matches[0]})
    support.save(folder/'validated-rules.json',accepted);support.save(folder/'rejections.json',rejections)
    print(ident+': '+str(len(accepted))+' independently reviewed supplemental rules',flush=True)
    return accepted,provenance

PLAN={'type':'object','required':['cases'],'properties':{'cases':{'type':'array','items':{'type':'object','required':['test_id','rule_ids','conflict_rule_ids','reason'],'properties':{'test_id':{'enum':['T1','T2','T3','T4','T5']},'rule_ids':{'type':'array','items':{'type':'string'}},'conflict_rule_ids':{'type':'array','items':{'type':'string'}},'reason':{'type':'string'}}}}}}

def changes(run,rules,norm,addresses,geos,api):
    """Models identify relevant records; deterministic address/date evaluation computes sets."""
    folder=run/'change-plan';folder.mkdir();tests=read(HERE/'change_tests.json')
    original=json.dumps(rules,ensure_ascii=False)
    relevant=[x for x in read(run/'provenance.json') if x['team_rule_id'] in {r['team_rule_id'] for r in rules if r['category']=='algorithmic_rent_setting'}] if (run/'provenance.json').exists() else []
    original+='\nORIGINAL ALGORITHMIC SOURCE EVIDENCE\n'+json.dumps([{'team_rule_id':x['team_rule_id'],'spans':x['supporting_spans']} for x in relevant],ensure_ascii=False)
    plan=api.call(folder,'identify','Map each supplied change-case TITLE to relevant AUTOMATICALLY EXTRACTED rule IDs. '
        'Do not manufacture missing rules or use the expected test outcomes as source evidence. '
        'T1 requires CA AB325/SB763; T2 city-specific algorithmic bans; T3 NJ FAIR; T4 MA S2983/H5222; T5 FAILED IP25-21. '
        'For T5 do not substitute an unrelated rent-cap record or a pending bill. Empty rule_ids explicitly means evidence missing. '
        'T2 selects only actual algorithmic bans, excluding generic renewal notices and disclosures. For T3 identify potentially conflicting municipal algorithmic bans alongside NJ FAIR preemption/savings provisions; this is a potential overlap flag, not a finding of actual invalidity. Cite the relevant competing requirements and carveouts in the reason. '
        'Reason must identify the source/citation basis.\nTITLES\n'+json.dumps([{k:t[k] for k in ['test_id','title']} for t in tests])+'\nRULES\n'+original,PLAN,5000)
    support.save(folder/'candidate.json',plan)
    review=api.call(folder,'review','Independently verify that every selected rule genuinely concerns the named law/change. '
        'Reject manufactured relationships or absence presented as success. T2 must include algorithmic bans only, never unrelated renewal disclosures. T5 needs an actual failed IP25-21 record. T3 flags possible overlap between local algorithmic prohibitions and NJ FAIR statewide regulation/preemption/savings provisions, not adjudicated actual conflict. Review the described substantive overlap and exemptions; do not require proof of actual invalidity for a potential-conflict flag. '
        'Return supported/unsupported/uncertain per test; reason must explain source basis.\nPLAN\n'+json.dumps(plan)+'\nRULES\n'+original,
        {'type':'object','required':['reviews'],'properties':{'reviews':{'type':'array','items':{'type':'object','required':['test_id','verdict','reason'],'properties':{'test_id':{'type':'string'},'verdict':{'enum':['supported','unsupported','uncertain']},'reason':{'type':'string'}}}}}},3500)
    support.save(folder/'review.json',review)
    ids={x['team_rule_id']:x for x in rules};output={};receipts=[]
    for t in tests:
        key=t['test_id'];items=[x for x in plan['cases'] if x['test_id']==key];rev=[x for x in review['reviews'] if x['test_id']==key]
        approved=len(items)==1 and len(rev)==1 and rev[0]['verdict']=='supported' and bool(rev[0]['reason'].strip())
        case=items[0] if len(items)==1 else {};selected=case.get('rule_ids',[]);conflict=case.get('conflict_rule_ids',[])
        approved=approved and bool(selected) and len(set(selected))==len(selected) and all(x in ids for x in selected+conflict)
        affected=[];flagged=[];uncertain=[];confirmed=[];potential=[];checks=[]
        if approved:
            rr=[ids[x] for x in selected]
            before=t.get('as_of_before',t.get('as_of','2026-10-01'));after=t.get('as_of_after',before)
            for a in addresses:
                geo=geos.get(a['address_id']);b=lookup(a,geo,rr,norm,before);c=lookup(a,geo,rr,norm,after)
                if key in ('T1','T3'):
                    hits=[x for x in c if x['result']=='applies'];un=[x for x in c if x['result']=='unknown']
                    if hits:affected.append(a['address_id'])
                    if un:uncertain.append(a['address_id'])
                elif key=='T4':
                    if any(x['result']=='pending' for x in c):affected.append(a['address_id'])
                elif key=='T2':
                    # Change notification dependencies differ from definite property eligibility.
                    # Only a resolved legal-city match can establish this local dependency.
                    legal_city=((geo or {}).get('jurisdiction') or {}).get('legal_city')
                    actual=[x for x in c if x['result']=='applies']
                    unknown=[x for x in c if x['result']=='unknown']
                    if actual:affected.append(a['address_id']);confirmed.append(a['address_id'])
                    elif unknown and any(r['level']=='city' and r['jurisdiction']==legal_city for r in rr):
                        affected.append(a['address_id']);potential.append(a['address_id'])
                    if unknown:uncertain.append(a['address_id'])
                elif key=='T5' and c:uncertain.append(a['address_id'])
                if key=='T3' and a['address_id'] in affected and conflict:
                    local=lookup(a,geo,[ids[x] for x in conflict],norm,after)
                    # Unknown local eligibility still needs human conflict review; resolved boundary only.
                    if ((geo or {}).get('jurisdiction') or {}).get('legal_city') and local:flagged.append(a['address_id'])
                checks.append({'address_id':a['address_id'],'before':b,'after':c})
            support.save(folder/(key+'-address-receipts.json'),checks)
        output[key]={'affected_address_ids':sorted(set(affected)),'conflict_flag_address_ids':sorted(set(flagged)),
            'notes':('Reviewed source mapping. '+case.get('reason','') if approved else 'UNRESOLVED: no independently approved relevant source-rule mapping.')+
            (' T2 affected IDs are change-notification dependencies; potential IDs are NOT confirmed applicable protections. ' if key=='T2' else '')+' Unknown coverage addresses: '+str(len(set(uncertain)))+'. '+('T4 set is hypothetical if enacted; these bills remain pending.' if key=='T4' else ''),
            'confirmed_affected_address_ids':sorted(set(confirmed)) if key=='T2' else sorted(set(affected)),
            'potentially_affected_address_ids':sorted(set(potential)), 'impact_basis':'Resolved legal-place dependency, with conditional eligibility separately disclosed' if key=='T2' else 'Saved rule/date evaluation',
            'unknown_address_ids':sorted(set(uncertain)),'mapping_status':'reviewed' if approved else 'unresolved'}
        expected_states=t.get('states',[])
        expected={a['address_id'] for a in addresses if a['state'] in expected_states}
        passed=approved
        if key in ('T1','T3','T4'):passed=passed and set(affected)==expected
        if key in ('T1','T3'):
            passed=passed and all(any(x['result']=='not_yet_effective' for x in z['before']) for z in checks if z['address_id'] in expected)
        if key=='T2':
            wanted={a['address_id'] for a in addresses if (((geos.get(a['address_id']) or {}).get('jurisdiction') or {}).get('legal_city')) in ('Hoboken','Jersey City')}
            passed=passed and set(affected)==wanted and {ids[x]['jurisdiction'] for x in selected if ids[x]['level']=='city'}=={'Hoboken','Jersey City'}
        if key=='T3':
            wanted={a['address_id'] for a in addresses if (((geos.get(a['address_id']) or {}).get('jurisdiction') or {}).get('legal_city')) in ('Hoboken','Jersey City')}
            passed=passed and set(flagged)==wanted
        if key=='T5':passed=passed and not affected and not uncertain and all(ids[x]['status']=='failed' for x in selected)
        receipts.append({'test_id':key,'status':'pass' if passed else 'fail' if approved else 'not_run','affected':len(set(affected)),
            'unknown':len(set(uncertain)), 'confirmed_affected':len(set(confirmed)) if key=='T2' else len(set(affected)), 'potentially_affected':len(set(potential)), 'rule_ids':selected,'scope':'Actual extraction/coverage results; expected case is an assertion, never substituted as an output.'})
    support.save(run/'changes.json',output);support.save(run/'change-test-results.json',receipts)
    return receipts

def main():
    p=argparse.ArgumentParser();p.add_argument('--project',type=Path,required=True);p.add_argument('--max-usd',type=float,default=40);p.add_argument('--workers',type=int,default=3);a=p.parse_args()
    for name,h in read(HERE/'package_hashes.json').items():
        if support.sha((HERE/name).read_bytes())!=h:raise ValueError('Bundled input changed: '+name)
    if not os.environ.get('ANTHROPIC_API_KEY'):raise ValueError('Key is missing from this window. Do not print or upload it.')
    run=a.project/'outputs'/'engine-v2_3'/(dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S')+'-'+uuid.uuid4().hex[:8]);run.mkdir(parents=True)
    support.VERSION='engine-2.3-municipal-chain';api=support.Api(run,a.project/'evidence'/'engine-v2_3-cache',a.max_usd,80)
    api.sources={f.stem:f.read_text(encoding='utf-8') for f in (HERE/'source_text').glob('*.txt')}
    rules=read(HERE/'data/rules.json');prov=read(HERE/'data/provenance.json');addresses=read(HERE/'data/addresses.json');geos={x['address_id']:x for x in read(HERE/'data/jurisdictions.json')};schema=read(HERE/'rule_record.schema.json')
    for row in addresses:row['dataset_residential_scope']=True
    support.save(run/'dataset-scope-basis.json',{'fact':'dataset_residential_scope','value':True,'basis':'Organizer Participant Guide sections1 and4.1: apartment addresses / multifamily sample.',
        'guide_sha256':support.sha((HERE/'participant-guide.md').read_bytes()),'limits':'Property scope only. No inference of an active tenancy, owner, occupancy certificate or exemption.'})
    errors=[];targets={'V4S002','V4S003'};manifest=read(HERE/'supplemental_sources/source_manifest.json')
    for meta in manifest:
        capture=(HERE/'supplemental_sources'/meta['text_file']).read_text(encoding='utf-8')
        blocks=verbatim_sections(capture)
        if blocks:api.sources[meta['source_id']]='\n'.join(blocks)
    link_audit=authorize_companions(prov,api.sources,manifest)
    support.save(run/'companion-evidence-audit.json',link_audit)
    for meta in manifest:
        if meta['source_id'] not in targets:continue
        try:
            rr,pp=supplemental(meta,schema,api);rules.extend(rr);prov.extend(pp)
        except Exception as e:errors.append({'source_id':meta['source_id'],'error':safe_error(e,api)})
    support.save(run/'rules.json',rules);support.save(run/'provenance.json',prov);support.save(run/'addresses.json',addresses);support.save(run/'jurisdictions.json',list(geos.values()))
    baseline=read(HERE/'data/coverage.json'); existing={x['team_rule_id'] for x in baseline}; by_source={}
    for r in rules:
        if r['team_rule_id'] not in existing and (r['source_doc_id'].startswith('V4S') or r['team_rule_id']=='HN-SUP-P005-002'):by_source.setdefault(r['source_doc_id'],[]).append(r)
    print('Preserving '+str(len(baseline))+' reviewed predicates; retrying '+str(sum(len(x) for x in by_source.values()))+' unresolved/target rules in batches of2.',flush=True)
    groups=[rows[i:i+2] for rows in by_source.values() for i in range(0,len(rows),2)];compiled=baseline.copy();reject=[];provs={x['team_rule_id']:x for x in prov}
    with ThreadPoolExecutor(max_workers=min(max(a.workers,1),4)) as pool:
        jobs={pool.submit(batch,i+1,rows,provs,api):i+1 for i,rows in enumerate(groups)}
        for job in as_completed(jobs):
            try:ok,bad=job.result(); replaced={x['team_rule_id'] for x in ok};compiled=[x for x in compiled if x['team_rule_id'] not in replaced];compiled.extend(ok);reject.extend(bad)
            except Exception as e:errors.append({'batch':jobs[job],'error':safe_error(e,api)})
            support.save(run/'coverage.json',compiled);support.save(run/'coverage-rejections.json',reject);support.save(run/'errors.json',errors)
    norm={x['team_rule_id']:x for x in compiled};dates=['2025-12-31','2026-01-02','2026-10-01','2027-07-02']
    for date in dates:
        support.save(run/('lookups-'+date+'.json'),{'as_of':date,'lookups':{x['address_id']:lookup(x,geos.get(x['address_id']),rules,norm,date) for x in addresses}})
    support.save(run/'lookups.json',read(run/'lookups-2026-10-01.json'))
    try:checks=changes(run,rules,norm,addresses,geos,api)
    except Exception as e:
        errors.append({'stage':'change-tests','error':safe_error(e,api)});checks=[{'test_id':'T'+str(i),'status':'not_run'} for i in range(1,6)]
        support.save(run/'change-test-results.json',checks)
    support.save(run/'report.json',{'version':'engine-2.3','as_of':'2026-10-01','rules':len(rules),'coverage_approved':len(compiled),'coverage_unresolved':len(rules)-len(compiled),
        'addresses':len(addresses),'genuine_api_calls':api.calls,'estimated_usd':round(api.spent,6),'change_tests':checks,'errors':errors,'usage':api.usage,
        'limitations':['Preliminary model-reviewed output; not legal advice or counsel certification.','Organizer source-byte manifest mismatch unresolved.',
            '20 legal cities unknown. Missing owner/certificate/tenant facts preserved.','Supplemental provenance distinguishes raw official/publisher downloads from browser transcriptions and third-party hosting.',
            'No reviewed cross-source stricter-rule supersession or duplicate consolidation yet.','T2 potential impact is a legal-place change-notification dependency, not confirmed eligibility; individual missing facts stay unknown.','County is recovered geography metadata; supplied rule schema has state/city only.','Court opinion is third-party hosted; direct official final IP25-21 endpoint remains unavailable.',
            'Historical/future snapshots conservative where full temporal validity is not established.']})
    downloads=Path(os.environ.get('USERPROFILE',str(Path.home())))/'Downloads';downloads.mkdir(exist_ok=True)
    output=downloads/('Housing_Engine_v2_3_Return-'+run.name+'.zip')
    with zipfile.ZipFile(output,'x',zipfile.ZIP_DEFLATED) as z:
        for f in run.rglob('*'):
            if f.is_file():z.write(f,str(f.relative_to(run.parent)))
    print('\nRETURN ZIP: '+str(output),flush=True);print('Upload this ZIP for integration review. Source/coverage/change failures remain explicit.',flush=True)

if __name__=='__main__':main()
