"""
Layer Meso  —  H_meso_conv  (the missing scale between L2 and L3)
================================================================

Role in holarchy : mediator between H_macro_ocean (L2, weeks-months) and
                   H_micro_storm (L3, minutes-hours).
Scale            : regional ; Timescale : hours-days.
Question it answers: does macro-scale preparation ORGANISE into convection
                   capable of converting to micro-scale activation?

Core physics
------------
Meso organisation is NOT "more CAPE" (that is L3). It is whether large-scale
preparation aggregates into organised convective systems. We compose:

    organisation = w_mjo*mjo + w_olr*olr + w_shear*shear + w_rh*midlevel_rh

and then GATE it by convective inhibition (the cap):

    meso_score   = organisation * cin_gate(CIN)

CIN is multiplicative, not additive. High CAPE + high CIN = capped = no
realisation. This is the mechanism that lets the layer distinguish two
physically different chain breaks:
    organisation low                  -> break is macro_to_meso
    organisation high but cin_gate low -> break is meso_to_micro (capped)

Data sources (wire these in your ingestion cell; module is feed-agnostic)
-------------------------------------------------------------------------
See MESO_SOURCES. The module consumes a plain dict of normalised inputs and
returns the SAME layer schema as L0-L6 so it drops straight into the stack.
"""
from __future__ import annotations
import math

LAYER_ID   = "L2p5_meso_convection"   # sits between L2 and L3
HOLON_ID   = "H_meso_conv"
HOLON_ROLE = "mediator"

# --------------------------------------------------------------------------- #
# DATA SOURCE CONTRACT  (what to ingest; product + variable + cadence + role)
# --------------------------------------------------------------------------- #
MESO_SOURCES = {
    "mjo_amplitude": dict(product="BoM RMM (Wheeler-Hendon)", var="RMM amplitude",
                          cadence="daily", role="organisation_envelope",
                          note="active MJO (amp>1) enhances regional convective organisation"),
    "mjo_phase":     dict(product="BoM RMM", var="RMM phase 1-8", cadence="daily",
                          role="organisation_envelope",
                          note="phase determines which longitudes are favoured"),
    "olr_anomaly":   dict(product="NOAA interpolated OLR", var="OLR anomaly W/m^2",
                          cadence="daily", role="organisation_proxy",
                          note="negative anomaly = enhanced deep convection"),
    "shear_0_6km":   dict(product="ERA5 / GFS", var="0-6km bulk wind shear m/s",
                          cadence="6-hourly", role="organisation_potential",
                          note="MCS organisation peaks ~12-18 m/s"),
    "midlevel_rh":   dict(product="ERA5 / GFS", var="700-500 hPa mean RH %",
                          cadence="6-hourly", role="organisation_sustain",
                          note=">50-60% sustains organised systems"),
    "cin":           dict(product="ERA5 / GFS / SPC mesoanalysis", var="CIN J/kg",
                          cadence="hourly-6hourly", role="realisation_gate",
                          note="multiplicative cap; high CIN suppresses realisation"),
    # optional refinements:
    "iorg":          dict(product="derived from IR Tb<241K or IMERG", var="Iorg aggregation index",
                          cadence="hourly", role="organisation_direct", optional=True,
                          note="0.5=random, >0.5 aggregated; direct organisation measure"),
}

# --------------------------------------------------------------------------- #
# component transfer functions (each returns 0..1)
# --------------------------------------------------------------------------- #
def _mjo_term(amp, phase, favoured_phases=(2, 3, 4, 5)):
    """Active MJO in a favoured phase -> high. amp in ~0..3, phase 1..8."""
    if amp is None:
        return None
    amp_n = max(0.0, min(1.0, amp / 2.0))          # amp 2 -> saturated
    phase_boost = 1.0 if (phase in favoured_phases) else 0.55
    return amp_n * phase_boost

def _olr_term(olr_anom):
    """Negative OLR anomaly = enhanced convection. Map -40..+20 W/m^2 -> 1..0."""
    if olr_anom is None:
        return None
    return max(0.0, min(1.0, (20.0 - olr_anom) / 60.0))

def _shear_term(shear, lo=8.0, opt_lo=12.0, opt_hi=18.0, hi=30.0):
    """Bell-shaped MCS support: peak in the optimal band, falls off both sides."""
    if shear is None:
        return None
    s = shear
    if s <= lo or s >= hi:
        return 0.1
    if opt_lo <= s <= opt_hi:
        return 1.0
    if s < opt_lo:
        return 0.1 + 0.9 * (s - lo) / (opt_lo - lo)
    return 0.1 + 0.9 * (hi - s) / (hi - opt_hi)

