import test from 'node:test';
import assert from 'node:assert/strict';
import {LocalLLM} from '../src/local-llm.mjs';

test('a healthy endpoint running the wrong local model is refused',async()=>{
  const realFetch=globalThis.fetch;
  globalThis.fetch=async(url)=>({json:async()=>String(url).endsWith('/health')?{status:'ok'}:{data:[{id:'unintended-model.gguf'}]}});
  try{await assert.rejects(new LocalLLM(()=>{}).startMonitor(),/LOCAL_MODEL_IDENTITY_MISMATCH/);}
  finally{globalThis.fetch=realFetch;}
});
