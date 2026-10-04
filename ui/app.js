'use strict';

const CATEGORIES = [
  ['rent_increase_limits', 'Rent increase limits'],
  ['just_cause_eviction', 'Just-cause eviction'],
  ['security_deposits', 'Security deposits'],
  ['application_screening_fees', 'Application & screening fees'],
  ['screening_restrictions', 'Screening restrictions'],
  ['algorithmic_rent_setting', 'Algorithmic rent-setting']
];
const CHANGE_TITLES = {
  T1: 'California AB 325 / SB 763 takes effect',
  T2: 'Hoboken vs Jersey City local algorithmic bans',
  T3: 'New Jersey FAIR Act',
  T4: 'Massachusetts pending bills S.2983 / H.5222',
  T5: 'Massachusetts rent-control ballot question struck'
};
const state = {
  manifest: null, addresses: [], jurisdictions: [], rules: [], provenance: [], report: null,
  lookups: null, changes: null, selectedAddressId: null, mode: 'production',
  lookupError: null, changeError: null, snapshotRequestId: 0, residentClaims: [], ruleFingerprints: new Map()
};
const $ = (id) => document.getElementById(id);

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined && text !== null) node.textContent = String(text);
  return node;
}
function valueOrMissing(value, label = 'Unavailable') {
  return value === null || value === undefined || String(value).trim() === '' ? label : String(value);
}
function displayDate(value) {
  if (!value) return 'Unavailable';
  const m = String(value).match(/^(\d{4})-(\d{2})-(\d{2})/);
  return m ? `${m[2]}/${m[3]}/${m[1]}` : String(value);
}
function safeUrl(raw) {
  try {
    const u = new URL(String(raw), window.location.href);
    return ['http:', 'https:'].includes(u.protocol) ? u.href : null;
  } catch { return null; }
}
async function fetchJson(url, required = true) {
  try {
    const res = await fetch(url, {cache: 'no-store'});
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
    return LookupCodec.decode(await res.json());
  } catch (err) {
    if (required) throw new Error(`Could not load ${url}: ${err.message}`);
    return null;
  }
}
function resolveRelative(baseManifestUrl, relativeUrl) {
  return new URL(relativeUrl, window.location.href).toString();
}
function setLoad(message, isError = false) {
  $('loadState').textContent = message;
  $('loadState').classList.toggle('error', isError);
}

