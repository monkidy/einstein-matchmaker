"""Verify every completed benchmark block and compare equal-ceiling arms."""
import json
import pathlib
import sys
from independent_verify import main, concurrency

root=pathlib.Path(__file__).resolve().parents[1]
base=root/'runs/benchmark'
blocks=sorted(base.glob('block-*/*/receipt.json'))
if len(blocks)!=12:sys.exit('BENCHMARK_INCOMPLETE: expected twelve six-case arm blocks')
reports=[main(p.parent) for p in blocks]
comparison=json.loads((base/'comparison.json').read_text())
receipts=[json.loads(p.read_text()) for p in blocks]
fingerprints={tuple(r[k] for k in ['corpusSha256','protocolSha256'])+(r['assets']['modelSha256'],r['assets']['engineSha256'],json.dumps(r['resourceCeilings'],sort_keys=True)) for r in receipts}
if len(fingerprints)!=1:sys.exit('UNEQUAL_RESOURCES_OR_SOURCE')
frozen=json.loads((root/'evaluation/cases.json').read_text())
for mode in ['solo','serial','parallel']:
    observed=[case for r in receipts if r['mode']==mode for case in r['caseIds']]
    if sorted(observed)!=sorted(c['id']for c in frozen['cases']):sys.exit('CASE_SET_DIFFERS')
    report=[r for r in reports if r['mode']==mode]
    if sum(r['negative_controls_abstained']for r in report)!=6:sys.exit('NEGATIVE_CONTROLS_FAILED')
if not any(r['concurrency']['parallel_proven']for r in reports if r['mode']=='parallel'):sys.exit('NO_REAL_PARALLEL_EXECUTION')
summary={'result':'PASS','verified_blocks':len(blocks),'same_corpus_protocol_model_engine_and_resource_ceilings':True,
         'same_24_cases_per_arm':True,'negative_abstentions_per_arm':6,
         'verified_source_claims':sum(r['source_claims_independently_verified']for r in reports),
         'actual_model_responses':sum(r['verified_actual_model_responses']for r in reports),
         'real_mozaik_and_server_concurrency':True,'comparison':comparison,
         'quality_uplift_proven':False,'natural_no_match_gold_available':False}
(base/'independent-verification.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary))
