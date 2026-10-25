# Holarchic Coupling Analysis — Report V1

**Run:** 2026-10-25T13:16:05.698473+00:00  
**Snapshots:** 539  
**Holons:** 11 (0 uninstrumented)

## 1. Welche Skala dominiert?

| Holon | Layer | Scale | mean score | Status |
|---|---|---|---|---|
| H_external | L0 | global | 0.199 | measured |
| H_lithosphere | L1 | global | 0.399 | measured |
| H_macro_ocean | L2 | basin/global | 0.602 | measured |
| H_meso_conv | L2p5 | regional | 0.690 | proxy |
| H_micro_storm | L3 | local | 0.203 | measured |
| H_field_iono | L4 | global | 0.315 | measured |
| H_field_gec | L5 | global | 0.336 | measured |
| H_field_reso | L6 | global | 0.284 | proxy |
| H_obs_diag | L7 | system | **n/a** | measured (keine Werte) |
| H_obs_learn | L8 | system | **n/a** | measured (keine Werte) |
| H_obs_valid | L9 | system | **n/a** | measured (keine Werte) |
Makro-Vorbereitung (`H_macro_ocean`) ist der höchste physische Score, Mikro-Aktivierung (`H_micro_storm`) der niedrigste. Die Meso-Skala ist instrumentiert (Wolken-Uebergangsproxy, `confound_type=proxy`); n=369 Snapshots mit Meso-Daten, s. Kopplungstabelle unten.

## 2. Wo bricht die Kette?

Empirische Kopplungsstärken entlang der Aktivierungskette:

| Span | Typ | r | n | Evidenz |
|---|---|---|---|---|
| H_macro_ocean→H_meso_conv | top_down_constraint | +0.125 | 369 | negligible |
| H_meso_conv→H_micro_storm | bottom_up_aggregation | -0.206 | 368 | weak |
| H_micro_storm→H_field_gec | bottom_up_aggregation | +0.072 | 539 | negligible |
| H_field_gec→H_field_reso | field_feedback | +0.401 | 539 | moderate |

**Befund:** Der Downstream-Abschnitt (micro→electric→resonance) ist intakt und stark. Der einzige Bruch sitzt bei **macro→micro** und ist in 429/539 Snapshots (80%) die dominante Bruchstelle. Er ist **nicht lokalisierbar**, weil die Meso-Ebene keine Datenquelle hat.

Break-Verteilung über die History: `macro_to_micro`=429, `electric_to_resonance`=41, `micro_to_electric`=39, `none`=30

## 3. Welche Rückkopplung ist plausibel?

- `H_field_iono→H_field_reso`: r=+0.278 (weak) — Cavity-Hoehe/Leitfaehigkeit moduliert Frequenz und Q
- `H_field_gec→H_field_reso`: r=+0.401 (moderate) — GEC ist die elektrische Architektur der Resonanz

Das Resonanzfeld (`H_field_reso`) ist als **proxy** markiert (non-geometrischer Anteil modelliert, nicht direkt gemessen). Kopplungen *in* dieses Holon dürfen nicht als unabhängige Bestätigung gelten.

## 4. Welche Evidenz fehlt?

1. **Meso-Skala — unabhaengige Organisationsmessung.** Instrumentiert seit kurzem ueber einen Wolken-Uebergangsproxy (`confound_type=proxy`); die Kettenbruch-LOKALISIERUNG (macro→meso vs. meso→micro, statt nur macro→micro) nutzt den Meso-Score selbst noch nicht und bleibt bis dahin blind. Echtes OLR wuerde die Kopplung von proxy auf measured heben.
2. **Unabhängiger Resonanz-Messwert** — um `H_field_reso` von proxy auf measured zu heben.
3. **Mehr Aktivierungs-Events** — Downstream-Kopplung ist nur sichtbar, wenn L3 zündet; bei dominanter Bruchstelle macro→micro gibt es davon wenige.

## 5. Empfohlener nächster Datenschritt

Meso ist instrumentiert (Wolken-Proxy) und persistiert (`layer2p5_meso_state.json`), aber zwei Schritte offen: (a) genug Historie ansammeln, bis die L2→L2.5/L2.5→L3-Kopplung oben eine belastbare Fallzahl hat, (b) die Kettenbruch-Lokalisierung (`_locate_break`) so erweitern, dass sie den Meso-Score selbst befragt statt nur macro/micro — erst dann wird `macro_to_micro` (blind) zu `macro_to_meso` ODER `meso_to_micro` (lokalisiert) auflösbar. Echtes OLR (statt Wolken-Proxy) bliebe danach der Schritt von proxy zu measured.
