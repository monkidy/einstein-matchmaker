// Pure deterministic plan: never use scored results to choose arm order.
export const ARM_ORDERS=[['parallel','solo','serial'],['solo','serial','parallel'],['serial','parallel','solo']];
export function makePlan(cases){
  if(!Array.isArray(cases)||cases.length!==24)throw Error('INVALID_FROZEN_CASE_COUNT');
  const ids=cases.map(x=>x.id);
  if(ids.some(x=>typeof x!=='string')||new Set(ids).size!==24)throw Error('INVALID_FROZEN_CASE_IDS');
  const plan=[];
  for(let block=0;block<4;block++){
    const six=cases.slice(block*6,block*6+6);
    for(const mode of ARM_ORDERS[block%3])plan.push(Object.freeze({block:block+1,mode,cases:six}));
  }
  return Object.freeze(plan);
}
export function checkpointDecision({exists,hasReceipt,independentPass}){
  if(!exists)return 'START_NEW';
  if(hasReceipt)return independentPass?'REUSE_VERIFIED':'REFUSE_BAD_RECEIPT';
  return 'QUARANTINE_INCOMPLETE';
}
