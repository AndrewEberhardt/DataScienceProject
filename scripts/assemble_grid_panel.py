"""Assemble the per-tile Hansen counts (from build_grid_panel.py) into one grid-cell file.

Run once, locally, after build_grid_panel.py. Output (committed to GitHub):
    data/processed/grid_cells.csv.gz : one row per 5 arc-minute cell with forest in 2000
        cell_id, row, col, lat, lon        GAEZ grid position (lat/lon = cell center)
        iso3, in_tropics                   sample country; cell center within 23.44 N / S
        pixel_area_ha                      area of one Hansen pixel at the cell latitude (WGS84)
        forest{T}_px                       pixels with tree cover in 2000 > T percent
        loss{T}_{YYYY}                     pixels of forest{T} lost in year YYYY (2001-2025)
    for T in 25 (Berman et al. 2023 baseline) and 50 (robustness).

Country assignment: a cell belongs to the sample country that contains its center.
Cells whose center is in no sample country (mostly coastal cells with the center at sea)
go to the sample country with the largest overlap with the cell.

It also writes a validation table (our country totals vs Global Forest Watch, threshold 25)
to the console.
"""

import glob
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

from build_grid_panel import CELL_DIR, N_COLS_GLOBAL, N_YEARS, REPO

YEARS = list(range(2001, 2001 + N_YEARS))
OUT_THRESHOLDS = [25, 50]
TROPIC_LAT = 23.44
OUT_FILE = REPO / "data/processed/grid_cells.csv.gz"


def load_tiles():
    """Stack all per-tile .npz files into one table of cells (pixel counts)."""
    parts = []
    for f in sorted(CELL_DIR.glob("*.npz")):
        z = np.load(f)
        d = {"cell_id": z["cell_id"]}
        hist = z["tc_hist"]
        for t in (25, 30, 50):
            d[f"forest{t}_px"] = hist[:, t + 1:].sum(axis=1)
            loss = z[f"loss_{t}"]
            for k, y in enumerate(YEARS):
                d[f"loss{t}_{y}"] = loss[:, k]
        parts.append(pd.DataFrame(d))
    cells = pd.concat(parts, ignore_index=True)
    assert cells.cell_id.is_unique, "a cell appears in two tiles"
    cells["row"], cells["col"] = np.divmod(cells.cell_id.values, N_COLS_GLOBAL)
    cells["lat"] = 90 - (cells.row + 0.5) / 12
    cells["lon"] = -180 + (cells.col + 0.5) / 12
    return cells


def pixel_area_ha(lat):
    """Area (ha) of a 1/4000 degree Hansen pixel centered at each latitude, WGS84 ellipsoid."""
    from pyproj import Geod

    geod = Geod(ellps="WGS84")
    p = 1 / 4000
    rows = np.unique(lat)
    area = {la: abs(geod.polygon_area_perimeter([0, p, p, 0], [la - p / 2, la - p / 2, la + p / 2, la + p / 2])[0]) / 1e4
            for la in rows}
    return np.array([area[la] for la in lat])


def assign_countries(cells):
    """Return the iso3 of the sample country of each cell (NaN if none)."""
    import geopandas as gpd
    from shapely.geometry import box

    countries = []
    for f in sorted(glob.glob(str(REPO / "data/raw/gadm/gadm41_*_1.json.zip"))):
        g = gpd.read_file(f"zip://{f}!{zipfile.ZipFile(f).namelist()[0]}")
        g["geometry"] = g.geometry.make_valid()
        countries.append(g.dissolve().assign(iso3=Path(f).name.split("_")[1])[["iso3", "geometry"]])
    countries = pd.concat(countries, ignore_index=True).set_crs(4326, allow_override=True)

    pts = gpd.GeoDataFrame({"i": np.arange(len(cells))}, geometry=gpd.points_from_xy(cells.lon, cells.lat), crs=4326)
    hit = gpd.sjoin(pts, countries, predicate="within", how="inner").drop_duplicates("i")
    iso = pd.Series(np.nan, index=np.arange(len(cells)), dtype=object)
    iso[hit.i.values] = hit.iso3.values

    # Cells with the center outside every sample country: largest overlap
    rest = np.where(iso.isna())[0]
    h = 1 / 24
    boxes = gpd.GeoDataFrame({"i": rest}, geometry=[box(x - h, y - h, x + h, y + h)
                                                     for x, y in zip(cells.lon.values[rest], cells.lat.values[rest])], crs=4326)
    ov = gpd.overlay(boxes, countries, how="intersection", keep_geom_type=True)
    ov["a"] = ov.geometry.area
    best = ov.sort_values("a").drop_duplicates("i", keep="last")
    iso[best.i.values] = best.iso3.values
    print(f"cells assigned by center: {len(hit):,} | by largest overlap: {len(best):,} | outside sample: {iso.isna().sum():,}")
    return iso.values


