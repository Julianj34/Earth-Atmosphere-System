"""
atmosphere/config/domain.py — EINZIGE Quelle fuer die raeumliche Stichprobe und
den Zeitbezug des Analyse-Stacks (L2, L3, Meso).

L3 nutzt KEINE zusammenhaengende Region, sondern 6 feste globale Punkte
(identisch mit Layer 2) und mittelt ueber sie. Damit L3 und der Meso-Holon
garantiert dieselbe Stichprobe + denselben Zeitbezug verwenden, stehen die Werte
genau EINMAL hier; beide Seiten importieren sie von hier statt sie zu duplizieren.

Werte uebernommen aus der L3-Ingestion (OM_POINTS; Open-Meteo, forecast_hours=6,
timezone=UTC, aktuellster Stundenwert, Mittel ueber die Punkte).
"""

# 6 feste Stichprobenpunkte (== Layer 2 == Layer 3). Single Source.
OM_POINTS = [
    {'name': 'Mitteleuropa',   'lat': 48.0,  'lon': 11.0},
    {'name': 'Tropen (Kongo)', 'lat': -4.0,  'lon': 23.0},
    {'name': 'Arktis',         'lat': 78.0,  'lon': 15.0},
    {'name': 'Pazifik (ITCZ)', 'lat':  5.0,  'lon': -150.0},
    {'name': 'Amazonia',       'lat': -5.0,  'lon': -60.0},
    {'name': 'Sahel',          'lat': 13.0,  'lon': 10.0},
]

# Zeitbezug + Aggregation, exakt wie L3 sie anwendet.
TIME_BASIS = {
    "source":  "open-meteo",
    "select":  "first_nonnull_hourly",   # aktuellster Stundenwert
    "horizon": "forecast_hours=6",
    "tz":      "UTC",
    "agg":     "mean_over_points",        # Mittel ueber OM_POINTS
}


def points_match(points) -> bool:
    """True wenn `points` exakt OM_POINTS (Name+lat+lon) entspricht — der
    Alignment-Check des Meso-Holons gegen L3."""
    if not points or len(points) != len(OM_POINTS):
        return False
    key = lambda p: (p.get('name'), p.get('lat'), p.get('lon'))
    return sorted(map(key, points)) == sorted(map(key, OM_POINTS))
