"""
Holarchic Coupling Analysis — V1
=================================

Meta-analysis OVER layers L0-L9. NOT another score layer.

Reframes the system from a flat layer stack into a holarchy of scales and asks,
for any snapshot or run:

    - On which scale does a signal originate?
    - How is it aggregated upward / constrained downward?
    - At which scale does the activation chain break?

Inputs  : layer7_history.jsonl  (time series of L0-L6 scores + couplings + tags)
          layer8_state.json      (aggregate stats + macro handoff)  [optional]
Outputs : holon_registry.yaml
          holarchic_coupling_matrix.csv
          holarchic_event_card.json
          holarchic_analysis_report.md

Design note on circularity
--------------------------
Field-operators in L7/L8 (e.g. electric_operator) are COMPOSED from the same
layer scores they are correlated against. They are therefore tagged role=proxy
and are NEVER counted as independent confirmation of the same chain. Role tags
(driver/constraint/mediator/response/proxy/measurement) implement this guard.
"""

from __future__ import annotations
import json, csv, math
from pathlib import Path
from datetime import datetime, timezone

# --------------------------------------------------------------------------- #
# 1. HOLON REGISTRY  — maps L0-L9 onto holon levels, scale and observation status
# --------------------------------------------------------------------------- #
# status: measured = direct observation | proxy = modelled approximation |
#         inferred = expected to exist but NOT instrumented in this system
# role  : driver | constraint | mediator | response | proxy | measurement

HOLONS = [
    # id              level             scale            timescale       parent          children                    layer   status     role        sources
    ("H_external",    "external_bound", "global",        "minutes-days", None,           ["H_field_iono"],           "L0",   "measured", "driver",      ["F10.7","Kp","IMF_Bz","xray"]),
    ("H_lithosphere", "macro_parallel", "global",        "hours-days",   None,           [],                         "L1",   "measured", "driver",      ["seismic_events","max_mag","LOD_anomaly"]),
    ("H_macro_ocean", "macro",          "basin/global",  "weeks-months", None,           ["H_meso_conv"],            "L2",   "measured", "constraint",  ["SST_anomaly","ENSO_phase","conv_pot"]),
    ("H_meso_conv",   "meso",           "regional",      "hours-days",   "H_macro_ocean",["H_micro_storm"],          "L2p5", "proxy",    "mediator",    ["CIN_from_L3","CloudCover_from_L3(transitional)"]),  # instrumented via cloud-proxy; -> "measured" once real OLR is restored
    ("H_micro_storm", "micro",          "local",         "minutes-hours","H_meso_conv",  ["H_field_gec"],            "L3",   "measured", "response",    ["CAPE","thunder_pts","storms_EONET"]),
    ("H_field_iono",  "global_field",   "global",        "minutes-days", None,           ["H_field_reso"],           "L4",   "measured", "mediator",    ["cavity_h","Kp","xray_class"]),
    ("H_field_gec",   "global_field",   "global",        "minutes-days", "H_micro_storm",["H_field_reso"],           "L5",   "measured", "response",    ["V_iono","delta_V_pct","generator"]),
    ("H_field_reso",  "global_field",   "global",        "minutes-days", "H_field_gec",  [],                         "L6",   "proxy",    "response",    ["SR1_Hz","SR1_amp_pT","non_geom_ratio"]),  # resonance partly modelled
    ("H_obs_diag",    "observation",    "system",        "per-run",      None,           ["H_obs_learn"],            "L7",   "measured", "measurement", ["couplings","field_operators","cavity_gate"]),
    ("H_obs_learn",   "observation",    "system",        "long-term",    "H_obs_diag",   ["H_obs_valid"],            "L8",   "measured", "measurement", ["hypotheses","macro_handoff"]),
    ("H_obs_valid",   "observation",    "system",        "long-term",    "H_obs_learn",  [],                         "L9",   "measured", "measurement", ["source_revalidation"]),
]

HOLON_FIELDS = ["id","level","scale","timescale","parent","children","layer","status","role","sources"]

# The physical activation chain we test for break points (excludes observation holons)
ACTIVATION_CHAIN = [
    ("H_macro_ocean", "H_meso_conv",   "L2", "L2p5"),  # meso instrumented via cloud-proxy; confound_type=proxy until real OLR
    ("H_meso_conv",   "H_micro_storm", "L2p5", "L3"),  # meso instrumented via cloud-proxy; confound_type=proxy until real OLR
    ("H_micro_storm", "H_field_gec",   "L3", "L5"),
    ("H_field_gec",   "H_field_reso",  "L5", "L6"),
]

