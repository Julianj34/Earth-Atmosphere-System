# Earth-Atmosphere-System

Gekoppeltes Multi-Layer-Zustandsanalyse-System für das Erd-Atmosphäre-System
(**L0–L9** plus Meso-Skala **L2.5** und holarchische Meta-Analyse). Läuft vollständig
lokal — die Pipeline braucht kein GitHub, keine Cloud, keinen Scheduler.

> **Earth Field Observatory** — untersucht, wann Oberfläche, Ozean, Atmosphäre,
> Ionosphäre, Globaler Stromkreis (GEC) und Resonanzfeld gemeinsam in bestimmte
> Systemzustände übergehen.

**Status:** post-holarchy Refactor · ~108 Snapshots · Meso-Skala aktiv über
Wolken-Übergangsproxy (echtes OLR wartet auf Quellen-Migration)

---

## Kernidee

Die Erde wird nicht als isolierte Einzelvariablen analysiert, sondern als
gekoppeltes System — und zwar als **Holarchie von Skalen**, nicht als flacher Stack.
Jeder Layer ist ein *Holon*: ein Ganzes auf seiner eigenen Skala und ein Teil der
Skala darüber.

**Systemformel:**

```
L2   Vorbereitung        (makro, Becken, Wochen–Monate)
 └→ L2.5 Meso-Organisation (meso, regional, Stunden–Tage)   [Mediator]
     └→ L3  Aktivierung     (mikro, lokal, Minuten–Stunden)
         └→ L5  Elektrische Antwort (GEC)
             └→ L6  Resonanz-Antwort  (Proxy)
                 └→ L8  Muster / Hypothesen  (confound-gated)
                     └→ L9  Externe Validierung
```

Der zentrale strukturelle Befund dieser Version: Die Aktivierungskette ist
**ab L3 abwärts intakt und stark, aber am Makro→Mikro-Übergang (L2→L3) gebrochen**.
Dieser Bruch ist kein Modellfehler — es ist eine **fehlende Skala**. Genau dort
sitzt jetzt der Meso-Holon `H_meso_conv` (L2.5).

---

## Layer-Architektur

| Layer | Holon | Skala / Zeitskala | Rolle | Status |
|-------|-------|-------------------|-------|--------|
| L0 | `H_external` | global / Minuten–Tage | driver | measured |
| L1 | `H_lithosphere` | global / Stunden–Tage | driver | measured |
| L2 | `H_macro_ocean` | Becken·global / Wochen–Monate | constraint | measured |
| **L2.5** | **`H_meso_conv`** | **regional / Stunden–Tage** | **mediator** | **measured\* (cloud-proxy)** |
| L3 | `H_micro_storm` | lokal / Minuten–Stunden | response | measured |
| L4 | `H_field_iono` | global / Minuten–Tage | mediator | measured |
| L5 | `H_field_gec` | global / Minuten–Tage | response | measured |
| L6 | `H_field_reso` | global / Minuten–Tage | response | **proxy** (teilmodelliert) |
| L7 | `H_obs_diag` | System / pro Lauf | measurement | measured |
| L8 | `H_obs_learn` | System / langfristig | measurement | measured |
| L9 | `H_obs_valid` | System / langfristig | measurement | measured |

**Legende Beobachtungsstatus:**

```
measured  = direkte Beobachtung
proxy     = modellierte Näherung — zählt NIE als unabhängige Bestätigung
inferred  = physikalisch erwartet, aber in diesem System nicht instrumentiert
```

\* **cloud-proxy** = L2.5 wird über einen *realen, aber schwächeren* Ersatz-Feed
gemessen (Gesamtbewölkung aus L3 / Open-Meteo), solange die primäre OLR-Quelle
nicht verfügbar ist. Explizit geflaggt (`organisation_source="cloud_proxy"`),
nie still, nie synthetisch.

**Saubere architektonische Trennung:**

```
Layer 0–6   →   Physikalische / datenbasierte Zustände (die eigentliche Holarchie)
Layer 7     →   State Engine (schreibt, forscht nicht)
Layer 8     →   Musteranalyse + Hypothesen (liest History, confound-gated)
Layer 9     →   Externe Validierung (NOAA CPC ONI, NOAA SWPC, NASA EONET)
```

---

## Empirische Kopplungsmatrix (n ≈ 108 Snapshots)

