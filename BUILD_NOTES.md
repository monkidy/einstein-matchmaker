# Build notes

**Event window.** The EINSTEIN Matchmaker implementation in this repository was authored
after the official kickoff on 30 October 2026. What existed beforehand and is disclosed as
prior work: the generic Mozaik SDK setup, and the organizer's official track corpus, which
is fetched rather than vendored. Rule 4 allows pre-existing frameworks, libraries and
boilerplate; the substance here was built during the event.

**What was built.** Four real Mozaik agents (research profiler, industry analyst, proposal
writer, independent critic), an FTS5 evidence index over the official corpus, source and
identity gates, a conservative abstention path, a separate raw-file verifier that
reconstructs records without the application's SQLite index, and an equal-resource
comparison between one agent and four, sequential and concurrent.

**Tests.** 28 adversarial tests pass: 14 covering evidence, citation, authorship and model
identity, and 14 covering serialization, slot drain, fail-closed behaviour on malformed slot
payloads, and resumption. Replayed on the compute host on 31 October 2026.

**Model selection, including what failed.** Two earlier candidates were tried and rejected
on semantic triage quality, Qwen3-0.6B (Q8_0), then Qwen2.5-1.5B-Instruct (Q4_K_M). Their
negative results are kept under `runs/`, not deleted, because a rejected candidate is
evidence about the selection. The final model is Qwen3-4B-Q4_K_M, pinned by content hash and
checked against the served model before any case runs.

**Read these before trusting any run.**

- `evaluation/DEVELOPMENT_DISCLOSURE.md`, which cases were inspected during development,
  which model each run used, and why `runs/development-initial/` cannot certify the final
  version.
- `CHECKPOINT.json`, point-in-time state, with its own caveats listed.
- `runs/benchmark-v2/independent-verification.json`, the live verdict on the comparison. It
  overrides any narrative in the documentation. The comparison is complete only at
  `result = PASS` with `case_arm_evaluations = 72`.

**Known limit to report, not to hide.** Under the per-case deadline of 120 s with a ceiling
of 4 model calls on 4 CPU threads, some cases abstain because they ran out of time rather
than because evidence was missing. Timeout abstentions and evidence-based refusals are
different things and are reported separately.

**Status.** Public repository opened on 31 October 2026 with the author's explicit approval,
as the event requires a judge-accessible repository. No message has been sent to any
researcher or company; the dataset is fictional. No hosted model API and no paid provider
were used at any point: `hostedInferenceCalls` and `paidProviderCalls` are both `0` in every
run receipt.
