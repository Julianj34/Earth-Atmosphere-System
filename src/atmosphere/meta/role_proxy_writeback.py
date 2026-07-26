"""
Role-Tag & Proxy-Status Write-back  —  for L7 / L8
==================================================

Purpose
-------
Annotate the existing L7 and L8 state with:
  1. holon ROLE per layer        (driver/constraint/mediator/response/proxy/measurement)
  2. holon STATUS per layer       (measured | proxy)
  3. operator COMPOSITION          (which layers each field-operator is built from)
  4. coupling CONFOUND flags       (target is proxy, or shares inputs)
  5. hypothesis INDEPENDENCE       (independent | confounded_circular | confounded_proxy)
  6. a confound-aware PROMOTION GUARD that blocks circular/proxy evidence from
     entering model logic, regardless of review status.

Why first (before instrumenting the meso layer)
-----------------------------------------------
The field-operators are composed from the same layer scores they are correlated
against. e.g. electric_operator = f(L3, L5, L6). A hypothesis "electric predicts
L3" therefore predicts L3 partly FROM L3 -> circular. Promoting that into model
logic and THEN feeding more (meso) data would let the model keep confirming its
own assumptions. This guard makes that impossible.

Integration
-----------
These are pure functions over the state dicts. In the L7 notebook, call
`annotate_l7(state)` right before writing layer7_state.json. In the L8 notebook,
call `annotate_l8(state)` right before writing layer8_state.json. No other change
to your scoring logic is required.
"""
from __future__ import annotations
import re, json, copy
from pathlib import Path

# --------------------------------------------------------------------------- #
# CANONICAL holon roles & status per layer  (single source of truth)
# --------------------------------------------------------------------------- #
LAYER_ROLE = {
    "L0_external_drivers":        "driver",
    "L1_planetary_body":          "driver",
    "L2_surface_zone":            "constraint",
    "L2p5_meso":                  "mediator",   # meso-scale organisation holon (L2 -> L2.5 -> L3)
    "L3_atmosphere":              "response",
    "L4_ionosphere":              "mediator",
    "L5_global_electric_circuit": "response",
    "L6_resonance_field":         "response",
}
# measured = direct observation ; proxy = modelled ; derived_proxy = computed
# from other layers (not an independent measurement)
LAYER_STATUS = {
    "L0_external_drivers":        "measured",
    "L1_planetary_body":          "measured",
    "L2_surface_zone":            "measured",
    "L2p5_meso":                  "derived_proxy",   # organisation term is a cloud-cover fallback proxy
                                                       # (real OLR frozen, s. meso_ingest.py); NOT a
                                                       # LAYER_ROLE-score derivation like L5 -- it reuses
                                                       # raw CIN/cloud INPUT DATA from L3, not L3's score.
                                                       # -> belongs in DERIVED_FROM's spirit as "shared raw
                                                       # input", not literal score-circularity. Flip to
                                                       # "measured" once real OLR is restored (single swap
                                                       # point: _OLR_DAILY in meso_ingest.py).
    "L3_atmosphere":              "measured",
    "L4_ionosphere":              "measured",
    "L5_global_electric_circuit": "derived_proxy",   # V_iono/generator computed from L3 CAPE+thunder
    "L6_resonance_field":         "proxy",            # non_geometric_dominant -> modelled component
}

# layers that are computed FROM other layers -> not independent of those layers.
# VERIFIED against atmosphere_analysis_layer5.ipynb (cell 8): generator_strength
# = 0.5*CAPE/ref + 0.5*f(thunder_score), both L3; scaled by F10.7 (L4) and
# ground conductivity (L1). L3 is the dominant driver.
DERIVED_FROM = {
    "L5_global_electric_circuit": ["L3_atmosphere", "L4_ionosphere", "L1_planetary_body"],
}

# Which layers each field-operator is COMPOSED from. An operator must never be
# used as an independent predictor of any layer in its own composition.
# VERIFIED against atmosphere_analysis_layer7.ipynb (cell 13).
OPERATOR_COMPOSITION = {
    "thermal":                ["L2_surface_zone"],                       # nur L2 (Vorbereitung) — enthält KEIN L3
    "electric":               ["L3_atmosphere", "L5_global_electric_circuit"],
    "ionization":             ["L0_external_drivers", "L4_ionosphere"],
    "geomagnetic":            ["L0_external_drivers", "L4_ionosphere", "L5_global_electric_circuit"],
    "resonance_model":        ["L4_ionosphere", "L5_global_electric_circuit", "L6_resonance_field"],  # modelled -> proxy
    "cross_layer_activation": ["L2_surface_zone", "L3_atmosphere", "L4_ionosphere",
                               "L5_global_electric_circuit", "L6_resonance_field"],  # gaps over all spans
    "tidal_gravity":          ["L1_planetary_body"],
}
# operators whose value is itself a modelled quantity (not a direct measurement)
PROXY_OPERATORS = {"resonance_model"}