def validate(cells):
    """Compare country totals (threshold 25) with Global Forest Watch country tables."""
    gfw = pd.read_excel(REPO / "data/raw/forest/global.xlsx", "Country tree cover loss")
    gfw = gfw[gfw.threshold == 25]
    names = pd.read_csv(REPO / "data/processed/shock_panel.csv")[["iso3", "country"]].drop_duplicates()
    gfw = gfw.merge(names, on="country")
    a = cells.pixel_area_ha
    ours = pd.DataFrame({
        "iso3": cells.iso3,
        "extent": cells.forest25_px * a,
        "loss": cells[[f"loss25_{y}" for y in YEARS]].sum(axis=1) * a,
    }).groupby("iso3").sum()
    ref = gfw.set_index("iso3")
    ref_loss = ref[[f"tc_loss_ha_{y}" for y in YEARS]].sum(axis=1)
    v = pd.DataFrame({
        "extent_ratio": ours.extent / ref.extent_2000_ha,
        "loss_ratio": ours.loss / ref_loss,
    }).round(3)
    corr = {}
    for iso in v.index:
        c = cells[cells.iso3 == iso]
        o = (c[[f"loss25_{y}" for y in YEARS]].multiply(c.pixel_area_ha, axis=0)).sum().values
        r = ref.loc[iso, [f"tc_loss_ha_{y}" for y in YEARS]].values.astype(float)
        corr[iso] = np.corrcoef(o, r)[0, 1]
    v["yearly_corr"] = pd.Series(corr).round(3)
    print("\nValidation against GFW (threshold 25), ours / GFW:")
    print(v.describe().loc[["min", "25%", "50%", "75%", "max"]].to_string())
    print("\nCountries with a ratio outside 0.97-1.03:")
    print(v[(v.extent_ratio.sub(1).abs() > 0.03) | (v.loss_ratio.sub(1).abs() > 0.03)].to_string())
    tot = pd.Series({"extent": ours.extent.sum() / ref.extent_2000_ha.sum(), "loss": ours.loss.sum() / ref_loss.sum()})
    print("\nSample totals, ours / GFW:", tot.round(4).to_dict())
    return v


def main():
    cells = load_tiles()
    print(f"cells with tree cover in 2000 (any): {len(cells):,}")
    cells = cells[cells.forest25_px > 0].reset_index(drop=True)
    cells["iso3"] = assign_countries(cells)
    cells = cells[cells.iso3.notna()].reset_index(drop=True)
    cells["in_tropics"] = (cells.lat.abs() <= TROPIC_LAT).astype(int)
    cells["pixel_area_ha"] = pixel_area_ha(cells.lat.values).round(6)
    print(f"cells kept (forest25 > 0, sample country): {len(cells):,} | in tropics: {cells.in_tropics.sum():,}")

    validate(cells)

    cols = ["cell_id", "row", "col", "lat", "lon", "iso3", "in_tropics", "pixel_area_ha"]
    for t in OUT_THRESHOLDS:
        cols += [f"forest{t}_px"] + [f"loss{t}_{y}" for y in YEARS]
    cells[cols].to_csv(OUT_FILE, index=False, float_format="%.6f", compression={"method": "gzip", "compresslevel": 9})
    print(f"\nsaved {OUT_FILE.relative_to(REPO)}: {OUT_FILE.stat().st_size / 1e6:.1f} MB, {len(cells):,} rows x {len(cols)} columns")


if __name__ == "__main__":
    main()