def _rh_term(rh):
    """Mid-level RH; <40% dry-chokes organisation, >70% fully supportive."""
    if rh is None:
        return None
    return max(0.0, min(1.0, (rh - 40.0) / 30.0))

def _iorg_term(iorg):
    if iorg is None:
        return None
    return max(0.0, min(1.0, (iorg - 0.5) / 0.4))   # 0.5 random -> 0 ; 0.9 -> 1


# Ankerpunkte der Wolken-Rampe [%]. NICHT kalibriert: es gibt bisher zu wenige
# Meso-Snapshots fuer eine echte Verteilung. Die Werte sind ein physikalischer
# Prior fuer die Wolkenfraktion AN EINEM konvektiven Punkt, kein Fit.
# Sobald `messpunkte[].cloud` genug Historie hat, gehoeren hier Perzentile hin
# (z.B. p33/p67 der konvektiven Punkte) statt fester Zahlen.
_CLOUD_RAMP_LO, _CLOUD_RAMP_HI = 50.0, 100.0


def _cloud_term(cloud_pct):
    """UEBERGANGS-Proxy fuer OLR aus dem Wolken-Anteil [%].

    Erwartet den Wert der KONVEKTIVEN Punkte (s. _CLOUD_FIELD in meso_ingest);
    das fruehere globale Mittel ueber alle sechs Punkte mischte Arktis und
    Mitteleuropa hinein. Bleibt SCHWAECHER als echtes OLR, weil auch
    nicht-konvektive Schichtbewoelkung mitzaehlt -> Ergebnis wird als
    construct_status='derived_proxy' gefuehrt, nie als Messung."""
    if cloud_pct is None:
        return None
    span = _CLOUD_RAMP_HI - _CLOUD_RAMP_LO
    return max(0.0, min(1.0, (cloud_pct - _CLOUD_RAMP_LO) / span))

def cin_gate(cin, soft=25.0, hard=150.0):
    """Multiplicative realisation gate. CIN<soft -> ~1 (open).
    CIN>hard -> ~0 (capped). Smooth in between."""
    if cin is None:
        return 1.0
    if cin <= soft:
        return 1.0
    if cin >= hard:
        return 0.05
    # smooth decay
    frac = (cin - soft) / (hard - soft)
    return max(0.05, 1.0 - frac ** 0.8)

# --------------------------------------------------------------------------- #
# main score
# --------------------------------------------------------------------------- #
# weights for the organisation composite (renormalised over available terms)
_BASE_WEIGHTS = {"mjo": 0.28, "olr": 0.24, "shear": 0.22, "rh": 0.16, "iorg": 0.10}

