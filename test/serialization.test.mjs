import test from 'node:test';
import assert from 'node:assert/strict';
import {LocalLLM} from '../src/local-llm.mjs';
const ok=(content)=>({ok:true,json:async()=>content});
function harness({serialized=true,slotProvider=()=>[{id:0,is_processing:false},{id:1,is_processing:false}],reply=null}={}){
  const trace=[];let now=0;let active=0;let peak=0;let starts=0;
  const read=async(url)=>{
    if(url.endsWith('/slots'))return ok(slotProvider());
    if(url.endsWith('/health'))return ok({status:'ok'});
    if(url.endsWith('/v1/models'))return ok({data:[{id:'mock.gguf'}]});
    if(url.endsWith('/v1/chat/completions')){
      active++;starts++;peak=Math.max(peak,active);
      if(reply)await reply({active,starts});
      else await new Promise(resolve=>setImmediate(resolve));
      active--;
      return ok({choices:[{message:{content:'{}'},finish_reason:'stop'}],usage:{prompt_tokens:1,completion_tokens:1}});
    }
    throw Error('UNEXPECTED_ENDPOINT:'+url);
  };
  const llm=new LocalLLM((type,data)=>trace.push({type,...data}),{
    serialized,modelName:'mock.gguf',fetchImpl:read,now:()=>now,sleep:async(ms)=>{now+=ms;await Promise.resolve();}});
  return {llm,trace,metrics:()=>({peak,starts,now})};
}
test('RED control: concurrently invoked solo inference is strictly serialized',async()=>{
  const h=harness();
  await Promise.all([h.llm.infer('research','p',{},'r1'),h.llm.infer('industry','p',{},'i1')]);
  assert.equal(h.metrics().peak,1);
  assert.equal(h.metrics().starts,2);
  assert.equal(h.trace.filter(x=>x.type==='server.drain.ready').length,2);
});
test('parallel arm still permits simultaneous requests',async()=>{
  let release;let started=0;
  const gate=new Promise(resolve=>release=resolve);
  const h=harness({serialized:false,reply:async()=>{started++;if(started===2)release();await gate;}});
  await Promise.all([h.llm.infer('research','p',{},'r1'),h.llm.infer('industry','p',{},'i1')]);
  assert.equal(h.metrics().peak,2);
});
test('drain refuses busy engine then succeeds only after three clean samples',async()=>{
  let n=0;
  const h=harness({slotProvider:()=>{n++;return n<=3 ? [{id:0,is_processing:true},{id:1,is_processing:false}]:[{id:0,is_processing:false},{id:1,is_processing:false}];}});
  await h.llm.requireDrained();
  assert.equal(n,6);
  assert.equal(h.trace.filter(x=>x.type==='server.drain.busy').length,3);
});
for(const [name,response] of [
  ['missing slots',[]],
  ['partial slots',[{id:0,is_processing:false}]],
  ['bad Boolean',[{id:0,is_processing:false},{id:1,is_processing:null}]],
  ['duplicate ids',[{id:0,is_processing:false},{id:0,is_processing:false}]],
  ['unknown payload',{slots:[]}],
])test('fail closed on '+name,async()=>{
  const h=harness({slotProvider:()=>response});
  await assert.rejects(h.llm.requireDrained(),/SERIAL_ENGINE_NOT_DRAINED/);
  assert.equal(h.trace.some(x=>x.type==='server.drain.ready'),false);
  assert.equal(h.metrics().starts,0);
});
test('serialized arm waits for any stale active server inference before first trace',async()=>{
  let reads=0;
  const h=harness({slotProvider:()=>{reads++;return [{id:0,is_processing:reads<=2},{id:1,is_processing:false}];}});
  await h.llm.startMonitor();
  await h.llm.stopMonitor();
  assert.ok(reads>=5);
  assert.ok(h.trace.some(x=>x.type==='server.drain.ready'));
});
test('the parallel arm also waits at an arm boundary, without serializing its own calls',async()=>{
  let reads=0;
  const h=harness({serialized:false,slotProvider:()=>{reads++;return [{id:0,is_processing:reads<=1},{id:1,is_processing:false}];}});
  await h.llm.startMonitor();
  await h.llm.stopMonitor();
  assert.ok(reads>=4);
});
test('client abort followed by a still-busy server cannot start a new solo call',async()=>{
  let serverBusy=0;let launched=0;
  const h=harness({
    slotProvider:()=>[{id:0,is_processing:serverBusy>0},{id:1,is_processing:false}],
    reply:async()=>{
      launched++;
      if(launched===1){serverBusy=2;throw Error('CLIENT_TIMEOUT');}
    }
  });
  await assert.rejects(h.llm.infer('research','p',{},'r1'),/CLIENT_TIMEOUT/);
  // The modeled server is still processing even though the client has aborted.
  // Drain cannot fake a success, so no second HTTP request occurs.
  await assert.rejects(h.llm.infer('industry','p',{},'i1'),/SERIAL_ENGINE_NOT_DRAINED/);
  assert.equal(launched,1);
});
