# EINSTEIN Proof — private review

All people, companies and publications below are fictional organizer data. Proposed experiments are hypotheses, not demonstrated results.

## DEMO1 · C001-CH1 · ACCEPTED

**Pair:** Krisztina Kiss (R1008) × ArmaturaSec d.o.o. (C001).

**Research question — proposed:** How can we detect unusual behavior in Modbus and BACnet networks without labelled attack data?

**Experiment — proposed:** Use a machine learning model trained on traffic archives and hardware to detect anomalies, with a baseline for normal behavior.

**Success criterion — proposed:** The model flags anomalies with a false positive rate below 10% and a response time of less than 100ms.

### Source-controlled facts

- [C001-CH1](https://github.com/jigjoy-ai/einstein-matchmaker-data/blob/4fb99b3749adf0d10b5977089ff4c73f4f522240/data/companies.json), /companies/0/challenges/0, field `text`: We need to detect unusual behaviour on Modbus and BACnet networks without labelled attack data — our clients have never been breached (or don't know it), so we have zero examples of malicious traffic and supervised classifiers are useless to us.
- [C001](https://github.com/jigjoy-ai/einstein-matchmaker-data/blob/4fb99b3749adf0d10b5977089ff4c73f4f522240/data/companies.json), /companies/0, field `sector`: Cybersecurity
- [R1008](https://github.com/jigjoy-ai/einstein-matchmaker-data/blob/4fb99b3749adf0d10b5977089ff4c73f4f522240/data/researchers.json), /researchers/1007, field `fields`: Industrial cybersecurity; Network traffic analysis; Machine learning and statistical modelling; Industrial control systems
- [SYN-PUB-10477](https://github.com/jigjoy-ai/einstein-matchmaker-data/blob/4fb99b3749adf0d10b5977089ff4c73f4f522240/data/publications.jsonl#L10477), /, field `title`: Anomaly Detection in Industrial Control Systems
- [SYN-PUB-10482](https://github.com/jigjoy-ai/einstein-matchmaker-data/blob/4fb99b3749adf0d10b5977089ff4c73f4f522240/data/publications.jsonl#L10482), /, field `title`: Comparing Score Aggregation Strategies for Multi-Protocol ICS Anomaly Detection

### Work plan — to agree with both partners

- **Scoping:** Confirm exact technical problem, data access, candidate availability, ethics, IP and baseline with both partners.
- **Pilot:** Run the proposed baseline and candidate method on a held-out test set; record failure cases, latency, uncertainty and resources.
- **Decision:** Independent review with the company: continue only if pre-agreed measures improve; publish only with both partners consent.

**Independent critic:** The proposed experiment is a plausible task-specific research link, as it involves detecting unusual behavior in Modbus and BACnet networks using machine learning models trained on traffic archives and hardware. The success criterion is well-defined and aligns with the research question. No mismatch, invented capability, unavailable evidence, or unrelated experiment is present.

**Limits:** Official dataset is synthetic; no real collaboration or consent established. Researchers are proposed for task fit; no score of personal worth. Company resources and researcher availability require confirmation. No funding, budget, supervisor, data permission or production gain is asserted.

## DEMO2 · C149-CH1 · ABSTAIN

Explicit abstention: .

## DEMO3 · C150-CH2 · ACCEPTED

**Pair:** Radomir Simić (R0414) × SanaFarma Digitale d.o.o. (C150).

**Research question — proposed:** What changes can be made to the app to improve usability for elderly users?

**Experiment — proposed:** A structured usability session with 60 elderly users aged 70+ in the Sombor and Subotica pilots, using a mixed-methods approach.

**Success criterion — proposed:** A prioritized list of specific changes to improve cognitive flow and reduce error rates.

### Source-controlled facts

- [C150-CH2](https://github.com/jigjoy-ai/einstein-matchmaker-data/blob/4fb99b3749adf0d10b5977089ff4c73f4f522240/data/companies.json), /companies/149/challenges/1, field `text`: We interviewed 60 elderly users and found that 40% stop using the app within three weeks because the font sizes and navigation flow do not match the cognitive and motor patterns of people over 70; we need a systematic redesign but our two-person team has no UX research background.
- [C150](https://github.com/jigjoy-ai/einstein-matchmaker-data/blob/4fb99b3749adf0d10b5977089ff4c73f4f522240/data/companies.json), /companies/149, field `sector`: Medtech and digital health
- [R0414](https://github.com/jigjoy-ai/einstein-matchmaker-data/blob/4fb99b3749adf0d10b5977089ff4c73f4f522240/data/researchers.json), /researchers/413, field `fields`: Cognitive psychology; Human-computer interaction; Ergonomics and human factors; Gerontechnology
- [SYN-PUB-04977](https://github.com/jigjoy-ai/einstein-matchmaker-data/blob/4fb99b3749adf0d10b5977089ff4c73f4f522240/data/publications.jsonl#L4977), /, field `title`: Comparing error rates on icon-only versus icon-plus-label navigation bars across age and digital experience levels
- [SYN-PUB-03354](https://github.com/jigjoy-ai/einstein-matchmaker-data/blob/4fb99b3749adf0d10b5977089ff4c73f4f522240/data/publications.jsonl#L3354), /, field `title`: Age-related change in working memory updating between 48 and 72 months: a longitudinal observational study

### Work plan — to agree with both partners

- **Scoping:** Confirm exact technical problem, data access, candidate availability, ethics, IP and baseline with both partners.
- **Pilot:** Run the proposed baseline and candidate method on a held-out test set; record failure cases, latency, uncertainty and resources.
- **Decision:** Independent review with the company: continue only if pre-agreed measures improve; publish only with both partners consent.

**Independent critic:** The proposed experiment is a hypothesis, not a factual outcome, and it aligns with the research question of improving usability for elderly users. The source evidence supports the need for a systematic redesign based on user feedback, and the researcher's evidence includes relevant fields and publications that support the hypothesis.

**Limits:** Official dataset is synthetic; no real collaboration or consent established. Researchers are proposed for task fit; no score of personal worth. Company resources and researcher availability require confirmation. No funding, budget, supervisor, data permission or production gain is asserted.

## DEMO_NEG · C001-CH1 · ABSTAIN

Explicit abstention: NO_RESEARCH_EVIDENCE.

