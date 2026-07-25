# Meso Layer Integration — H_meso_conv (L2.5)

Instrumentiert die fehlende Skala zwischen L2 (ENSO/SST, weeks-months) und
L3 (CAPE/Gewitter, minutes-hours). Mediator-Holon. Löst den bisher blinden
`macro_to_micro`-Bruch auf.

## Was der Layer physikalisch macht

Nicht „mehr CAPE" (das ist L3), sondern **Organisation**: ob makroskalige
Vorbereitung sich in organisierte Konvektion umsetzt — und ob diese realisiert
oder gedeckelt wird.

```
organisation = w*MJO + w*OLR + w*Scherung + w*MidLevelRH   (+ optional Iorg)
meso_score   = organisation × cin_gate(CIN)
```

CIN ist **multiplikativ** (Gate), nicht additiv. Dadurch trennt der Layer zwei
physikalisch verschiedene Brüche:

| Zustand | Bruch | Bedeutung |
|---|---|---|
| Organisation niedrig | `macro_to_meso` | Vorbereitung organisiert sich nicht (MJO/Scherung/Feuchte fehlen) |
| Organisation hoch, Gate offen, micro low | `meso_to_micro` (other) | organisiert, nicht gedeckelt, zündet trotzdem nicht (Timing) |
| Organisation hoch, Gate zu | `meso_to_micro` (cin_cap) | organisiert, aber CIN-gedeckelt → keine Realisierung |

## Datenquellen (in deine Ingestion-Zelle wiren)

Modul ist feed-agnostisch — `score_meso(dict)` nimmt normalisierte Inputs.
Pflicht-Feeds (siehe `MESO_SOURCES` für Produkt/Variable/Kadenz):

- **MJO**: BoM RMM (Wheeler-Hendon) — Amplitude + Phase, daily
- **OLR-Anomalie**: NOAA interpolated OLR, daily
- **0–6 km Scherung**: ERA5 / GFS, 6-hourly
- **Mid-Level RH** (700–500 hPa): ERA5 / GFS, 6-hourly
- **CIN**: ERA5 / GFS / SPC mesoanalysis, hourly–6-hourly
- *optional* **Iorg** (Aggregationsindex aus IR Tb<241K oder IMERG)

Der Layer rechnet auch mit Teil-Inputs (Gewichte renormalisieren über
Verfügbares) und meldet `confidence` = Anteil vorhandener Kern-Inputs.

## Platzierung im Stack

Neue Layer-ID `L2p5_meso_convection`. In deinem Snapshot-Run nach L2, vor L3:

```python
from layer_meso import score_meso
meso = score_meso(meso_inputs)            # meso_inputs aus Ingestion
snapshot["layers"]["L2p5_meso_convection"] = meso
```

Schema ist identisch zu L0–L6 (score, level, confidence, dominant_component,
flags, key_metrics) plus meso-spezifisch `organisation` und `cin_gate`.

## Kopplungen, die jetzt beobachtbar werden

In L7 die zwei bisher als `unobservable_no_meso_data` markierten Spans aktiv
schalten:

- `H_macro_ocean → H_meso_conv` (top_down_constraint): ENSO/SST → Organisation
- `H_meso_conv → H_micro_storm` (bottom_up_aggregation): Organisation → Zellen

Sobald ~30–40 Snapshots mit echtem Meso vorliegen, berechnet die Holarchic
Coupling Analysis V1 für beide Spans echte Pearson-Werte statt `—`. Der
`chain_break_distribution`-Block teilt sich dann real auf.

## Holarchie-Update

In `holarchic_coupling_analysis.py`:
- `H_meso_conv` Status `inferred` → `measured`, `layer: L2p5_meso_convection`
- `localise_break` aus `layer_meso.py` ersetzt die blinde macro→micro-Logik

## Demo-Ergebnis (SYNTHETISCHE Inputs — nur Mechanik-Test)

Mit synthetischem Meso-Backfill über die 106 Timestamps spalten sich die 90
blinden `macro_to_micro`-Brüche in `macro_to_meso` und `meso_to_micro` (inkl.
CIN-Cap-Attribution). Die Verhältnisse sind **illustrativ, kein Befund** —
sie hängen vollständig an den synthetischen Treibern. Erst mit echten Feeds
wird die Aufteilung physikalisch aussagekräftig.

## Vor dem ersten echten Run zu kalibrieren

Die Schwellen sind Literatur-Defaults, kein Fit an dein System:
- `cin_gate(soft=25, hard=150)` J/kg — regional anpassen
- Scherungs-Optimum 12–18 m/s — je nach Breitengrad/Regime verschieben
- Organisations-Gewichte `_BASE_WEIGHTS` — nach ersten echten Daten gewichten

Empfehlung: erst 1–2 Wochen Meso-Daten ohne Promotion sammeln, dann Schwellen
gegen beobachtete L3-Realisierung kalibrieren — und zwar mit der Confound-Sperre
aktiv, damit die Kalibrierung nicht auf zirkulären Operatoren beruht.
