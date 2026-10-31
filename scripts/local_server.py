"""Foreground CPU-only local model, isolated child environment, no service install."""
import json
import hashlib
import os
import pathlib
import shutil
import socket
import sys

root = pathlib.Path(__file__).resolve().parents[1]
assets = json.loads((root / 'runtime/assets.json').read_text())
model = root / 'runtime' / assets['model']['name']
if hashlib.sha256(model.read_bytes()).hexdigest()!=assets['model']['sha256']:
    sys.exit('LOCAL_MODEL_HASH_MISMATCH')
if shutil.disk_usage(root).free < 1024**3:
    sys.exit('INSUFFICIENT_DISK')
available = int(next(s.split()[1] for s in pathlib.Path('/proc/meminfo').read_text().splitlines() if s.startswith('MemAvailable:'))) * 1024
if available < 6 * 1024**3:
    sys.exit('INSUFFICIENT_RAM')
with socket.socket() as probe:
    try:
        probe.bind(('127.0.0.1', 18879))
    except OSError:
        sys.exit('LOCAL_PORT_ALREADY_OCCUPIED')
engine = next((root / 'runtime/llama-b11756').rglob('llama-server'))
if hashlib.sha256(engine.read_bytes()).hexdigest()!=assets['engine']['binary_sha256']:
    sys.exit('LOCAL_ENGINE_BINARY_HASH_MISMATCH')
(root / 'runtime/engine-pid.json').write_text(json.dumps({'procfsPid':int(pathlib.Path('/proc/self/stat').read_text().split()[0]),'namespacePid':os.getpid()}))
args = [str(engine), '--model', str(model), '--host', '127.0.0.1', '--port', '18879',
        '--threads', '4', '--threads-batch', '4', '--parallel', '2', '--ctx-size', '8192',
        '--n-predict', '180', '--slots', '--metrics', '--no-warmup', '--seed', '700', '--temp', '0']
os.execve(engine, args, {'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'LANG': 'C.UTF-8'})
