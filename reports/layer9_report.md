# Layer 9 — External Grounding & Validation

**Run:** 2026-07-25T21:14:20.121628Z
**Validation Score:** 0.875  (exploratory_signal)

## Aggregat
- ✅ Passed:       3
- ❌ Failed:       0
- ⚠️  Uncertain:  1
- ❓ Inconclusive: 1

## Failed Checks
- keine

## Uncertain Checks
- **V_consistency_seasonal** (consistency_validation): Meta-Score-Konsistenz für seasonal_transition_state

## Model Adjustment Suggestions
- keine

## Validation Checks (alle)
- ✅ **V_kp_consistency**: Modell-Kp und NOAA-Kp im gleichen Zeitfenster konsistent
  - Erwartet: |Δ Kp| <= 1.0  (Fenster: current_1m)
  - Beobachtet: model_current=0.0  vs  noaa_current=0.0  →  |Δ|=0.00
- ❓ **V_schumann_data_availability**: Externe Schumann-Resonanz-Messdaten für Vergleich verfügbar
  - Erwartet: real-time SR1 amplitude/frequency feed
  - Beobachtet: no public feed available
- ✅ **V_consistency_tags**: Baseline-Tags und Signal-Tags sind disjunkt
  - Erwartet: no overlap
  - Beobachtet: overlap = []
- ⚠️ **V_consistency_seasonal**: seasonal_transition_state: preparation > 0.45 und downstream < 0.35
  - Erwartet: prep > 0.45 AND downstream < 0.35
  - Beobachtet: prep=0.557, downstream=0.390
- ✅ **V_backtest_carnegie_anomalous**: anomalous_resonance_state tritt überwiegend (>= 80%) abends auf
  - Erwartet: >= 80% evening
  - Beobachtet: 100.0% evening (7/7)