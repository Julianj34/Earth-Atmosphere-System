# Layer 8 — Research Report

**Run:** 2026-08-16T20:44:52.851022Z
**Snapshots analysiert:** 263
**Vollständige Tagespaare:** 43

## System-State Häufigkeit

- `seasonal_transition_state` — 246× (93.5%)
- `cavity_condition_shift_state` — 6× (2.3%)
- `anomalous_resonance_state` — 6× (2.3%)
- `geomagnetic_disturbance_state` — 3× (1.1%)
- `normal_background_state` — 2× (0.8%)

## Tagespaare (ΔL3 Aktivierung)

| Datum | L3 früh | L3 abend | ΔL3 | Abend-State |
|---|---|---|---|---|
| 2026-05-04 | 0.170 | 0.236 | +0.066 | anomalous_resonance |
| 2026-05-08 | 0.133 | 0.197 | +0.064 | anomalous_resonance |
| 2026-05-09 | 0.150 | 0.149 | -0.002 | seasonal_transition |
| 2026-05-11 | 0.103 | 0.166 | +0.063 | seasonal_transition |
| 2026-05-12 | 0.103 | 0.157 | +0.054 | anomalous_resonance |
| 2026-05-18 | 0.176 | 0.187 | +0.011 | seasonal_transition |
| 2026-05-19 | 0.170 | 0.229 | +0.059 | seasonal_transition |
| 2026-05-22 | 0.222 | 0.221 | -0.001 | seasonal_transition |
| 2026-05-23 | 0.163 | 0.178 | +0.015 | seasonal_transition |
| 2026-05-26 | 0.145 | 0.151 | +0.005 | seasonal_transition |
| 2026-05-27 | 0.123 | 0.127 | +0.004 | seasonal_transition |
| 2026-06-02 | 0.148 | 0.190 | +0.042 | seasonal_transition |
| 2026-06-05 | 0.183 | 0.242 | +0.059 | cavity_condition_shift |
| 2026-06-08 | 0.157 | 0.227 | +0.070 | seasonal_transition |
| 2026-06-09 | 0.245 | 0.233 | -0.011 | seasonal_transition |
| 2026-06-11 | 0.223 | 0.211 | -0.012 | seasonal_transition |
| 2026-06-16 | 0.174 | 0.237 | +0.063 | seasonal_transition |
| 2026-06-28 | 0.206 | 0.173 | -0.033 | seasonal_transition |
| 2026-07-09 | 0.165 | 0.193 | +0.028 | seasonal_transition |
| 2026-07-13 | 0.181 | 0.236 | +0.055 | seasonal_transition |
| 2026-07-16 | 0.257 | 0.294 | +0.037 | normal_background |
| 2026-07-20 | 0.129 | 0.198 | +0.069 | seasonal_transition |
| 2026-07-21 | 0.197 | 0.206 | +0.008 | seasonal_transition |
| 2026-07-25 | 0.200 | 0.301 | +0.102 | seasonal_transition |
| 2026-07-28 | 0.221 | 0.184 | -0.037 | seasonal_transition |
| 2026-07-29 | 0.147 | 0.160 | +0.012 | seasonal_transition |
| 2026-07-30 | 0.150 | 0.181 | +0.031 | seasonal_transition |
| 2026-07-31 | 0.162 | 0.196 | +0.034 | seasonal_transition |
| 2026-08-01 | 0.184 | 0.178 | -0.006 | seasonal_transition |
| 2026-08-02 | 0.149 | 0.191 | +0.042 | seasonal_transition |
| 2026-08-03 | 0.216 | 0.194 | -0.022 | seasonal_transition |
| 2026-08-04 | 0.183 | 0.171 | -0.012 | seasonal_transition |
| 2026-08-05 | 0.173 | 0.164 | -0.009 | seasonal_transition |
| 2026-08-07 | 0.162 | 0.186 | +0.025 | seasonal_transition |
| 2026-08-08 | 0.145 | 0.150 | +0.005 | geomagnetic_disturbance |
| 2026-08-09 | 0.109 | 0.187 | +0.078 | seasonal_transition |
| 2026-08-10 | 0.159 | 0.245 | +0.086 | seasonal_transition |
| 2026-08-11 | 0.165 | 0.194 | +0.029 | seasonal_transition |
| 2026-08-12 | 0.172 | 0.256 | +0.083 | seasonal_transition |
| 2026-08-13 | 0.194 | 0.202 | +0.008 | seasonal_transition |
| 2026-08-14 | 0.181 | 0.172 | -0.009 | seasonal_transition |
| 2026-08-15 | 0.153 | 0.199 | +0.046 | seasonal_transition |
| 2026-08-16 | 0.148 | 0.211 | +0.063 | seasonal_transition |

**ΔL3-Schwelle (empirisch):** +0.049

## L2 ↔ L3 Beziehung

- Pearson: **-0.023**
- L2 Trend: +0.00006 / Snapshot
- L3 Trend: +0.00006 / Snapshot
- Gap-Trend: -0.00000 / Snapshot
- Schwache Kopplung sichtbar — mehr Daten nötig.

## Field Operators

Coverage: 245/263 Snapshots

### Aktuelle Operator-Rangliste

- **resonance_model**: 0.457 — modellierter nicht-geometrischer Anteil über Cavity-Geometrie hinaus
- **thermal**: 0.427 — moderate thermische Vorbereitung vorhanden
- **ionization**: 0.314 — moderate ionosphärische Modulation
- **electric**: 0.279 — GEC nahe Referenz, keine elektrische Aktivierung  ⚠️ confounded_circular
- **cross_layer_activation**: 0.176 — schwache Übergangsspannung bei L2_to_L3  ⚠️ confounded_circular
- **geomagnetic**: 0.110 — ruhige geomagnetische Bedingungen

### Operator ↔ ΔL3 Korrelation

- electric: r = +0.377  ⚠️ **confounded_circular** — Operator enthält L3, kein unabhängiger Prädiktor
- resonance_model: r = +0.297
- ionization: r = -0.144
- geomagnetic: r = -0.100
- thermal: r = -0.082
- cross_layer_activation: r = -0.029  ⚠️ **confounded_circular** — Operator enthält L3, kein unabhängiger Prädiktor

## Hypothesen

### ⚠️ H1: Tritt anomalous_resonance_state ausschließlich abends (>= 18 MESZ) auf?  ✓ unabhängig (Backbone)

- **Status:** mixed
- **Evidenz:** 3/6 Anomalous-Events im Abend-Slot (50.0%). Morning: 0.
- **Nächster Schritt:** Mehr Snapshots; ggf. mittäglichen Slot ergänzen für Bestätigung.

### 🚫 H4: Moduliert L6_evening die Carnegie-Amplitude (L5 abends)?

- **Status:** confound_blocked (confounded_proxy) — nicht promotbar, nur exploratorisch
- **Evidenz:** Pearson L5_evening vs L6_evening = +0.815 über 43 Abende.
- **Nächster Schritt:** Korrelation in größerer Stichprobe bestätigen.

### 🚫 H_combined: Ist combined_activation_score (ΔL3+L5+L6) besser als ΔL3 allein?

- **Status:** confound_blocked (confounded_circular) — nicht promotbar, nur exploratorisch
- **Evidenz:** combined Overlap=True vs ΔL3 Overlap=True. combined Schwelle=0.4200.
- **Nächster Schritt:** Mehr Tagespaare für robuste Trennung. ROC-Analyse ab n>=20.
