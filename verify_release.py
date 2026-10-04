"""Read-only release integrity gate. Passing is not a legal-accuracy certification."""
import argparse, collections, hashlib, json
from pathlib import Path

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def verify(root):
    ui=root/'ui'; data=ui/'data'; problems=[]
    def check(ok, message):
        if not ok: problems.append(message)
    rules=read(data/'rules.json'); addresses=read(data/'addresses.json')
    rulemap={r['team_rule_id']:r for r in rules}; ids={a['address_id'] for a in addresses}
    check(len(ids)==len(addresses)==500,'Expected exactly 500 unique supplied addresses')
    check(len(rulemap)==len(rules),'Duplicate rule IDs')
    manifest=read(data/'manifest.json'); summaries={}
    for snapshot in manifest['snapshots']:
        path=ui/snapshot['lookups_url']; obj=read(path)
        if obj.get('format')=='lookup-table-1':
            from compact_transport import expand
            obj=expand(obj)
        check(obj['as_of']==snapshot['as_of'],'Snapshot date mismatch: '+path.name)
        check(set(obj['lookups'])==ids,'Incomplete address coverage: '+path.name)
        counts=collections.Counter()
        for address_id, rows in obj['lookups'].items():
            seen=set()
            for row in rows:
                rid=row['team_rule_id']; check(rid in rulemap,'Unknown rule '+rid)
                check(rid not in seen,'Duplicate lookup rule '+rid+' at '+address_id); seen.add(rid)
                status=row['result']; counts[status]+=1
                check(status in {'applies','unknown','pending','not_yet_effective','superseded'},'Invalid lookup status')
                if rid in rulemap:
                    check(rulemap[rid]['status']!='failed','Failed measure in lookup '+rid)
                    check(not(status in {'applies','superseded'} and rulemap[rid]['status']=='pending'),'Pending measure shown as current '+rid)
        summaries[obj['as_of']]=dict(counts)
    changes=read(data/'changes.json'); check(set(changes)=={'T1','T2','T3','T4','T5'},'Missing change cases')
    for case, obj in changes.items():
        for key, values in obj.items():
            if key.endswith('address_ids') and isinstance(values,list):
                check(set(values)<=ids,'Unknown change address ID: '+case+'/'+key)
    check(not changes['T5'].get('affected_address_ids'),'Failed T5 measure must affect no addresses')
    # Credentials must never enter the static publication bundle.
    for path in ui.rglob('*'):
        if path.is_file():
            check(path.name not in {'.env','.env.local'},'Environment file in public UI')
            if path.suffix.lower() in {'.json','.js','.html','.txt','.md'}:
                check('sk-ant-' not in path.read_text(encoding='utf-8-sig'),'Possible API key in public UI: '+str(path.relative_to(ui)))
    return {'gate':'release-integrity-1','passed':not problems,'problems':problems,
            'rules':len(rules),'addresses':len(addresses),'snapshot_status_counts':summaries,
            'limits':['Integrity checks do not measure legal accuracy.','A change test pass does not confirm all property eligibility.','Browser interaction and public deployment require separate verification.'],
            'hashes':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(ui.rglob('*')) if p.is_file()}}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=Path(__file__).parent); parser.add_argument('--report',type=Path); args=parser.parse_args()
    report=verify(args.root); payload=json.dumps(report,ensure_ascii=False,indent=2)
    if args.report:
        if args.report.exists(): raise FileExistsError('Preserve existing reports; choose a new report path')
        args.report.write_text(payload,encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='hashes'},indent=2))
    raise SystemExit(0 if report['passed'] else 1)
if __name__=='__main__':main()
