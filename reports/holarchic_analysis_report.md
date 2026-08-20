# Holarchic Coupling Analysis — Report V1

**Run:** 2026-08-20T20:53:06.190460+00:00  
**Snapshots:** 279  
**Holons:** 11 (0 uninstrumented)

## 1. Welche Skala dominiert?

| Holon | Layer | Scale | mean score | Status |
|---|---|---|---|---|
| H_external | L0 | global | 0.213 | measured |
| H_lithosphere | L1 | global | 0.384 | measured |
| H_macro_ocean | L2 | basin/global | 0.574 | measured |
| H_meso_conv | L2p5 | regional | 0.654 | proxy |
| H_micro_storm | L3 | local | 0.196 | measured |
| H_field_iono | L4 | global | 0.326 | measured |
| H_field_gec | L5 | global | 0.354 | measured |
| H_field_reso | L6 | global | 0.298 | proxy |
| H_obs_diag | L7 | system | **n/a** | measured (keine Werte) |
| H_obs_learn | L8 | system | **n/a** | measured (keine Werte) |
| H_obs_valid | L9 | system | **n/a** | measured (keine Werte) |
Makro-Vorbereitung (`H_macro_ocean`) ist der höchste physische Score, Mikro-Aktivierung (`H_micro_storm`) der niedrigste. Die Meso-Skala ist instrumentiert (Wolken-Uebergangsproxy, `confound_type=proxy`); n=109 Snapshots mit Meso-Daten, s. Kopplungstabelle unten.

## 2. Wo bricht die Kette?

Empirische Kopplungsstärken entlang der Aktivierungskette:

| Span | Typ | r | n | Evidenz |
|---|---|---|---|---|
| H_macro_ocean→H_meso_conv | top_down_constraint | -0.136 | 109 | negligible |
| H_meso_conv→H_micro_storm | bottom_up_aggregation | -0.181 | 108 | negligible |
| H_micro_storm→H_field_gec | bottom_up_aggregation | +0.490 | 279 | moderate |
| H_field_gec→H_field_reso | field_feedback | +0.521 | 279 | moderate |

**Befund:** Der Downstream-Abschnitt (micro→electric→resonance) ist intakt und stark. Der einzige Bruch sitzt bei **macro→micro** und ist in 244/279 Snapshots (87%) die dominante Bruchstelle. Er ist **nicht lokalisierbar**, weil die Meso-Ebene keine Datenquelle hat.

Break-Verteilung über die History: `macro_to_micro`=244, `none`=22, `electric_to_resonance`=10, `micro_to_electric`=3

## 3. Welche Rückkopplung ist plausibel?

- `H_field_iono→H_field_reso`: r=+0.186 (negligible) — Cavity-Hoehe/Leitfaehigkeit moduliert Frequenz und Q
- `H_field_gec→H_field_reso`: r=+0.521 (moderate) — GEC ist die elektrische Architektur der Resonanz

Das Resonanzfeld (`H_field_reso`) ist als **proxy** markiert (non-geometrischer Anteil modelliert, nicht direkt gemessen). Kopplungen *in* dieses Holon dürfen nicht als unabhängige Bestätigung gelten.

## 4. Welche Evidenz fehlt?

1. **Meso-Skala — unabhaengige Organisationsmessung.** Instrumentiert seit kurzem ueber einen Wolken-Uebergangsproxy (`confound_type=proxy`); die Kettenbruch-LOKALISIERUNG (macro→meso vs. meso→micro, statt nur macro→micro) nutzt den Meso-Score selbst noch nicht und bleibt bis dahin blind. Echtes OLR wuerde die Kopplung von proxy auf measured heben.
2. **Unabhängiger Resonanz-Messwert** — um `H_field_reso` von proxy auf measured zu heben.
3. **Mehr Aktivierungs-Events** — Downstream-Kopplung ist nur sichtbar, wenn L3 zündet; bei dominanter Bruchstelle macro→micro gibt es davon wenige.

## 5. Empfohlener nächster Datenschritt

Meso ist instrumentiert (Wolken-Proxy) und persistiert (`layer2p5_meso_state.json`), aber zwei Schritte offen: (a) genug Historie ansammeln, bis die L2→L2.5/L2.5→L3-Kopplung oben eine belastbare Fallzahl hat, (b) die Kettenbruch-Lokalisierung (`_locate_break`) so erweitern, dass sie den Meso-Score selbst befragt statt nur macro/micro — erst dann wird `macro_to_micro` (blind) zu `macro_to_meso` ODER `meso_to_micro` (lokalisiert) auflösbar. Echtes OLR (statt Wolken-Proxy) bliebe danach der Schritt von proxy zu measured.