| Kopplung | r (Pearson) | Evidenz | Confounded | Mechanismus |
|----------|-------------|---------|------------|-------------|
| L2 → L2.5 | — | pending | — | ENSO/SST setzt regionale Konvektionswahrscheinlichkeit; Meso jetzt instrumentiert, Statistik wartet auf History |
| L2.5 → L3 | — | pending | — | Organisierte konvektive Systeme → Gewitterzellen / Blitze |
| **L3 → L5** | +0.649 | stark (roh) | **ja — zirkulär** | Gewitter laden den Generator (CAPE → V_iono); aber L5 wird deterministisch aus L3 berechnet |
| L3 → L6 | +0.481 | moderat | ja (proxy) | Blitze regen Schumann-Resonanz an |
| L4 → L6 | −0.196 | vernachlässigbar | ja (proxy) | Kavitätshöhe / Leitfähigkeit moduliert Frequenz & Q |
| **L5 → L6** | +0.603 | stark | ja (proxy) | GEC ist die elektrische Architektur der Resonanz |
| L0 → L4 | +0.380 | schwach | nein | Solarwind / F10.7 / X-Ray ionisieren die Ionosphäre |
| L0 → L5 | +0.132 | vernachlässigbar | nein | Kp moduliert ionosphärische Leitfähigkeit (GEC-Widerstand) |

**Wichtig beim Lesen:** Die stärksten Korrelationen des Systems (L3→L5, L5→L6)
sind **keine unabhängige Bestätigung**. L5 ist eine deterministische Transformation
von L3 (`0.5·CAPE_L3 + 0.5·thunder_L3`) — die Korrelation ist erzwungen, nicht
evidenziell. Diese Zirkularität ist explizit kodiert (`CIRCULAR_COUPLINGS`-Set,
`confound_type`-Spalte) und wird vom Promotion-Lock in L8 durchgesetzt: zirkuläre
und Proxy-Kopplungen können nie zu bestätigten Hypothesen befördert werden.
Das echte Backbone sind **H1, H6 und die thermal→L3 Lead-Lag-Beziehung**.

---

## Konservative Inferenz als Projektprinzip

Statistische Erweiterungen sind **explizit aufgeschoben**, bis die Datenmenge sie
rechtfertigt — das ist ein stehendes Projektprinzip, keine vorübergehende Notlösung:

- Bootstrap-Konfidenzintervalle, p-Werte, Spearman-Korrelationen: erst wenn die
  Meso-Zeitreihe mindestens eine Konvektionssaison umfasst
- Regressionsmodelle mit Dreifach-Interaktionstermen und ein Kopplungstensor über
  acht Zustandsdimensionen: gleiche Bedingung
- Aktuell: ~63 vollständige Tagespaare, ~92 % davon in `seasonal_transition_state`
  — zu homogen für belastbare Interaktionsstatistik

Hypothesen durchlaufen eine explizite, evidenz-basierte State Machine
(`active → idle → dormant → retired/accepted` mit `missing_runs`-Tracking) statt
automatischer Retirement-Heuristiken.

---

## Repository-Struktur

```
Earth-Atmosphere-System/
├── notebooks/          Layer-Scoring L0–L9 (Interface)
├── src/atmosphere/
│   ├── paths.py        zentrale Pfadauflösung (CWD-unabhängig)
│   ├── config/         domain.py (OM_POINTS/TIME_BASIS — eine Quelle für L2/L3/Meso)
│   ├── layers/         layer_meso.py (L2.5)
│   ├── ingest/         meso_ingest.py (OLR-Feed + Wolken-Fallback + CIN aus L3)
│   └── meta/           role_proxy_writeback.py, holarchic_coupling_analysis.py
├── states/
│   ├── current/        layer{0..9}_state.json
│   ├── history/        layer7_history.jsonl
│   ├── registry/       hypothesis_registry.json, holon_registry.yaml
│   └── coupling/       holarchic_coupling_matrix.csv, holarchic_event_card.json
├── reports/            layer8_report.md, layer9_report.md, holarchic_analysis_report.md
├── config/             meso_feeds.yaml
├── pipeline/           run_pipeline.py
└── .github/workflows/  run_pipeline.yml
```

`.project-root` ist eine leere Markerdatei im Projekt-Top — jedes Notebook findet
darüber die Projektwurzel, unabhängig davon, von wo Jupyter gestartet wurde.

---

## Setup & Ausführung