def _opname(raw: str) -> str:
    """Normalise 'electric_operator' / 'electric_t' / 'electric' -> 'electric'."""
    s = raw.replace("_operator", "")
    s = re.sub(r"_t$", "", s)
    return s

# --------------------------------------------------------------------------- #
# 1. L7 ANNOTATION
# --------------------------------------------------------------------------- #
def annotate_l7(state: dict) -> dict:
    """Add holon role/status to layers, composition to operators, confound flags
    to couplings. Returns the same dict (mutated) for convenience."""
    # layers
    for key, layer in state.get("layers", {}).items():
        layer["holon_role"]      = LAYER_ROLE.get(key, "unknown")
        layer["holon_status"]    = LAYER_STATUS.get(key, "measured")
        layer["evidence_status"] = LAYER_STATUS.get(key, "measured")
        if key in DERIVED_FROM:
            layer["derived_from_layers"] = DERIVED_FROM[key]
            layer["independence_limits"] = [f"not_independent_of:{l}" for l in DERIVED_FROM[key]]
            layer["directly_observed"]   = False
    # operators: restore composition + independence guard
    fops = state.get("field_operators", {})
    for raw_name, op in fops.items():
        if not isinstance(op, dict):
            continue
        comp = OPERATOR_COMPOSITION.get(_opname(raw_name), [])
        op["source_layers"]  = comp
        op["is_proxy"]       = _opname(raw_name) in PROXY_OPERATORS
        op["not_independent_of"] = comp
    # couplings: flag confound when target is not a clean measurement, or when a
    # coupling feeds a derived layer from one of its own source layers
    for c in state.get("couplings", []):
        src, tgt = c.get("from"), c.get("to")
        c["target_status"] = LAYER_STATUS.get(tgt, "measured")
        derived_circular = (tgt in DERIVED_FROM and src in DERIVED_FROM[tgt])
        c["confounded"]    = (LAYER_STATUS.get(tgt, "measured") != "measured") or derived_circular
        if derived_circular:
            c["confound_reason"] = f"{tgt} is derived from {src} (not independent)"
    state["role_proxy_writeback"] = {"version": "1.0", "applied": True}
    return state

# --------------------------------------------------------------------------- #
# 2. HYPOTHESIS INDEPENDENCE CLASSIFIER
# --------------------------------------------------------------------------- #
# explicit overrides for non-operator source_metrics
EXPLICIT_INDEPENDENCE = {
    "slot_annotation":                ("independent",
        "temporal pattern on external time-of-day annotation"),
    "event_tag_frequency":            ("independent",
        "meta tag-hygiene; no predictive circularity"),
    "combined_activation_score":      ("confounded_circular",
        "composite of L3+L5+L6 used to predict a state derived from the same layers"),
    "cavity_gate_outcome":            ("confounded_proxy",
        "cavity_gate built from L4 + L6(proxy); also very low n"),
}

# layers that carry a modelled (proxy) component
PROXY_LAYER_TOKENS = ("L6", "resonance")

def _references_proxy(metric: str) -> bool:
    return any(tok in metric for tok in PROXY_LAYER_TOKENS)

# parses 'electric_t__L3_atmosphere_t+2' -> ('electric', 'L3_atmosphere', 2)
LEADLAG_RE = re.compile(r"^(?P<op>[a-z_]+?)_t__(?P<layer>L\d_[a-z_]+)_t\+(?P<lag>\d+)$")

