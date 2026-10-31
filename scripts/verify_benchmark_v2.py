"""Independent aggregate audit of all 72 arm-case outputs on one source freeze."""
import hashlib
import json
import pathlib
import sys
from collections import defaultdict
from independent_verify import main as verify_block

ROOT=pathlib.Path(__file__).resolve().parents[1]
BASE=ROOT/'runs/benchmark-v2'
FROZEN=json.loads((ROOT/'evaluation/cases.json').read_text())
FREEZE=ROOT/'evaluation/source-freeze.json'
FREEZE_DIGEST=hashlib.sha256(FREEZE.read_bytes()).hexdigest()
EXPECTED=[c['id'] for c in FROZEN['cases']]
ORDER=[['parallel','solo','serial'],['solo','serial','parallel'],['serial','parallel','solo']]
reports=[]
receipts=[]
results_by_mode=defaultdict(list)
receipt_fingerprints=[]

for block in range(1,5):
    expected_cases=EXPECTED[(block-1)*6:block*6]
    for mode in ORDER[(block-1)%3]:
        d=BASE/f'block-{block}'/mode
        receipt_path=d/'receipt.json'
        if not receipt_path.is_file():sys.exit(f'BENCHMARK_INCOMPLETE:{block}/{mode}')
        receipt=json.loads(receipt_path.read_text())
        if receipt['mode']!=mode or receipt['cases']!=6 or receipt['caseIds']!=expected_cases:
            sys.exit(f'CASE_OR_ARM_IDENTITY_CHANGED:{block}/{mode}')
        if receipt.get('sourceFreezeSha256')!=FREEZE_DIGEST:
            sys.exit(f'UNEQUAL_SOURCE_FREEZE:{block}/{mode}')
        report=verify_block(d)
        if report['result']!='PASS' or report['cases']!=6:
            sys.exit(f'INVALID_BLOCK:{block}/{mode}')
        results=json.loads((d/'results.json').read_text())
        results_by_mode[mode].extend(results)
        reports.append(report)
        receipts.append(receipt)
        identity=[receipt[k] for k in ('corpusSha256','protocolSha256','sourceFreezeSha256')]
        identity.extend((receipt['assets']['modelSha256'],receipt['assets']['engineSha256'],json.dumps(receipt['resourceCeilings'],sort_keys=True)))
        receipt_fingerprints.append(tuple(identity))
if len(reports)!=12 or len(set(receipt_fingerprints))!=1:
    sys.exit('UNEQUAL_RESOURCES_OR_SOURCE')
for mode in ('solo','serial','parallel'):
    rs=results_by_mode[mode]
    if len(rs)!=24 or sorted(x['caseId']for x in rs)!=sorted(EXPECTED):
        sys.exit(f'INCOMPLETE_ARM:{mode}')
    by_id={x['caseId']:x for x in rs}
    if any(by_id[c['id']]['status']!=c['expected'] for c in FROZEN['cases'] if 'expected' in c):
        sys.exit(f'NEGATIVE_CONTROL_FAILED:{mode}')
    arm_reports=[rep for rep in reports if rep['mode']==mode]
    if sum(r['negative_controls_abstained'] for r in arm_reports)!=6:
        sys.exit(f'NEGATIVE_CONTROL_COUNT_WRONG:{mode}')
if not any(r['concurrency']['parallel_proven'] for r in reports if r['mode']=='parallel'):
    sys.exit('NO_REAL_CONCURRENT_INFERENCE_PROVEN')
for mode in ('solo','serial'):
    if any(r['concurrency']['parallel_proven'] for r in reports if r['mode']==mode):
        sys.exit('INVALID_SERIAL_CONTROL')

def arm_summary(mode):
    rr=[r for r in receipts if r['mode']==mode]
    return {
        'cases':24,'accepted':sum(x['status']=='ACCEPTED' for x in results_by_mode[mode]),
        'natural_accepted':sum(x['status']=='ACCEPTED' and x['caseId'].startswith('N') for x in results_by_mode[mode]),
        'controlled_negative_abstained':6,
        'model_calls':sum(r['modelCalls']for r in rr),
        'input_tokens':sum(r['inputTokens']for r in rr),'output_tokens':sum(r['outputTokens']for r in rr),
        'cpu_ticks':sum(r['engineCpuTicks']or 0 for r in rr),
        'wall_ms':sum(r['wallMs']for r in rr),
        'peak_server_slots':max(r['peakServerSlots']for r in rr)
    }

def decision(mode,case_id):
    x=next(r for r in results_by_mode[mode] if r['caseId']==case_id)
    p=x.get('proposal')or{}
    return [x['status'],p.get('researcherId') if x['status']=='ACCEPTED' else None]
comparison={a+'Vs'+b:sum(decision(a,c)==decision(b,c) for c in EXPECTED) for a,b in [('parallel','solo'),('parallel','serial'),('solo','serial')]}
summary={
 'result':'PASS','verified_blocks':12,'case_arm_evaluations':72,
 'sourceFreezeSha256':FREEZE_DIGEST,'same_corpus_protocol_model_engine_source_and_budget':True,
 'same_24_cases_per_arm':True,'negative_abstentions_per_arm':6,
 'source_claims_independently_verified':sum(r['source_claims_independently_verified']for r in reports),
 'actual_model_responses':sum(r['verified_actual_model_responses']for r in reports),
 'real_mozaik_and_server_concurrency':True,'arms':{mode:arm_summary(mode)for mode in ('solo','serial','parallel')},
 'exact_status_pair_agreement':comparison,'quality_uplift_proven':False,'hidden_jury_gold_available':False,
 'caveat':'Equal resource ceilings and source provenance validated. No independent gold usefulness improvement is proven.'
}
path=BASE/'independent-verification.json'
tmp=path.with_suffix('.json.tmp')
tmp.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
tmp.replace(path)
print(json.dumps(summary))
