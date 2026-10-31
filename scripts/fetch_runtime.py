"""Download pinned public CPU inference assets, never call a hosted model API."""
import hashlib
import json
import pathlib
import tarfile
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
RUNTIME = ROOT / 'runtime'
RUNTIME.mkdir(exist_ok=True)
ENGINE_URL = 'https://github.com/ggml-org/llama.cpp/releases/download/b11756/llama-b11756-bin-ubuntu-x64.tar.gz'
ENGINE_SHA = '9def57d9e9b0149979a9ceba40896a4e2bf88c94734069a5567d2f487ceab551'
MODEL_REPO = 'Qwen/Qwen3-4B-GGUF'
MODEL_REV = 'bc640142c66e1fdd12af0bd68f40445458f3869b'
MODEL_NAME = 'Qwen3-4B-Q4_K_M.gguf'
MODEL_SHA256 = '7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5'
MODEL_URL = f'https://huggingface.co/{MODEL_REPO}/resolve/{MODEL_REV}/{MODEL_NAME}'

def download(url, dest, expected=None):
    digest = hashlib.sha256()
    if dest.exists():
        digest.update(dest.read_bytes())
    else:
        tmp = dest.with_suffix(dest.suffix + '.incomplete')
        with urllib.request.urlopen(url, timeout=60) as response, tmp.open('wb') as out:
            while block := response.read(2 * 1024 * 1024):
                digest.update(block)
                out.write(block)
        if expected and digest.hexdigest() != expected:
            tmp.unlink()
            raise RuntimeError('DOWNLOAD_HASH_MISMATCH')
        tmp.replace(dest)
    if expected and digest.hexdigest() != expected:
        raise RuntimeError('CACHED_HASH_MISMATCH')
    return {'name': dest.name, 'sha256': digest.hexdigest(), 'bytes': dest.stat().st_size, 'url': url}

engine = download(ENGINE_URL, RUNTIME / 'llama-b11756.tar.gz', ENGINE_SHA)
with tarfile.open(RUNTIME / 'llama-b11756.tar.gz') as archive:
    archive.extractall(RUNTIME / 'llama-b11756', filter='data')
# Obtain the upstream LFS content hash rather than trusting the transfer alone.
meta = json.load(urllib.request.urlopen(f'https://huggingface.co/api/models/{MODEL_REPO}/tree/{MODEL_REV}', timeout=20))
entry = next(e for e in meta if e['path'] == MODEL_NAME)
if entry['lfs']['oid'] != MODEL_SHA256: raise RuntimeError('PINNED_UPSTREAM_MODEL_METADATA_CHANGED')
model = download(MODEL_URL, RUNTIME / MODEL_NAME, MODEL_SHA256)
license_file = RUNTIME / 'Qwen-LICENSE'
license_file.unlink(missing_ok=True)
download(f'https://huggingface.co/{MODEL_REPO}/resolve/{MODEL_REV}/LICENSE', license_file)
receipt = {'engine': engine, 'model': model, 'model_revision': MODEL_REV, 'license': 'Apache-2.0', 'hosted_inference_calls': 0}
server = next((RUNTIME / 'llama-b11756').rglob('llama-server'))
receipt['engine']['binary_sha256'] = hashlib.sha256(server.read_bytes()).hexdigest()
(RUNTIME / 'assets.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt))
