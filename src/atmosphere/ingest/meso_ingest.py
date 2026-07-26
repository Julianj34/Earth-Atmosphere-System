"""
meso_ingest.py — Ingestion-Adapter fuer den Meso-Holon (L2.5).

Speist OLR (Organisations-Proxy) und CIN (das Gate) in layer_meso.score_meso ein.

WICHTIG nach L3-Abgleich:
- CIN ist KEIN neuer externer Feed. L3 ingestet convective_inhibition bereits
  (Open-Meteo, dieselben OM_POINTS) und exponiert es als
  raw_values['CIN_mean_Jkg']. Der Meso-Gate liest es von dort -> per Konstruktion
  alignt (gleiche Punkte, gleiche Zeit).
- OLR ist der EINZIGE wirklich neue Feed (NOAA interpolated OLR, Mittel ueber
  dieselben OM_POINTS).

ALIGNMENT-GUARD (strukturell): Die Stichprobe kommt aus config/domain.py
(OM_POINTS == L3). points_match() prueft, dass gegen exakt L3s Punkte gescort
wird; sonst bleibt der Holon "inferred".
"""
from typing import Callable, Optional
from atmosphere.layers.layer_meso import score_meso, LAYER_ID
from atmosphere.config.domain import OM_POINTS, TIME_BASIS, points_match


def ingest_meso(
    *,
    olr_loader: Callable[..., Optional[float]],
    cin_from_l3: Optional[float],
    cloud_cover: Optional[float] = None,
    points: Optional[list] = None,
    mjo_amplitude: Optional[float] = None,
    mjo_phase: Optional[int] = None,
    shear_0_6km: Optional[float] = None,
    midlevel_rh: Optional[float] = None,
    iorg: Optional[float] = None,
) -> dict:
    """
    points: Stichprobe; default = config OM_POINTS (== L3).
    olr_loader(points) -> OLR-Anomalie [W/m^2], Mittel ueber dieselben Punkte.
        None falls Quelle veraltet/fehlt. PRIMAERER Organisations-Proxy.
    cloud_cover -> Gesamtbewoelkung [%] aus layer3_state raw_values
        ['CloudCover_mean_pct]. UEBERGANGS-Fallback fuer OLR (score_meso nutzt
        ihn nur, wenn OLR fehlt). Schwaecher als echtes OLR, aber immer aktuell
        und alignt -> haelt den Holon waehrend der OLR-Quellen-Migration 'measured'.
    cin_from_l3 -> CIN [J/kg] aus layer3_state raw_values['CIN_mean_Jkg'].
        Schon ingested, automatisch alignt.
    """
    if points is None:
        points = OM_POINTS
    aligned = points_match(points)

    olr = olr_loader(points=points)
    cin = cin_from_l3

    # Organisation kann aus OLR ODER (Fallback) aus Bewoelkung kommen.
    org_present = (olr is not None) or (cloud_cover is not None)
    status = "measured" if (org_present and cin is not None and aligned) else "inferred"

    inp = {
        "olr_anomaly":   olr,
        "cloud_cover":   cloud_cover,
        "cin":           cin,
        "mjo_amplitude": mjo_amplitude,
        "mjo_phase":     mjo_phase,
        "shear_0_6km":   shear_0_6km,
        "midlevel_rh":   midlevel_rh,
        "iorg":          iorg,
    }
    result = score_meso(inp, source_status=status)
    result["ingest"] = {
        "layer": LAYER_ID,
        "aligned_to_l3_points": aligned,
        "time_basis": TIME_BASIS,
        "olr_present": olr is not None,
        "cloud_present": cloud_cover is not None,
        "organisation_source": result.get("organisation_source"),
        "cin_source": "layer3_state (reused)" if cin is not None else None,
        "source_status": status,
    }
    return result


