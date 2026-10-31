import {DatabaseSync} from 'node:sqlite';
import {createHash} from 'node:crypto';
import {resolve} from 'node:path';

export const DB_PATH = resolve(import.meta.dirname, '../cache/evidence.sqlite');
export const dbOpen = () => new DatabaseSync(DB_PATH, {readOnly: true});
export function source(db, id) {
  const row = db.prepare('SELECT * FROM sources WHERE id=?').get(id);
  return row ? {...row, record:JSON.parse(row.record)} : null;
}
export function sha(value) {return createHash('sha256').update(typeof value === 'string' ? value : JSON.stringify(value)).digest('hex');}
const stop = new Set(('a an the and or for to of in on at by with from as is are be we our us have has had this that it its do does not no need needs want wants can could would will about they them their but more into also some any should than there these which only very one two been how who what when where all each over under without through across between per get getting new much most other work works working research company university professor project data system model method using use used develop development such including based current currently well').split(' '));
const cyr = Object.fromEntries([...'абвгдђежзијклљмнњопрстћуфхцчџш'].map((c,i)=>[c,['a','b','v','g','d','dj','e','zh','z','i','j','k','l','lj','m','n','nj','o','p','r','s','t','c','u','f','h','c','c','dz','s'][i]]));
export function tokens(s) {
  return String(s).toLowerCase().replace(/[а-яђјљњћџ]/g,c=>cyr[c]??c).normalize('NFKD').replace(/\p{M}/gu,'').match(/[a-z][a-z0-9]{2,}/g)?.filter(t=>!stop.has(t))??[];
}
export function common(a,b) {const bset=new Set(tokens(b));return [...new Set(tokens(a))].filter(t=>bset.has(t));}
export function unavailable(r) {
  return /left the university|no longer (?:at|with)|fully retired|consulting (?:engagements )?only|limits (?:his |her |external )?engagement to consulting|retired and.*not available|not available for (?:research )?project (?:leadership|coordination)/i.test(`${r.notes??''} ${r.bio??''}`);
}
export function fieldQuote(record, key) {const v=record[key];return Array.isArray(v)?v.join('; '):String(v??'');}
export function cite(row, field, subjectId) {
  return {sourceId:row.id, subjectId, kind:row.kind, field, quote:fieldQuote(row.record,field),
    recordSha256:row.sha256, file:row.file, locator:row.locator, line:row.line, url:row.url};
}
const expansions = {
  electricity:['energy','load','optimisation'], noise:['acoustic','signal'], fraud:['anomaly','detection'],
  unusual:['anomaly','detection'], seed:['agricultural','vision'], mould:['fungal','contamination'],
  crack:['fracture','fatigue'], wastewater:['water','treatment'], brain:['neuroscience'],
  defect:['inspection','vision'], secure:['security','cryptography'], forecasts:['prediction','time'],
  waste:['circular','valorisation'], battery:['electrochemical','storage'], elderly:['gerontology','accessibility']
};
export function researchTask(challengeId, view) {
  const db=dbOpen();
  try {
    const ch=source(db,challengeId);
    if(!ch||view==='no_research_sources')return {candidates:[],reason:ch?'NO_RESEARCH_EVIDENCE':'CHALLENGE_NOT_FOUND',retrieval:{query:'',documents:0,limit:60}};
    const queryTokens=[...new Set(tokens(`${ch.record.text} ${ch.record.detail??''}`))];
    // All arms receive exactly the same fixed expansion tool and FTS search.
    const terms=[...new Set([...queryTokens.slice(0,45),...queryTokens.flatMap(t=>expansions[t]??[])])].slice(0,65);
    const query=terms.map(t=>`"${t}"`).join(' OR ');
    const rows=query?db.prepare(`SELECT search.id,bm25(search) AS rank FROM search JOIN sources s ON s.id=search.id
      WHERE search MATCH ? AND s.kind IN ('researcher','publication','project','patent') ORDER BY rank LIMIT 60`).all(query):[];
    const buckets=new Map();
    for(const hit of rows)for(const link of db.prepare('SELECT researcher_id FROM links WHERE source_id=?').all(hit.id)){
      const rid=link.researcher_id;
      const b=buckets.get(rid)??{id:rid,score:0,hits:[]};
      b.score+=Math.max(0,-hit.rank);b.hits.push(hit.id);buckets.set(rid,b);
    }
    const all=[];
    for(const b of buckets.values()){
      const researcher=source(db,b.id);if(!researcher||unavailable(researcher.record))continue;
      const docs=b.hits.map(id=>source(db,id)).filter(s=>s&&s.kind!=='researcher');
      // Retrieve a linked paper as well if the profile itself carried the match.
      if(!docs.some(d=>d.kind==='publication')) {
        for(const id of researcher.record.publications??[]){const p=source(db,id);if(p?.kind==='publication')docs.push(p);if(docs.filter(d=>d.kind==='publication').length>=3)break;}
      }
      const ranked=docs.map(d=>({d,terms:common(ch.record.text+' '+ch.record.detail,fieldQuote(d.record,'title')+' '+fieldQuote(d.record,'abstract')+' '+fieldQuote(d.record,'summary'))})).sort((a,b)=>b.terms.length-a.terms.length||a.d.id.localeCompare(b.d.id));
      const chosen=ranked.slice(0,2).map(x=>x.d);
      const overlap=common(ch.record.text+' '+ch.record.detail,JSON.stringify({fields:researcher.record.fields,keywords:researcher.record.keywords})+' '+chosen.map(d=>JSON.stringify(d.record)).join(' '));
      if(chosen.length<2||overlap.length<3)continue;
      all.push({researcherId:b.id,name:researcher.record.name,fitScore:Number(b.score.toFixed(6)),technicalTerms:overlap,
        fields:researcher.record.fields,notes:researcher.record.notes,
        sources:[cite(researcher,'fields',b.id),...chosen.flatMap(d=>[cite(d,'title',b.id),...(d.record.abstract?[cite(d,'abstract',b.id)]:d.record.summary?[cite(d,'summary',b.id)]:[])])],
        evidenceSummary:chosen.map(d=>({id:d.id,title:d.record.title,abstract:(d.record.abstract??d.record.summary??'').slice(0,1100)}))});
    }
    all.sort((a,b)=>b.fitScore-a.fitScore||a.researcherId.localeCompare(b.researcherId));
    return {candidates:all.slice(0,3),reason:all.length?'CANDIDATES':'INSUFFICIENT_DIRECT_EVIDENCE',retrieval:{query,documents:rows.length,limit:60}};
  }finally{db.close();}
}
export function industryTask(challengeId,view) {
  const db=dbOpen();
  try {
    const challenge=source(db,challengeId);
    if(!challenge||view==='no_company_sources')return {reason:challenge?'NO_COMPANY_EVIDENCE':'CHALLENGE_NOT_FOUND',company:null,challenge:null};
    const company=source(db,challenge.record.company_id);
    if(!company)return {reason:'COMPANY_NOT_FOUND',company:null,challenge:null};
    return {reason:'SOURCE_FOUND',company:{id:company.id,name:company.record.name,sector:company.record.sector,
      rd_capacity:company.record.rd_capacity??company.record.r_and_d_capacity??null},
      challenge:{id:challenge.id,text:challenge.record.text,detail:challenge.record.detail},
      sources:[cite(challenge,'text',company.id),cite(challenge,'detail',company.id),cite(company,'sector',company.id)]};
  }finally{db.close();}
}