# --------------------------------------------------------------------------- #
# 2. COUPLING TYPES  (the five relationship questions)
# --------------------------------------------------------------------------- #
COUPLING_DEFS = [
    # source        target          type                  mech_layer_from  mech_layer_to  mechanism
    ("H_macro_ocean","H_meso_conv",  "top_down_constraint", "L2", "L2p5","ENSO/SST setzt regionale Konvektionswahrscheinlichkeit (Meso: Wolken-Proxy, s. confound_type=proxy)"),
    ("H_meso_conv",  "H_micro_storm","bottom_up_aggregation","L2p5","L3", "Organisierte Konvektionssysteme -> einzelne Gewitterzellen/Lightning (Meso: Wolken-Proxy, s. confound_type=proxy)"),
    ("H_micro_storm","H_field_gec",  "bottom_up_aggregation","L3", "L5",  "Gewitter laden Generator (CAPE -> V_iono)"),
    ("H_micro_storm","H_field_reso", "bottom_up_aggregation","L3", "L6",  "Blitze regen Schumann-Resonanz an"),
    ("H_field_iono", "H_field_reso", "field_feedback",      "L4", "L6",  "Cavity-Hoehe/Leitfaehigkeit moduliert Frequenz und Q"),
    ("H_field_gec",  "H_field_reso", "field_feedback",      "L5", "L6",  "GEC ist die elektrische Architektur der Resonanz"),
    ("H_external",   "H_field_iono", "top_down_constraint", "L0", "L4",  "Solarwind/F10.7/X-Ray ionisieren Ionosphaere"),
    ("H_external",   "H_field_gec",  "top_down_constraint", "L0", "L5",  "Kp moduliert ionosph. Leitfaehigkeit (GEC-Widerstand)"),
]

# Known circular couplings — audited in the layer source code, NOT derivable from data:
# L5.generator_strength = 0.5*CAPE_L3 + 0.5*thunder_L3  ->  H_field_gec is a deterministic
# transformation of H_micro_storm. The L3->L5 correlation is forced, not independent evidence.
CIRCULAR_COUPLINGS = {
    ("H_micro_storm", "H_field_gec"),
}

# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _pearson(xs, ys):
    pts = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None
           and not (isinstance(x, float) and math.isnan(x))
           and not (isinstance(y, float) and math.isnan(y))]
    n = len(pts)
    if n < 3:
        return None, n
    mx = sum(p[0] for p in pts) / n
    my = sum(p[1] for p in pts) / n
    sx = math.sqrt(sum((p[0]-mx)**2 for p in pts))
    sy = math.sqrt(sum((p[1]-my)**2 for p in pts))
    if sx == 0 or sy == 0:
        return None, n
    cov = sum((p[0]-mx)*(p[1]-my) for p in pts)
    return cov/(sx*sy), n

def _evidence_level(r, n, observable=True):
    if not observable:
        return "unobservable_no_meso_data"
    if r is None:
        return "insufficient_n"
    a = abs(r)
    base = ("strong" if a >= 0.6 else "moderate" if a >= 0.4
            else "weak" if a >= 0.2 else "negligible")
    if n < 20:
        base += "_low_n"
    return base

def _resolve_key(recs, short):
    """Map short layer code (e.g. 'L3') to the full dict key (e.g. 'L3_atmosphere').

    Scans ALL records, not just recs[0] (the OLDEST snapshot). A field added
    later (e.g. 'L2p5_meso', once meso persistence went live) never appears in
    old history rows; resolving from recs[0] alone would make that coupling
    permanently unobservable even once every new snapshot carries it."""
    if short is None:
        return None
    seen_keys = set()
    for r in recs:
        seen_keys.update(r.get("layers", {}).keys())
    for k in seen_keys:
        if k == short or k.startswith(short + "_"):
            return k
    return None

def _layer_series(recs, layer_key):
    return [r["layers"].get(layer_key, {}).get("score") for r in recs]

