"""Run an app command alongside its ephemeral model in the same network namespace."""
import json
import os
import pathlib
import signal
import subprocess
import sys
import time
import urllib.request

root = pathlib.Path(__file__).resolve().parents[1]
command = sys.argv[1:] or ['node', 'src/cli.mjs', 'demo']
env = {k:v for k,v in os.environ.items() if not any(x in k.upper() for x in ['API_KEY','TOKEN','SECRET','PASSWORD','CREDENTIAL'])}
env['MOZAIK_API_KEY']=''
env['EINSTEIN_LOCAL_ONLY']='1'
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
log = (root / 'runtime/server.log').open('w')
server = subprocess.Popen([sys.executable, str(root / 'scripts/local_server.py')], cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT)
try:
    for _ in range(120):
        if server.poll() is not None:
            raise RuntimeError('LOCAL_ENGINE_EXITED: inspect runtime/server.log')
        try:
            if json.load(opener.open('http://127.0.0.1:18879/health', timeout=1)).get('status')=='ok': break
        except (OSError, ValueError): pass
        time.sleep(.25)
    else: raise RuntimeError('LOCAL_ENGINE_HEALTH_TIMEOUT')
    env['EINSTEIN_ENGINE_PID']=str(json.loads((root / 'runtime/engine-pid.json').read_text())['procfsPid'])
    result = subprocess.run(command, cwd=root, env=env)
    sys.exit(result.returncode)
finally:
    server.terminate()
    try: server.wait(timeout=10)
    except subprocess.TimeoutExpired:
        server.kill();server.wait(timeout=5)
    log.close()
