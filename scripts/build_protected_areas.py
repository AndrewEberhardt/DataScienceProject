"""Share of each 5 arc-minute grid cell inside a protected area (WDPA, November 2026).

Run once, locally. The WDPA geodatabase (about 2.5 GB unzipped) stays outside the repo in
~/Data/wdpa/. Output (committed to GitHub):
    data/processed/grid_protected.csv.gz : one row per cell of grid_cells.csv.gz
        cell_id
        pa2000          share of the cell protected with status year <= 2000 (before our period)
        pa2000_strict   same, IUCN categories Ia, Ib, II, III, IV only (strict protection)
        pa2025          share protected at any date (including unknown status year)
        pa_noyear       share protected only by areas with unknown status year (STATUS_YR = 0)
        pa_year         first year any part of the cell became protected (0 if never)

Selection of protected areas (Protected Planet methodology):
    polygons only (points have no boundary), STATUS Designated / Established / Inscribed
    (Proposed dropped), REALM not Marine, UNESCO-MAB Biosphere Reserves dropped (their buffer
    and transition zones are not protected), only areas in the 62 sample countries.

Method: protected areas are rasterized on a 30 arc-second grid (10 x 10 sub-cells per
5 arc-minute cell, about 0.9 km). A sub-cell is protected if its center is inside a protected
area. Each sub-cell keeps the earliest status year of the areas that cover it (overlaps are
counted once). Shares are the fraction of the 100 sub-cells of the cell (sub-cells have
almost the same area within one cell).
"""

from pathlib import Path

import numpy as np
import pandas as pd
import pyogrio
from rasterio.features import rasterize
from rasterio.transform import from_origin

REPO = Path(__file__).resolve().parents[1]
GDB = Path.home() / "Data/wdpa/WDPA_Nov2026_Public.gdb"
LAYER = "WDPA_poly_Nov2026"
OUT_FILE = REPO / "data/processed/grid_protected.csv.gz"

SUB = 10                         # sub-cells per cell side (5 arc-minutes / 30 arc-seconds)
N_COLS = 4320                    # GAEZ grid columns
CHUNK_ROWS = 60                  # cell rows rasterized at once (5 degrees)
UNKNOWN = 9999                   # code for unknown status year (overwritten by any known year)
STRICT = {"Ia", "Ib", "II", "III", "IV"}


def load_protected_areas(sample_iso3):
    cols = ["SITE_ID", "DESIG_ENG", "IUCN_CAT", "REALM", "STATUS", "STATUS_YR", "ISO3"]
    pa = pyogrio.read_dataframe(GDB, layer=LAYER, columns=cols)
    keep = (pa.STATUS.isin(["Designated", "Established", "Inscribed"])
            & (pa.REALM != "Marine")
            & (pa.DESIG_ENG != "UNESCO-MAB Biosphere Reserve")
            & pa.ISO3.str.split(";").apply(lambda l: any(i in sample_iso3 for i in l)))
    pa = pa[keep].copy()
    pa["year"] = pa.STATUS_YR.where(pa.STATUS_YR > 0, UNKNOWN).astype(int)
    print(f"{len(pa):,} protected areas kept, {(pa.year == UNKNOWN).mean():.1%} with unknown year")
    return pa


def burn(pa, r0, n_rows):
    """Earliest status year per 30 arc-second sub-cell for cell rows r0 .. r0 + n_rows (0 = not protected)."""
    transform = from_origin(-180, 90 - r0 / 12, 1 / (12 * SUB), 1 / (12 * SUB))
    pa = pa.sort_values("year", ascending=False)    # later shapes overwrite: earliest year wins
    if pa.empty:
        return np.zeros((n_rows * SUB, N_COLS * SUB), np.uint16)
    return rasterize(zip(pa.geometry, pa.year), out_shape=(n_rows * SUB, N_COLS * SUB),
                     transform=transform, fill=0, dtype="uint16")


def main():
    cells = pd.read_csv(REPO / "data/processed/grid_cells.csv.gz", usecols=["cell_id", "row", "col", "iso3"])
    pa = load_protected_areas(set(cells.iso3))
    strict = pa[pa.IUCN_CAT.isin(STRICT)]

    out = []
    for r0 in range(cells.row.min(), cells.row.max() + 1, CHUNK_ROWS):
        n = min(CHUNK_ROWS, cells.row.max() + 1 - r0)
        c = cells[(cells.row >= r0) & (cells.row < r0 + n)]
        if c.empty:
            continue
        lat_top, lat_bot = 90 - r0 / 12, 90 - (r0 + n) / 12
        box = pa.cx[:, lat_bot:lat_top]
        blocks = {}
        for name, layer in [("all", box), ("strict", strict.cx[:, lat_bot:lat_top])]:
            y = burn(layer, r0, n).reshape(n, SUB, N_COLS, SUB).transpose(0, 2, 1, 3).reshape(n, N_COLS, SUB * SUB)
            blocks[name] = y[c.row.to_numpy() - r0, c.col.to_numpy()]          # cells x 100 sub-cells
        a, s = blocks["all"], blocks["strict"]
        known = np.where((a > 0) & (a < UNKNOWN), a, UNKNOWN)
        out.append(pd.DataFrame({
            "cell_id": c.cell_id.to_numpy(),
            "pa2000": ((a > 0) & (a <= 2000)).mean(axis=1),
            "pa2000_strict": ((s > 0) & (s <= 2000)).mean(axis=1),
            "pa2025": (a > 0).mean(axis=1),
            "pa_noyear": (a == UNKNOWN).mean(axis=1),
            "pa_year": np.where(known.min(axis=1) < UNKNOWN, known.min(axis=1), 0),
        }))
        print(f"rows {r0}-{r0 + n}: {len(c):,} cells, {len(box):,} protected areas")

    res = cells[["cell_id", "iso3"]].merge(pd.concat(out), on="cell_id", how="left")
    assert res.pa2025.notna().all()

    # Check: share of the sample's forest cells protected, by country (compare with Protected Planet)
    check = res.groupby("iso3")[["pa2000", "pa2000_strict", "pa2025"]].mean().sort_values("pa2025")
    print(check.round(3).to_string())
    print("Sample:", res[["pa2000", "pa2000_strict", "pa2025", "pa_noyear"]].mean().round(3).to_dict())

    res.drop(columns="iso3").round(2).to_csv(OUT_FILE, index=False)
    print(f"Written {OUT_FILE} ({OUT_FILE.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
