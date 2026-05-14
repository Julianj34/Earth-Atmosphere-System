# Earth-Atmosphere-System
A layered Earth-system framework for mapping field states, atmospheric coupling, the Global Electric Circuit, and Schumann-resonance patterns.

## Status

Current implementation: **Layer 0–8**

- **Layer 0–6:** Physical system layers  
- **Layer 7:** Earth Field State Engine — creates standardized, time-stamped system snapshots  
- **Layer 8:** Research & Hypothesis Engine — analyzes the Layer-7 snapshot history for patterns, transitions, Field Operator behavior, Cavity Gate events, and emerging hypotheses  

Layer 8 becomes more valuable as the `layer7_test_history.jsonl` archive grows over time. With repeated daily snapshots, the system can move from exploratory pattern detection toward more stable hypothesis testing.

Planned next step: **Layer 9 – Model Integration / Prediction Layer**

---

## Core Idea

The Earth is not analyzed as isolated variables, but as a coupled system:

External drivers
→ planetary body
→ surface / ocean / contact zone
→ atmosphere / thunderstorms
→ ionosphere
→ Global Electric Circuit
→ resonance field / Schumann resonance
→ Earth Field State Engine
→ system analysis / research intelligence

The goal is to detect system states, layer gaps, dominant layers, coupling patterns, transitions, recurring tag combinations, and possible precursor patterns.

Layer Model
Layer 0 – External Drivers

Role: Everything that acts on the Earth system from outside.

Examples:

solar radiation
UV / X-Ray
solar wind
geomagnetic disturbances
cosmic radiation
planetary / orbital cycles

Function:
Layer 0 is the external modulator. It can influence the ionosphere, geomagnetic conditions, atmospheric coupling, and resonance conditions.

Core question:
Which external influences are changing the state of the Earth Field System?

---
Layer 1 – Planetary Body

Role: The Earth as the physical carrier of the system.

Examples:

Earth rotation
basic geomagnetic field structure
lithosphere
soil / rock
oceans
surface conductivity
planetary geometry
seismic activity
LOD anomaly

Function:
Layer 1 forms the material foundation. Without this layer, there would be no Earth-ionosphere cavity, no surface-ionosphere coupling, and no global electric circuit.

Stable baseline properties such as ocean conductivity are treated as boundary conditions, not as daily dynamic stress values.

Core question:
Which planetary base conditions shape the resonance and coupling space?

---
Layer 2 – Surface / Oceans / Contact Zone

Role: The boundary zone between Earth surface, oceans, land, biosphere, and atmosphere.

Examples:

land-ocean distribution
surface temperature
sea surface temperature
SST anomaly
ENSO / Niño3.4 context
humidity
vegetation
soil moisture
local electric fields
surface-atmosphere exchange

Function:
Layer 2 prepares atmospheric activity. It influences heat flux, moisture, convection, and indirectly thunderstorm and electrical processes.

This layer can become elevated even when the atmosphere has not yet activated.

Core question:
Is the surface prepared for atmospheric and thunderstorm activation?

---
Layer 3 – Atmosphere / Weather / Thunderstorms

Role: The dynamic weather and convection layer.

Examples:

temperature
humidity
air pressure
wind
CAPE
Lifted Index
convection
cloud formation
thunderstorm cells
lightning proxies
active storm events

Function:
Layer 3 determines whether surface preparation actually turns into atmospheric activation.

Thunderstorms and lightning are especially important because they energize the Global Electric Circuit and excite Schumann-resonance modes.

Important distinction:

Layer 2 = potential / preparation
Layer 3 = actual atmospheric activation

Core question:
How strong is the current atmospheric-electrical activity?

---
Layer 4 – Ionosphere

Role: The upper conductive boundary layer of the Earth-ionosphere resonance system.

Examples:

D-, E-, F-layers
electron density
ionization
day/night differences
solar UV influence
X-Ray / D-layer absorption
geomagnetic disturbance
ionospheric conductivity
cavity-height scenarios

Function:
Layer 4 forms the upper boundary of the Earth-ionosphere cavity. It changes the propagation conditions of electromagnetic waves and affects resonance conditions.

Important distinction:

Layer 4 geometric cavity model ≠ observed Schumann resonance

Layer 4 can provide an idealized geometric baseline. Layer 6 uses empirical Schumann-reference values and compares expected shifts against this baseline.