def load_cin_from_l3_state(layer3_state: dict) -> Optional[float]:
    """CIN [J/kg] aus L3s bereits ingestetem Wert (kein neuer Feed,
    per Konstruktion alignt)."""
    return (layer3_state.get("raw_values") or {}).get("CIN_mean_Jkg")


# EINZIGER Schalter fuer die Wolken-Aggregation des Organisations-Proxys.
# Moegliche Werte (L3 persistiert alle drei):
#   "CloudCover_convective_max_pct"   Max  ueber Kongo/ITCZ/Amazonia/Sahel   [Default]
#   "CloudCover_convective_mean_pct"  Mean ueber dieselben vier Punkte
#   "CloudCover_convland_max_pct"     Max  NUR ueber Landkonvektion (ohne ITCZ)
#   "CloudCover_convland_mean_pct"    Mean NUR ueber Landkonvektion (ohne ITCZ)
#   "CloudCover_mean_pct"             Mittel ueber ALLE sechs Punkte  (alt)
#
# Land vs. mit-ITCZ ist eine PHYSIKALISCHE Wahl, keine technische: die ITCZ ist der
# Archetyp organisierter Konvektion, mischt aber ein kontinuierlicheres Regime unter
# die tagesgang-dominierte Landkonvektion.
#
# Warum Maximum ueber konvektive Punkte: organisierte Konvektion ist ein LOKALES
# Phaenomen. Das globale Mittel mischte Svalbard, Mitteleuropa und Wuestenrand
# hinein und verduennte das Signal. Das Maximum beantwortet "ist IRGENDWO
# organisiert?" statt "ist es im Schnitt bewoelkt?".
# Umstellen = diese eine Zeile; L3 muss dafuer NICHT neu laufen.
_CLOUD_FIELD = "CloudCover_convective_max_pct"


def load_cloud_from_l3_state(layer3_state: dict) -> Optional[float]:
    """Wolken-Anteil [%] als Organisations-Proxy aus L3s bereits ingestetem Wert.

    Nutzt `_CLOUD_FIELD` (Default: Maximum ueber die konvektiven Punkte) und
    faellt auf das alte globale Mittel zurueck, damit States aus Laeufen VOR
    dieser Aenderung weiterhin lesbar bleiben."""
    rv = layer3_state.get("raw_values") or {}
    val = rv.get(_CLOUD_FIELD)
    if val is None:
        val = rv.get("CloudCover_mean_pct")   # Rueckfall fuer alte States
    return val


# ── OLR-Quelle (Konvektions-/Organisations-Proxy) ───────────────────────────
# ACHTUNG Quellen-Lage (Stand 2026-06): Die klassische PSL "interp_OLR"
# (Liebmann & Smith) ist EINGEFROREN (letzter Tag ~2022-12-31, PSL: "last
# planned update ... resume when funded"). Der NCEI-THREDDS-Daily-CDR (v01r02)
# ist ebenfalls ausser Betrieb -> umgezogen nach v02r00:
#   https://archive.data.noaa.gov/cdr#UMD_ESSIC/OLR_CDR/Daily/OLR-D-CDR_01B-21/
# Weitere Live-Optionen: AWS NODD-Bucket "noaa-cdr-atmospheric"; IRI Data Library
# (NOAA CPC daily OLR). Welcher Endpunkt bei dir live + erreichbar ist, MUSS auf
# deiner Maschine bestaetigt werden (ich erreiche NOAA von hier nicht).
#
# Trage unten die bei dir verifizierte, AKTUELLE Quelle ein. Der interp_OLR-Wert
# steht nur als (eingefrorene) Referenz; die Staleness-Pruefung lehnt ihn ohnehin ab.
_OLR_DAILY = "https://psl.noaa.gov/thredds/dodsC/Datasets/interp_OLR/olr.day.mean.nc"  # FROZEN -> ersetzen
_OLR_LTM   = "https://psl.noaa.gov/thredds/dodsC/Datasets/interp_OLR/olr.day.ltm.nc"
_OLR_VAR   = "olr"   # W/m^2, dims (time, lat, lon); lon 0..357.5

