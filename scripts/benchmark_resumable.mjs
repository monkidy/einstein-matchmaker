/**
 * Private Qwen3-4B benchmark with fixed plan and durable, source-locked recovery.
 * Run ONLY inside the pinned local runtime:
 *   python3 scripts/run_local.py node scripts/benchmark_resumable.mjs
 * No GitHub/OVH keys; this script makes no model calls outside LocalLLM.
 */
import {existsSync,readFileSync,mkdirSync,renameSync,writeFileSync} from 'node:fs';
import {resolve,join} from 'node:path';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {runCases} from '../src/cli.mjs';
import {makePlan,checkpointDecision} from './benchmark_plan.mjs';
const root=resolve(import.meta.dirname,'..');
const output=resolve(root,'runs/benchmark-v2');
const freezeFile=resolve(root,'evaluation/source-freeze.json');
const sha=b=>createHash('sha256').update(b).digest('hex');
const frozen=JSON.parse(readFileSync(resolve(root,'evaluation/cases.json'),'utf8'));
const plan=makePlan(frozen.cases);
mkdirSync(output,{recursive:true});
const freeze=JSON.parse(readFileSync(freezeFile,'utf8'));
const sourceFreezeSha256=sha(readFileSync(freezeFile));
function verifySource(){
 for(const [path,expected] of Object.entries(freeze.files)){
   const source=resolve(root,path);
   if(!existsSync(source)||sha(readFileSync(source))!==expected)throw Error('SOURCE_FREEZE_CHANGED:'+path);
 }
}
function check(runDir){
  const result=spawnSync('python3',[resolve(root,'scripts/independent_verify.py'),runDir],
    {cwd:root,encoding:'utf8',timeout:180000,maxBuffer:4*1024*1024});
  if(result.status!==0)throw Error('INDEPENDENT_BLOCK_REFUSED:'+runDir+':'+(result.stderr||'').slice(0,800));
  const report=JSON.parse(readFileSync(join(runDir,'independent-verification.json'),'utf8'));
  if(report.result!=='PASS'||report.cases!==6)throw Error('INDEPENDENT_BLOCK_NOT_PASS');
  return report;
}
function receiptMatches(runDir,item){
 const r=JSON.parse(readFileSync(join(runDir,'receipt.json'),'utf8'));
 if(r.mode!==item.mode||r.cases!==6||r.sourceFreezeSha256!==sourceFreezeSha256||
     JSON.stringify(r.caseIds)!==JSON.stringify(item.cases.map(x=>x.id)))throw Error('CHECKPOINT_IDENTITY_CHANGED');
 return r;
}
function safeSave(path,value){
 const temp=path+'.tmp';writeFileSync(temp,JSON.stringify(value,null,2)+'\n');renameSync(temp,path);
}
const summary=[];
verifySource();
for(const item of plan){
 verifySource();
 const outDir=join(output,`block-${item.block}`,item.mode);
 const state=checkpointDecision({exists:existsSync(outDir),hasReceipt:existsSync(join(outDir,'receipt.json')),
   independentPass:existsSync(join(outDir,'independent-verification.json'))});
 let status;
 if(state==='REFUSE_BAD_RECEIPT'){
   // A receipt is not trusted just because a JSON file exists. Re-check it.
   receiptMatches(outDir,item);check(outDir);status='RECHECKED_VERIFIED';
 }else if(state==='REUSE_VERIFIED'){
   receiptMatches(outDir,item);check(outDir);status='REUSED_VERIFIED';
 }else{
   if(state==='QUARANTINE_INCOMPLETE'){
     const q=join(output,'quarantine');mkdirSync(q,{recursive:true});
     const target=join(q,`block-${item.block}-${item.mode}-${Date.now()}`);
     renameSync(outDir,target);
     console.log('QUARANTINED_PARTIAL',target);
   }
   mkdirSync(outDir,{recursive:true});
   const result=await runCases({mode:item.mode,cases:item.cases,outDir});
   if(result.receipt.sourceFreezeSha256!==sourceFreezeSha256)throw Error('NEW_RECEIPT_SOURCE_FREEZE_MISMATCH');
   receiptMatches(outDir,item);check(outDir);status='NEW_VERIFIED';
 }
 summary.push({block:item.block,mode:item.mode,caseIds:item.cases.map(x=>x.id),status});
 safeSave(join(output,'progress.json'),{status:'INCOMPLETE',verified_blocks:summary.length,
    total_blocks:12,sourceFreezeSha256,completed:summary});
 console.log('BLOCK_VERIFIED',item.block,item.mode,summary.length,'/12');
}
const verify=spawnSync('python3',[resolve(root,'scripts/verify_benchmark_v2.py')],
 {cwd:root,encoding:'utf8',timeout:900000,maxBuffer:12*1024*1024});
if(verify.status!==0)throw Error('BENCHMARK_FINAL_INDEPENDENT_REFUSED:'+(verify.stderr||verify.stdout).slice(0,1500));
const final=JSON.parse(readFileSync(join(output,'independent-verification.json'),'utf8'));
if(final.result!=='PASS'||final.verified_blocks!==12)throw Error('BENCHMARK_FINAL_NOT_COMPLETE');
safeSave(join(output,'progress.json'),{status:'PASS',verified_blocks:12,total_blocks:12,sourceFreezeSha256,completed:summary});
console.log('BENCHMARK_72_VERIFIED',JSON.stringify({verified_blocks:final.verified_blocks,quality_uplift_proven:false}));