Core question:
How does the ionosphere modify the resonance and coupling conditions?

---
Layer 5 – Global Electric Circuit

Role: The electrical macro-architecture of the Earth.

Examples:

thunderstorms as generators
ionospheric potential
vertical currents
fair-weather return currents
surface ↔ ionosphere electrical coupling
global charge circulation

Function:
Layer 5 connects thunderstorms, Earth surface, and ionosphere into a global electric circuit.

Core logic:

thunderstorms / lightning
→ ionospheric potential
→ vertical currents
→ global electrical feedback

Layer 5 estimates whether the Global Electric Circuit is near reference, elevated, or suppressed.

Core question:
How strongly is the global electric circuit currently activated?

---
Layer 6 – Resonance Field / Schumann Resonance

Role: The observable or modeled electromagnetic resonance pattern of the system.

Examples:

SR-1 fundamental mode
higher Schumann modes
amplitude
frequency shift
band structure
Q-factor
daily pattern
seasonal pattern
anomalies
geometric vs. non-geometric delta

Function:
Layer 6 describes the resonance behavior of the Earth-ionosphere cavity.

Currently, this layer works as a model-expected resonance state, not as a direct measurement layer.

measurement_status = model_expected_not_observed

Later, real Schumann-resonance measurements can be added.

The Schumann resonance is not treated as an isolated frequency. It is treated as a possible expression of coupled states involving:

thunderstorm activity
ionospheric conductivity
Global Electric Circuit
day/night structure
damping
lightning-source distribution
propagation conditions

Important distinction:

empirical Schumann reference values
≠
idealized geometric cavity frequencies

Empirical reference examples:

SR-1 ≈ 7.83 Hz
SR-2 ≈ 14.3 Hz
SR-3 ≈ 20.8 Hz
SR-4 ≈ 27.3 Hz

Core question:
What information about the total Earth Field System is contained in the resonance pattern?

---
Layer 7 – Earth Field State Engine

Role: The integration layer and state machine of the system.

Examples:

Layer 0–6 state files
normalized layer scores
layer confidence
cross-layer couplings
meta-scores
Field Operators
Cavity Gate status
event tags
system-state classification
snapshot history

Function:
Layer 7 does not collect new raw data. It combines the outputs of Layer 0–6 into one standardized, time-stamped Earth Field snapshot.

It detects which layers are dominant, which layers are weak, how strongly the layers are coupled, and whether the system is in a background, transition, cavity-shift, mixed-coupled, or anomalous resonance state.

Layer 7 is the handoff layer for Layer 8. Each run saves the current state as `layer7_test_state.json` and appends one snapshot to `layer7_test_history.jsonl`.

Important distinction:

Layer 0–6 = physical system layers  
Layer 7 = current system-state engine  
Layer 8 = long-term pattern and hypothesis analysis

Core question:
What is the current integrated state of the Earth Field System?

---
Layer 8 – Research & Hypothesis Engine

Role: The analytical research layer of the system.

Examples:

layer7_test_history.jsonl
snapshot history
morning / midday / evening / night slots
day-pair analysis
ΔL3 / ΔL5 / ΔL6 activation
Field Operator trends
state transitions
Cavity Event Study
hypothesis registry
hypothesis candidates

Function:
Layer 8 does not collect new field data. It reads the growing Layer 7 snapshot archive and searches for reproducible patterns across time.

It analyzes daily activation cycles, especially the difference between morning baseline and evening activation. ΔL3, ΔL5, and ΔL6 are used to study whether atmospheric activation, Global Electric Circuit response, and resonance-field response appear together.

Layer 8 also evaluates Field Operators over time, studies state transitions, detects possible precursor patterns, and generates structured hypotheses for later testing.

Important distinction:

Layer 7 = current system-state snapshot  
Layer 8 = long-term pattern research and hypothesis testing  
Layer 9 = future model integration / prediction layer

Core question:
Which repeating patterns, transitions, and hypotheses emerge from the Earth Field snapshot history?

Outputs:

`layer8_test_state.json` — machine-readable research state  
`layer8_test_report.md` — human-readable research report  
`test_hypothesis_registry.json` — persistent hypothesis archive  
`test_hypothesis_candidates/*.json` — automatically generated hypothesis candidates