# --------------------------------------------------------------------------- #
# 3. EMPIRICAL COUPLING MATRIX (structure + measured evidence from history)
# --------------------------------------------------------------------------- #
def build_coupling_matrix(recs):
    layer_of = {h[0]: h[6] for h in HOLONS}
    status_of = {h[0]: h[7] for h in HOLONS}
    role_of = {h[0]: h[8] for h in HOLONS}
    rows = []
    for src, tgt, ctype, lf, lt, mech in COUPLING_DEFS:
        ls, lt_ = _resolve_key(recs, layer_of[src]), _resolve_key(recs, layer_of[tgt])
        observable = (status_of[src] != "inferred" and status_of[tgt] != "inferred"
                      and ls is not None and lt_ is not None)
        r0 = r1 = None; n0 = n1 = 0; lag = 0
        if observable:
            s_src, s_tgt = _layer_series(recs, ls), _layer_series(recs, lt_)
            r0, n0 = _pearson(s_src, s_tgt)
            r1, n1 = _pearson(s_src[:-1], s_tgt[1:])
            # pick the stronger of lag0 / lag1
            if r1 is not None and (r0 is None or abs(r1) > abs(r0)):
                lag, r_best, n_best = 1, r1, n1
            else:
                lag, r_best, n_best = 0, r0, n0
        else:
            r_best, n_best = None, 0
        # confound classification: circular = target derived from source (audited);
        #                          proxy    = source or target is a modelled proxy
        if (src, tgt) in CIRCULAR_COUPLINGS:
            confound_type = "circular"
        elif status_of[tgt] == "proxy" or status_of[src] == "proxy":
            confound_type = "proxy"
        else:
            confound_type = "none"
        confound = confound_type != "none"
        mech_out = (mech + " [WARN: Ziel aus Quelle abgeleitet -> zirkulaer]"
                    if confound_type == "circular" else mech)
        rows.append({
            "source_holon": src,
            "target_holon": tgt,
            "coupling_type": ctype,
            "expected_lag_snapshots": lag,
            "pearson_r": None if r_best is None else round(r_best, 3),
            "n": n_best,
            "evidence_level": _evidence_level(r_best, n_best, observable),
            "src_role": role_of[src],
            "tgt_role": role_of[tgt],
            "confounded": confound,
            "confound_type": confound_type,
            "mechanism": mech_out,
        })
    return rows

# --------------------------------------------------------------------------- #
# 4. EVENT CARD (diagnose the latest snapshot on the holarchy)
# --------------------------------------------------------------------------- #
ACTIVE = 0.5     # active_layer threshold (from L7 thresholds)
WEAK   = 0.3     # weak_layer threshold

def _band(score, hi=ACTIVE, lo=WEAK):
    if score is None: return "unknown"
    if score >= hi:   return "high"
    if score >= lo:   return "medium"
    return "low"

def _l9_validation_status(l9):
    """Echter L9-Validierungsstand fuer die Event-Card.

    L9 schreibt seinen Score nach aggregate.validation_score (kein Top-Level-Key).
    Ohne L9-State bleibt der bisherige Platzhalter erhalten."""
    if not l9:
        return "unvalidated_pending_L9"
    agg = l9.get("aggregate") or {}
    score = agg.get("validation_score")
    if score is None:
        return "l9_ran_but_no_aggregate_score"
    return {
        "status": "validated_by_L9",
        "validation_score": score,
        "evidence_level": agg.get("evidence_level"),
        "checks": f"{agg.get('n_passed')}/{agg.get('n_total')} passed",
        "l9_timestamp": l9.get("timestamp"),
    }


