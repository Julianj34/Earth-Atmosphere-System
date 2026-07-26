"""
ENSO-Ingest: CPC Weekly Nino3.4 + ONI
=====================================
Gemeinsamer Parser fuer L2 (Makro-Zustand) und L9 (externe Validierung).
Beide Notebooks trugen je eine eigene Kopie; die ONI-Variante war in beiden
identisch defekt.

VERIFIZIERT gegen das echte Dateiformat (2026-07-25):

    oni.ascii.txt          SEAS YR TOTAL ANOM       -> 4 Spalten, ANOM = Index 3
      SEAS YR TOTAL ANOM
      DJF 1950 24.72 -1.53

    Der alte Parser verlangte `len(parts) >= 5` und las `parts[4]`. Die
    Bedingung ist fuer JEDE Datenzeile falsch -> `oni_vals` blieb leer, und weil
    am `if oni_vals:` ein `else` fehlte, ohne jede Meldung. Folge: `enso_oni`
    war bei jedem Lauf None. Daraus wiederum:
      - die El-Nino-Hochstufung (verlangt `enso_oni is not None`) lief nie,
      - `phase_observed` fiel auf 'warm_neutral' zurueck, waehrend
        `macro_phase` 'el_nino' sagte (widerspruechliche Felder im selben JSON),
      - der einzige echte externe Check in L9 lief ins Leere.

DESIGN (Lehre aus dem Befund)
-----------------------------
- Parser sind REINE Funktionen ueber Text: kein Netzzugriff, damit testbar.
- Sie melden Fehlschlaege LAUT ueber `meta['reason']`, statt still None zu
  liefern. "Quelle geliefert, aber nichts geparst" ist ein anderer Zustand als
  "Quelle nicht erreichbar" und muss unterscheidbar bleiben.
- Zahlen werden per Regex geholt und der LETZTE Float einer Zeile als Anomalie
  genommen. Das ueberlebt sowohl die 4-Spalten-Variante als auch eine
  zusaetzliche CLIM-Spalte und den Fixed-Width-Fall, in dem eine negative
  Anomalie ohne Leerzeichen an den Vorwert stossen kann ("24.72-1.53").
"""
from __future__ import annotations

import datetime as _dt
import re
from typing import Optional

# Ein Float, optional mit Vorzeichen. Faengt auch "24.72-1.53" als zwei Werte.
_FLOAT = re.compile(r"[+-]?\d+\.\d+")

# Die zwoelf ueberlappenden Dreimonats-Saisons der ONI-Datei.
_SEASONS = {
    "DJF", "JFM", "FMA", "MAM", "AMJ", "MJJ",
    "JJA", "JAS", "ASO", "SON", "OND", "NDJ",
}

_MONTHS = {
    "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
    "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12,
}

# Plausibilitaetsgrenzen: ausserhalb liegt kein realer ENSO-Wert.
_ANOM_MIN, _ANOM_MAX = -4.0, 4.0


def parse_oni_ascii(text: Optional[str]) -> tuple[Optional[float], dict]:
    """CPC ONI (3-Monats-Mittel) aus oni.ascii.txt.

    Returns (letzter_anom_wert, meta). Bei Fehlschlag ist der Wert None und
    meta['reason'] sagt WARUM - nie stilles None.
    """
    meta = {
        "source": "cpc_oni_ascii",
        "n_lines": 0, "n_parsed": 0,
        "last_season": None, "last_year": None,
        "reason": None,
    }
    if not text:
        meta["reason"] = "no_text (Abruf fehlgeschlagen oder leer)"
        return None, meta

    lines = text.splitlines()
    meta["n_lines"] = len(lines)
    vals, seasons, years = [], [], []

    for line in lines:
        parts = line.split()
        # Datenzeile: Saison-Code + Jahr. Header ('SEAS YR ...') faellt raus.
        if len(parts) < 3 or parts[0].upper() not in _SEASONS:
            continue
        nums = _FLOAT.findall(line)
        if not nums:
            continue
        try:
            anom = float(nums[-1])          # ANOM ist immer der LETZTE Float
        except ValueError:
            continue
        if not (_ANOM_MIN <= anom <= _ANOM_MAX):
            continue
        vals.append(anom)
        seasons.append(parts[0].upper())
        years.append(parts[1])

    meta["n_parsed"] = len(vals)
    if not vals:
        meta["reason"] = (
            f"no_valid_rows (0 von {len(lines)} Zeilen geparst) - "
            "Dateiformat pruefen: erwartet 'SEAS YR TOTAL ANOM'"
        )
        return None, meta

    meta["last_season"] = seasons[-1]
    meta["last_year"] = years[-1]
    return round(vals[-1], 2), meta


def parse_weekly_nino34(text: Optional[str]) -> tuple[Optional[float], dict]:
    """CPC Weekly Nino3.4 SSTA aus wksst9120.for (Fixed-Width).

    Zeilenformat (nach dem 10-stelligen Datum) sechs Zahlenpaare:
        N12_SST N12_SSTA N3_SST N3_SSTA N34_SST N34_SSTA
    Nino3.4-SSTA ist damit der Float mit Index 5.
    """
    meta = {
        "source": "cpc_weekly", "n_lines": 0, "n_parsed": 0,
        "last_date": None, "age_days": None, "stale": False, "reason": None,
    }
    if not text:
        meta["reason"] = "no_text (Abruf fehlgeschlagen oder leer)"
        return None, meta

    data_lines = [l.strip() for l in text.splitlines()
                  if l.strip() and l.strip()[0].isdigit()]
    meta["n_lines"] = len(data_lines)
    vals, dates = [], []

    for line in data_lines:
        rest = line[10:]
        nums = _FLOAT.findall(rest)
        if len(nums) < 6:
            continue
        try:
            ssta = float(nums[5])
        except ValueError:
            continue
        if not (_ANOM_MIN <= ssta <= _ANOM_MAX):
            continue
        vals.append(ssta)
        dates.append(line[:10].strip())

    meta["n_parsed"] = len(vals)
    if not vals:
        meta["reason"] = (
            f"no_valid_rows (0 von {len(data_lines)} Datenzeilen geparst)"
        )
        return None, meta

    meta["last_date"] = dates[-1]
    meta["age_days"], meta["stale"] = _age_of(dates[-1])
    return round(vals[-1], 2), meta


def parse_weekly_series(text: Optional[str]) -> list:
    """Nur die Weekly-Reihe (fuer den Trend der letzten Wochen)."""
    if not text:
        return []
    out = []
    for line in text.splitlines():
        line = line.strip()
        if not line or not line[0].isdigit():
            continue
        nums = _FLOAT.findall(line[10:])
        if len(nums) < 6:
            continue
        try:
            ssta = float(nums[5])
        except ValueError:
            continue
        if _ANOM_MIN <= ssta <= _ANOM_MAX:
            out.append(ssta)
    return out


def _age_of(date_str: str, max_age_days: int = 90) -> tuple[Optional[int], bool]:
    """Alter eines '28APR2026'-Datums in Tagen + Stale-Flag."""
    m = re.match(r"(\d{2})([A-Z]{3})(\d{4})", (date_str or "").strip().upper())
    if not m or m.group(2) not in _MONTHS:
        return None, False
    try:
        last = _dt.date(int(m.group(3)), _MONTHS[m.group(2)], int(m.group(1)))
    except ValueError:
        return None, False
    age = (_dt.date.today() - last).days
    return age, age > max_age_days
