#!/usr/bin/env python3
"""
run_pipeline.py — runs the whole chain locally.

Order:
  1. L0..L9 sequentially. Each notebook reads its predecessors' states and writes
     its own. L7 appends to layer7_history.jsonl; L7/L8 run the confound guard
     (annotate_l7 / annotate_l8) right before writing.
  2. holarchic_coupling_analysis.run() over the history — meta-analysis, coupling
     matrix (with confound_type), event card, holon registry, report.

L2.5 (meso) is NOT executed here — it is blocked until real feeds are wired in
config/meso_feeds.yaml (meta.real_feeds: true). See docs/Atmosphären_Architektur.md §4.

Usage:
    python pipeline/run_pipeline.py                # full chain L0..L9 + holarchic
    python pipeline/run_pipeline.py --from 7       # resume at L7 (states already present)
    python pipeline/run_pipeline.py --only 7 8 9   # run a specific subset
    python pipeline/run_pipeline.py --holarchic    # only the holarchic meta-analysis
    python pipeline/run_pipeline.py --timeout 900  # per-notebook timeout (s)
    python pipeline/run_pipeline.py --keep-outputs # Grafiken im Notebook behalten
"""
from __future__ import annotations
import sys
import time
import shutil
import pathlib
import argparse
import subprocess

# --------------------------------------------------------------------------- #
# resolve project root (CWD-independent) and make src importable
# --------------------------------------------------------------------------- #
_root = pathlib.Path(__file__).resolve().parent
while not (_root / ".project-root").exists() and _root != _root.parent:
    _root = _root.parent
if not (_root / ".project-root").exists():
    sys.exit("ERROR: .project-root marker not found above pipeline/. "
             "Place an empty .project-root at the repository top.")
sys.path.insert(0, str(_root / "src"))

from atmosphere import paths  # noqa: E402  (after sys.path insert)

NOTEBOOKS = _root / "notebooks"
ALL_LAYERS = list(range(10))  # L0..L9


# --------------------------------------------------------------------------- #
def strip_outputs(nb_path: pathlib.Path, retries: int = 4, delay: float = 0.3) -> int:
    """Zell-Outputs nach dem Lauf entfernen. Gibt gesparte Bytes zurueck.

    Warum als Nachschritt: `nbconvert --execute --inplace` schreibt die Outputs
    immer zurueck, und das erste plotly-Diagramm bettet die komplette
    plotly.js-Bibliothek (~4,7 MB) als HTML in die Datei ein — pro Notebook, bei
    jedem Lauf. Beim Pipeline-Betrieb sieht die niemand; sie kosten nur Platz
    und machen Git-Diffs unlesbar.

    `--ClearOutputPreprocessor.enabled=True` hilft NICHT: nbconvert fuehrt diesen
    Preprocessor VOR dem Execute-Schritt aus, die Outputs entstehen also danach
    neu. Deshalb hier, nach erfolgreichem Lauf.

    WINDOWS: `os.replace` scheitert mit "Zugriff verweigert" (WinError 5), sobald
    irgendein Prozess ein Handle auf die ZIELdatei haelt — Jupyter im Browser,
    VS Code, OneDrive-Sync oder der Virenscanner, der die eben geschriebene Datei
    prueft. Unter POSIX ist das erlaubt, unter Windows nicht. Deshalb:
      1. mehrere Versuche mit wachsender Wartezeit (faengt kurzlebige Scanner-Locks),
      2. Rueckfall auf direktes Ueberschreiben (nicht atomar, klappt aber, wenn
         der Lock nur ein LESE-Handle ist — der haeufigste Fall),
      3. die temporaere Datei wird in JEDEM Fall aufgeraeumt.

    Der Quelltext bleibt unangetastet — nur `outputs` und `execution_count`.
    """
    import json
    import time

    try:
        before = nb_path.stat().st_size
        nb = json.loads(nb_path.read_text(encoding="utf-8"))
        for c in nb.get("cells", []):
            if c.get("cell_type") == "code":
                c["outputs"] = []
                c["execution_count"] = None
        payload = json.dumps(nb, indent=1, ensure_ascii=False) + "\n"
    except Exception as e:
        print(f"      (Outputs konnten nicht gelesen/aufbereitet werden: {e})")
        return 0

    tmp = nb_path.with_name(nb_path.name + ".tmp")
    last_err = None
    try:
        # 1) bevorzugt: atomar ersetzen, mit Wiederholungen gegen kurzlebige Locks
        for attempt in range(retries):
            try:
                tmp.write_text(payload, encoding="utf-8")
                tmp.replace(nb_path)
                return before - nb_path.stat().st_size
            except OSError as e:
                last_err = e
                time.sleep(delay * (attempt + 1))
        # 2) Rueckfall: direkt schreiben
        try:
            nb_path.write_text(payload, encoding="utf-8")
            return before - nb_path.stat().st_size
        except OSError as e:
            last_err = e
    finally:
        try:
            tmp.unlink()               # nie eine verwaiste .tmp zuruecklassen
        except OSError:
            pass

    print(f"      (Outputs nicht entfernt: {last_err})")
    print(f"       Unter Windows haelt meist Jupyter/VS Code die Datei offen, sonst "
          f"OneDrive oder der Virenscanner.")
    print(f"       Notebook schliessen und erneut laufen lassen — oder dauerhaft "
          f"mit --keep-outputs abschalten.")
    return 0


