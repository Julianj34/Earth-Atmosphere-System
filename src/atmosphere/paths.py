"""
atmosphere.paths — single source of truth for every read/write location.

Resolves the project root independently of the current working directory
(Jupyter sets CWD inconsistently), so notebooks never hardcode relative paths.
Root is found by walking upward until a marker file is seen.

Place this at:  src/atmosphere/paths.py
Marker file  :  drop an empty `.project-root` (or keep `pyproject.toml`) at the top.

Usage in any notebook:
    from atmosphere.paths import layer_state, HISTORY, REPORTS
    # encoding IMMER explizit angeben — der open()-Default ist plattformabhaengig
    # (Windows: cp1252). Ohne das brechen Umlaute/Emoji beim Lesen und Schreiben.
    with open(layer_state(0), "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
"""
from __future__ import annotations
from pathlib import Path

_MARKERS = ("pyproject.toml", ".project-root")


def find_root(start: Path | None = None) -> Path:
    p = (start or Path.cwd()).resolve()
    for cand in (p, *p.parents):
        if any((cand / m).exists() for m in _MARKERS):
            return cand
    raise RuntimeError(
        "project root not found — drop an empty `.project-root` file at the "
        "repository top level so paths can be resolved from any working directory."
    )


ROOT = find_root()

# --- canonical directories ------------------------------------------------- #
STATES          = ROOT / "states"
STATES_CURRENT  = STATES / "current"
STATES_HISTORY  = STATES / "history"
STATES_REGISTRY = STATES / "registry"
STATES_COUPLING = STATES / "coupling"
REPORTS         = ROOT / "reports"
CONFIG          = ROOT / "config"

# create on import so a fresh checkout never fails on a missing folder
for _d in (STATES_CURRENT, STATES_HISTORY, STATES_REGISTRY, STATES_COUPLING, REPORTS, CONFIG):
    _d.mkdir(parents=True, exist_ok=True)

# --- canonical file paths -------------------------------------------------- #
HISTORY = STATES_HISTORY / "layer7_history.jsonl"


def layer_state(n) -> Path:
    """L0–L8 state file. n is an int (0–8) or a string like '2p5_meso'."""
    return STATES_CURRENT / f"layer{n}_state.json"


def state(filename: str) -> Path:
    """Any file under states/current/ by explicit name."""
    return STATES_CURRENT / filename


def report(filename: str) -> Path:
    return REPORTS / filename


def registry(filename: str) -> Path:
    return STATES_REGISTRY / filename


def coupling(filename: str) -> Path:
    return STATES_COUPLING / filename
