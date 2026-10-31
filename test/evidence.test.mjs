import test from 'node:test';
import assert from 'node:assert/strict';
import {researchTask,industryTask,dbOpen,source,cite,tokens,unavailable} from '../src/evidence.mjs';
import {auditProposal} from '../src/critic.mjs';

function fixture(){
  const r=researchTask('C001-CH1').candidates[0];const i=industryTask('C001-CH1');
  return {status:'PROPOSED',researcherId:r.researcherId,companyId:i.company.id,challengeId:i.challenge.id,claims:[...i.sources,...r.sources]};
}
test('exact official evidence and authorship passes an independent source audit',()=>assert.equal(auditProposal(fixture()).valid,true));
test('invented publication id is refused',()=>{
  const p=fixture();p.claims[3].sourceId='SYN-PUB-999999';
  const a=auditProposal(p);assert.equal(a.valid,false);assert(a.reasons.some(x=>x.startsWith('INVENTED_SOURCE')));
});
test('real publication assigned to the wrong person is refused',()=>{
  const p=fixture();const db=dbOpen();const unrelated=source(db,'SYN-PUB-00001');db.close();
  p.claims[3]=cite(unrelated,'title',p.researcherId);
  const a=auditProposal(p);assert.equal(a.valid,false);assert(a.reasons.some(x=>x.startsWith('MISATTRIBUTED_RESEARCH')));
});
test('a forged quotation is refused even with a real source id',()=>{
  const p=fixture();p.claims[2].quote='Guaranteed 99.99% production accuracy';assert.equal(auditProposal(p).valid,false);
});
test('source hash changes are refused',()=>{const p=fixture();p.claims[2].recordSha256='0'.repeat(64);assert.equal(auditProposal(p).valid,false);});
test('an invented current baseline inside proposed text is still refused',()=>{
  const p=fixture();p.hypothesis={successCriterion:'Improve on the current 90% false-positive rate.'};
  const a=auditProposal(p);assert.equal(a.valid,false);assert(a.reasons.some(x=>x.startsWith('UNSUPPORTED_PRESENT_BASELINE_NUMBER')));
});
test('cross-company citation substitution is refused',()=>{const p=fixture();p.companyId='C002';assert.equal(auditProposal(p).valid,false);});
test('same-name identity cannot replace stable researcher id',()=>{const p=fixture();p.researcherId='R0001';assert.equal(auditProposal(p).valid,false);});
test('redacted evidence views cannot pass through the critic',()=>{
  for(const view of ['no_research_sources','no_company_sources'])assert.equal(auditProposal(fixture(),view).valid,false);
});
test('missing challenge and missing source views return no evidence',()=>{
  assert.equal(researchTask('C999-CH999').candidates.length,0);
  assert.equal(researchTask('C001-CH1','no_research_sources').candidates.length,0);
  assert.equal(industryTask('C001-CH1','no_company_sources').company,null);
});
test('search never resolves person identities by name and preserves stable links',()=>{
  const r=researchTask('C001-CH1');assert.equal(r.retrieval.documents,60);assert(r.candidates.length>0);
  for(const c of r.candidates)assert(c.sources.every(s=>s.subjectId===c.researcherId));
});
test('Serbian Cyrillic and diacritics are normalized only for search',()=>assert.deepEqual(tokens('моделовање modelovanje'),['modelovanje','modelovanje']));
test('explicitly left/retired-for-project profiles are excluded',()=>{
  assert(unavailable({notes:'Left the University of Novi Sad in March 2026'}));
  assert(unavailable({notes:'Fully retired; consulting engagements only.'}));
});
