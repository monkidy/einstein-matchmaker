# EINSTEIN Proof — private review

All people, companies and publications below are fictional organizer data. Proposed experiments are hypotheses, not demonstrated results.

## N01 · C088-CH2 · ABSTAIN

Explicit abstention: Uncertain link between citric acid pre-treatment and gel layer formation in dairy wastewater. No direct evidence supports this method for reducing fouling..

## N02 · C102-CH3 · ACCEPTED

**Pair:** Lazar Marković (R0763) × Pulmoteh d.o.o. (C102).

**Research question — proposed:** Can a simulation model optimize scheduling to reduce inventory imbalance and forecast lead times?

**Experiment — proposed:** Run a discrete-event simulation using historical order data and component lead times to generate a weekly production schedule

**Success criterion — proposed:** Proposed gate: measure Inventory imbalance cost reduction percentage on a frozen held-out test set against a transparent control agreed at scoping. Pre-register the minimum useful improvement and uncertainty bounds with both partners. No present baseline value is assumed.

### Source-controlled facts

- [C102-CH3](https://github.com/jigjoy-ai/einstein-matchmaker-data/blob/4fb99b3749adf0d10b5977089ff4c73f4f522240/data/companies.json), /companies/101/challenges/2, field `text`: We assemble 200 to 300 units per month on a mixed-model line with three operators, but scheduling which variant to build on which shift is done on paper and we routinely end up with stockouts on one SKU and overstock on another, tying up roughly €40,000 in unnecessary inventory.
- [C102-CH3](https://github.com/jigjoy-ai/einstein-matchmaker-data/blob/4fb99b3749adf0d10b5977089ff4c73f4f522240/data/companies.json), /companies/101/challenges/2, field `detail`: We build four variants of the SP-400 — differing in connectivity options and mouthpiece configurations — and two variants of the SP-200, for a total of six SKUs on one mixed-model assembly line with three operators working two shifts. Production volumes run between 200 and 300 units a month depending on orders. Scheduling which variant to build on which shift is currently managed by our production coordinator, Bojana Marić, using a printed weekly plan and a whiteboard. The problem is that demand for each variant is not uniform and not easy to predict more than two weeks out, and our current approach does not account for component lead times or shared subassembly constraints well enough. In practice, we end up short on one or two SKUs almost every month while accumulating buffer stock on others. Our finance team estimates the excess inventory tied up by this imbalance averages around €40,000 at any given time. We track orders and shipments in an older version of a Serbian ERP system, MikroERP, which exports to Excel. We have 30 months of order history by SKU. We are not looking for a large enterprise software replacement; we want a scheduling or planning tool or method that our coordinator can run each week without specialised training, ideally integrated with or at least feeding from our existing Excel exports. A reasonable budget for this is €8,000 to €12,000, and we would want something usable within six months.
- [C102](https://github.com/jigjoy-ai/einstein-matchmaker-data/blob/4fb99b3749adf0d10b5977089ff4c73f4f522240/data/companies.json), /companies/101, field `sector`: Medtech and digital health
- [R0763](https://github.com/jigjoy-ai/einstein-matchmaker-data/blob/4fb99b3749adf0d10b5977089ff4c73f4f522240/data/researchers.json), /researchers/762, field `fields`: Industrial and Production Engineering; Manufacturing Systems Engineering; Operations Research and Simulation; Digital Manufacturing
- [SYN-PUB-08390](https://github.com/jigjoy-ai/einstein-matchmaker-data/blob/4fb99b3749adf0d10b5977089ff4c73f4f522240/data/publications.jsonl#L8390), /, field `title`: Simulation-based capacity assessment for a mixed-model assembly line in a small-series automotive supplier
- [SYN-PUB-08390](https://github.com/jigjoy-ai/einstein-matchmaker-data/blob/4fb99b3749adf0d10b5977089ff4c73f4f522240/data/publications.jsonl#L8390), /, field `abstract`: This paper presents a discrete-event simulation study of a mixed-model assembly line producing five vehicle body variants at a tier-two automotive supplier in Vojvodina. A Plant Simulation model was built from time-study data collected over six weeks, comprising 1 240 observed task times across 18 workstations and three operator skill categories. The model was validated against three months of production logs, achieving a throughput deviation of less than 2.1% for all product variants. Scenario analysis covering four capacity expansion alternatives—including workstation splitting, buffer insertion, and cross-training policies—showed that targeted cross-training at two identified bottleneck stations yielded a 14.3% increase in daily output without capital investment. The paper also discusses the sensitivity of throughput to task-time variability modelled through empirically fitted lognormal distributions, and identifies conditions under which a simple deterministic model underestimates true cycle time by up to 8.7%.
- [SYN-PUB-08392](https://github.com/jigjoy-ai/einstein-matchmaker-data/blob/4fb99b3749adf0d10b5977089ff4c73f4f522240/data/publications.jsonl#L8392), /, field `title`: Modelling operator flexibility in mixed-model assembly using combined DES and multi-skill workforce assignment
- [SYN-PUB-08392](https://github.com/jigjoy-ai/einstein-matchmaker-data/blob/4fb99b3749adf0d10b5977089ff4c73f4f522240/data/publications.jsonl#L8392), /, field `abstract`: Workforce flexibility is a primary lever in low-volume, high-variety assembly but is rarely integrated into discrete-event simulation models in a tractable way. This paper describes a modelling approach in which operator skill profiles—defined as three-level competency ratings across 24 task types—are encoded directly in a Plant Simulation model and linked to a rule-based assignment heuristic updated at every takt boundary. The approach was applied to a 16-station electronic control unit assembly line where 11 operators cover 32 tasks. Three staffing scenarios were simulated over a horizon of 240 shifts. Results showed that a skill-matrix reshaping requiring training of four additional task competencies reduced average station idle time by 19% and reduced peak work-in-process by 23%. The paper further discusses how training cost can be incorporated as a constraint and presents a Pareto frontier of throughput versus training investment.

### Work plan — to agree with both partners

- **Scoping:** Confirm exact technical problem, data access, candidate availability, ethics, IP and baseline with both partners.
- **Pilot:** Run the proposed baseline and candidate method on a held-out test set; record failure cases, latency, uncertainty and resources.
- **Decision:** Independent review with the company: continue only if pre-agreed measures improve; publish only with both partners consent.

**Independent critic:** Simulation models can optimize scheduling and account for lead times, aligning with the company's need for improved inventory management.

**Limits:** Official dataset is synthetic; no real collaboration or consent established. Researchers are proposed for task fit; no score of personal worth. Company resources and researcher availability require confirmation. No funding, budget, supervisor, data permission or production gain is asserted.

## N03 · C058-CH3 · ABSTAIN

Explicit abstention: The operation was aborted due to timeout.

## N04 · C119-CH1 · ACCEPTED

**Pair:** Ildikó Papp (R0626) × Vizura Studio d.o.o. (C119).

**Research question — proposed:** Can a machine learning model classify prepress errors in packaging artwork PDFs to improve dieline registration accuracy?

**Experiment — proposed:** Train a model on 3,847 packaging artwork PDFs with error annotations to predict dieline registration issues

**Success criterion — proposed:** Proposed gate: measure Error detection accuracy in identifying registration issues during dieline structure analysis on a frozen held-out test set against a transparent control agreed at scoping. Pre-register the minimum useful improvement and uncertainty bounds with both partners. No present baseline value is assumed.

### Source-controlled facts

- [C119-CH1](https://github.com/jigjoy-ai/einstein-matchmaker-data/blob/4fb99b3749adf0d10b5977089ff4c73f4f522240/data/companies.json), /companies/118/challenges/0, field `text`: We produce roughly 600 packaging variants a year and our senior designer spends two days per project manually fitting artwork into structural dielines; we need a way to automate or semi-automate that layout step so turnaround drops from five days to two.
- [C119-CH1](https://github.com/jigjoy-ai/einstein-matchmaker-data/blob/4fb99b3749adf0d10b5977089ff4c73f4f522240/data/companies.json), /companies/118/challenges/0, field `detail`: We produce around 600 packaging variants every year, and the bottleneck is always the same step: taking finished artwork and fitting it into the structural dieline for that specific SKU. Our senior designer Jovana Petrović does almost all of this manually in Illustrator and Esko ArtPro. On a straightforward rectangular box it takes half a day. On a shaped carton or a multi-panel sleeve it can take two full days. That means our average packaging turnaround is five days from approved artwork to print-ready file. Clients, especially the larger retail ones, are now expecting three days or less. We have looked at scripting some of the repetitive placement steps inside Illustrator, and Dragan built a few basic actions, but the dielines vary too much in anchor points and bleed zones for a simple macro to handle reliably. We have also looked at one commercial plug-in but it assumed flat rectangular formats only. What we want is something that can read a dieline structure, identify the printable panels, and place and scale artwork into those panels with minimal manual correction, ideally reducing Jovana's involvement to a review step rather than a build step. Our constraint is that the solution has to produce files that our existing offset and digital print vendors can accept without extra conversion work.
- [C119](https://github.com/jigjoy-ai/einstein-matchmaker-data/blob/4fb99b3749adf0d10b5977089ff4c73f4f522240/data/companies.json), /companies/118, field `sector`: Marketing tech, media and creative studios
- [R0626](https://github.com/jigjoy-ai/einstein-matchmaker-data/blob/4fb99b3749adf0d10b5977089ff4c73f4f522240/data/researchers.json), /researchers/625, field `fields`: Graphic Engineering and Reproduction Technology; Computational Geometry and Layout Automation; Digital Color Science; Packaging Design and Engineering
- [SYN-PRJ-0519](https://github.com/jigjoy-ai/einstein-matchmaker-data/blob/4fb99b3749adf0d10b5977089ff4c73f4f522240/data/projects.json), /projects/518, field `title`: Rule-Driven Parametric Artwork-to-Structure Registration for Sustainable Folding-Carton Production
- [SYN-PRJ-0519](https://github.com/jigjoy-ai/einstein-matchmaker-data/blob/4fb99b3749adf0d10b5977089ff4c73f4f522240/data/projects.json), /projects/518, field `summary`: PACKRULE addressed the gap between structural dieline design and graphic artwork placement in folding-carton production, where manual registration adjustments account for a disproportionate share of make-ready time and material waste. The project built a rule engine that reads a structural dieline in CFF2 format, extracts registered feature positions (score lines, cut edges, window apertures), and automatically constrains artwork element positions in a linked PDF document. Registration correction rules were derived from a database of 1,800 production runs covering four board grades and three printing processes. The project produced a validated software prototype, three journal papers, and two master's theses. One regional packaging converter participated as an industry observer and provided production data under a non-disclosure agreement.
- [SYN-PUB-07157](https://github.com/jigjoy-ai/einstein-matchmaker-data/blob/4fb99b3749adf0d10b5977089ff4c73f4f522240/data/publications.jsonl#L7157), /, field `title`: Machine learning classification of prepress preflight errors from PDF structural features
- [SYN-PUB-07157](https://github.com/jigjoy-ai/einstein-matchmaker-data/blob/4fb99b3749adf0d10b5977089ff4c73f4f522240/data/publications.jsonl#L7157), /, field `abstract`: Preflight error classification in prepress workflows typically relies on hard-coded rule sets that require expert maintenance as standards evolve. This paper investigates whether machine learning classifiers trained on features extracted from the PDF object tree can identify error categories without explicit rule authoring. A dataset of 3,847 packaging artwork PDFs, each manually annotated with up to five error categories, was assembled from three prepress bureaus. Forty-one structural and colorimetric features were extracted per file. Random forest, gradient boosting, and a small fully connected neural network were evaluated using stratified 5-fold cross-validation. Gradient boosting achieved the highest macro F1 score of 0.83 across 11 error categories. Performance was lowest for the 'insufficient bleed' category (F1 = 0.61) due to ambiguity in page-box definitions. Feature importance analysis confirmed that colorspace object count and overprint flag frequency were the most discriminative features.

### Work plan — to agree with both partners

- **Scoping:** Confirm exact technical problem, data access, candidate availability, ethics, IP and baseline with both partners.
- **Pilot:** Run the proposed baseline and candidate method on a held-out test set; record failure cases, latency, uncertainty and resources.
- **Decision:** Independent review with the company: continue only if pre-agreed measures improve; publish only with both partners consent.

**Independent critic:** Research addresses dieline registration and error classification, aligning with company's need for automated layout adjustment.

**Limits:** Official dataset is synthetic; no real collaboration or consent established. Researchers are proposed for task fit; no score of personal worth. Company resources and researcher availability require confirmation. No funding, budget, supervisor, data permission or production gain is asserted.

## N05 · C054-CH1 · ABSTAIN

Explicit abstention: The operation was aborted due to timeout.

## N06 · C108-CH1 · ABSTAIN

Explicit abstention: The operation was aborted due to timeout.

