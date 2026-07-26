"""
atmosphere/history.py — KANONISCHER History-Loader
==================================================

Eine Antwort auf die Frage "was ist die Stichprobe".

Vorher las jeder Konsument `layer7_history.jsonl` selbst, mit vier
verschiedenen Ergebnissen aus derselben Datei:

    L7 (schreibt)  ->  n roh
    L8             ->  dedupt nach Timestamp, keep-FIRST
    L9             ->  roh, kein Dedup
    holarchic      ->  roh, kein Dedup
    Analyse-Layer  ->  dedupt, keep-LAST

Damit meldeten benachbarte Layer verschiedene Snapshot-Zahlen fuer denselben
Lauf (z.B. 174 vs. 177), und niemand konnte sagen, welche Zahl "die" Stichprobe
ist. Dieses Modul definiert sie genau einmal; alle Konsumenten importieren sie.

WARUM keep-LAST (und nicht keep-first)
--------------------------------------
Verifiziert an den drei realen Duplikat-Paaren im Bestand: die Datensaetze sind
NICHT identisch, und der jeweils SPAETERE ist der reichere --
    2026-05-03  unterscheidet sich in `layers` und `layer8_handoff`
    2026-05-10  nur der zweite hat `field_operators`
    2026-05-12  nur der zweite hat `field_operator_vector`
Offenbar Wiederholungslaeufe mit erweiterter Engine. keep-first (wie L8 es bis
jetzt machte) verwirft also die vollstaendigeren Records -- unter anderem den
Operator-Vektor, aus dem die Thermal-Lead-Lag-Analyse ihre Werte zieht.

DESIGN
------
- `encoding` immer explizit: der open()-Default ist plattformabhaengig
  (Windows: cp1252) und wuerde Umlaute still verfaelschen.
- Defekte Zeilen werden GEZAEHLT und gemeldet, nicht verschluckt.
- Das Schema der History ist ueber die Zeit gewachsen (Engine 1.0 -> 2.0,
  spaeter `meta_scores`, dann `L2p5_meso`). `schema_coverage()` macht sichtbar,
  welcher Anteil der Stichprobe ein Feld ueberhaupt traegt -- damit niemand
  unbemerkt ueber zwei Schemata hinweg mittelt.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Optional

__all__ = [
    "load_history", "load_history_raw", "schema_coverage",
    "sample_signature", "DEDUP_POLICY",
]

DEDUP_POLICY = "timestamp_keep_last"


def _default_path() -> Path:
    from atmosphere.paths import HISTORY
    return Path(HISTORY)


def _read_lines(path: Path) -> tuple[list[dict], int, int]:
    """JSONL zeilenweise lesen. Returns (records, json_errors, blank_lines)."""
    recs: list[dict] = []
    errors = blanks = 0
    text = Path(path).read_text(encoding="utf-8")   # encoding EXPLIZIT
    for line in text.splitlines():
        if not line.strip():
            blanks += 1
            continue
        try:
            recs.append(json.loads(line))
        except json.JSONDecodeError:
            errors += 1                              # zaehlen, nicht verschlucken
    return recs, errors, blanks


def load_history_raw(path: Optional[Any] = None) -> tuple[list[dict], dict]:
    """Alle Zeilen OHNE Dedup, in Dateireihenfolge.

    Nur benutzen, wenn die Roh-Reihenfolge wirklich gebraucht wird (z.B. um
    Mehrfachlaeufe selbst zu untersuchen). Fuer Statistik immer `load_history`.
    """
    p = Path(path) if path is not None else _default_path()
    recs, errors, blanks = _read_lines(p)
    meta = {
        "path": str(p), "view": "raw",
        "raw_records": len(recs), "json_errors": errors, "blank_lines": blanks,
    }
    return recs, meta


def load_history(path: Optional[Any] = None) -> tuple[list[dict], dict]:
    """KANONISCHE Stichprobe: dedupliziert (keep-last), chronologisch sortiert.

    Returns (records, meta). `meta` traegt die vollstaendige Provenienz, damit
    jeder Report sagen kann, worueber er rechnet.
    """
    p = Path(path) if path is not None else _default_path()
    recs, errors, blanks = _read_lines(p)

    by_ts: dict[str, dict] = {}
    without_ts = 0
    for r in recs:
        ts = r.get("timestamp")
        if not ts:
            without_ts += 1
            continue
        by_ts[ts] = r                                # keep-last: spaeterer gewinnt

    out = sorted(by_ts.values(), key=lambda r: r["timestamp"])
    meta = {
        "path": str(p), "view": "canonical",
        "raw_records": len(recs),
        "json_errors": errors,
        "blank_lines": blanks,
        "without_timestamp": without_ts,
        "unique_records": len(out),
        "duplicates": len(recs) - without_ts - len(out),
        "dedup_policy": DEDUP_POLICY,
        "first": out[0]["timestamp"] if out else None,
        "last": out[-1]["timestamp"] if out else None,
        "engine_versions": dict(Counter(r.get("engine_version") for r in out)),
    }
    return out, meta


def schema_coverage(recs: Iterable[dict], fields: Optional[Iterable[str]] = None) -> dict:
    """Anteil der Snapshots, die ein Feld tragen.

    Die History ist ueber die Zeit gewachsen; wer ueber alle Snapshots mittelt,
    mischt sonst unbemerkt Schemata. Deckung < 100% heisst: die Groesse ist
    NICHT ueber die ganze Stichprobe definiert.
    """
    recs = list(recs)
    n = len(recs)
    if fields is None:
        fields = ["meta_scores", "field_operator_vector", "field_operators",
                  "enso_context", "system_state", "avg_score", "couplings"]
    cov = {}
    for f in fields:
        c = sum(1 for r in recs if r.get(f) is not None)
        cov[f] = {"n": c, "pct": round(100.0 * c / n, 1) if n else 0.0}
    layer_keys: Counter = Counter()
    for r in recs:
        layer_keys.update((r.get("layers") or {}).keys())
    cov["_layers"] = {k: {"n": v, "pct": round(100.0 * v / n, 1) if n else 0.0}
                      for k, v in sorted(layer_keys.items())}
    return cov


def sample_signature(meta: dict) -> str:
    """Einzeiler fuer Reports — macht die verwendete Stichprobe nachvollziehbar."""
    if meta.get("view") == "raw":
        return (f"{meta['raw_records']} rohe Snapshots (ohne Dedup), "
                f"{meta['json_errors']} JSON-Fehler")
    return (f"{meta['unique_records']} eindeutige von {meta['raw_records']} rohen "
            f"Snapshots ({meta['duplicates']} Duplikate, {meta['json_errors']} JSON-Fehler, "
            f"Policy: {meta['dedup_policy']})")
