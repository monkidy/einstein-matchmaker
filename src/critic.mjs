// This module independently reads raw indexed records. It never trusts writer verdicts.
import {dbOpen,source,fieldQuote,common,unavailable} from './evidence.mjs';

export function auditProposal(proposal,view) {
  const db=dbOpen();const reasons=[];
  try {
    if(!proposal||proposal.status!=='PROPOSED')return {valid:false,reasons:['NO_PROPOSAL']};
    const researcher=source(db,proposal.researcherId),company=source(db,proposal.companyId),challenge=source(db,proposal.challengeId);
    if(!researcher||researcher.kind!=='researcher')reasons.push('RESEARCHER_NOT_FOUND');
    if(!company||company.kind!=='company')reasons.push('COMPANY_NOT_FOUND');
    if(!challenge||challenge.kind!=='challenge')reasons.push('CHALLENGE_NOT_FOUND');
    if(challenge?.record.company_id!==company?.id)reasons.push('WRONG_CHALLENGE_COMPANY');
    if(researcher&&unavailable(researcher.record))reasons.push('RESEARCHER_UNAVAILABLE_FOR_PROJECT');
    if(view==='no_research_sources'||view==='no_company_sources')reasons.push('EVIDENCE_REDACTED_IN_VIEW');
    if(!Array.isArray(proposal.claims)||proposal.claims.length<4)reasons.push('TOO_FEW_GROUNDED_CLAIMS');
    const documents=new Set();let exact=0;
    for(const claim of proposal.claims??[]){
      const s=source(db,claim.sourceId);
      if(!s){reasons.push('INVENTED_SOURCE:'+claim.sourceId);continue;}
      if(s.sha256!==claim.recordSha256)reasons.push('SOURCE_HASH_MISMATCH:'+s.id);
      if(s.file!==claim.file||s.locator!==claim.locator||s.url!==claim.url)reasons.push('SOURCE_LOCATOR_MISMATCH:'+s.id);
      if(!claim.quote||fieldQuote(s.record,claim.field)!==claim.quote)reasons.push('QUOTE_MISMATCH:'+s.id);
      else exact++;
      if(claim.subjectId===proposal.researcherId){
        if(s.kind==='researcher'){
          if(s.id!==proposal.researcherId)reasons.push('WRONG_PERSON_PROFILE');
        }else {
          const people=(s.kind==='publication'?s.record.authors:s.kind==='project'?s.record.participants:s.kind==='patent'?s.record.inventors:[])??[];
          if(!people.some(p=>p.researcher_id===proposal.researcherId))reasons.push('MISATTRIBUTED_RESEARCH:'+s.id);
          documents.add(s.id);
        }
      }else if(claim.subjectId===proposal.companyId){
        if(s.kind==='challenge'&&s.record.company_id!==proposal.companyId)reasons.push('WRONG_COMPANY_CHALLENGE');
        else if(s.kind==='company'&&s.id!==proposal.companyId)reasons.push('WRONG_COMPANY');
        else if(!['company','challenge','company_page'].includes(s.kind))reasons.push('WRONG_COMPANY_SOURCE_TYPE');
      }else reasons.push('UNKNOWN_CLAIM_SUBJECT');
    }
    if(documents.size<2)reasons.push('TOO_FEW_INDEPENDENT_RESEARCH_DOCUMENTS');
    // Proposal thresholds may be invented as hypotheses; asserted present values may not.
    const narrative=Object.values(proposal.hypothesis??{}).filter(x=>typeof x==='string').join(' ');
    const companyQuotes=(proposal.claims??[]).filter(c=>c.subjectId===proposal.companyId).map(c=>c.quote).join(' ').replace(/\s+/g,' ').toLowerCase();
    const assertedNumbers=[...narrative.matchAll(/\b(?:current|currently|existing|observed|reported|previous)\b[^.!?]{0,70}?([0-9]+(?:[.,][0-9]+)?\s*(?:%|ms|kg|kw|kwh|euros?|hours?|days?|years?)?)/gi)];
    for(const match of assertedNumbers)if(!companyQuotes.includes(match[1].toLowerCase()))reasons.push('UNSUPPORTED_PRESENT_BASELINE_NUMBER:'+match[1]);
    if(researcher&&challenge){
      const full=[researcher.record.fields,researcher.record.keywords,...[...documents].map(id=>source(db,id)?.record)];
      if(common(challenge.record.text+' '+challenge.record.detail,JSON.stringify(full)).length<3)reasons.push('WEAK_TECHNICAL_CONNECTION');
    }
    return {valid:reasons.length===0,reasons:[...new Set(reasons)],claimsChecked:proposal.claims?.length??0,exactQuotes:exact,independentResearchDocuments:documents.size,
      scope:'Exact attribution and quotes plus conservative lexical fit; not a proof of real-world feasibility.'};
  }finally{db.close();}
}
