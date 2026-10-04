import copy, json, tempfile, unittest
from pathlib import Path
from verify_release import verify

class IntegrityTests(unittest.TestCase):
    def fixture(self,root):
        data=root/'ui'/'data';data.mkdir(parents=True)
        addresses=[{'address_id':f'A{i:04}'} for i in range(500)]
        rules=[{'team_rule_id':'R1','status':'in_force'}]
        lookup={'as_of':'2026-10-01','lookups':{a['address_id']:[{'team_rule_id':'R1','result':'applies'}] for a in addresses}}
        files={'addresses.json':addresses,'rules.json':rules,'lookups.json':lookup,'manifest.json':{'snapshots':[{'as_of':'2026-10-01','lookups_url':'data/lookups.json'}]},'changes.json':{f'T{i}':{'affected_address_ids':[]} for i in range(1,6)}}
        for name,value in files.items(): (data/name).write_text(json.dumps(value),encoding='utf-8')
        return data,files
    def run_case(self,edit):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); data, files=self.fixture(root); edit(data,files)
            return verify(root)
    def test_complete_integrity(self):
        self.assertTrue(self.run_case(lambda d,f:None)['passed'])
    def test_missing_address_snapshot_fails(self):
        def edit(d,f):
            f['lookups.json']['lookups'].pop('A0000');(d/'lookups.json').write_text(json.dumps(f['lookups.json']),encoding='utf-8')
        self.assertFalse(self.run_case(edit)['passed'])
    def test_pending_cannot_be_current(self):
        def edit(d,f):
            f['rules.json'][0]['status']='pending';(d/'rules.json').write_text(json.dumps(f['rules.json']),encoding='utf-8')
        self.assertFalse(self.run_case(edit)['passed'])
    def test_failed_change_cannot_notify(self):
        def edit(d,f):
            f['changes.json']['T5']['affected_address_ids']=['A0001'];(d/'changes.json').write_text(json.dumps(f['changes.json']),encoding='utf-8')
        self.assertFalse(self.run_case(edit)['passed'])
    def test_credentials_cannot_publish(self):
        self.assertFalse(self.run_case(lambda d,f:(d/'.env').write_text('SAMPLE=placeholder',encoding='utf-8'))['passed'])
if __name__=='__main__':unittest.main()