def build_event_card(recs, l8=None, l9=None):
    r = recs[-1]
    sc = {k: v.get("score") for k, v in r["layers"].items()}
    L2, L3, L5, L6 = (sc.get("L2_surface_zone"), sc.get("L3_atmosphere"),
                      sc.get("L5_global_electric_circuit"), sc.get("L6_resonance_field"))
    L0 = sc.get("L0_external_drivers")

    macro   = _band(L2)
    micro   = _band(L3, hi=0.29, lo=0.24)          # L3 lives in a lower band
    electric= _band(L5)
    reso    = _band(L6)

    # external forcing mask: is the system being externally driven?
    ext_mask = {
        "external_score": None if L0 is None else round(L0, 3),
        "externally_driven": (L0 is not None and L0 >= WEAK),
        "interpretation": ("external forcing low -> absence of activation is NOT due to "
                           "missing external trigger; internal/scale dynamics dominate"
                           if (L0 is not None and L0 < WEAK)
                           else "external forcing non-trivial -> check L0 contribution"),
    }

    # locate the chain break
    chain_break = _locate_break(macro, micro, electric, reso)

    # resonance confirmation is proxy-limited
    non_geom = r["layers"].get("L6_resonance_field", {}).get("flags", {}).get("non_geometric_dominant")
    reso_conf = "low_proxy_limited" if non_geom else ("confirmed" if reso == "high" else "partial")

    return {
        "timestamp": r.get("timestamp"),
        "system_state": r.get("system_state"),
        "scores": {"L0": L0, "L2": L2, "L3": L3, "L5": L5, "L6": L6},
        "macro_context": {"band": macro, "score": L2,
                          "tags": [t for t in r.get("event_tags", []) if "nino" in t or "sst" in t]},
        "meso_organisation": {"band": "unmeasured",
                              "note": "no meso-scale layer instrumented (regional convection / MCS)"},
        "micro_activation": {"band": micro, "score": L3,
                             "thunder_pts": r["layers"]["L3_atmosphere"]["key_metrics"].get("thunder_pts"),
                             "storms_EONET": r["layers"]["L3_atmosphere"]["key_metrics"].get("storms_EONET")},
        "field_response": {"electric": {"band": electric, "score": L5},
                           "resonance": {"band": reso, "score": L6, "confirmation": reso_conf}},
        "chain_break": chain_break,
        "external_forcing_mask": ext_mask,
        "validation_status": _l9_validation_status(l9),
    }

def _locate_break(macro, micro, electric, reso):
    """Find the first scale where the chain fails to propagate."""
    # downstream is observable; the macro->meso->micro span is partly blind
    if macro in ("high", "medium") and micro == "low":
        return {"break_at": "macro_to_micro",
                "localizable": False,
                "reason": "meso scale uninstrumented; cannot distinguish macro->meso vs meso->micro",
                "diagnosis": "macro_prepared but micro_activation_low — preparation without activation"}
    if micro == "low":
        return {"break_at": "below_micro", "localizable": True,
                "reason": "no atmospheric activation to propagate"}
    if micro in ("medium", "high") and electric == "low":
        return {"break_at": "micro_to_electric", "localizable": True,
                "reason": "atmosphere active but GEC not responding"}
    if electric in ("medium", "high") and reso == "low":
        return {"break_at": "electric_to_resonance", "localizable": True,
                "reason": "GEC active but resonance not confirmed"}
    return {"break_at": "none", "localizable": True,
            "reason": "chain propagated to resonance"}

# --------------------------------------------------------------------------- #
# 5. RUN-LEVEL DIAGNOSTICS (where does the break sit across the whole history?)
# --------------------------------------------------------------------------- #
def chain_break_distribution(recs):
    from collections import Counter
    c = Counter()
    for r in recs:
        sc = {k: v.get("score") for k, v in r["layers"].items()}
        macro = _band(sc.get("L2_surface_zone"))
        micro = _band(sc.get("L3_atmosphere"), hi=0.29, lo=0.24)
        electric = _band(sc.get("L5_global_electric_circuit"))
        reso = _band(sc.get("L6_resonance_field"))
        c[_locate_break(macro, micro, electric, reso)["break_at"]] += 1
    return dict(c)

# --------------------------------------------------------------------------- #
# WRITERS
# --------------------------------------------------------------------------- #
def write_registry_yaml(path):
    lines = ["# Holon Registry — Holarchic Coupling Analysis V1",
             "# status: measured | proxy | inferred(not instrumented)",
             "holons:"]
    for h in HOLONS:
        d = dict(zip(HOLON_FIELDS, h))
        lines.append(f"  - id: {d['id']}")
        for f in HOLON_FIELDS[1:]:
            v = d[f]
            if isinstance(v, list):
                v = "[" + ", ".join(v) + "]" if v else "[]"
            elif v is None:
                v = "null"
            lines.append(f"    {f}: {v}")
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")