def score_meso(inp: dict, source_status: str = "inferred") -> dict:
    """inp keys: mjo_amplitude, mjo_phase, olr_anomaly, shear_0_6km,
    midlevel_rh, cin, [iorg]. Returns the standard layer schema.

    source_status stays "inferred" until REAL feeds are wired in the
    ingestion cell; only then pass source_status="measured". This keeps the
    holarchy from treating placeholder/synthetic meso data as observable.
    """
    # OLR ist der primaere Organisations-Proxy; cloud_cover ist ein UEBERGANGS-
    # Fallback im SELBEN Slot (kein additiver Term -> keine Doppelzaehlung, da
    # Wolke und OLR dieselbe konvektive Bewoelkung messen).
    _org_val = _olr_term(inp.get("olr_anomaly"))
    organisation_source = "olr" if _org_val is not None else None
    if _org_val is None:
        _cloud_val = _cloud_term(inp.get("cloud_cover"))
        if _cloud_val is not None:
            _org_val = _cloud_val
            organisation_source = "cloud_proxy"
    terms = {
        "mjo":   _mjo_term(inp.get("mjo_amplitude"), inp.get("mjo_phase")),
        "olr":   _org_val,
        "shear": _shear_term(inp.get("shear_0_6km")),
        "rh":    _rh_term(inp.get("midlevel_rh")),
        "iorg":  _iorg_term(inp.get("iorg")),
    }
    avail = {k: v for k, v in terms.items() if v is not None}
    if not avail:
        return _empty_layer("no_meso_inputs")

    wsum = sum(_BASE_WEIGHTS[k] for k in avail)
    organisation = sum(_BASE_WEIGHTS[k] * v for k, v in avail.items()) / wsum

    cin = inp.get("cin")
    gate = cin_gate(cin)
    score = organisation * gate

    dominant = max(avail, key=lambda k: _BASE_WEIGHTS[k] * avail[k])
    # Ehrlichkeits-Fix: der Organisations-Slot heisst intern immer "olr" (technischer
    # Schluessel), auch wenn der Wolken-Fallback ihn fuellte. dominant_component wird
    # aber direkt in Reports/L7 angezeigt -> muss die tatsaechliche Quelle nennen,
    # sonst liest es sich wie echtes OLR, wenn es der schwaechere Proxy war.
    dominant_label = (f"organisation({organisation_source})" if dominant == "olr" and organisation_source
                       else dominant)
    confidence = len(avail) / 5.0   # fraction of core inputs present

    level = ("aktiv" if score >= 0.6 else "moderat" if score >= 0.4
             else "schwach" if score >= 0.25 else "ruhig")

    flags = {
        "mjo_active":       (inp.get("mjo_amplitude") or 0) > 1.0,
        "mcs_organised":    organisation >= 0.5,
        "cin_capped":       gate < 0.6,
        "shear_supportive": (terms["shear"] is not None and terms["shear"] >= 0.6),
        "midlevel_dry":     (inp.get("midlevel_rh") is not None and inp["midlevel_rh"] < 40),
        "organised_but_capped": (organisation >= 0.5 and gate < 0.6),
    }

    return {
        "score": round(score, 4),
        "organisation": round(organisation, 4),
        "cin_gate": round(gate, 4),
        "level": level,
        "confidence": round(confidence, 3),
        "dominant_component": dominant_label,
        "organisation_source": organisation_source,
        "flags": flags,
        "key_metrics": {
            "MJO_amp": inp.get("mjo_amplitude"),
            "MJO_phase": inp.get("mjo_phase"),
            "OLR_anom": inp.get("olr_anomaly"),
            "cloud_cover": inp.get("cloud_cover"),
            "shear_0_6km": inp.get("shear_0_6km"),
            "midlevel_RH": inp.get("midlevel_rh"),
            "CIN": cin,
        },
        "available": True,
        "holon_role": HOLON_ROLE,
        "holon_status": source_status,
        "component_terms": {k: round(v, 3) for k, v in avail.items()},
    }

def _empty_layer(reason):
    return {"score": None, "level": "unknown", "confidence": 0.0,
            "available": False, "reason": reason, "holon_role": HOLON_ROLE,
            "holon_status": "inferred", "flags": {}, "key_metrics": {}}

# --------------------------------------------------------------------------- #
# chain-break localisation, now that meso is observable
# --------------------------------------------------------------------------- #
def localise_break(macro_score, meso, micro_score,
                   macro_active=0.5, micro_active=0.24):
    """With meso instrumented, the previously-blind macro->micro span splits.

    Decision uses ORGANISATION (pre-gate) and the CIN gate SEPARATELY, not the
    gated score: a capped snapshot has high organisation but a low gated score,
    so judging on the gated score alone would misfile it as macro_to_meso.
    """
    macro_hi = macro_score is not None and macro_score >= macro_active
    micro_hi = micro_score is not None and micro_score >= micro_active
    organisation = meso.get("organisation")
    gate = meso.get("cin_gate", 1.0)
    org_hi    = organisation is not None and organisation >= 0.5
    gate_open = gate is not None and gate >= 0.6

    if micro_hi:
        return {"break_at": "none", "detail": "chain propagated to micro and beyond"}
    if not macro_hi:
        return {"break_at": "below_macro", "localizable": True,
                "detail": "no macro preparation to organise"}
    if not org_hi:
        return {"break_at": "macro_to_meso", "localizable": True,
                "detail": "macro prepared but no meso organisation (MJO/shear/RH insufficient)"}
    if not gate_open:
        return {"break_at": "meso_to_micro", "localizable": True, "cause": "cin_cap",
                "detail": "organised convection present but CIN-capped -> no realisation"}
    return {"break_at": "meso_to_micro", "localizable": True, "cause": "other",
            "detail": "organised and uncapped but not realising; timing/other factor"}

if __name__ == "__main__":
    # smoke test: organised but capped vs organised and open
    capped = score_meso(dict(mjo_amplitude=1.6, mjo_phase=3, olr_anomaly=-15,
                             shear_0_6km=14, midlevel_rh=62, cin=180))
    open_  = score_meso(dict(mjo_amplitude=1.6, mjo_phase=3, olr_anomaly=-15,
                             shear_0_6km=14, midlevel_rh=62, cin=10))
    import json
    print("CAPPED:", json.dumps({k: capped[k] for k in ("score","organisation","cin_gate","flags")}, ensure_ascii=False))
    print("OPEN  :", json.dumps({k: open_[k]  for k in ("score","organisation","cin_gate","flags")}, ensure_ascii=False))