# Maximales Alter des neuesten OLR-Tags; aelter -> als veraltet ABGELEHNT (-> None).
# Verhindert, dass ein eingefrorener/haengender Datensatz still alte Werte einspeist.
_OLR_MAX_AGE_DAYS = 10


def _olr_anomaly_from_arrays(olr, clim, points, *, max_age_days=_OLR_MAX_AGE_DAYS, now=None):
    """Reine Logik (ohne Netz): OLR-Anomalie = neuester Tageswert minus
    Tagesklimatologie an der naechsten Gitterzelle, gemittelt ueber `points`.
    Lehnt VERALTETE Daten ab: ist der neueste Tag aelter als `max_age_days`,
    -> (None, meta mit stale=True). `now` nur fuer Tests injizierbar."""
    import numpy as np, pandas as pd
    latest = olr["time"].values[-1]
    try:
        day = pd.Timestamp(latest)
    except Exception:                      # cftime o.ae. -> auf datetime64 zwingen
        day = pd.Timestamp(np.datetime64(str(latest)[:10]))
    now = pd.Timestamp(now) if now is not None else pd.Timestamp.utcnow().tz_localize(None)
    age_days = int((now.normalize() - day.normalize()).days)

    doy = int(day.dayofyear)
    ci  = min(doy - 1, clim.sizes["time"] - 1)            # LTM: 365 Tageseintraege
    anoms = []
    for p in points:
        lat = p["lat"]; lon = p["lon"] % 360.0            # Gitter ist 0..360
        v = float(olr.sel(time=latest, lat=lat, lon=lon, method="nearest").values)
        c = float(clim.isel(time=ci).sel(lat=lat, lon=lon, method="nearest").values)
        if np.isfinite(v) and np.isfinite(c):
            anoms.append(v - c)
    val  = float(np.mean(anoms)) if anoms else None
    meta = {"olr_day": str(np.datetime64(day.to_datetime64(), "D")),
            "age_days": age_days, "n_points": len(anoms),
            "lag_note": "daily, ~1-2 Tage Verzug; nicht stundengleich mit L3"}

    if age_days > max_age_days:           # VERALTET -> ablehnen, Holon bleibt inferred
        meta["stale"] = True
        meta["reason"] = f"neuester OLR-Tag {meta['olr_day']} ist {age_days}d alt (> {max_age_days}d)"
        return None, meta
    return val, meta


def load_olr_anomaly(points: list, return_meta: bool = False):
    """OLR-Anomalie [W/m^2], Mittel ueber dieselben `points` wie L3, fuer den
    neuesten verfuegbaren PSL-Tag. Negativer = mehr Konvektion.
    Braucht: xarray, netCDF4 (OPeNDAP). Bei Netz-/Quellfehler -> None
    (Holon bleibt 'inferred', statt den Lauf zu brechen).
    return_meta=True -> (val, meta) fuer Diagnose; sonst nur val (so ruft
    ingest_meso() es auf)."""
    try:
        import xarray as xr
        ds  = xr.open_dataset(_OLR_DAILY)
        ltm = xr.open_dataset(_OLR_LTM, use_cftime=True)  # LTM-Zeitachse ist Klimatologie (Basisjahr <1582); cftime vermeidet die SerializationWarning. Anomalie matcht ueber day-of-year, daher mit datetime64-Daily kompatibel.
        try:
            val, meta = _olr_anomaly_from_arrays(ds[_OLR_VAR], ltm[_OLR_VAR], points)
        finally:
            ds.close(); ltm.close()
        return (val, meta) if return_meta else val
    except Exception as e:
        print(f"  load_olr_anomaly: Quelle nicht erreichbar ({str(e)[:80]}) -> inferred")
        return (None, {"error": str(e)}) if return_meta else None
