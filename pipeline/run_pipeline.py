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
def run_notebook(n: int, timeout: int = 600) -> bool:
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
    print(f"ok ({time.time() - t0:.0f}s)")
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
        if not run_notebook(n, timeout=args.timeout):
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
