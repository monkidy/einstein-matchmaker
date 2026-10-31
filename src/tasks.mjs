import {Worker} from 'node:worker_threads';
import {auditProposal} from './critic.mjs';
import {objectSchema} from './local-llm.mjs';

function compute(role,task,trace){
  return new Promise((resolve,reject)=>{
    const worker=new Worker(new URL('./worker.mjs',import.meta.url),{workerData:{role,challengeId:task.challengeId,view:task.view}});
    worker.once('message',m=>{
      if(!m.ok){reject(Error(m.error));return;}
      trace('worker.compute',{role,caseId:task.caseId,...m.compute});resolve(m.result);
    });
    worker.once('error',reject);
    worker.once('exit',code=>{if(code)reject(Error('RETRIEVAL_WORKER_EXIT_'+code));});
  });
}
const str={type:'string',maxLength:240};
export async function executeTask(role,task,llm,trace){
  if(role==='research'){
    const result=await compute('research',task,trace);
    if(!result.candidates.length)return {...result,selected:null};
    const ids=result.candidates.map(c=>c.researcherId);
    const prompt='Select the best supported researcher for this industrial challenge. Prefer directly relevant methods. Return a provided ID or NONE. Reason: at most 20 words.\n'+JSON.stringify({challenge:task.challengeText.slice(0,1600),candidates:result.candidates.map(c=>({researcherId:c.researcherId,fields:c.fields,notes:c.notes?.slice(0,300),documents:c.evidenceSummary.map(d=>({...d,abstract:d.abstract.slice(0,450)}))}))});
    const choice=await llm.infer(role,prompt,objectSchema({researcherId:{type:'string',enum:[...ids,'NONE']},reason:str}),task.taskId);
    return {...result,selected:result.candidates.find(c=>c.researcherId===choice.researcherId)??null,modelReview:choice};
  }
  if(role==='industry'){
    const result=await compute('industry',task,trace);
    if(!result.challenge)return {...result,classification:'INSUFFICIENT'};
    const prompt='Decide whether this problem could support an applied research pilot. RESEARCH: a technical or scientific problem with a testable unknown, even if no solution or in-house research team exists yet. SERVICE: routine procurement, ordinary legal paperwork, generic marketing or administration with no research question. INSUFFICIENT: no clear problem or evidence. Write the key constraint in your own words, then a brief reason. Do not copy these instructions.\n'+JSON.stringify({company:result.company,challenge:{id:result.challenge.id,text:result.challenge.text,detail:result.challenge.detail?.slice(0,1400)}});
    const triage=await llm.infer(role,prompt,objectSchema({classification:{type:'string',enum:['RESEARCH','SERVICE','INSUFFICIENT']},constraint:str,reason:str}),task.taskId);
    return {...result,...triage};
  }
  if(role==='writer'){
    const {research,industry}=task;
    if(!research.selected||industry.classification!=='RESEARCH')return {status:'ABSTAIN',reason:!research.selected?(research.reason==='CANDIDATES'?'MODEL_FOUND_NO_SUPPORTED_MATCH':research.reason):'INDUSTRY_'+industry.classification};
    const selected=research.selected;
    const prompt='Design a bounded joint research pilot for this exact company problem and researcher. Give one specific research question, one proposed intervention with a transparent baseline chosen for the experiment, and the primary measurable metric. Do not invent current baseline numbers, existing resources, funding, time commitments, consent or demonstrated results. All actions are FUTURE proposals. Whole answer: at most 60 words.\n'+JSON.stringify({company:industry.company,challenge:{...industry.challenge,detail:industry.challenge.detail?.slice(0,1400)},researcher:{id:selected.researcherId,fields:selected.fields,evidence:selected.evidenceSummary.map(d=>({...d,abstract:d.abstract.slice(0,650)}))}});
    const generated=await llm.infer(role,prompt,objectSchema({researchQuestion:str,experiment:str,metric:str}),task.taskId);
    const hypothesis={researchQuestion:generated.researchQuestion,experiment:generated.experiment,metric:generated.metric,
      successCriterion:`Proposed gate: measure ${generated.metric} on a frozen held-out test set against a transparent control agreed at scoping. Pre-register the minimum useful improvement and uncertainty bounds with both partners. No present baseline value is assumed.`};
    return {status:'PROPOSED',challengeId:task.challengeId,companyId:industry.company.id,companyName:industry.company.name,
      researcherId:selected.researcherId,researcherName:selected.name,claims:[...industry.sources,...selected.sources],
      hypothesis:{...hypothesis,label:'PROPOSED_EXPERIMENT_NOT_ESTABLISHED_FACT'},
      plan:[{phase:'Scoping',deliverable:'Confirm exact technical problem, data access, candidate availability, ethics, IP and baseline with both partners.'},
        {phase:'Pilot',deliverable:'Run the proposed baseline and candidate method on a held-out test set; record failure cases, latency, uncertainty and resources.'},
        {phase:'Decision',deliverable:'Independent review with the company: continue only if pre-agreed measures improve; publish only with both partners consent.'}],
      limitations:['Official dataset is synthetic; no real collaboration or consent established.','Researchers are proposed for task fit; no score of personal worth.','Company resources and researcher availability require confirmation.','No funding, budget, supervisor, data permission or production gain is asserted.']};
  }
  if(role==='critic'){
    const audit=auditProposal(task.proposal,task.view);
    trace('critic.source_audit',{caseId:task.caseId,...audit});
    if(!audit.valid)return {accepted:false,audit,semantic:{compatible:false,reason:'Source gate refused before semantic review.'}};
    const p=task.proposal;
    // A different agent receives evidence and proposal; no writer hidden state or ranking score.
    const prompt='Independently assess this proposed research pilot. Company and research statements below are verified quotations. Accept a plausible technical link between the methods and company problem. Future experiments may be new proposals. Any asserted CURRENT baseline value, resource, historical result or capability must be supported by the quotations. Reject invented facts, an unrelated method, a routine non-research service or an impossible measurement. Return false if uncertain. Reason: at most 25 words.\n'+JSON.stringify({companyProblem:p.claims.filter(c=>c.kind==='challenge').map(c=>({field:c.field,quote:c.quote.slice(0,1600)})),researcherEvidence:p.claims.filter(c=>c.subjectId===p.researcherId).map(c=>({id:c.sourceId,field:c.field,quote:c.quote.slice(0,1300)})),proposal:p.hypothesis});
    const semantic=await llm.infer(role,prompt,objectSchema({compatible:{type:'boolean'},reason:str}),task.taskId);
    return {accepted:semantic.compatible===true,audit,semantic};
  }
  throw Error('UNKNOWN_ROLE');
}
