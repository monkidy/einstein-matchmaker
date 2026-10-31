// Counterbalanced, sequential arms on one shared bounded local engine.
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {resolve} from 'node:path';
import {runCases} from '../src/cli.mjs';
const root=resolve(import.meta.dirname,'..');
const frozen=JSON.parse(readFileSync(resolve(root,'evaluation/cases.json'),'utf8'));
const orders=[['parallel','solo','serial'],['solo','serial','parallel'],['serial','parallel','solo']];
// Six-case blocks counterbalance warm-up/order without peeking at scores.
const runs={};
for(let b=0;b<4;b++)for(const mode of orders[b%3]){
  const cases=frozen.cases.slice(b*6,b*6+6);
  const dir=resolve(root,'runs/benchmark',`block-${b+1}`,mode);
  const result=await runCases({mode,cases,outDir:dir});
  (runs[mode]??=[]).push({dir,receipt:result.receipt,results:result.results});
}
const summaries={};
for(const [mode,blocks] of Object.entries(runs)){
  const results=blocks.flatMap(b=>b.results);const rs=blocks.map(b=>b.receipt);
  summaries[mode]={cases:results.length,accepted:results.filter(r=>r.status==='ACCEPTED').length,
    naturalAccepted:results.filter(r=>r.caseId.startsWith('N')&&r.status==='ACCEPTED').length,
    controlledNegativeAbstained:results.filter(r=>r.caseId.startsWith('X')&&r.status==='ABSTAIN').length,
    modelCalls:rs.reduce((n,r)=>n+r.modelCalls,0),inputTokens:rs.reduce((n,r)=>n+r.inputTokens,0),outputTokens:rs.reduce((n,r)=>n+r.outputTokens,0),
    engineCpuTicks:rs.reduce((n,r)=>n+(r.engineCpuTicks??0),0),wallMs:rs.reduce((n,r)=>n+r.wallMs,0),peakServerSlots:Math.max(...rs.map(r=>r.peakServerSlots)),
    blocks:blocks.map(b=>b.dir.replace(root+'/',''))};
}
const pairs=Object.fromEntries(Object.entries(runs).map(([mode,blocks])=>[mode,Object.fromEntries(blocks.flatMap(b=>b.results).map(r=>[r.caseId,{status:r.status,pair:r.status==='ACCEPTED'?r.proposal.researcherId:null}]))]));
const compare=(a,b)=>frozen.cases.filter(c=>JSON.stringify(pairs[a][c.id])===JSON.stringify(pairs[b][c.id])).length;
const report={protocol:frozen.protocol,corpusSha256:frozen.corpus_sha256,arms:summaries,
  exactStatusAndPairAgreement:{parallelVsSolo:compare('parallel','solo'),parallelVsSerial:compare('parallel','serial'),total:24},
  qualityUpliftProven:false,hiddenJuryGold:false,
  conclusion:'These measurements evaluate execution, source integrity and abstention under equal ceilings. Acceptance rate is not usefulness or correctness against hidden jury gold. Do not infer a multi-agent quality gain from it.'};
mkdirSync(resolve(root,'runs/benchmark'),{recursive:true});
writeFileSync(resolve(root,'runs/benchmark/comparison.json'),JSON.stringify(report,null,2)+'\n');
console.log('BENCHMARK_REPORT '+JSON.stringify(report));