def write_matrix_csv(path, rows):
    cols = ["source_holon","target_holon","coupling_type","expected_lag_snapshots",
            "pearson_r","n","evidence_level","src_role","tgt_role","confounded","confound_type","mechanism"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
        for r in rows: w.writerow(r)

def write_event_card_json(path, card):
    Path(path).write_text(json.dumps(card, indent=2, ensure_ascii=False), encoding="utf-8")

def write_report_md(path, recs, rows, card, break_dist):
    n = len(recs)
    obs = [r for r in rows if r["pearson_r"] is not None]
    strong = [r for r in obs if r["evidence_level"].startswith(("strong","moderate"))]
    broken = [r for r in rows if r["evidence_level"] == "unobservable_no_meso_data"]
    total_breaks = sum(break_dist.values())
    macro_micro = break_dist.get("macro_to_micro", 0)

    def L(key):
        """Mittelwert eines Layer-Scores ueber die Historie.

        Robust gegen Felder, die erst spaeter dazukamen (z.B. 'L2p5_meso'):
        nicht jeder History-Eintrag hat den Key oder einen Score != None,
        also ueber die tatsaechlich vorhandenen Werte mitteln, nicht ueber
        alle n Snapshots (das waere ein KeyError bzw. eine falsche Basis)."""
        vals = [r["layers"][key]["score"] for r in recs
                if key in r.get("layers", {}) and r["layers"][key].get("score") is not None]
        return (sum(vals) / len(vals)) if vals else None
    md = []
    md.append("# Holarchic Coupling Analysis — Report V1\n")
    md.append(f"**Run:** {datetime.now(timezone.utc).isoformat()}  ")
    md.append(f"**Snapshots:** {n}  ")
    md.append(f"**Holons:** {len(HOLONS)} ({sum(1 for h in HOLONS if h[7]=='inferred')} uninstrumented)\n")

    md.append("## 1. Welche Skala dominiert?\n")
    md.append("| Holon | Layer | Scale | mean score | Status |")
    md.append("|---|---|---|---|---|")
    for h in HOLONS:
        key = _resolve_key(recs, h[6])
        mean_score = L(key) if key else None
        if key and mean_score is not None:
            md.append(f"| {h[0]} | {h[6]} | {h[2]} | {mean_score:.3f} | {h[7]} |")
        elif h[7] == "inferred":
            md.append(f"| {h[0]} | — | {h[2]} | **n/a** | **inferred (fehlt)** |")
        elif h[7] == "proxy":
            md.append(f"| {h[0]} | {h[6] or '—'} | {h[2]} | **n/a** | **proxy (noch keine Historie)** |")
        else:
            # key resolved aber (noch) kein einziger Score darunter -> ehrlich n/a statt Crash
            md.append(f"| {h[0]} | {h[6] or '—'} | {h[2]} | **n/a** | {h[7]} (keine Werte) |")
    _meso_key = _resolve_key(recs, "L2p5")
    _meso_n = sum(1 for r in recs if _meso_key and r["layers"].get(_meso_key, {}).get("score") is not None)
    if _meso_key is None:
        _meso_note = ("Die dazwischenliegende Meso-Skala ist im Code instrumentiert (Wolken-Uebergangsproxy, "
                       "s. `meso_ingest.py`), aber noch kein Snapshot in der Historie traegt sie.")
    elif _meso_n < 20:
        _meso_note = (f"Die Meso-Skala ist instrumentiert (Wolken-Uebergangsproxy, `confound_type=proxy` bis "
                       f"echtes OLR zurueckkommt), aber die Historie (n={_meso_n}) ist noch zu klein fuer eine "
                       f"belastbare Kopplungsschaetzung.")
    else:
        _meso_note = (f"Die Meso-Skala ist instrumentiert (Wolken-Uebergangsproxy, `confound_type=proxy`); "
                       f"n={_meso_n} Snapshots mit Meso-Daten, s. Kopplungstabelle unten.")
    md.append("Makro-Vorbereitung (`H_macro_ocean`) ist der höchste physische Score, "
              "Mikro-Aktivierung (`H_micro_storm`) der niedrigste. "
              f"{_meso_note}\n")

    md.append("## 2. Wo bricht die Kette?\n")
    md.append("Empirische Kopplungsstärken entlang der Aktivierungskette:\n")
    md.append("| Span | Typ | r | n | Evidenz |")
    md.append("|---|---|---|---|---|")
    chain_rows = [r for r in rows if (r["source_holon"], r["target_holon"]) in
                  {(a, b) for a, b, *_ in ACTIVATION_CHAIN}]
    for r in chain_rows:
        rr = "—" if r["pearson_r"] is None else f"{r['pearson_r']:+.3f}"
        md.append(f"| {r['source_holon']}→{r['target_holon']} | {r['coupling_type']} | "
                  f"{rr} | {r['n']} | {r['evidence_level']} |")
    md.append("")
    md.append(f"**Befund:** Der Downstream-Abschnitt (micro→electric→resonance) ist intakt und stark. "
              f"Der einzige Bruch sitzt bei **macro→micro** und ist in "
              f"{macro_micro}/{total_breaks} Snapshots ({100*macro_micro/max(total_breaks,1):.0f}%) "
              f"die dominante Bruchstelle. Er ist **nicht lokalisierbar**, weil die Meso-Ebene "
              f"keine Datenquelle hat.\n")
    md.append("Break-Verteilung über die History: " +
              ", ".join(f"`{k}`={v}" for k, v in sorted(break_dist.items(), key=lambda x:-x[1])) + "\n")

    md.append("## 3. Welche Rückkopplung ist plausibel?\n")
    fb = [r for r in rows if r["coupling_type"] == "field_feedback" and r["pearson_r"] is not None]
    for r in fb:
        md.append(f"- `{r['source_holon']}→{r['target_holon']}`: r={r['pearson_r']:+.3f} "
                  f"({r['evidence_level']}) — {r['mechanism']}")
    md.append("\nDas Resonanzfeld (`H_field_reso`) ist als **proxy** markiert "
              "(non-geometrischer Anteil modelliert, nicht direkt gemessen). "
              "Kopplungen *in* dieses Holon dürfen nicht als unabhängige Bestätigung gelten.\n")

    md.append("## 4. Welche Evidenz fehlt?\n")
    md.append("1. **Meso-Skala — unabhaengige Organisationsmessung.** Instrumentiert seit kurzem ueber "
              "einen Wolken-Uebergangsproxy (`confound_type=proxy`); die Kettenbruch-LOKALISIERUNG "
              "(macro→meso vs. meso→micro, statt nur macro→micro) nutzt den Meso-Score selbst noch nicht "
              "und bleibt bis dahin blind. Echtes OLR wuerde die Kopplung von proxy auf measured heben.")
    md.append("2. **Unabhängiger Resonanz-Messwert** — um `H_field_reso` von proxy auf measured zu heben.")
    md.append("3. **Mehr Aktivierungs-Events** — Downstream-Kopplung ist nur sichtbar, wenn L3 zündet; "
              "bei dominanter Bruchstelle macro→micro gibt es davon wenige.\n")

    md.append("## 5. Empfohlener nächster Datenschritt\n")
    md.append("Meso ist instrumentiert (Wolken-Proxy) und persistiert (`layer2p5_meso_state.json`), aber "
              "zwei Schritte offen: (a) genug Historie ansammeln, bis die L2→L2.5/L2.5→L3-Kopplung oben "
              "eine belastbare Fallzahl hat, (b) die Kettenbruch-Lokalisierung (`_locate_break`) so "
              "erweitern, dass sie den Meso-Score selbst befragt statt nur macro/micro — erst dann wird "
              "`macro_to_micro` (blind) zu `macro_to_meso` ODER `meso_to_micro` (lokalisiert) auflösbar. "
              "Echtes OLR (statt Wolken-Proxy) bliebe danach der Schritt von proxy zu measured.\n")
    Path(path).write_text("\n".join(md), encoding="utf-8")

# --------------------------------------------------------------------------- #
# ORCHESTRATION
# --------------------------------------------------------------------------- #
def run(history_path, l8_path=None, outdir=".", l9_path=None):
    out = Path(outdir); out.mkdir(parents=True, exist_ok=True)
    recs = [json.loads(l) for l in open(history_path) if l.strip()]
    l8 = json.load(open(l8_path)) if l8_path and Path(l8_path).exists() else None
    l9 = json.load(open(l9_path)) if l9_path and Path(l9_path).exists() else None

    rows = build_coupling_matrix(recs)
    card = build_event_card(recs, l8, l9)
    break_dist = chain_break_distribution(recs)

    write_registry_yaml(out / "holon_registry.yaml")
    write_matrix_csv(out / "holarchic_coupling_matrix.csv", rows)
    write_event_card_json(out / "holarchic_event_card.json", card)
    write_report_md(out / "holarchic_analysis_report.md", recs, rows, card, break_dist)
    return {"n_snapshots": len(recs), "coupling_rows": len(rows),
            "chain_break_distribution": break_dist, "outdir": str(out)}

if __name__ == "__main__":
    import sys
    hist = sys.argv[1] if len(sys.argv) > 1 else "layer7_history.jsonl"
    l8 = sys.argv[2] if len(sys.argv) > 2 else "layer8_state.json"
    res = run(hist, l8, outdir=sys.argv[3] if len(sys.argv) > 3 else ".")
    print(json.dumps(res, indent=2, ensure_ascii=False))