async function init() {
  const params = new URLSearchParams(location.search);
  state.mode = params.get('fixture') === '1' ? 'fixture' : 'production';
  const manifestPath = state.mode === 'fixture' ? 'fixtures/manifest.json' : 'manifest.json';
  $('fixtureBanner').hidden = state.mode !== 'fixture';
  $('modePill').textContent = state.mode === 'fixture' ? 'Fixture · synthetic' : 'Saved engine results';
  try {
    state.manifest = await fetchJson(manifestPath);
    validateManifest(state.manifest);
    const base = manifestPath;
    const load = (key, required = true) => fetchJson(resolveRelative(base, state.manifest[key]), required);
    const [addresses, rules, provenance, jurisdictions, report] = await Promise.all([
      load('addresses_url'), load('rules_url'), load('provenance_url'), load('jurisdictions_url'),
      state.manifest.report_url ? load('report_url', false) : Promise.resolve(null)
    ]);
    for (const [label, value] of [['addresses', addresses], ['rules', rules], ['provenance', provenance], ['jurisdictions', jurisdictions]]) {
      if (!Array.isArray(value)) throw new Error(`${label}.json is malformed: expected a JSON list.`);
    }
    state.addresses = addresses;
    state.rules = rules;
    state.provenance = provenance;
    state.jurisdictions = jurisdictions;
    state.report = report;
    if(state.mode!=='fixture'){
      const artifact=await fetchJson('resident-claims.json',false);
      if(artifact?.version==='resident-claims-1'&&Array.isArray(artifact.claims)){
        state.residentClaims=artifact.claims;
        try { for(const rule of rules)state.ruleFingerprints.set(rule.team_rule_id,await ResidentLogic.fingerprint(rule)); }
        catch(err){state.residentClaims=[];console.warn('Reviewed prose unavailable; using original rule requirements.');}
      }
    }
    populateSnapshots();
    populateAddresses(params.get('address'));
    bindEvents();
    await loadSnapshot($('snapshotSelect').value);
    renderAll();
    if (!state.lookupError && !state.changeError) setLoad(`${state.addresses.length} sample addresses are available. Choose your home to see the saved check.`);
  } catch (err) {
    setLoad(err.message, true);
    renderFatal(err.message);
  }
}
function validateManifest(m) {
  const required = ['contract_version','mode','default_as_of','addresses_url','rules_url','provenance_url','jurisdictions_url','snapshots'];
  const missing = required.filter(k => !(k in (m || {})));
  if (missing.length) throw new Error(`Manifest is missing required fields: ${missing.join(', ')}`);
  if (m.contract_version !== '1') throw new Error(`Unsupported manifest contract version: ${m.contract_version}`);
  if (!['production','fixture'].includes(m.mode)) throw new Error(`Unsupported manifest mode: ${m.mode}`);
  if (m.mode !== state.mode) throw new Error(`Manifest mode ${m.mode} does not match requested ${state.mode} mode.`);
  if (!Array.isArray(m.snapshots) || !m.snapshots.length) throw new Error('Manifest contains no generated snapshots.');
  const urls = ['addresses_url','rules_url','provenance_url','jurisdictions_url'];
  if (m.report_url !== undefined) urls.push('report_url');
  for (const key of urls) validateRelativeResource(m[key], `manifest.${key}`);
  const dates = new Set();
  for (const [i, snap] of m.snapshots.entries()) {
    if (!snap || typeof snap !== 'object') throw new Error(`Snapshot ${i + 1} is malformed.`);
    for (const key of ['as_of','lookups_url','changes_url']) {
      if (typeof snap[key] !== 'string' || !snap[key].trim()) throw new Error(`Snapshot ${i + 1} is missing ${key}.`);
    }
    if (dates.has(snap.as_of)) throw new Error(`Manifest contains duplicate snapshot date ${snap.as_of}.`);
    dates.add(snap.as_of);
    validateRelativeResource(snap.lookups_url, `snapshots[${i}].lookups_url`);
    validateRelativeResource(snap.changes_url, `snapshots[${i}].changes_url`);
  }
  if (!dates.has(m.default_as_of)) throw new Error(`Default snapshot ${m.default_as_of} is not present in snapshots.`);
}
function validateRelativeResource(raw, label) {
  if (typeof raw !== 'string' || !raw.trim()) throw new Error(`${label} must be a relative URL.`);
  const value = raw.trim();
  if (/^[a-zA-Z][a-zA-Z0-9+.-]*:/.test(value) || value.startsWith('//') || value.startsWith('/')) {
    throw new Error(`${label} must be relative to the UI, not an external or root URL.`);
  }
}
function populateSnapshots() {
  const select = $('snapshotSelect'); select.replaceChildren();
  for (const snap of state.manifest.snapshots) {
    const o = el('option'); o.value = snap.as_of; o.textContent = snap.as_of;
    if (snap.as_of === state.manifest.default_as_of) o.selected = true;
    select.append(o);
  }
}
function addressLabel(a) {
  const zip = valueOrMissing(a.zip, 'ZIP unknown');
  return `${a.street_address} · ${a.postal_city}, ${a.state} ${zip} · ${a.address_id}`;
}
function populateAddresses(preferredId) {
  const select = $('addressList'); select.replaceChildren();
  for (const a of state.addresses) {
    const o = el('option'); o.value = a.address_id; o.textContent = addressLabel(a); select.append(o);
  }
  state.selectedAddressId = state.addresses.some(a => a.address_id === preferredId) ? preferredId : (state.addresses[0]?.address_id || null);
  if (state.selectedAddressId) select.value = state.selectedAddressId;
  filterAddresses('');
}
function filterAddresses(query) {
  const q = query.trim().toLowerCase();
  let shown = 0;
  for (const option of $('addressList').options) {
    const match = !q || option.textContent.toLowerCase().includes(q);
    option.hidden = !match;
    if (match) shown++;
  }
  $('addressSearch').setAttribute('aria-expanded', shown > 0 ? 'true' : 'false');
}
function bindEvents() {
  $('addressSearch').addEventListener('input', e => filterAddresses(e.target.value));
  $('addressList').addEventListener('change', () => {
    state.selectedAddressId = $('addressList').value;
    renderAll();
  });
  $('addressList').addEventListener('dblclick', () => $('answerView').scrollIntoView({behavior:'smooth'}));
  $('snapshotSelect').addEventListener('change', async () => {
    await loadSnapshot($('snapshotSelect').value);
    renderAll();
  });
  const tabs = [...document.querySelectorAll('.tab')];
  tabs.forEach((btn, index) => {
    btn.addEventListener('click', () => switchView(btn.dataset.view));
    btn.addEventListener('keydown', e => {
      let nextIndex = null;
      if (e.key === 'ArrowRight' || e.key === 'ArrowDown') nextIndex = (index + 1) % tabs.length;
      if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') nextIndex = (index - 1 + tabs.length) % tabs.length;
      if (e.key === 'Home') nextIndex = 0;
      if (e.key === 'End') nextIndex = tabs.length - 1;
      if (nextIndex === null) return;
      e.preventDefault();
      const next = tabs[nextIndex];
      switchView(next.dataset.view);
      next.focus();
    });
  });
  $('closeEvidence').addEventListener('click', () => $('evidenceDialog').close());
  $('evidenceDialog').addEventListener('click', e => { if (e.target === $('evidenceDialog')) $('evidenceDialog').close(); });
}
async function loadSnapshot(asOf) {
  const requestId = ++state.snapshotRequestId;
  const snap = state.manifest.snapshots.find(s => s.as_of === asOf);
  state.lookupError = null; state.changeError = null;
  if (!snap) {
    state.lookups = null; state.changes = null;
    state.lookupError = state.changeError = `Engine evaluation is unavailable for ${asOf}. Only generated snapshots can be shown.`;
    setLoad(state.lookupError, true);
    return true;
  }
  const manifestUrl = state.mode === 'fixture' ? 'fixtures/manifest.json' : 'manifest.json';
  const [lookupResult, changeResult] = await Promise.allSettled([
    fetchJson(resolveRelative(manifestUrl, snap.lookups_url)),
    fetchJson(resolveRelative(manifestUrl, snap.changes_url))
  ]);
  if (requestId !== state.snapshotRequestId || $('snapshotSelect').value !== asOf) return false;
  if (lookupResult.status === 'fulfilled') {
    const payload = lookupResult.value;
    if (!payload || typeof payload.lookups !== 'object' || Array.isArray(payload.lookups)) {
      state.lookups = null; state.lookupError = 'Lookup payload is malformed: expected a lookups object.';
    } else if (payload.as_of !== snap.as_of) {
      state.lookups = null; state.lookupError = `Lookup payload as_of ${valueOrMissing(payload.as_of)} does not match selected snapshot ${snap.as_of}.`;
    } else state.lookups = payload;
  } else {
    state.lookups = null; state.lookupError = lookupResult.reason?.message || 'Lookup data could not be loaded.';
  }
  if (changeResult.status === 'fulfilled' && changeResult.value && typeof changeResult.value === 'object' && !Array.isArray(changeResult.value)) {
    state.changes = changeResult.value;
  } else {
    state.changes = null;
    state.changeError = changeResult.status === 'rejected' ? (changeResult.reason?.message || 'Change-case data could not be loaded.') : 'Change-case payload is malformed.';
  }
  const problems = [state.lookupError && `Address results: ${state.lookupError}`, state.changeError && `Change cases: ${state.changeError}`].filter(Boolean);
  if (problems.length) setLoad(problems.join(' '), true);
  else setLoad(`Loaded generated snapshot ${snap.as_of}.`);
  return true;
}
function switchView(name) {
  document.querySelectorAll('.tab').forEach(b => {
    const active = b.dataset.view === name;
    b.classList.toggle('active', active);
    b.setAttribute('aria-selected', active ? 'true' : 'false');
    b.tabIndex = active ? 0 : -1;
  });
  for (const v of ['answer','changes','audit']) {
    const node = $(`${v}View`); const active = v === name;
    node.hidden = !active; node.classList.toggle('active', active);
  }
}
function renderAll() { $('answerDatePill').textContent = `As of ${$('snapshotSelect').value || 'unavailable'}`; renderAddressSummary(); renderCategories(); renderChanges(); renderAudit(); }
function renderFatal(message) {
  $('addressSummary').replaceChildren(el('div','notice danger', message));
  $('categoryGrid').replaceChildren(el('div','notice danger','Results are unavailable. No legal conclusion can be drawn.'));
}
function selectedAddress() { return state.addresses.find(a => a.address_id === state.selectedAddressId); }
function selectedJurisdiction() { return state.jurisdictions.find(j => j.address_id === state.selectedAddressId); }
function addKv(dl, label, value, missingLabel = 'Unavailable') {
  dl.append(el('dt', '', label));
  const missing = value === null || value === undefined || String(value).trim() === '';
  dl.append(el('dd', missing ? 'missing' : '', missing ? missingLabel : value));
}
function structuredValue(value) {
  if (value === null || value === undefined) return null;
  if (typeof value === 'object') { try { return JSON.stringify(value); } catch { return 'Unserializable structured value'; } }
  return value;
}
function renderAddressSummary() {
  const host=$('addressSummary');host.replaceChildren();const a=selectedAddress();if(!a)return;
  const j=selectedJurisdiction();const summary=el('div','home-context');
  summary.append(el('h3','',a.street_address));
  const matched=j?.jurisdiction_result==='matched_geography';
  summary.append(el('p','',matched ? `${j.jurisdiction.legal_city}, ${j.jurisdiction.state} · ${j.jurisdiction.county || 'County not confirmed'}` : 'We have not confirmed the legal city for this address.'));
  summary.append(el('p','home-facts',`${a.units || 'Unknown number of'} homes · Built ${a.year_built || 'year unknown'} · As of ${state.lookups?.as_of || $('snapshotSelect').value}`));
  const details=el('details','address-details');details.append(el('summary','','Check address details'));renderAddressDetails(details);summary.append(details);host.append(summary);
}
function renderAddressDetails(host) {
  const a = selectedAddress(); if (!a) return;
  const j = selectedJurisdiction();
  const wrap = el('div','summary-card');
  const postal = el('article','summary-panel'); postal.append(el('p','eyebrow','Original assessor / postal record'), el('h3','',a.street_address));
  const pdl = el('dl','kv');
  addKv(pdl,'Address ID',a.address_id); addKv(pdl,'Postal city',a.postal_city); addKv(pdl,'State',a.state); addKv(pdl,'ZIP',a.zip,'Missing in supplied record'); addKv(pdl,'Year built',a.year_built,'Unknown'); addKv(pdl,'Units',a.units,'Unknown'); addKv(pdl,'Use',a.use_description); addKv(pdl,'Dataset',a.source_dataset); addKv(pdl,'Retrieved',displayDate(a.retrieved_at)); postal.append(pdl);
  const geo = el('article','summary-panel'); geo.append(el('p','eyebrow','Matched geography'), el('h3','', j?.jurisdiction_result === 'matched_geography' ? 'Census address-range match' : 'Jurisdiction unresolved'));
  const gdl = el('dl','kv');
  if (j?.jurisdiction_result === 'matched_geography' && j.jurisdiction) {
    addKv(gdl,'Legal city',j.jurisdiction.legal_city); addKv(gdl,'State',j.jurisdiction.state); addKv(gdl,'County',j.jurisdiction.county); addKv(gdl,'County GEOID',j.jurisdiction.county_geoid); addKv(gdl,'Matched address',j.jurisdiction.matched_address); addKv(gdl,'Place GEOID',j.jurisdiction.place_geoid); addKv(gdl,'Benchmark',j.jurisdiction.benchmark?.benchmarkName || j.jurisdiction.benchmark); addKv(gdl,'Vintage',j.jurisdiction.vintage?.vintageName || j.jurisdiction.vintage); addKv(gdl,'Retrieved',displayDate(j.jurisdiction.retrieved_at));
  } else {
    addKv(gdl,'Status',j?.jurisdiction_result || null,'No resolver record'); addKv(gdl,'Limitation',j?.limitation || null,'Jurisdiction data unavailable');
  }
  geo.append(gdl);
  const limit = el('div','notice', j?.jurisdiction_result === 'matched_geography'
    ? 'Matched geography is a current Census address-range result, not parcel or historical legal-jurisdiction certification.'
    : 'Postal city is not treated as legal jurisdiction. Applicability may be unknown until geography is resolved.');
  geo.append(limit); wrap.append(postal,geo); host.append(wrap);
}
function lookupEntries() {
  if (!state.lookups || typeof state.lookups.lookups !== 'object') return null;
  const entries = state.lookups.lookups[state.selectedAddressId];
  return entries === undefined ? [] : entries;
}
function ruleById(id) { return state.rules.find(r => r.team_rule_id === id); }
function provenanceById(id) { return state.provenance.find(p => p.team_rule_id === id); }
function renderCategories() {
  const host = $('categoryGrid'); host.replaceChildren();
  const entries = lookupEntries();
  $('resultCount').textContent = entries === null ? 'Unavailable' : `${Array.isArray(entries) ? entries.length : 0} returned`;
  if (entries === null) {
    host.append(el('div','notice danger',`${state.lookupError || 'Lookup data is unavailable for this snapshot.'} Do not interpret this as “no restrictions.”`));
    return;
  }
  if (!Array.isArray(entries)) {
    host.append(el('div','notice danger','The lookup record for this address is malformed. The UI stopped rather than inventing a result.'));
    return;
  }
  const grouped = new Map(CATEGORIES.map(([key]) => [key, []]));
  for (const entry of entries) {
    const rule = ruleById(entry.team_rule_id);
    const key = rule?.category;
    if (grouped.has(key)) grouped.get(key).push({entry,rule});
    else grouped.set('__unresolved__', [...(grouped.get('__unresolved__') || []), {entry,rule}]);
  }
  for (const [key,label] of CATEGORIES) host.append(renderCategory(key,label,grouped.get(key) || []));
  if (grouped.get('__unresolved__')?.length) host.append(renderCategory('__unresolved__','Unresolved rule references',grouped.get('__unresolved__')));
}
function renderCategory(key,label,items) {
  const section=el('section','category-section resident-card');
  const summary=ResidentLogic.summarize(items);
  const header=el('div','resident-card-header');
  header.append(el('h3','',ResidentLogic.QUESTIONS[key] || label),el('span',`status-badge ${summary.tone}`,summary.label));section.append(header);
  section.append(el('p','resident-answer',summary.answer));
  if(summary.extra)section.append(el('p','resident-qualification',summary.extra));
  const previewItem=[...items].sort((a,b)=>(a.entry.result==='applies'?0:1)-(b.entry.result==='applies'?0:1)).find(x=>x.rule&&approvedClaim(x.rule));
  if(previewItem){
    const claim=approvedClaim(previewItem.rule);const preview=el('div','reviewed-preview');
    preview.append(el('p','eyebrow',previewItem.entry.result==='applies'?'One rule that applies':'One rule to check'));
    const compact=ResidentLogic.compactClaim(claim);
    if(compact.showInline)preview.append(el('p','reviewed-answer',claim.text));
    else{
      preview.append(el('p','reviewed-answer',compact.explanation));
      const full=el('details','full-reviewed-explanation');full.append(el('summary','','Read the full reviewed explanation'),el('p','reviewed-answer',claim.text));preview.append(full);
    }
    preview.append(el('p','eligibility-qualification',ResidentLogic.eligibilityCopy(previewItem.entry)));
    const button=el('button','button','Check this answer’s homework');button.type='button';button.addEventListener('click',()=>openEvidence(previewItem.entry,previewItem.rule));preview.append(button);section.append(preview);
  }
  const details=el('details','topic-details');
  details.append(el('summary','',`See all ${items.length} ${items.length===1?'rule':'rules'} and sources`));
  details.append(el('p','topic-note','These are separate rules, not a single legal verdict. Each answer below has its own source and eligibility check.'));
  const list=el('div','rule-list');
  if(!items.length)list.append(el('p','empty-state','No result was returned for this topic. Source coverage may be incomplete.'));
  const order={applies:0,unknown:1,superseded:2,not_yet_effective:3,pending:4};
  for(const item of [...items].sort((a,b)=>(order[a.entry.result]??5)-(order[b.entry.result]??5)))list.append(renderRule(item.entry,item.rule));
  details.append(list);section.append(details);return section;
}
function approvedClaim(rule){
  return ResidentLogic.selectClaim(state.residentClaims,rule,provenanceById(rule.team_rule_id),state.ruleFingerprints.get(rule.team_rule_id));
}
function renderRule(entry, rule) {
  const card = el('article','rule-card' + (entry.conflict_flag || rule?.conflict_flag ? ' conflict' : ''));
  const top = el('div','rule-topline');
  top.append(el('span',`status-badge ${entry.result || ''}`, humanStatus(entry.result)));
  top.append(el('span',`status-badge ${rule?.status || ''}`, `Source: ${humanStatus(rule?.status || 'unavailable')}`));
  if (entry.conflict_flag || rule?.conflict_flag) top.append(el('span','status-badge','Conflict review'));
  card.append(top);
  card.append(el('h3','rule-title', rule?.title || `Missing rule record: ${entry.team_rule_id}`));
  const claim=rule?approvedClaim(rule):null;
  if(claim)card.append(el('p','rule-meaning',claim.text));
  else if(rule?.requirement)card.append(el('p','rule-meaning',rule.requirement));
  card.append(el('p','eligibility-qualification',ResidentLogic.eligibilityCopy(entry)));
  if(!claim&&rule)card.append(el('p','source-language-note','Original extracted rule summary; reviewed everyday wording is not available.'));
  const reason=el('details','eligibility-details');reason.append(el('summary','','Does this cover my situation?'));
  reason.append(el('p','rule-explanation',entry.explanation || 'We have not confirmed the eligibility details.'));card.append(reason);
  const meta = el('div','rule-meta');
  meta.append(el('span','',`Jurisdiction: ${rule?.jurisdiction || 'unavailable'}`));
  meta.append(el('span','',`Citation: ${rule?.citation || 'unavailable'}`));
  meta.append(el('span','',`Rule ID: ${entry.team_rule_id}`));
  meta.append(el('span','',`As of: ${state.lookups?.as_of || $('snapshotSelect').value || 'unavailable'}`));
  card.append(meta);
  if (!rule) card.append(el('div','notice danger','The lookup references a rule ID that is absent from rules.json. Evidence is unavailable.'));
  if (entry.conflict_flag || rule?.conflict_flag) card.append(el('div','notice danger', rule?.conflict_note || 'The engine flagged a possible conflict for human review.'));
  const actions = el('div','rule-actions');
  const btn = el('button','button','Check my homework'); btn.type='button'; btn.disabled = !rule; btn.addEventListener('click',()=>openEvidence(entry,rule)); actions.append(btn);
  card.append(actions); return card;
}
function humanStatus(s) {
  return ({applies:'Applies',unknown:'Unknown',superseded:'Superseded',not_yet_effective:'Not yet effective',pending:'Pending',in_force:'In force',failed:'Failed',unavailable:'Unavailable'})[s] || String(s || 'Unavailable').replaceAll('_',' ');
}
function evidenceDisclosure(title){
  const disclosure=el('details','evidence-box evidence-disclosure');disclosure.append(el('summary','',title));return disclosure;
}
function openEvidence(entry,rule) {
  const host = $('evidenceContent'); host.replaceChildren();
  const prov = provenanceById(rule.team_rule_id);
  const claim=approvedClaim(rule);
  if(claim){
    const receipt=el('section','evidence-box');receipt.append(el('h3','','The everyday explanation'));
    if(ResidentLogic.compactClaim(claim).showInline)receipt.append(el('p','',claim.text));
    else{const full=evidenceDisclosure('Read the full reviewed explanation');full.append(el('p','reviewed-answer',claim.text));receipt.append(full);}
    receipt.append(el('p','eligibility-qualification',ResidentLogic.eligibilityCopy(entry)));
    receipt.append(el('p','receipt-citation',rule.citation || 'Citation unavailable'));
    const passages=evidenceDisclosure('Read the exact passages behind this explanation');
    for(const evidence of claim.evidence){
      let span=null;
      if(evidence.span_id.startsWith('companion:'))span=prov?.authorized_companion_spans?.[Number(evidence.span_id.split(':')[1])];
      else if(evidence.span_id.startsWith('support:'))span=prov?.supporting_spans?.[Number(evidence.span_id.split(':')[1])];
      else span=[...(prov?.supporting_spans||[]),...(prov?.authorized_companion_spans||[])].find(x=>x.id===evidence.span_id);
      passages.append(el('p','receipt-span-id',`Supporting passage: ${evidence.span_id} · ${span?.source_doc_id || rule.source_doc_id || 'Source ID unavailable'}`),el('p','quote',evidence.text));
      const url=safeUrl(span?.source_url || rule.source_url);if(url){const link=el('a','evidence-link','Open this passage’s source');link.href=url;link.target='_blank';link.rel='noopener noreferrer';passages.append(link);}
    }
    receipt.append(passages);
    receipt.append(el('p','topic-note','Reviewed as an explanation of the rule, not a new check of your household facts.'));host.append(receipt);
  }
  const summary = el('section','evidence-box'); summary.append(el('h3','','What this rule says'));
  const dl = el('dl','kv'); addKv(dl,'Applicability',humanStatus(entry.result)); addKv(dl,'Source status',humanStatus(rule.status)); addKv(dl,'Effective date',rule.effective_date,'Not verified'); addKv(dl,'As-of date',state.lookups?.as_of || $('snapshotSelect').value); addKv(dl,'Citation',rule.citation);addKv(dl,'Source retrieved',displayDate(prov?.retrieved_at),'Not verified'); summary.append(dl);
  const visibleSource=safeUrl(rule.source_url);if(visibleSource){const a=el('a','evidence-link','Open the cited source');a.href=visibleSource;a.target='_blank';a.rel='noopener noreferrer';summary.append(a);}
  const condition=evidenceDisclosure('Read the full rule summary, coverage and exceptions');const cdl=el('dl','kv');addKv(cdl,'Requirement',rule.requirement);addKv(cdl,'Coverage',structuredValue(rule.coverage_conditions));addKv(cdl,'Exemptions',rule.exemptions);condition.append(cdl);summary.append(condition);
  host.append(summary);
  const quote = evidenceDisclosure('Read the exact rule quotation'); quote.append(el('p','quote',rule.quoted_span || 'Exact quotation unavailable.')); host.append(quote);
  const source = evidenceDisclosure('Source details and integrity');
  const sdl = el('dl','kv'); addKv(sdl,'Document ID',rule.source_doc_id); addKv(sdl,'Retrieved',displayDate(prov?.retrieved_at)); addKv(sdl,'Source hash',prov?.source_sha256); addKv(sdl,'Manifest hash',prov ? (prov.manifest_hash_match === true ? 'Matched' : prov.manifest_hash_match === false ? 'Mismatch / unresolved' : 'Unknown') : null); source.append(sdl);
  const u = safeUrl(rule.source_url); if (u) { const link=el('a','evidence-link','Open supplied source URL'); link.href=u; link.target='_blank'; link.rel='noopener noreferrer'; source.append(link); }
  if (!prov) host.append(el('div','notice danger','No provenance record was supplied for this rule. Treat source verification as unavailable.'));
  if(prov?.manifest_hash_match===false)host.append(el('p','integrity-note','Source integrity note: the captured-text hash does not match the original organizer manifest. The exact source snapshot is preserved below.'));
  host.append(source);
  if (prov?.authorized_companion_spans?.length) {
    const helper=evidenceDisclosure('Read linked companion evidence');
    for(const span of prov.authorized_companion_spans){helper.append(el('p','',span.source_doc_id || ''),el('p','quote',span.text || '')); const url=safeUrl(span.source_url);if(url){const a=el('a','evidence-link','Open companion source');a.href=url;a.target='_blank';a.rel='noopener noreferrer';helper.append(a);}}
    host.append(helper);
  }
  if (prov?.supporting_spans?.length) {
    const spans = evidenceDisclosure('Read the complete saved supporting passages');
    for (const s of prov.supporting_spans) { const p=el('p','quote',s.text || ''); spans.append(p); }
    host.append(spans);
  }
  if (prov?.skeptic) {
    const sk = evidenceDisclosure('Read the independent review note'); const dl2=el('dl','kv'); addKv(dl2,'Verdict',prov.skeptic.verdict); addKv(dl2,'Reason',prov.skeptic.reason); sk.append(dl2); host.append(sk);
  }
  const changeAction = el('section','evidence-box'); changeAction.append(el('h3','','Continue the audit trail'), el('p','rule-explanation','Review the supplied T1-T5 change outputs for the selected snapshot. The UI does not infer which test maps to this rule.')); const changeBtn=el('button','button','View supplied change cases'); changeBtn.type='button'; changeBtn.addEventListener('click',()=>{ $('evidenceDialog').close(); switchView('changes'); const tab=document.querySelector('.tab[data-view=\"changes\"]'); tab?.focus(); $('changesView').scrollIntoView({behavior:'smooth'}); }); changeAction.append(changeBtn); host.append(changeAction);
  $('evidenceTitle').textContent = rule.title || 'Check my homework'; $('evidenceDialog').showModal();
}
function renderChanges() {
  $('changeDatePill').textContent = `Snapshot ${$('snapshotSelect').value || 'unavailable'}`;
  const host = $('changeCases'); host.replaceChildren();
  if (!state.changes || typeof state.changes !== 'object') { host.append(el('div','notice danger',state.changeError || 'Change-case output is unavailable for this snapshot.')); return; }
  for (const id of ['T1','T2','T3','T4','T5']) {
    const c = state.changes[id]; const card = el('article','change-card'); card.append(el('p','eyebrow',id), el('h3','',CHANGE_TITLES[id]));
    if (!c) { card.append(el('div','notice danger','No engine output supplied for this change case.')); host.append(card); continue; }
    const affected = Array.isArray(c.affected_address_ids) ? c.affected_address_ids : [];
    const conflicts = Array.isArray(c.conflict_flag_address_ids) ? c.conflict_flag_address_ids : [];
    const stats=el('div','change-stats'); stats.append(el('span','stat',`${affected.length} affected address IDs`),el('span','stat',`${conflicts.length} conflict flags`)); card.append(stats);
    if(c.verification_status && c.verification_status !== 'pass') card.append(el('div','notice danger',`Verification: ${c.verification_status}. This change case is incomplete; an empty affected set does not establish no impact.`));
    if(c.mapping_status === 'unresolved') {card.append(el('div','notice danger','Source-rule mapping unresolved.'),el('p','rule-explanation',c.notes || ''));host.append(card);continue;}
    const unknown = Array.isArray(c.unknown_address_ids) ? c.unknown_address_ids : [];
    const selectedUnknown = unknown.includes(state.selectedAddressId);
    const potential=Array.isArray(c.potentially_affected_address_ids)?c.potentially_affected_address_ids:[];
    if(potential.length)card.append(el('div','notice',`${potential.length} IDs are potential notification dependencies, not confirmed applicable protections.`));
    const selectedAffected = affected.includes(state.selectedAddressId); const selectedConflict = conflicts.includes(state.selectedAddressId);
    card.append(el('div','selected-impact', `${state.selectedAddressId || 'Selected address'}: ${selectedAffected ? 'included in affected set' : 'not in affected set'}${selectedConflict ? ' · possible conflict flagged' : ''}${selectedUnknown ? ' · some relevant eligibility remains unknown' : ''}.`));
    card.append(el('p','rule-explanation',c.notes || 'No notes supplied.')); host.append(card);
  }
}
function metric(label,value) { const m=el('div','metric'); m.append(el('strong','',valueOrMissing(value,'—')),el('span','',label)); return m; }
function renderAudit() {
  const host=$('auditContent'); host.replaceChildren(); const r=state.report;
  $('generatedPill').textContent = r?.generated_at ? `Generated ${displayDate(r.generated_at)}` : 'Report unavailable';
  if (!r) { host.append(el('div','notice','No report.json was supplied. Validation and extraction metrics are unavailable; the UI does not fabricate them.')); return; }
  const metrics=el('div','audit-grid'); metrics.append(metric('Documents attempted',r.extraction?.documents_attempted),metric('Accepted rule records',r.extraction?.accepted_rules),metric('Model/API calls — this snapshot run',r.extraction?.api_calls),metric('Estimated API cost — this snapshot run',r.extraction?.estimated_usd == null ? null : `$${Number(r.extraction.estimated_usd).toFixed(2)}`)); host.append(metrics,el('p','section-intro','Call count and estimated cost describe this snapshot run only. They do not include earlier extraction, source, review or presentation runs.'));
  const geo=el('div','audit-block'); geo.append(el('h3','','Jurisdiction resolution')); const g=el('div','audit-grid'); g.append(metric('Addresses checked',r.jurisdictions?.checked),metric('Matched geography',r.jurisdictions?.matched),metric('Unknown geography',r.jurisdictions?.unknown)); geo.append(g); host.append(geo);
  const checks=el('div','audit-block'); checks.append(el('h3','','Validation checks')); const list=el('ul','check-list');
  const checkRows=Array.isArray(r.validation?.checks) ? r.validation.checks : [];
  if (!checkRows.length) list.append(el('li','missing','No validation checks supplied.'));
  for (const c of checkRows) { const li=el('li','check-row'); li.append(el('span',`check-status ${c.status || 'not_run'}`,c.status || 'not_run'),el('span','',`${c.name || 'Unnamed check'} - ${c.detail || 'No detail supplied.'}`)); list.append(li); } checks.append(list); host.append(checks);
  const lim=el('div','audit-block'); lim.append(el('h3','','Known limitations')); const ul=el('ul','limitations'); const ls=Array.isArray(r.limitations)?r.limitations:[]; if(!ls.length) ul.append(el('li','missing','No limitation list supplied.')); for(const item of ls) ul.append(el('li','notice',item)); lim.append(ul); host.append(lim);
  const integrity=el('div','audit-block'); integrity.append(el('h3','','Provenance integrity snapshot')); const bad=state.provenance.filter(p=>p.manifest_hash_match===false).length; const missing=state.rules.filter(rule=>!provenanceById(rule.team_rule_id)).length; const ig=el('div','audit-grid'); ig.append(metric('Provenance records',state.provenance.length),metric('Manifest hash unresolved',bad),metric('Rules missing provenance',missing)); integrity.append(ig,el('p','section-intro','Hash mismatch or missing provenance is an integrity warning, not proof that the legal text is wrong. Source completeness and legal accuracy remain separate questions.')); host.append(integrity);
}

document.addEventListener('DOMContentLoaded', init);
