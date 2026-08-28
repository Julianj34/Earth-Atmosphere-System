# Layer 9 — External Grounding & Validation

**Run:** 2026-08-28T20:16:38.919276Z
**Validation Score:** 0.9286  (exploratory_signal)

## Aggregat
- ✅ Passed:       6
- ❌ Failed:       0
- ⚠️  Uncertain:  1
- ❓ Inconclusive: 1

## Failed Checks
- keine

## Uncertain Checks
- **V_storm_atmosphere** (storm_validation): EONET open storms=7. L3=0.191, active_thunderstorms=False

## Model Adjustment Suggestions
- keine

## Validation Checks (alle)
- ✅ **V_enso_phase**: Layer-2-ENSO-Klassifikation stimmt mit offiziellem NOAA ONI überein
  - Erwartet: el_nino
  - Beobachtet: el_nino
- ✅ **V_kp_consistency**: Modell-Kp und NOAA-Kp im gleichen Zeitfenster konsistent
  - Erwartet: |Δ Kp| <= 1.0  (Fenster: current_1m)
  - Beobachtet: model_current=3.0  vs  noaa_current=3.0  →  |Δ|=0.00
- ⚠️ **V_storm_atmosphere**: Bei >= 5 offenen Sturm-Events weltweit ist L3 >= 0.3
  - Erwartet: L3 >= 0.3
  - Beobachtet: L3 = 0.191
- ❓ **V_schumann_data_availability**: Externe Schumann-Resonanz-Messdaten für Vergleich verfügbar
  - Erwartet: real-time SR1 amplitude/frequency feed
  - Beobachtet: no public feed available
- ✅ **V_consistency_tags**: Baseline-Tags und Signal-Tags sind disjunkt
  - Erwartet: no overlap
  - Beobachtet: overlap = []
- ✅ **V_consistency_seasonal**: seasonal_transition_state: preparation > 0.45 und downstream < 0.35
  - Erwartet: prep > 0.45 AND downstream < 0.35
  - Beobachtet: prep=0.616, downstream=0.307
- ✅ **V_backtest_carnegie_anomalous**: anomalous_resonance_state tritt überwiegend (>= 80%) abends auf
  - Erwartet: >= 80% evening
  - Beobachtet: 100.0% evening (6/6)
- ✅ **V_backtest_enso_consistency**: Bei externem ONI >= 0.2 sind >= 50% der Snapshots warm-klassifiziert
  - Erwartet: >= 50% warm
  - Beobachtet: 89.6% warm