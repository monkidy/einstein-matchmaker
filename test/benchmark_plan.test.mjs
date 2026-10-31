import test from 'node:test';
import assert from 'node:assert/strict';
import {makePlan,ARM_ORDERS,checkpointDecision} from '../scripts/benchmark_plan.mjs';
const cases=Array.from({length:24},(_,i)=>({id:'N'+String(i+1).padStart(2,'0')}));
test('deterministic 12 six-case counterbalanced blocks',()=>{
 const p=makePlan(cases);assert.equal(p.length,12);
 assert.deepEqual(p.map(b=>b.mode),[...ARM_ORDERS[0],...ARM_ORDERS[1],...ARM_ORDERS[2],...ARM_ORDERS[0]]);
 for(const mode of ['solo','serial','parallel']){
   const ids=p.filter(x=>x.mode===mode).flatMap(x=>x.cases.map(c=>c.id));
   assert.deepEqual(ids,cases.map(c=>c.id));
 }
});
test('refuse changed or duplicate frozen cases',()=>{
 assert.throws(()=>makePlan(cases.slice(1)),/INVALID_FROZEN_CASE_COUNT/);
 assert.throws(()=>makePlan([...cases.slice(0,23),cases[0]]),/INVALID_FROZEN_CASE_IDS/);
});
test('never skips unverified checkpoint and quarantines incomplete',()=>{
 assert.equal(checkpointDecision({exists:false,hasReceipt:false,independentPass:false}),'START_NEW');
 assert.equal(checkpointDecision({exists:true,hasReceipt:false,independentPass:false}),'QUARANTINE_INCOMPLETE');
 assert.equal(checkpointDecision({exists:true,hasReceipt:true,independentPass:false}),'REFUSE_BAD_RECEIPT');
 assert.equal(checkpointDecision({exists:true,hasReceipt:true,independentPass:true}),'REUSE_VERIFIED');
});
