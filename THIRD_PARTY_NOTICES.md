# Third-party notices

This repository contains no third-party binaries, model weights or dataset files. Each
component below is fetched from its own owner at run time and verified against a pinned
content hash before use. Nothing here asserts a redistribution licence over any of them.

## Agent runtime

**Mozaik** (`@mozaik-ai/core`), MIT licence. Installed from the public npm registry and
pinned by `package-lock.json`. Required by the event: this entry runs on Mozaik and uses
its loop, shared state and peer bus.

No Mozaik Cloud pairing is performed and no API key is used. The runtime prints a notice
that telemetry is disabled; that is the intended state for this entry.

## Inference engine

**llama.cpp**, release `b11756`, MIT licence (ggml-org/llama.cpp).

- Archive: `llama-b11756-bin-ubuntu-x64.tar.gz`
- Archive SHA-256: `9def57d9e9b0149979a9ceba40896a4e2bf88c94734069a5567d2f487ceab551`
- Server binary SHA-256: `d04baf3c29546141804b03519f61639167f3b441a060a4f657277518d613c285`
- Source: https://github.com/ggml-org/llama.cpp/releases/tag/b11756

Fetched by `scripts/fetch_runtime.py`, which refuses a hash mismatch.

## Language model

**Qwen3-4B**, GGUF quantization `Q4_K_M`, Apache-2.0 licence (Qwen team, Alibaba Cloud).

- File: `Qwen3-4B-Q4_K_M.gguf`, 2497280256 bytes
- SHA-256: `7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5`
- Repository revision: `bc640142c66e1fdd12af0bd68f40445458f3869b`
- Source: https://huggingface.co/Qwen/Qwen3-4B-GGUF

The Qwen licence file is downloaded alongside the weights and kept next to them as
`runtime/Qwen-LICENSE`. The model runs entirely on the local CPU; `hosted_inference_calls`
is `0` in `evidence/runtime-assets.json`.

Two earlier model candidates were evaluated and rejected on triage quality, and their
negative results are retained under `runs/`: **Qwen3-0.6B** (Q8_0) and
**Qwen2.5-1.5B-Instruct** (Q4_K_M), both Apache-2.0, both from the official Qwen
repositories. See `evaluation/DEVELOPMENT_DISCLOSURE.md`.

## Dataset

The **official EINSTEIN Matchmaker track corpus** supplied by the organizers for this
event, at revision `4fb99b3749adf0d10b5977089ff4c73f4f522240`. All people, companies,
publications, projects and patents in it are fictional.

- Fetched and hash-checked by `scripts/prepare_data.py`
- File hashes recorded in `corpus.lock.json`, LF-normalized so that a Windows checkout
  does not change dataset identity
- Corpus content hash observed at install: `bc3b57e31909eb667c0127b931c9b519ca7caffb6e4aedd33796645a55789224`
- Record counts observed: 1047 researchers, 1823 projects, 111 patents, 153 companies,
  489 challenges, 10779 publications, 917 company pages

The corpus is referenced and downloaded, never redistributed from this repository. Rights
in it remain with the organizers.

## Platform

Node.js 24.22.1 and Python 3 are expected to be present. They are not vendored here.
Remaining npm dependencies are those recorded in `package-lock.json` and installed with
`npm ci --ignore-scripts`; their own licences apply.