def classify_independence(source_metric: str, hyp_type: str = "",
                          target_layer: str | None = None) -> tuple[str, str]:
    """Return (independence, reason).
    independence in {independent, confounded_circular, confounded_proxy, unclassified}."""
    if source_metric in EXPLICIT_INDEPENDENCE:
        return EXPLICIT_INDEPENDENCE[source_metric]

    # raw cross-layer Pearson correlations (e.g. pearson_L2_L3,
    # pearson_L5evening_vs_L3_evening). Independent UNLESS a proxy or
    # derived layer is involved.
    if source_metric.startswith("pearson"):
        refs = set(re.findall(r"L\d", source_metric))
        # proxy layer (L6/resonance) on either side
        if _references_proxy(source_metric):
            return ("confounded_proxy",
                    f"raw correlation but involves a proxy layer (L6/resonance): {source_metric}")
        # derived layer (e.g. L5) correlated with one of its own source layers
        for dl, srcs in DERIVED_FROM.items():
            tag = dl.split("_")[0]   # 'L5'
            if tag in refs:
                others = refs - {tag}
                overlap = others & {s.split("_")[0] for s in srcs}
                if overlap:
                    return ("confounded_circular",
                            f"{dl} is derived from {sorted(overlap)}; correlating them is "
                            f"partly construction, not independent confirmation")
                return ("confounded_proxy",
                        f"{dl} is a derived_proxy (computed from {srcs}), not a direct measurement")
        return ("independent",
                f"raw cross-layer correlation ({source_metric}); distinct measured layers, no shared inputs")

    # lead-lag operator -> layer
    m = LEADLAG_RE.match(source_metric)
    if m:
        op, layer, lag = _opname(m["op"]), m["layer"], int(m["lag"])
        comp = OPERATOR_COMPOSITION.get(op, [])
        if layer in comp:
            return ("confounded_circular",
                    f"{op}_operator is composed from {layer}; predicting {layer}_t+{lag} "
                    f"is partly self-prediction (layer autocorrelated; lag reduces but "
                    f"does not remove the confound)")
        if op in PROXY_OPERATORS:
            return ("confounded_proxy",
                    f"{op}_operator is a modelled (proxy) quantity, not a direct measurement")
        return ("independent",
                f"{op}_operator does not contain {layer}; cross-scale lead-lag is admissible")

    # bare operator predictor (e.g. cross_layer_activation_operator vs dL3)
    op = _opname(source_metric)
    if op in OPERATOR_COMPOSITION:
        comp = OPERATOR_COMPOSITION[op]
        tgt = target_layer or "L3_atmosphere"   # operator predictors target dL3 by default
        if tgt in comp:
            return ("confounded_circular",
                    f"{op}_operator is composed from {tgt}; cannot be an independent "
                    f"predictor of {tgt}")
        if op in PROXY_OPERATORS:
            return ("confounded_proxy", f"{op}_operator is a modelled (proxy) quantity")
        return ("independent", f"{op}_operator does not contain {tgt}")

    # unknown -> conservative: do not auto-promote; flag for a classifier rule
    return ("unclassified", "source_metric not recognised; classifier rule required")

# --------------------------------------------------------------------------- #
# 3. L8 ANNOTATION + PROMOTION GUARD
# --------------------------------------------------------------------------- #
def annotate_l8(state: dict) -> dict:
    """Tag each hypothesis with independence and apply the confound-aware
    promotion guard. Independent evidence keeps the notebook's own review gate
    (review_status -> include_in_model_logic). Circular/proxy/unclassified
    evidence is hard-blocked from model logic regardless of review status."""
    backbone, blocked = [], []
    for h in state.get("hypothesis_candidates", []):
        indep, reason = classify_independence(h.get("source_metric", ""), h.get("type", ""))
        h["evidence_independence"] = indep
        h["independence_reason"]   = reason

        if indep == "independent":
            # leave the notebook's review gate intact; just mark eligibility
            h["promotion_eligible"] = True
            backbone.append(h["id"])
        else:
            # override the review gate: confound/proxy/unclassified never promote
            h["promotion_eligible"]     = False
            h["include_in_model_logic"] = False
            h["promotion_blocked_reason"] = (
                f"confound:{indep}" if indep.startswith("confounded")
                else "unclassified_source_metric")
            blocked.append(h["id"])

    state["independence_audit"] = {
        "version": "1.1",
        "independent_backbone": backbone,
        "confound_blocked": blocked,
        "rule": ("independent -> notebook review gate applies; "
                 "confounded/proxy/unclassified -> hard-blocked from model logic"),
    }
    return state

# --------------------------------------------------------------------------- #
# 4. STANDALONE RUNNER (produces annotated copies for inspection)
# --------------------------------------------------------------------------- #
def run(l7_path, l8_path, outdir="."):
    out = Path(outdir); out.mkdir(parents=True, exist_ok=True)
    # encoding explizit (Windows-Default ist cp1252, nicht UTF-8)
    l7 = annotate_l7(json.loads(Path(l7_path).read_text(encoding="utf-8")))
    l8 = annotate_l8(json.loads(Path(l8_path).read_text(encoding="utf-8")))
    (out / "layer7_state.annotated.json").write_text(
        json.dumps(l7, indent=2, ensure_ascii=False), encoding="utf-8")
    (out / "layer8_state.annotated.json").write_text(
        json.dumps(l8, indent=2, ensure_ascii=False), encoding="utf-8")
    return {
        "l7_layers_tagged": len(l7.get("layers", {})),
        "l7_proxy_layers": [k for k, v in LAYER_STATUS.items() if v == "proxy"],
        "l8_audit": l8.get("independence_audit"),
    }

if __name__ == "__main__":
    import sys
    res = run(sys.argv[1] if len(sys.argv) > 1 else "layer7_state.json",
              sys.argv[2] if len(sys.argv) > 2 else "layer8_state.json",
              sys.argv[3] if len(sys.argv) > 3 else ".")
    print(json.dumps(res, indent=2, ensure_ascii=False))
