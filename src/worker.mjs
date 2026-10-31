import {parentPort,workerData} from 'node:worker_threads';
import {researchTask,industryTask} from './evidence.mjs';
const started=performance.timeOrigin+performance.now();
try {
  const result=(workerData.role==='research'?researchTask:industryTask)(workerData.challengeId,workerData.view);
  parentPort.postMessage({ok:true,result,compute:{start:started,end:performance.timeOrigin+performance.now(),thread:'worker'}});
}catch(error){parentPort.postMessage({ok:false,error:error.message});}
