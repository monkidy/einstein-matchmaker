# Submission text

Ready to paste into the organizer's submission form. Rule 5 asks for a project name, a
repository the judges can access, a description, and an explanation of how the agents run
concurrently.

---

## Project name

**EINSTEIN Matchmaker, Proof or Abstain**

## Track

EINSTEIN Matchmaker (solo entry)

## Repository

`https://github.com/monkidy/einstein-matchmaker`

Everything the judges need is in `README.md`: a five-command setup from a clean folder, the
claim-status table saying exactly what is proven and what is not, and the commands that
redraw every measurement from the raw traces.

---

## Live deployment

`https://monkidy.github.io/einstein-matchmaker/`, which carries the demo video, the measured result and the commands to reproduce.

## Demo video

`https://monkidy.github.io/einstein-matchmaker/film/einstein_matchmaker_demo.mp4`, 1:33, narration by a synthetic voice, disclosed on the end card.

## Description

A company posts a technical challenge. The system has to find the researcher who can
actually address it, and the hard part is not finding a candidate, it is refusing the ones
that only look right.

Four Mozaik agents work on the challenge at the same time. A research profiler and an
industry analyst run independently and genuinely concurrently on one local Qwen3-4B model. A
writer consumes both results from shared Mozaik state. Then an independent critic, running in
a fresh agent and model context with its own source-audit path, decides whether the proposal
survives.

It survives only if every factual claim is a quotation of a source field, carrying the record
hash, the file, the JSON pointer and an immutable official URL, and only if the candidate has
two independently linked research documents. Otherwise the system abstains, out loud, with a
reason. In the demo run, one case is accepted with full citations and one deliberately
stripped case is refused with `NO_RESEARCH_EVIDENCE`.

The whole thing runs on CPU, with no hosted model API and no API key, the receipt records
`hosted_inference_calls: 0`. The model, the inference engine and the organizer's corpus are
each pinned by content hash and verified before use, and the served model is checked against
the expected one before any case runs.

What makes it more than a demo: it ships the measurements that would expose it. Twenty-eight
adversarial tests cover fabricated citations, misattributed authorship, altered hashes, and
false concurrency. An equal-resource comparison pits one agent against four, sequential
against concurrent, at identical ceilings for model calls, tokens, retrieved documents and
CPU threads, and the README states up front that no quality advantage is claimed, because
the natural challenges have no organizer answer key. If the measurements show no advantage,
the repository says so.

A system that cannot refuse cannot be trusted when it accepts.

---

## How the agents run concurrently

Two HTTP requests in flight do not prove that two agents are thinking at the same time. So
this entry does not claim concurrency from the client side. It proves it from the inference
server.

The research agent and the industry agent are separate Mozaik agents driven independently
through `runLoop` on the same runtime. Their retrieval runs on worker threads; both then
perform real local model inference against a llama.cpp server started with two slots. The
trace samples the server's slot table throughout the run, recording which slots are actually
in `PROCESSING` state.

For a run to be accepted, the independent verifier requires all three of:

1. two distinct Mozaik producer IDs,
2. overlapping task intervals, and
3. at least one timestamp inside that overlap at which two distinct inference slots are both
   in `PROCESSING` state.

A negative control deletes all server-slot evidence and must be rejected, and is.

Measured on the demo run with the final model, from `evidence/concurrency-demo-qwen3-4b.json`:

- 2018 slot samples taken during the run
- **807 of them show two slots processing at the same instant, 40.0 % of observed compute**
- 98.4 seconds of genuine concurrency across 2 windows, out of 246.5 seconds observed
- maximum simultaneous slots: 2, which is the server's full capacity

The comparison arms are held to the opposite standard, which is the part that is easy to fake
and hard to prove: the sequential and single-agent arms must show a mutex plus three
consecutive clean readings of both slots idle before each call and at every arm boundary. An
arm that claims to be sequential cannot quietly overlap, and a client abort while the server
is still busy cannot start a new call.

`evidence/concurrency-demo-qwen3-4b.svg` draws this from the trace alone, green where two
slots are busy, with no interpolated or decorative element. Any judge can regenerate it:

```bash
python3 scripts/concurrency_figure.py runs/demo evidence/concurrency-demo-qwen3-4b
```

---

## Notes for the judges

- `README.md` has a claim-status table: every claim is marked PROVEN, pointed at its
  verification file, or marked NOT CLAIMED. Nothing is asserted beyond what a file shows.
- `evaluation/DEVELOPMENT_DISCLOSURE.md` records what was tried and rejected, including two
  model candidates whose negative results are kept rather than deleted, and which cases were
  inspected during development.
- Prior work is disclosed: the Mozaik SDK setup and the organizer dataset existed before the
  event; the source in this repository was authored after the 30 October kickoff.
- `LICENSE` grants the organizers, the judging panel and any reviewer the right to read,
  build, run, test and reproduce, and to present the project as the rules provide.
