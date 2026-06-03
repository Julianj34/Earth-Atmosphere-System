# Layer 8 — Research Report

**Run:** 2026-06-03T22:40:44.268039Z
**Snapshots analyzed:** 21
**Complete day pairs:** 3  (morning + evening)
**Complete day quads:** 3  (all 4 slots)

## System State Frequency

- `seasonal_transition_state` — 11× (52.4%)
- `cavity_condition_shift_state` — 7× (33.3%)
- `anomalous_resonance_state` — 3× (14.3%)

## Day Pairs (ΔL3 Activation)

| Date | L3 morning | L3 midday | L3 evening | ΔL3 | ΔL3 midday | Evening State |
|---|---|---|---|---|---|---|
| 2026-05-11 | 0.108 | 0.155 | 0.179 | +0.071 | +0.047 | anomalous_resonance |
| 2026-05-12 | 0.140 | 0.157 | 0.173 | +0.032 | +0.017 | anomalous_resonance |
| 2026-05-13 | 0.127 | 0.117 | 0.207 | +0.080 | -0.009 | anomalous_resonance |

## L2 ↔ L3 Relationship

- Pearson: **-0.140**
- L2 trend: -0.00152 / snapshot
- L3 trend: +0.00038 / snapshot
- Gap trend: -0.00190 / snapshot
- Weak coupling visible — more data needed.

## Field Operators

Coverage: 4/21 snapshots

### Current Operator Ranking

- **resonance_model**: 0.455 — modeled non-geometric component exceeds cavity geometry
- **electric**: 0.317 — moderate electrical coupling
- **thermal**: 0.290 — thermal preparation weak
- **ionization**: 0.270 — moderate ionospheric modulation
- **geomagnetic**: 0.123 — quiet geomagnetic conditions
- **cross_layer_activation**: 0.092 — no transition tension — layers coherent

## Hypotheses

### ❓ H1: Does anomalous_resonance_state occur exclusively in the evening slot (>= 18 CEST)?

- **Status:** open
- **Evidence:** 3/3 anomalous events in evening slot (100.0%). Morning: 0.
- **Next step:** More snapshots; add midday slot for confirmation if needed.

### ❓ H6: Which tags are persistent background vs actual activation signal?

- **Status:** open
- **Evidence:** Present in 100% of all snapshots: el_nino_developing, non_geometric_dominance. These are seasonal background, not activation signals.
- **Next step:** Separate background tags from Layer 7 tag list or mark as baseline_tags.

### 🔶 H8: Is "mixed" the dominant operator regime?

- **Status:** likely
- **Evidence:** 4/4 snapshots (100.0%) in regime "mixed".
- **Next step:** Analyze transition patterns between regimes (Layer 9?).
