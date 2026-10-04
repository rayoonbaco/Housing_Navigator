"""Lossless web transport, preserving challenge exports separately."""
import argparse,json
from pathlib import Path
def compact(value):
    dictionaries=[[],[],[]];indexes=[{}, {}, {}];rows={}
    for ident,records in value['lookups'].items():
        out=[]
        for record in records:
            if set(record)!={'team_rule_id','result','explanation','conflict_flag'} or type(record['conflict_flag']) is not bool:raise ValueError('Unexpected canonical record fields')
            row=[]
            for i,key in enumerate(['team_rule_id','result','explanation']):
                text=record[key]
                if text not in indexes[i]:indexes[i][text]=len(dictionaries[i]);dictionaries[i].append(text)
                row.append(indexes[i][text])
            row.append(record['conflict_flag']);out.append(row)
        rows[ident]=out
    return {'format':'lookup-table-1','as_of':value['as_of'],'rule_ids':dictionaries[0],'statuses':dictionaries[1],'explanations':dictionaries[2],'rows':rows}
def expand(value):
    return {'as_of':value['as_of'],'lookups':{ident:[{'team_rule_id':value['rule_ids'][r[0]],'result':value['statuses'][r[1]],'explanation':value['explanations'][r[2]],'conflict_flag':r[3]} for r in records] for ident,records in value['rows'].items()}}
def main():
    p=argparse.ArgumentParser();p.add_argument('--ui',type=Path,required=True);a=p.parse_args()
    for path in (a.ui/'data').glob('lookups*.json'):
        original=json.loads(path.read_text(encoding='utf-8-sig'))
        if original.get('format')=='lookup-table-1':continue
        result=compact(original)
        if expand(result)!=original:raise ValueError('Round-trip changed canonical content')
        before=path.stat().st_size;path.write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')),encoding='utf-8');print(path.name,before,'->',path.stat().st_size)
if __name__=='__main__':main()