def run_notebook(n: int, timeout: int = 600, strip: bool = True) -> bool:
    """Execute one layer notebook in place via nbconvert. Returns success."""
    nb = NOTEBOOKS / f"atmosphere_analysis_layer{n}.ipynb"
    if not nb.exists():
        print(f"  L{n}: notebook missing — skipped")
        return False
    print(f"  ▶ L{n} …", end=" ", flush=True)
    t0 = time.time()
    proc = subprocess.run(
        [sys.executable, "-m", "jupyter", "nbconvert",
         "--to", "notebook", "--execute", "--inplace",
         f"--ExecutePreprocessor.timeout={timeout}", str(nb)],
        capture_output=True, text=True)
    if proc.returncode != 0:
        print("FAILED")
        tail = (proc.stderr or proc.stdout or "").strip().splitlines()[-25:]
        print("\n".join("      " + l for l in tail))
        return False
    saved = strip_outputs(nb) if strip else 0
    extra = f", {saved/1e6:.1f} MB Outputs entfernt" if saved > 1e6 else ""
    print(f"ok ({time.time() - t0:.0f}s{extra})")
    return True


def run_holarchic() -> bool:
    """Run the holarchic meta-analysis and place its 4 outputs in canonical dirs."""
    from atmosphere.meta.holarchic_coupling_analysis import run
    print("  ▶ holarchic_coupling_analysis …", end=" ", flush=True)
    if not paths.HISTORY.exists():
        print("FAILED — history not found (run L7 first)")
        return False
    l8 = paths.layer_state(8)
    l9 = paths.layer_state(9)
    res = run(str(paths.HISTORY),
              l8_path=str(l8) if l8.exists() else None,
              outdir=str(paths.STATES_COUPLING),
              l9_path=str(l9) if l9.exists() else None)
    # run() writes all four into STATES_COUPLING; move report -> reports/ and
    # registry -> registry/ so each artifact lives in its canonical place.
    moves = {
        "holarchic_analysis_report.md": paths.REPORTS,
        "holon_registry.yaml":          paths.STATES_REGISTRY,
    }
    for fname, dest in moves.items():
        src = paths.STATES_COUPLING / fname
        if src.exists():
            shutil.move(str(src), str(dest / fname))
    print(f"ok ({res['n_snapshots']} snapshots, "
          f"break: {max(res['chain_break_distribution'], key=res['chain_break_distribution'].get)})")
    return True


# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser(description="atmosphere_analysis pipeline runner")
    ap.add_argument("--from", dest="start", type=int, default=0,
                    help="resume at layer N (default 0)")
    ap.add_argument("--only", nargs="+", type=int,
                    help="run only these layers (overrides --from)")
    ap.add_argument("--holarchic", action="store_true",
                    help="run only the holarchic meta-analysis")
    ap.add_argument("--no-holarchic", action="store_true",
                    help="skip the holarchic step after the notebooks")
    ap.add_argument("--timeout", type=int, default=600,
                    help="per-notebook timeout in seconds (default 600)")
    ap.add_argument("--keep-outputs", action="store_true",
                    help="Zell-Outputs im Notebook belassen (Default: nach dem "
                         "Lauf entfernen — spart ~4,7 MB plotly.js pro Notebook)")
    args = ap.parse_args()

    print("=" * 60)
    print("atmosphere_analysis — pipeline")
    print(f"root: {_root}")
    print("=" * 60)

    if args.holarchic:
        ok = run_holarchic()
        sys.exit(0 if ok else 1)

    layers = args.only if args.only else [n for n in ALL_LAYERS if n >= args.start]

    t0 = time.time()
    for n in layers:
        if not run_notebook(n, timeout=args.timeout, strip=not args.keep_outputs):
            print(f"\nAborted at L{n}. Fix the error, then resume with "
                  f"`--from {n}`.")
            sys.exit(1)

    if not args.no_holarchic:
        if not run_holarchic():
            sys.exit(1)

    print("=" * 60)
    print(f"✅ done in {time.time() - t0:.0f}s")
    print("=" * 60)


if __name__ == "__main__":
    main()
