# Layer 9 — External Grounding & Validation

**Run:** 2026-08-08T20:54:51.767920Z
**Validation Score:** 1.0  (exploratory_signal)

## Aggregat
- ✅ Passed:       6
- ❌ Failed:       0
- ⚠️  Uncertain:  0
- ❓ Inconclusive: 1

## Failed Checks
- keine

## Uncertain Checks
- keine

## Model Adjustment Suggestions
- keine

## Validation Checks (alle)
- ✅ **V_enso_phase**: Layer-2-ENSO-Klassifikation stimmt mit offiziellem NOAA ONI überein
  - Erwartet: el_nino
  - Beobachtet: el_nino
- ✅ **V_kp_consistency**: Modell-Kp und NOAA-Kp im gleichen Zeitfenster konsistent
  - Erwartet: |Δ Kp| <= 1.0  (Fenster: current_1m)
  - Beobachtet: model_current=6.0  vs  noaa_current=6.0  →  |Δ|=0.00
- ✅ **V_storm_flag**: Bei Kp >= 5 ist geomagnetic_storm-Flag gesetzt
  - Erwartet: True
  - Beobachtet: True
- ❓ **V_schumann_data_availability**: Externe Schumann-Resonanz-Messdaten für Vergleich verfügbar
  - Erwartet: real-time SR1 amplitude/frequency feed
  - Beobachtet: no public feed available
- ✅ **V_consistency_tags**: Baseline-Tags und Signal-Tags sind disjunkt
  - Erwartet: no overlap
  - Beobachtet: overlap = []
- ✅ **V_backtest_carnegie_anomalous**: anomalous_resonance_state tritt überwiegend (>= 80%) abends auf
  - Erwartet: >= 80% evening
  - Beobachtet: 100.0% evening (6/6)
- ✅ **V_backtest_enso_consistency**: Bei externem ONI >= 0.2 sind >= 50% der Snapshots warm-klassifiziert
  - Erwartet: >= 50% warm
  - Beobachtet: 86.1% warm