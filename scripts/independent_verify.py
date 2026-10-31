"""Independent offline verifier: raw organizer files, not the application's DB/scorer."""
import argparse
import hashlib
import json
import pathlib
import sys
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[1]

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def canonical(value): return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))

def concurrency(events, mode, require_parallel=True):
    answers={e['taskId']:e for e in events if e['event']=='mozaik.answer'}
    requests={e['taskId']:e for e in events if e['event']=='task.start'}
    spans=[e for e in events if e['event']=='task.end']
    overlap=[]
    for i,a in enumerate(spans):
        for b in spans[i+1:]:
            if a['caseId']==b['caseId'] and {a['role'],b['role']}=={'research','industry'} and max(a['start'],b['start'])<min(a['end'],b['end']):
                aa,ab=answers.get(a['taskId']),answers.get(b['taskId'])
                if not aa or not ab or aa['agentId']==ab['agentId']: continue
                server=[e for e in events if e['event']=='server.slots' and max(a['start'],b['start'])<=e['at']<=min(a['end'],b['end'])
                        and len({s['id'] for s in e['slots'] if s['processing']})>=2]
                if server: overlap.append(a['caseId'])
    parallel_proven=bool(overlap)
    if mode=='parallel' and require_parallel and not parallel_proven: raise ValueError('NO_SERVER_AND_DISTINCT_MOZAIK_AGENT_CONCURRENCY')
    if mode in ('solo','serial') and any(len(e.get('slots',[]))>1 for e in events if e['event']=='server.slots'):
        raise ValueError('SERIAL_CONTROL_HAS_PARALLEL_INFERENCE')
    return {'parallel_proven':parallel_proven,'case_ids':sorted(set(overlap)),
            'distinct_agents':len({a['agentId'] for a in answers.values()}),'mozaik_answers':len(answers)}

