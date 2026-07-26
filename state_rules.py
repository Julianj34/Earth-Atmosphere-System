"""
atmosphere/state_rules.py — Zustandsregeln als versionierte DATEN
=================================================================

Der L7-Klassifikator entschied bis 2026-07 ueber eine Kette hartkodierter
if-Zweige. Alles, was ihn steuert, war damit unsichtbar:

  - die Schwellen (0.45, 0.35, 0.4, ...) standen als nackte Zahlen im Code,
  - die PRIORITAET war nur die Reihenfolge der if-Zweige,
  - es gab keine Version: aendert sich eine Schwelle, verschiebt sich die
    Bedeutung ALLER kuenftigen Labels, ohne dass die History das vermerkt.

Genau das ist der A9-Fall: die sechs `anomalous_resonance`-Ereignisse liegen
alle in der fruehen Engine-Aera, und niemand kann heute belegen, ob sich die
Physik oder die Regel geaendert hat.

Dieses Modul aendert das Verhalten NICHT. Es verlagert Schwellen, Prioritaeten,
Zustandsnamen und Konfidenzen nach `config/state_rules.json` und stempelt
`rule_version` in jeden Snapshot. Erst danach ist eine Schwellenaenderung ein
datierter, nachvollziehbarer Vorgang statt eines stillen Bruchs.

BEWUSST KEIN eval()
-------------------
Die Bedingungen sind ein kleines, geschlossenes Vokabular (unten dokumentiert),
kein auswertbarer Ausdruck. Damit ist die Regeldatei Konfiguration und keine
Codeausfuehrung — sie darf ohne Sicherheitsbedenken versioniert, geteilt und
von Hand editiert werden.

Bedingungstypen
---------------
  {"metric": "<meta_scores-Key>", "op": "<|<=|>|>=", "value": x}
  {"layer_score": "<Layer>", "op": ..., "value": x}
  {"var": "avg_conf", "op": ..., "value": x}
  {"any_flag": ["<Layer>.<flag>", ...]}          -> wahr, wenn IRGENDEIN Flag gesetzt
  {"count": "active_layers", "op": ">=", "value": n}
  {"count": "strong_couplings", "op": ">=", "value": n, "strength_min": 0.5}

Score-Ausdruecke (benannt, im Code definiert — keine Formeln in der Datei):
  downstream | preparation | cavity | max_external_L4 | mean_external_L4
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

__all__ = ["load_rules", "classify", "RULES_FILENAME"]

RULES_FILENAME = "state_rules.json"

_OPS = {
    "<":  lambda a, b: a < b,
    "<=": lambda a, b: a <= b,
    ">":  lambda a, b: a > b,
    ">=": lambda a, b: a >= b,
    "==": lambda a, b: a == b,
}


def _rules_path() -> Path:
    from atmosphere.paths import CONFIG
    return Path(CONFIG) / RULES_FILENAME


def load_rules(path: Optional[Any] = None) -> dict:
    """Regeldatei laden. encoding explizit (Windows-Default ist cp1252)."""
    p = Path(path) if path is not None else _rules_path()
    spec = json.loads(p.read_text(encoding="utf-8"))
    if not spec.get("rules"):
        raise ValueError(f"{p}: keine Regeln definiert")
    if not spec.get("rule_version"):
        raise ValueError(f"{p}: rule_version fehlt — ohne Version kein datierbarer Bruch")
    return spec


def _layer_score(normalized: dict, name: str) -> float:
    v = (normalized.get(name) or {}).get("score")
    return float(v) if v is not None else 0.0


def _flag(normalized: dict, dotted: str) -> bool:
    layer, _, flag = dotted.partition(".")
    return bool(((normalized.get(layer) or {}).get("flags") or {}).get(flag))


def _score_value(kind: str, meta: dict, normalized: dict) -> float:
    ext = meta.get("external_score", 0.0)
    l4 = _layer_score(normalized, "L4_ionosphere")
    table = {
        "downstream":       meta.get("downstream_score"),
        "preparation":      meta.get("preparation_score"),
        "cavity":           meta.get("cavity_gate_score"),
        "max_external_L4":  max(ext, l4),
        "mean_external_L4": (ext + l4) / 2,
    }
    if kind not in table:
        raise KeyError(f"Unbekannter score-Ausdruck {kind!r} — erlaubt: {sorted(table)}")
    return table[kind]


def _cond_true(cond: dict, ctx: dict) -> bool:
    normalized = ctx["normalized"]
    meta = ctx["meta"]

    if "any_flag" in cond:
        return any(_flag(normalized, f) for f in cond["any_flag"])

    if "count" in cond:
        what = cond["count"]
        if what == "active_layers":
            n = len(ctx["active"])
        elif what == "strong_couplings":
            thr = cond.get("strength_min", 0.5)
            n = sum(1 for c in ctx["couplings"] if (c.get("strength") or 0) > thr)
        else:
            raise KeyError(f"Unbekannter count {what!r}")
        return _OPS[cond["op"]](n, cond["value"])

    if "metric" in cond:
        val = meta.get(cond["metric"])
    elif "layer_score" in cond:
        val = _layer_score(normalized, cond["layer_score"])
    elif "var" in cond:
        if cond["var"] != "avg_conf":
            raise KeyError(f"Unbekannte var {cond['var']!r}")
        val = ctx["avg_conf"]
    else:
        raise KeyError(f"Unverstaendliche Bedingung: {cond}")

    if val is None:
        return False              # fehlender Wert erfuellt keine Schwelle
    return _OPS[cond["op"]](val, cond["value"])


def classify(normalized: dict, couplings: list, dominant, active: list,
             meta: dict, *, avg_conf: float, spec: dict) -> tuple[str, float, float, str, str]:
    """Zustand nach Regeldatei bestimmen.

    Returns (state, score, confidence, rule_id, rule_version) — Regel-ID und
    Version wandern in den Snapshot, damit spaeter nachvollziehbar ist, WELCHE
    Regel unter WELCHER Fassung gegriffen hat.
    """
    ctx = {"normalized": normalized, "couplings": couplings or [],
           "dominant": dominant, "active": active or [], "meta": meta,
           "avg_conf": avg_conf}
    for rule in spec["rules"]:
        if all(_cond_true(c, ctx) for c in rule.get("all", [])):
            return (rule["state"],
                    _score_value(rule["score"], meta, normalized),
                    rule["confidence"],
                    rule["id"],
                    spec["rule_version"])
    raise RuntimeError("Keine Regel griff — die Regeldatei braucht eine Default-Regel "
                       "mit leerem `all`.")