```bash
pip install -r requirements.txt
pip install -e .          # optional; die Notebooks haben einen eigenen Bootstrap

# Setup prüfen (läuft ohne Internet in Sekunden):
python -c "import atmosphere.paths as p; print(p.ROOT)"
python pipeline/run_pipeline.py --holarchic
```

**Ganze Kette:**

```bash
python pipeline/run_pipeline.py
```

Führt L0…L9 der Reihe nach aus (jedes Notebook schreibt seinen State nach
`states/current/`; L7 hängt an `states/history/layer7_history.jsonl` an) und
danach die holarchische Meta-Analyse.

**Nützliche Optionen:**

```bash
python pipeline/run_pipeline.py --from 7      # ab L7 fortsetzen
python pipeline/run_pipeline.py --only 7 8 9  # nur diese Layer
python pipeline/run_pipeline.py --holarchic   # nur die Meta-Analyse über die History
```

Einzelne Notebooks lassen sich normal in Jupyter öffnen — der Bootstrap in Zelle 1
löst die Pfade selbst auf, egal von wo Jupyter gestartet wurde.

---

## Meso-Layer (L2.5) — Status & Datenquelle

`layer_meso` läuft **nicht** auf synthetischen Daten und ist nicht blockiert:

- **CIN** (das multiplikative Gate) stammt aus L3 (`raw_values.CIN_mean_Jkg`) —
  kein neuer Feed, automatisch an dieselbe Stichprobengeometrie alignt.
- **Organisation**: primär OLR-Anomalie. Alle vier bekannten Live-OLR-Quellen sind
  derzeit unbrauchbar (PSL eingefroren auf Ende 2022, NCEI 404, AWS NODD ohne
  skriptbaren Pfad, IRI Timeout). Ein **Staleness-Guard** (> 10 Tage → ablehnen)
  verhindert, dass alte Werte einsickern.
- **Fallback**: Gesamtbewölkung aus L3 (Open-Meteo) tritt in denselben Slot; der
  Holon wird `measured` mit `organisation_source="cloud_proxy"`. Schwächer als
  echtes OLR (zählt auch nicht-konvektive Schichtbewölkung mit) — deshalb
  konservativ geschwellt und ehrlich als Übergang markiert.
- **Swap-Punkt**: Sobald wieder eine Live-OLR-Tagesquelle existiert, wird nur die
  Konstante `_OLR_DAILY` in `meso_ingest.py` umgestellt. OLR hat dann automatisch
  wieder Vorrang, der Wolken-Pfad fällt still in die Reserve.

---

## Confound-Guard

Diese Invarianten setzt `meta/role_proxy_writeback.py` bei jedem Lauf durch, bevor
L7 und L8 ihre States schreiben:

- **L5 ist `derived_proxy` von L3** — `generator_strength` wird aus CAPE und
  Gewitterscore berechnet, ist also keine unabhängige Messung.
- **L6 ist `proxy`** — der nicht-geometrische Anteil ist modelliert
  (`measurement_status: model_expected_not_observed`).
- **Der thermal-Operator ist L2-only** und damit der einzige saubere
  Cross-Scale-Prädiktor unter den Feldoperatoren.
- **Promotion-Lock:** zirkuläre, Proxy- und unklassifizierte Evidenz wird hart von
  der Modelllogik ausgeschlossen — unabhängig vom Review-Status.
- **Die holarchische Matrix** markiert L3→L5 als `circular` und die
  L6-Kopplungen als `proxy` (`confound_type`-Spalte in
  `holarchic_coupling_matrix.csv`).
- **`layer_meso`** gatet CIN multiplikativ und fällt defensiv auf
  `source_status="inferred"` zurück, wenn die Stichprobe nicht exakt zu L3 passt.

---

## Roadmap

- **Kurzfristig:** Meso-State (`layer2p5_meso_state.json`) persistieren und in die
  `layer7_history` einspeisen; Score-Normalisierung im
  `cross_layer_activation_operator` auf Median/MAD-basierte z-Scores umstellen
- **Mittelfristig:** deskriptiver Topologie-Klassifikator
  (`state_dependent_effect_topology.py`), sobald Meso-History akkumuliert ist
- **Aufgeschoben** (bis ≥ 1 Konvektionssaison Meso-Zeitreihe): Interaktions-
  Regressionen, Kopplungstensor, Bootstrap-CIs
- **Offen:** Live-OLR-Quelle — bekannte Endpunkte ausgeschöpft, wird periodisch
  neu geprüft

---

## Lizenz

MIT — siehe [LICENSE](LICENSE).