def main(run):
    run=pathlib.Path(run)
    receipt=json.loads((run/'receipt.json').read_text())
    results=json.loads((run/'results.json').read_text())
    events=[json.loads(line) for line in (run/'trace.jsonl').read_text().splitlines()]
    if receipt['traceSha256']!=digest(run/'trace.jsonl') or receipt['resultsSha256']!=digest(run/'results.json'):
        raise ValueError('RUN_RECEIPT_HASH_MISMATCH')
    if receipt.get('sourceFreezeSha256'):
        freeze=ROOT/'evaluation/source-freeze.json'
        if digest(freeze)!=receipt['sourceFreezeSha256']:raise ValueError('SOURCE_FREEZE_CHANGED')
        for name,expected_hash in json.loads(freeze.read_text())['files'].items():
            if digest(ROOT/name)!=expected_hash:raise ValueError('EXECUTABLE_SOURCE_CHANGED:'+name)
    lock=json.loads((ROOT/'corpus.lock.json').read_text())
    for name,m in lock['files'].items():
        raw=(ROOT/'corpus'/name).read_bytes().replace(b'\r\n',b'\n')
        if hashlib.sha256(raw).hexdigest()!=m['sha256_lf']: raise ValueError('CORPUS_CHANGED:'+name)
    raw_sources={}
    for group in ['researchers','companies','projects','patents']:
        for n,r in enumerate(json.loads((ROOT/f'corpus/data/{group}.json').read_text())[group]):
            raw_sources[r['id']]={'record':r,'locator':f'/{group}/{n}','file':f'data/{group}.json'}
            if group=='companies':
                for j,c in enumerate(r['challenges']):raw_sources[c['id']]={'record':{**c,'company_id':r['id']},'locator':f'/companies/{n}/challenges/{j}','file':'data/companies.json'}
    for name in ['publications','company-pages']:
        for n,line in enumerate((ROOT/f'corpus/data/{name}.jsonl').read_text().splitlines(),1):
            r=json.loads(line);key=r['id'] if name=='publications' else f'{r["company_id"]}-PAGE-L{n}'
            raw_sources[key]={'record':r,'locator':'/','file':f'data/{name}.jsonl','line':n}
    checked=0
    for result in results:
        if result['status']!='ACCEPTED':continue
        if not result['critic'].get('accepted') or not result['critic']['audit']['valid']:raise ValueError('ACCEPTED_WITHOUT_CRITIC')
        p=result['proposal']
        for c in p['claims']:
            src=raw_sources[c['sourceId']];r=src['record'];v=r[c['field']]
            quote='; '.join(v) if isinstance(v,list) else str(v)
            if quote!=c['quote']:raise ValueError('BAD_QUOTE')
            if hashlib.sha256(canonical(r).encode()).hexdigest()!=c['recordSha256']:raise ValueError('RECORD_HASH_CHANGED')
            if src['file']!=c['file'] or src['locator']!=c['locator']:raise ValueError('BAD_LOCATOR')
            url=f'https://github.com/jigjoy-ai/einstein-matchmaker-data/blob/{lock["revision"]}/{src["file"]}'
            if src.get('line'):url+=f'#L{src["line"]}'
            if c['url']!=url:raise ValueError('BAD_CITATION_URL')
            if c['subjectId']==p['researcherId'] and c['kind']!='researcher':
                people=r.get('authors',r.get('participants',r.get('inventors',[])))
                if not any(a.get('researcher_id')==p['researcherId'] for a in people):raise ValueError('MISATTRIBUTED_PUBLICATION')
            checked+=1
    frozen=json.loads((ROOT/'evaluation/cases.json').read_text())
    expected={c['id']:c['expected'] for c in frozen['cases'] if 'expected'in c}
    negatives=[r for r in results if r['caseId'] in expected]
    if any(r['status']!=expected[r['caseId']] for r in negatives):raise ValueError('NEGATIVE_CONTROL_FALSE_ACCEPTANCE')
    task_cases={e['taskId']:e['caseId'] for e in events if e['event']=='task.start'}
    llm_roles={}
    for e in events:
        if e['event']=='llm.request': llm_roles.setdefault(task_cases[e['taskId']],set()).add(e['role'])
    eligible_for_overlap=any({'industry','research'}<=roles for roles in llm_roles.values())
    c=concurrency(events,receipt['mode'],require_parallel=eligible_for_overlap)
    # Known-bad instrumentation controls. Forged client overlap alone cannot pass.
    no_server=[e for e in events if e['event']!='server.slots']
    bad_rejected=False
    try: concurrency(no_server,'parallel')
    except ValueError:bad_rejected=True
    if not bad_rejected:raise ValueError('CLIENT_ONLY_FALSE_CONCURRENCY_ACCEPTED')
    forged_agents=[{**e,'agentId':'same-agent'} if e['event']=='mozaik.answer' else e for e in events]
    same_agent_refused=False
    try:concurrency(forged_agents,'parallel')
    except ValueError:same_agent_refused=True
    if not same_agent_refused:raise ValueError('ONE_AGENT_FALSE_CONCURRENCY_ACCEPTED')
    answers={e['taskId']:e for e in events if e['event']=='mozaik.answer'}
    peers=[e for e in events if e['event']=='mozaik.peer']
    if any(e['listenerId']==e['producerId'] or answers.get(e['taskId'],{}).get('agentId')!=e['producerId'] for e in peers):
        raise ValueError('PEER_MESSAGE_SPOOFED')
    inputs=[e for e in events if e['event']=='llm.request']
    outputs=[e for e in events if e['event']=='llm.response']
    if any(len(e['prompt'])>14000 or e['maxTokens']>180 for e in inputs):raise ValueError('MODEL_BUDGET_EXCEEDED')
    bycase=Counter()
    starts={e['taskId']:e for e in events if e['event']=='task.start'}
    for e in inputs:bycase[starts[e['taskId']]['caseId']]+=1
    if any(n>4 for n in bycase.values()):raise ValueError('CALL_BUDGET_EXCEEDED')
    report={'result':'PASS','mode':receipt['mode'],'cases':len(results),'accepted':sum(r['status']=='ACCEPTED'for r in results),
            'source_claims_independently_verified':checked,'negative_controls':len(negatives),'negative_controls_abstained':sum(r['status']=='ABSTAIN'for r in negatives),
            'concurrency':c,'client_only_false_concurrency_rejected':bad_rejected,'same_agent_false_concurrency_rejected':same_agent_refused,'verified_peer_events':len(peers),'verified_actual_model_responses':len(outputs),
            'hidden_jury_gold_available':False,'usefulness_uplift_proven':False,'verifier':'raw-file Python implementation independent of Node app/SQLite scorer'}
    (run/'independent-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report));return report

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('run',nargs='?',default=str(ROOT/'runs/demo'));args=parser.parse_args()
    try:main(args.run)
    except (ValueError,KeyError,OSError) as exc:print('VERIFY_REFUSED: '+str(exc),file=sys.stderr);sys.exit(1)
