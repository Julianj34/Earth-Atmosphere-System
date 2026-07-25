# Earth-Atmosphere-System

[![Run pipeline](https://github.com/Julianj34/Earth-Atmosphere-System/actions/workflows/run_pipeline.yml/badge.svg)](https://github.com/Julianj34/Earth-Atmosphere-System/actions/workflows/run_pipeline.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

An exploratory, layered system for observing coupled Earth–atmosphere states, tracing macro–meso–micro transitions, and generating testable hypotheses.

The project treats the Earth–atmosphere environment as a connected system rather than a collection of isolated variables. It integrates external drivers, surface and ocean preparation, mesoscale organization, atmospheric activation, ionospheric conditions, the Global Electric Circuit, resonance-related proxies, historical state sequences, and hypothesis validation.

> [!IMPORTANT]
> This is **not a weather forecasting model** and it does not establish causal physical relationships by itself.
>
> Measured signals, derived proxies, modeled expectations, and unknown states must remain distinguishable. A downstream layer derived from an upstream layer cannot count as independent confirmation of that same upstream signal.

---

## Core research question

Under what conditions does broad Earth-system preparation develop into organized mesoscale structure, local atmospheric activation, electrical response, and wider system-level change?

The main analytical chain is:

```text
External and background conditions
        ↓
Surface and ocean preparation
        ↓
Mesoscale organization
        ↓
Atmospheric activation
        ↓
Ionospheric and electrical response
        ↓
Resonance-related response
        ↓
Integrated system state
        ↓
Pattern analysis and hypothesis generation
        ↓
External validation
```

The system is designed to preserve uncertainty and to distinguish between:

- a variable being present,
- a proxy suggesting a process,
- several layers changing together,
- a relationship being circular or confounded,
- and a hypothesis receiving genuinely independent support.

---

## System architecture

| Layer | Conceptual role | Current interpretation |
|---|---|---|
| **L0** | External drivers | Background forcing and external context |
| **L1** | Planetary/background state | Broad environmental state and slow context |
| **L2** | Surface and ocean preparation | Macro-scale preparation conditions |
| **L2.5** | Mesoscale organization | Bridge between broad preparation and local activation |
| **L3** | Atmospheric activation | Local or regional atmospheric response |
| **L4** | Ionospheric state | Upper-atmosphere and ionospheric conditions |
| **L5** | Global Electric Circuit | Electrical-response layer; currently partly proxy-derived |
| **L6** | Resonance-related state | Model- and proxy-limited resonance layer |
| **L7** | Integrated state engine | Time-stamped total-system snapshots and history |
| **L8** | Pattern and hypothesis layer | Transitions, coupling patterns, and hypothesis candidates |
| **L9** | Validation layer | External checks, promotion gates, and status updates |

### Macro–meso–micro bridge

A central design problem is the transition from broad preparation to local activation:

```text
L2 macro preparation
    → L2.5 mesoscale organization
        → L3 local atmospheric activation
```

Without the mesoscale bridge, broad conditions can appear favorable while no local event develops. L2.5 therefore acts as an organization and gating layer rather than another independent endpoint.

### Holarchic analysis

The project also evaluates the system as a hierarchy of interacting subsystems, or holons. The holarchic analysis asks whether a state change:

- remains local,
- propagates across layers,
- is amplified or damped,
- is delayed,
- is blocked by an intermediate layer,
- or only appears coupled because two layers share the same underlying input.

The main modules are:

```text
src/atmosphere/meta/holarchic_coupling_analysis.py
src/atmosphere/meta/role_proxy_writeback.py
```

---

## Scientific interpretation contract

Every signal should be interpreted according to its provenance and role.

| Signal type | Meaning | Can independently confirm another layer? |
|---|---|---|
| `measured` | Directly based on an observational input | Potentially, subject to quality and confound checks |
| `derived_proxy` | Calculated from one or more upstream variables | No, not when testing the source relationship |
| `modeled_proxy` | Expected or simulated response | No, unless externally validated |
| `transitional_proxy` | Temporary substitute for a missing feed | Only as exploratory evidence |
| `unknown` | Evidence is absent, stale, invalid, or insufficient | No |

This distinction is essential for preventing circular conclusions.

For example, when an electrical state is derived primarily from atmospheric activation, a strong L3–L5 relationship may reflect construction logic rather than independent physics. The relationship can still be operationally useful, but it must be labeled as dependent.

---

## Current development status

| Component | Status |
|---|---|
| Layer notebooks L0–L9 | Implemented |
| Central pipeline runner | Implemented |
| Current-state storage | Implemented |
| L7 historical state sequence | Implemented |
| Hypothesis registry | Implemented |
| Hypothesis-candidate artifacts | Implemented |
| Holarchic coupling analysis | Implemented |
| Role/proxy writeback | Implemented |
| Mesoscale integration | Implemented with transitional feed logic |
| Independent Global Electric Circuit validation | In development |
| Independent resonance validation | In development |
| Formal test suite | Planned |
| Scientific maturity | Exploratory research system |

### Important current limitations

1. **L2.5 is transitional.**  
   Mesoscale organization currently depends on a transitional proxy configuration. The target is a more independent organization layer using feeds such as outgoing longwave radiation and convective inhibition where reliable data are available.

2. **L5 is not fully independent.**  
   Parts of the Global Electric Circuit representation are derived from lower-layer atmospheric variables. L5 must therefore not be treated as independent confirmation of L3.

3. **L6 remains proxy- and model-limited.**  
   Resonance-related states are useful for system exploration, but they do not yet provide an independently validated observational layer.

4. **Correlation is not causation.**  
   Cross-layer alignment may arise from shared inputs, temporal autocorrelation, construction rules, common seasonality, or other confounders.

5. **L9 is an evolving validation layer.**  
   Hypotheses should remain candidates until they pass independent data checks, falsification attempts, and explicit promotion criteria.

---

## Repository structure

```text
Earth-Atmosphere-System/
├── .github/
│   └── workflows/
│       └── run_pipeline.yml
├── config/
│   └── meso_feeds.yaml
├── notebooks/
│   ├── atmosphere_analysis_layer0.ipynb
│   ├── atmosphere_analysis_layer1.ipynb
│   ├── atmosphere_analysis_layer2.ipynb
│   ├── atmosphere_analysis_layer3.ipynb
│   ├── atmosphere_analysis_layer4.ipynb
│   ├── atmosphere_analysis_layer5.ipynb
│   ├── atmosphere_analysis_layer6.ipynb
│   ├── atmosphere_analysis_layer7.ipynb
│   ├── atmosphere_analysis_layer8.ipynb
│   └── atmosphere_analysis_layer9.ipynb
├── pipeline/
│   └── run_pipeline.py
├── reports/
│   ├── holarchic_analysis_report.md
│   ├── layer8_report.md
│   ├── layer9_report.md
│   └── meso_integration_spec.md
├── src/
│   └── atmosphere/
│       ├── __init__.py
│       ├── paths.py
│       ├── config/
│       │   ├── __init__.py
│       │   └── domain.py
│       ├── ingest/
│       │   ├── __init__.py
│       │   └── meso_ingest.py
│       ├── layers/
│       │   ├── __init__.py
│       │   └── layer_meso.py
│       └── meta/
│           ├── __init__.py
│           ├── holarchic_coupling_analysis.py
│           └── role_proxy_writeback.py
├── states/
│   ├── current/
│   │   ├── layer0_state.json
│   │   ├── layer1_state.json
│   │   ├── layer2_state.json
│   │   ├── layer2p5_meso_state.json
│   │   ├── layer3_state.json
│   │   ├── layer4_state.json
│   │   ├── layer5_state.json
│   │   ├── layer6_state.json
│   │   ├── layer7_state.json
│   │   ├── layer8_state.json
│   │   └── layer9_state.json
│   ├── history/
│   │   └── layer7_history.jsonl
│   ├── registry/
│   │   ├── holon_registry.yaml
│   │   ├── hypothesis_registry.json
│   │   └── hypothesis_candidates/
│   └── coupling/
│       ├── holarchic_coupling_matrix.csv
│       └── holarchic_event_card.json
├── .gitignore
├── .project-root
├── LICENSE
├── README.md
├── pyproject.toml
└── requirements.txt
```

---

## Installation

A recent Python 3 environment is recommended. Python 3.11 is a suitable default.

### 1. Clone the repository

```bash
git clone https://github.com/Julianj34/Earth-Atmosphere-System.git
cd Earth-Atmosphere-System
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

Linux or macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

The editable install makes the `src/atmosphere` package available while allowing local source changes without reinstalling the project after every edit.

---

## Running the system

### Run the complete pipeline

```bash
python pipeline/run_pipeline.py
```

### Start from a later layer

```bash
python pipeline/run_pipeline.py --from 7
```

### Run selected layers

```bash
python pipeline/run_pipeline.py --only 7 8 9
```

### Run holarchic analysis

```bash
python pipeline/run_pipeline.py --holarchic
```

The pipeline reads the required upstream state artifacts, executes the requested layers, and updates the corresponding files under `states/` and `reports/`.

---

## GitHub Actions

The workflow is located at:

```text
.github/workflows/run_pipeline.yml
```

To run it manually:

1. Open the repository on GitHub.
2. Select **Actions**.
3. Open **Run pipeline**.
4. Select **Run workflow**.
5. Choose the branch and start the run.

The project can also run fully on a local machine. GitHub Actions is an execution and automation layer, not a runtime dependency.

---

## Outputs

### Current states

```text
states/current/
```

These JSON artifacts contain the latest state produced by each layer.

### Historical system sequence

```text
states/history/layer7_history.jsonl
```

L7 appends time-stamped integrated system states. This history is the main temporal input for transition and pattern analysis.

### Hypothesis registry

```text
states/registry/hypothesis_registry.json
states/registry/hypothesis_candidates/
```

The registry stores hypothesis status, evidence, restrictions, and promotion state. Candidate files preserve hypotheses separately so they can be reviewed without automatically changing the operational model.

### Holarchic coupling artifacts

```text
states/coupling/holarchic_coupling_matrix.csv
states/coupling/holarchic_event_card.json
reports/holarchic_analysis_report.md
```

These artifacts summarize cross-layer coupling, event structure, and system-level interpretation.

### Analysis reports

```text
reports/layer8_report.md
reports/layer9_report.md
reports/meso_integration_spec.md
```

---

## Analytical safeguards

The project is designed around conservative interpretation.

### Provenance awareness

Every analytical result should retain enough metadata to determine:

- its source,
- its observation time,
- its processing time,
- whether it is measured or derived,
- which upstream variables contributed to it,
- and whether the input was stale or missing.

### Confound control

A relationship should be downgraded when it may be explained by:

- direct mathematical construction,
- a shared upstream source,
- temporal autocorrelation,
- seasonality,
- regime changes,
- missing-data substitution,
- or a proxy being mistaken for a measurement.

### Circularity control

A derived layer cannot be used as independent proof of the layer from which it was derived.

### Promotion gates

Hypotheses should not move into model logic merely because they are interesting or repeatedly observed. Promotion should require:

- explicit evidence,
- an identified falsification test,
- independent inputs where possible,
- confound review,
- provenance completeness,
- and a documented decision.

### Preservation of unknown states

Missing or ambiguous evidence should remain `unknown`. The pipeline should not convert uncertainty into false certainty simply to complete a state vector.

---

## Example analytical interpretation

Suppose the system observes:

```text
L2 preparation: elevated
L2.5 organization: weak
L3 activation: absent
```

The correct interpretation is not that the macro signal failed. A more precise interpretation is:

> Broad preparation was present, but the mesoscale organization gate did not form strongly enough for local atmospheric activation.

A second example:

```text
L3 activation: elevated
L5 electrical proxy: elevated
```

When L5 is calculated partly from L3, this is not two independent observations. It is one observation plus a dependent transformation. The relationship can describe the model state, but it cannot independently validate the underlying physical coupling.

---

## Research workflow

```text
1. Ingest or update inputs
        ↓
2. Produce layer states
        ↓
3. Build the integrated L7 snapshot
        ↓
4. Append the historical state sequence
        ↓
5. Detect transitions and cross-layer patterns
        ↓
6. Generate hypothesis candidates
        ↓
7. Run confound and circularity checks
        ↓
8. Test against independent evidence
        ↓
9. Promote, retain, revise, or reject
```

This separates observation from interpretation and interpretation from model promotion.

---

## Roadmap

Current priorities include:

- stabilizing independent mesoscale feeds,
- integrating stronger organization and gating variables,
- separating measured and derived Global Electric Circuit components,
- adding independent resonance-related observations,
- improving lead–lag tests with autocorrelation and regime controls,
- expanding provenance and staleness validation,
- adding a dedicated automated test suite,
- formalizing hypothesis promotion and rejection criteria,
- and improving long-run pattern analysis across the L7 history.

---

## Scope and responsible use

This repository is intended for exploratory research, system architecture development, data analysis, and hypothesis generation.

It should not be used as:

- an operational weather-warning system,
- a substitute for established meteorological services,
- proof of causal geophysical mechanisms,
- or evidence for extraordinary claims without independent validation.

Results should be interpreted together with source quality, uncertainty, proxy dependence, and the current maturity of each layer.

---

## Contributing

Contributions are welcome when they improve:

- data provenance,
- independent observational coverage,
- reproducibility,
- confound detection,
- validation logic,
- tests,
- documentation,
- or scientific clarity.

For substantial changes, open an issue first and describe:

1. the layer or module affected,
2. the proposed evidence source,
3. whether the signal is measured or derived,
4. expected failure modes,
5. and how the change can be tested.

---

## License

This project is licensed under the [MIT License](LICENSE).
