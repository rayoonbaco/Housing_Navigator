"""Deterministic three-valued property coverage; no manually authored legal rules."""
import datetime as dt
CITY_STATE={'Los Angeles':'CA','San Francisco':'CA','San Diego':'CA','Berkeley':'CA','Santa Ana':'CA','Boston':'MA','Cambridge':'MA','Jersey City':'NJ','Hoboken':'NJ','Newark':'NJ'}
FIELDS={'dataset_residential_scope','units','year_built','use_code','use_description','owner_type','owner_occupied','owner_properties','certificate_of_occupancy_date','exemption_notice','eviction_ground','tenancy_duration_months','subsidized','rso_registered','new_construction_exemption','tenant_service_member','tenant_age','tenant_disability','rent_amount','deposit_amount','lease_type','tenancy_start_date'}

def city_jurisdiction(label):
    """Parse organizer city labels without changing the original rule record.

    Both bare labels and exact ``City, ST`` labels are supplied in the corpus.
    A conflicting suffix is invalid; mailing cities never enter this parser.
    """
    if not isinstance(label,str):return None
    parts=[x.strip() for x in label.split(',')]
    if len(parts)==1:
        city=parts[0];state=CITY_STATE.get(city)
    elif len(parts)==2:
        city,state=parts
        if CITY_STATE.get(city)!=state:return None
    else:return None
    return (city,state) if state else None

def validate_predicate(p,depth=0):
    if depth>12 or not isinstance(p,dict):raise ValueError('Invalid/deep coverage predicate')
    op=p.get('op')
    if op in ('true','false'):return
    if op=='unknown':
        if not isinstance(p.get('reason'),str) or not p['reason'].strip():raise ValueError('Unknown needs an explanation')
        return
    if op in ('all','any'):
        if not isinstance(p.get('args'),list) or not p['args'] or len(p['args'])>20:raise ValueError('Invalid predicate arguments')
        for x in p['args']:validate_predicate(x,depth+1)
        return
    if op=='not':validate_predicate(p.get('arg'),depth+1);return
    if op=='cmp':
        if p.get('field') not in FIELDS or p.get('comparison') not in ('eq','ne','lt','le','gt','ge','starts_with'):raise ValueError('Invalid field/comparison')
        v=p.get('value')
        if not isinstance(v,(str,int,float,bool)) or isinstance(v,float) and (v!=v or abs(v)==float('inf')):raise ValueError('Invalid comparison value')
        if p['field'] in ('units','year_built') and (not isinstance(v,(int,float)) or isinstance(v,bool)):raise ValueError('Numeric field needs numeric value')
        if p['comparison'] in ('lt','le','gt','ge') and p['field'] not in ('units','year_built','certificate_of_occupancy_date','tenancy_duration_months','owner_properties','tenant_age','rent_amount','deposit_amount','tenancy_start_date'):raise ValueError('Invalid ordered comparison')
        return
    raise ValueError('Unknown predicate operator')

def facts(address):
    # Only supplied assessor facts are available. No synthesized owner, tenant or certificate fields.
    out={k:address.get(k) or None for k in ('units','year_built','use_code','use_description','dataset_residential_scope')}
    for field in ('units','year_built'):
        try:out[field]=int(out[field])
        except (ValueError,TypeError):out[field]=None
    return out

def coverage(p,f):
    op=p['op']
    if op=='true':return True,[]
    if op=='false':return False,[]
    if op=='unknown':return None,[p['reason']]
    if op=='not':
        value,why=coverage(p['arg'],f);return (None if value is None else not value),why
    if op in ('all','any'):
        evaluated=[coverage(x,f) for x in p['args']];values=[x[0] for x in evaluated]
        if op=='all' and False in values:return False,[]
        if op=='any' and True in values:return True,[]
        if None in values:return None,list(dict.fromkeys(y for _,why in evaluated for y in why))
        return (all(values) if op=='all' else any(values)),[]
    value=f.get(p['field'])
    if value is None:return None,['Missing '+p['field']]
    expected=p['value'];operator=p['comparison']
    if type(value)!=type(expected) and not (type(value) in (int,float) and type(expected) in (int,float)):return None,['Incompatible '+p['field']+' fact']
    ops={'eq':lambda:value==expected,'ne':lambda:value!=expected,'lt':lambda:value<expected,'le':lambda:value<=expected,'gt':lambda:value>expected,'ge':lambda:value>=expected,'starts_with':lambda:isinstance(value,str) and isinstance(expected,str) and value.startswith(expected)}
    return ops[operator](),[]

def date_status(rule,normalized,as_of):
    query=dt.date.fromisoformat(as_of)
    if rule['status']=='failed':return None,'Failed measure; no current protection'
    if rule['status']=='pending':return 'pending','Proposal is pending; not current law'
    effective=normalized.get('effective_date') if normalized else rule.get('effective_date')
    if effective:
        try:start=dt.date.fromisoformat(effective)
        except (ValueError,TypeError):return 'unknown','Effective date lacks day-level precision'
        if query<start:return 'not_yet_effective','Enacted rule is not yet effective on this query date'
        return 'applies','Effective-date gate passed'
    if rule['status']=='not_yet_effective':return 'not_yet_effective' if query<=dt.date(2026,10,1) else 'unknown','Exact effective date unresolved'
    if as_of!='2026-10-01':return 'unknown','Historical/future status not established by the default-date snapshot'
    return 'applies','Source snapshot reports rule in force on the default query date'

def lookup(address,geo,rules,normalized,as_of):
    result=[];city=(geo.get('jurisdiction') or {}).get('legal_city') if geo else None
    for rule in rules:
        jurisdiction=rule['jurisdiction'];boundary_unknown=False
        if rule['level']=='state':
            if jurisdiction!=address['state']:continue
        else:
            parsed=city_jurisdiction(jurisdiction)
            if parsed is None:continue
            legal_rule_city,rule_state=parsed
            if rule_state!=address['state']:continue
            if city is not None and legal_rule_city!=city:continue
            boundary_unknown=city is None
        norm=normalized.get(rule['team_rule_id']);status,date_note=date_status(rule,norm,as_of)
        if status is None:continue
        if norm:
            fits,why=coverage(norm['coverage'],facts(address))
            if fits is False:continue
        else:fits=None;why=['Coverage compilation did not pass independent review']
        if boundary_unknown:fits=None;why+=['Legal city unresolved; local coverage is unverified']
        if status=='applies' and fits is None:status='unknown'
        explanation=date_note+'. '+(norm['coverage_note'] if norm else '')
        if why:explanation+=' Coverage uncertainty: '+'; '.join(why)+'.'
        if status=='applies':explanation+=' Property coverage passed; the cited requirement still governs its stated transaction/event conditions.'
        result.append({'team_rule_id':rule['team_rule_id'],'result':status,'explanation':explanation.strip(),'conflict_flag':bool(rule.get('conflict_flag',False))})
    return result
