"""Run once before a declared experiment; never silently refreeze its source."""
import hashlib
import json
import pathlib
from datetime import datetime, timezone

root=pathlib.Path(__file__).resolve().parents[1]
paths=sorted([*root.glob('src/*.mjs'),*root.glob('scripts/*.py'),*root.glob('scripts/*.mjs'),
              *root.glob('test/*.mjs'),root/'package.json',root/'package-lock.json',root/'corpus.lock.json',
              root/'evaluation/cases.json',root/'evaluation/protocol.json'])
data={'scope':'Executable source frozen for the final local Qwen3-4B comparison',
      'frozenUtc':datetime.now(timezone.utc).isoformat(),
      'files':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths}}
p=root/'evaluation/source-freeze.json';p.write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps({'files':len(paths),'sourceFreezeSha256':hashlib.sha256(p.read_bytes()).hexdigest()}))
