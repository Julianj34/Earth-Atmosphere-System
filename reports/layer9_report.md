# Layer 9 — External Grounding & Validation

**Run:** 2026-08-26T23:46:18.056813Z
**Validation Score:** 0.9167  (exploratory_signal)

## Aggregat
- ✅ Passed:       5
- ❌ Failed:       0
- ⚠️  Uncertain:  1
- ❓ Inconclusive: 1

## Failed Checks
- keine

## Uncertain Checks
- **V_storm_atmosphere** (storm_validation): EONET open storms=7. L3=0.200, active_thunderstorms=False

## Model Adjustment Suggestions
- keine

## Validation Checks (alle)
- ✅ **V_enso_phase**: Layer-2-ENSO-Klassifikation stimmt mit offiziellem NOAA ONI überein
  - Erwartet: el_nino
  - Beobachtet: el_nino
- ⚠️ **V_storm_atmosphere**: Bei >= 5 offenen Sturm-Events weltweit ist L3 >= 0.3
  - Erwartet: L3 >= 0.3
  - Beobachtet: L3 = 0.200
- ❓ **V_schumann_data_availability**: Externe Schumann-Resonanz-Messdaten für Vergleich verfügbar
  - Erwartet: real-time SR1 amplitude/frequency feed
  - Beobachtet: no public feed available
- ✅ **V_consistency_tags**: Baseline-Tags und Signal-Tags sind disjunkt
  - Erwartet: no overlap
  - Beobachtet: overlap = []
- ✅ **V_consistency_seasonal**: seasonal_transition_state: preparation > 0.45 und downstream < 0.35
  - Erwartet: prep > 0.45 AND downstream < 0.35
  - Beobachtet: prep=0.605, downstream=0.252
- ✅ **V_backtest_carnegie_anomalous**: anomalous_resonance_state tritt überwiegend (>= 80%) abends auf
  - Erwartet: >= 80% evening
  - Beobachtet: 100.0% evening (6/6)
- ✅ **V_backtest_enso_consistency**: Bei externem ONI >= 0.2 sind >= 50% der Snapshots warm-klassifiziert
  - Erwartet: >= 50% warm
  - Beobachtet: 89.4% warm