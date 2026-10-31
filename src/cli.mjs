// No hosted-provider credentials enter Mozaik or model children.
for(const k of Object.keys(process.env))if(/API_KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL/i.test(k))delete process.env[k];
process.env.MOZAIK_API_KEY='';
const {mkdirSync,writeFileSync,readFileSync,appendFileSync}=await import('node:fs');
const {resolve}=await import('node:path');
const {createTeam}=await import('./runtime.mjs');
const {LocalLLM}=await import('./local-llm.mjs');
const {dbOpen,source,sha}=await import('./evidence.mjs');
const root=resolve(import.meta.dirname,'..');

export async function runCases({mode='parallel',cases,outDir}) {
  if(!['solo','serial','parallel'].includes(mode))throw Error('INVALID_MODE');
  mkdirSync(outDir,{recursive:true});const tracefile=resolve(outDir,'trace.jsonl');writeFileSync(tracefile,'');
  let seq=0;
  const trace=(event,data)=>appendFileSync(tracefile,JSON.stringify({seq:++seq,event,at:Date.now(),...data})+'\n');
  const llm=new LocalLLM(trace,{serialized:mode!=='parallel'});await llm.startMonitor();
  const team=createTeam(mode,llm,trace);const results=[];const start=Date.now();
  const assets=JSON.parse(readFileSync(resolve(root,'runtime/assets.json'),'utf8'));
  const protocol=JSON.parse(readFileSync(resolve(root,'evaluation/protocol.json'),'utf8'));
  const db=dbOpen();const corpus=db.prepare('SELECT value FROM metadata WHERE key=?').get('corpus_sha256').value;db.close();
  const cpuStart=engineCpu();
  try{
    for(const test of cases){
      const begin=Date.now(),callsBefore=llm.calls,tokensBefore={input:llm.inputTokens,output:llm.outputTokens};
      const temp=dbOpen();const ch=source(temp,test.challenge_id);temp.close();
      // Expected negative labels are never passed to any agent.
      const base={caseId:test.id,challengeId:test.challenge_id,view:test.view,challengeText:ch?`${ch.record.text}\n${ch.record.detail??''}`:'UNKNOWN CHALLENGE'};
      trace('case.start',{caseId:test.id,challengeId:test.challenge_id,mode});
      let research,industry;
      if(mode==='parallel') [research,industry]=await Promise.all([team.call('research',base),team.call('industry',base)]);
      else {research=await team.call('research',base);industry=await team.call('industry',base);}
      let draft,critic;
      if(research.error||industry.error){draft={status:'ABSTAIN',reason:research.error??industry.error};critic={accepted:false,audit:{valid:false,reasons:['UPSTREAM_EXECUTION_REFUSED']}};}
      else {
        draft=await team.call('writer',{...base,research,industry});
        critic=draft.status==='PROPOSED'?await team.call('critic',{...base,proposal:draft}):{accepted:false,audit:{valid:false,reasons:[draft.reason??'WRITER_REFUSED']}};
      }
      const status=critic.accepted===true?'ACCEPTED':'ABSTAIN';
      const result={caseId:test.id,challengeId:test.challenge_id,view:test.view??null,status,
        reason:status==='ACCEPTED'?'INDEPENDENT_SOURCE_AND_PLAUSIBILITY_GATE_PASS':draft.reason||critic.audit?.reasons?.join(',')||critic.semantic?.reason||'CRITIC_REFUSED',
        proposal:draft.status==='PROPOSED'?draft:null,critic,shortlist:research.candidates?.map(c=>c.researcherId)??[],
        selection:research.modelReview??null,industryReview:industry.reason??null,industryClassification:industry.classification??null,
        retrieval:research.retrieval??null,metrics:{wallMs:Date.now()-begin,modelCalls:llm.calls-callsBefore,inputTokens:llm.inputTokens-tokensBefore.input,outputTokens:llm.outputTokens-tokensBefore.output}};
      results.push(result);trace('case.end',{caseId:test.id,status,reason:result.reason,...result.metrics});
      writeFileSync(resolve(outDir,'results.json'),JSON.stringify(results,null,2)+'\n');
      console.log(JSON.stringify({mode,caseId:test.id,status,pair:result.proposal?result.proposal.companyId+'/'+result.proposal.researcherId:null,ms:result.metrics.wallMs,modelCalls:result.metrics.modelCalls,reason:result.reason}));
    }
  } finally {team.close();await llm.stopMonitor();}
  const cpuEnd=engineCpu();
  const receipt={schema:'EINSTEIN_PROOF_RUN_V1',startedUtc:new Date(start).toISOString(),finishedUtc:new Date().toISOString(),mode,
    runtime:'@mozaik-ai/core@4.2.0',agents:team.agents,corpusSha256:corpus,protocolSha256:sha(JSON.stringify(protocol)),
    sourceFreezeSha256:sha(readFileSync(resolve(root,'evaluation/source-freeze.json'),'utf8')),
    assets:{modelSha256:assets.model.sha256,engineSha256:assets.engine.sha256,modelRevision:assets.model_revision},
    caseIds:cases.map(c=>c.id),cases:results.length,accepted:results.filter(r=>r.status==='ACCEPTED').length,
    abstained:results.filter(r=>r.status==='ABSTAIN').length,modelCalls:llm.calls,inputTokens:llm.inputTokens,outputTokens:llm.outputTokens,
    wallMs:Date.now()-start,engineCpuTicks:cpuEnd!==null&&cpuStart!==null?cpuEnd-cpuStart:null,
    peakServerSlots:Math.max(0,...llm.samples.map(s=>s.slots.length)),
    sharedStateResults:team.state.results.size,peerEvents:team.state.peerEvents.length,
    resultsSha256:sha(readFileSync(resolve(outDir,'results.json'),'utf8')),traceSha256:sha(readFileSync(tracefile,'utf8')),
    paidProviderCalls:0,hostedInferenceCalls:0,publication:false,submission:false,fictionalDataset:true,
    resourceCeilings:{callsPerCase:4,outputTokensPerCall:180,inputCharsPerCall:14000,cpuThreads:4,localServerSlots:2}};
  writeFileSync(resolve(outDir,'receipt.json'),JSON.stringify(receipt,null,2)+'\n');
  writeFileSync(resolve(outDir,'proposals.md'),renderProposals(results));
  console.log('RUN_RECEIPT '+JSON.stringify(receipt));return {receipt,results};
}
function engineCpu(){
  try{const s=readFileSync(`/proc/${process.env.EINSTEIN_ENGINE_PID}/stat`,'utf8');const f=s.slice(s.lastIndexOf(')')+2).split(' ');return Number(f[11])+Number(f[12]);}catch{return null;}
}
function renderProposals(results){
  let s='# EINSTEIN Proof — private review\n\nAll people, companies and publications below are fictional organizer data. Proposed experiments are hypotheses, not demonstrated results.\n\n';
  for(const r of results){
    s+=`## ${r.caseId} · ${r.challengeId} · ${r.status}\n\n`;
    const p=r.proposal;if(!p||r.status!=='ACCEPTED'){s+=`Explicit abstention: ${r.reason}.\n\n`;continue;}
    s+=`**Pair:** ${p.researcherName} (${p.researcherId}) × ${p.companyName} (${p.companyId}).\n\n`;
    s+=`**Research question — proposed:** ${p.hypothesis.researchQuestion}\n\n**Experiment — proposed:** ${p.hypothesis.experiment}\n\n**Success criterion — proposed:** ${p.hypothesis.successCriterion}\n\n`;
    s+='### Source-controlled facts\n\n';
    for(const c of p.claims)s+=`- [${c.sourceId}](${c.url}), ${c.locator}, field \`${c.field}\`: ${c.quote.replace(/\n/g,' ')}\n`;
    s+='\n### Work plan — to agree with both partners\n\n';
    for(const step of p.plan)s+=`- **${step.phase}:** ${step.deliverable}\n`;
    s+=`\n**Independent critic:** ${r.critic.semantic.reason}\n\n**Limits:** ${p.limitations.join(' ')}\n\n`;
  }return s;
}
if(process.argv[1]&&resolve(process.argv[1])===resolve(import.meta.filename)){
  const command=process.argv[2]??'demo';
  const frozen=JSON.parse(readFileSync(resolve(root,'evaluation/cases.json'),'utf8'));
  if(command==='demo'){
    const cases=['C001-CH1','C149-CH1','C150-CH2'].map((id,i)=>({id:'DEMO'+(i+1),challenge_id:id}));
    cases.push({id:'DEMO_NEG',challenge_id:'C001-CH1',view:'no_research_sources'});
    await runCases({mode:'parallel',cases,outDir:resolve(root,'runs/demo')});
  }else if(command==='run'){
    const mode=process.argv[3]??'parallel';
    await runCases({mode,cases:frozen.cases,outDir:resolve(process.argv[4]??resolve(root,'runs',mode))});
  }else throw Error('USAGE: cli.mjs demo | run [solo|serial|parallel] [output-directory]');
}
