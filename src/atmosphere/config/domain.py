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
#
# Zusatzattribute (additiv — Konsumenten, die nur name/lat/lon lesen, bleiben
# unberuehrt; points_match() vergleicht weiterhin nur name/lat/lon):
#
#   convective : liegt der Punkt im Regime TIEFER tropischer Konvektion?
#                Nur diese Punkte sind fuer den Meso-Holon (organisierte
#                Konvektion) physikalisch aussagekraeftig. Ein Mittel ueber
#                alle sechs mischt Svalbard und Mitteleuropa hinein und
#                verduennt genau das Signal, das gemessen werden soll.
#   land       : Landpunkt? Bodengebundene Groessen (z.B. soil_moisture)
#                sind ueber offenem Ozean strukturell 0 und duerfen nicht
#                als "trocken" in ein Mittel eingehen.
#
# Hinweis Arktis: Svalbard ist Landflaeche, liefert aber ganzjaehrig
# soil_moisture ~0 (Eis/Permafrost) — fuer bodenfeuchte-basierte Groessen
# also trotz land=True mit Vorsicht zu behandeln.
OM_POINTS = [
    {'name': 'Mitteleuropa',   'lat': 48.0,  'lon': 11.0,   'convective': False, 'land': True},
    {'name': 'Tropen (Kongo)', 'lat': -4.0,  'lon': 23.0,   'convective': True,  'land': True},
    {'name': 'Arktis',         'lat': 78.0,  'lon': 15.0,   'convective': False, 'land': True},
    {'name': 'Pazifik (ITCZ)', 'lat':  5.0,  'lon': -150.0, 'convective': True,  'land': False},
    {'name': 'Amazonia',       'lat': -5.0,  'lon': -60.0,  'convective': True,  'land': True},
    {'name': 'Sahel',          'lat': 13.0,  'lon': 10.0,   'convective': True,  'land': True},
]

# Namen der konvektiven Punkte — von L3 und dem Meso-Holon genutzt, damit die
# Auswahl an EINER Stelle steht. Der ITCZ-Punkt ist bewusst dabei: die
# innertropische Konvergenzzone ist der Archetyp organisierter Konvektion,
# auch wenn sie ueber Ozean liegt.
CONVECTIVE_POINTS = [p['name'] for p in OM_POINTS if p['convective']]
LAND_POINTS       = [p['name'] for p in OM_POINTS if p['land']]

# Teilmenge NUR der konvektiven LANDpunkte (Kongo, Amazonia, Sahel).
# Warum als eigene Menge: Land- und Ozeankonvektion sind verschiedene Regime.
# Ueber Land dominiert der Tagesgang (Nachmittagsmaximum), die ITCZ konvektiert
# kontinuierlicher. Beides in EIN Maximum zu werfen mischt die Regime -- relevant,
# weil die Stichprobenzeitpunkte ohnehin ueber die Lokalzeiten streuen.
# L3 rechnet BEIDE Mengen; welche der Meso-Holon nutzt, entscheidet _CLOUD_FIELD
# in meso_ingest.py -- ohne dass L3 dafuer neu laufen muss.
CONVECTIVE_LAND_POINTS = [p['name'] for p in OM_POINTS if p['convective'] and p['land']]

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
