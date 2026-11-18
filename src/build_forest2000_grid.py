"""Tree cover in 2000 (Hansen) aggregated to the 5 arc-minute GAEZ grid.

Run once, from the repository root:

    python src/build_forest2000_grid.py

It downloads the Hansen Global Forest Change "treecover2000" tiles (10 x 10 degrees,
30 m pixels) that cover our 62 countries, keeps the pixels with canopy density above
30% (the Global Forest Watch threshold used for our outcome), and adds up their area
(km2) in each 5' cell of the GAEZ v4 grid. Each tile is deleted once processed, so
the ~25 GB of tiles never sit on the disk together.

Output: data/processed/forest2000_5arcmin.csv, one row per 5' cell with forest:
    row, col     position in the global GAEZ grid (2160 x 4320, row 0 at 90N, col 0 at 180W)
    lat, lon     centre of the cell
    forest2000_km2

The notebooks load this small CSV from GitHub; they never need the tiles.
Results per tile are cached, so the script can be stopped and restarted.
"""

import concurrent.futures as cf
import os
import tempfile
import urllib.request
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from shapely.geometry import box

ROOT = Path(__file__).resolve().parents[1]
BORDERS = ROOT / "data/raw/boundaries/ne_10m_admin_0_countries.zip"
SAMPLE = ROOT / "data/processed/shock_panel.csv"  # final sample: 62 countries
OUT = ROOT / "data/processed/forest2000_5arcmin.csv"
CACHE = Path(tempfile.gettempdir()) / "hansen_forest2000_cache"

VERSION = "GFC-2024-v1.12"
URL = ("https://storage.googleapis.com/earthenginepartners-hansen/"
       f"{VERSION}/Hansen_{VERSION}_treecover2000_{{tile}}.tif")

THRESHOLD = 30          # canopy density (%) strictly above which a pixel is forest, as in GFW
CELLS_PER_DEG = 12      # 5 arc-minute grid
N_ROWS, N_COLS = 180 * CELLS_PER_DEG, 360 * CELLS_PER_DEG
EARTH_RADIUS_KM = 6371.0072
BLOCK_ROWS = 1000       # pixel rows read at a time (keeps memory low)
WORKERS = 4


def tile_name(top, left):
    """Hansen tiles are named by their top-left corner, e.g. 10N_070W."""
    ns = "N" if top >= 0 else "S"
    ew = "E" if left >= 0 else "W"
    return f"{abs(top):02d}{ns}_{abs(left):03d}{ew}"


def tiles_for_sample():
    """All 10-degree tiles that touch one of the sample countries."""
    iso3 = set(pd.read_csv(SAMPLE)["iso3"])
    world = gpd.read_file(f"zip://{BORDERS}")
    countries = world[world["ADM0_A3"].isin(iso3)]
    missing = iso3 - set(countries["ADM0_A3"])
    assert not missing, f"countries not found in Natural Earth: {missing}"
    shape = countries.union_all()
    return [tile_name(top, left)
            for top in range(80, -50, -10)
            for left in range(-180, 180, 10)
            if box(left, top - 10, left + 10, top).intersects(shape)]


def cell_index(coord_centres, origin, sign):
    """Index of the 5' cell containing each pixel centre (rows: from 90N, cols: from 180W)."""
    return np.floor(sign * (coord_centres - origin) * CELLS_PER_DEG).astype(int)


def process_tile(tile):
    """Forest area (km2) of one tile, summed in the 5' cells. Returns (rows, cols, km2)."""
    cached = CACHE / f"{tile}.npz"
    if cached.exists():
        d = np.load(cached)
        return d["rows"], d["cols"], d["km2"]

    path = CACHE / f"{tile}.tif"
    urllib.request.urlretrieve(URL.format(tile=tile), path)

    sums = {}
    with rasterio.open(path) as src:
        t = src.transform
        px = t.a                                    # pixel size in degrees (0.00025)
        lon = t.c + (np.arange(src.width) + 0.5) * px
        col_of_px = cell_index(lon, -180.0, +1)
        col_starts = np.flatnonzero(np.r_[True, np.diff(col_of_px) != 0])
        cols = col_of_px[col_starts]

        for r0 in range(0, src.height, BLOCK_ROWS):
            n = min(BLOCK_ROWS, src.height - r0)
            block = src.read(1, window=((r0, r0 + n), (0, src.width)))
            forest = (block > THRESHOLD).astype(np.uint32)

            # number of forest pixels per pixel row and 5' column
            counts = np.add.reduceat(forest, col_starts, axis=1)

            # area of one pixel in each row (km2), exact on the sphere
            top = t.f - (r0 + np.arange(n)) * px
            bottom = top - px
            area = (EARTH_RADIUS_KM ** 2 * np.deg2rad(px)
                    * (np.sin(np.deg2rad(top)) - np.sin(np.deg2rad(bottom))))
            km2 = counts * area[:, None]

            # add the pixel rows into their 5' rows
            row_of_px = cell_index((top + bottom) / 2, 90.0, -1)
            row_starts = np.flatnonzero(np.r_[True, np.diff(row_of_px) != 0])
            km2 = np.add.reduceat(km2, row_starts, axis=0)
            for i, r in enumerate(row_of_px[row_starts]):
                sums[r] = sums.get(r, 0) + km2[i]

    os.remove(path)
    rows, cols_out, vals = [], [], []
    for r, v in sums.items():
        keep = v > 0
        rows.append(np.full(keep.sum(), r))
        cols_out.append(cols[keep])
        vals.append(v[keep])
    rows = np.concatenate(rows) if rows else np.array([], int)
    cols_out = np.concatenate(cols_out) if cols_out else np.array([], int)
    vals = np.concatenate(vals) if vals else np.array([])
    np.savez(cached, rows=rows, cols=cols_out, km2=vals)
    return rows, cols_out, vals


def main():
    CACHE.mkdir(exist_ok=True)
    tiles = tiles_for_sample()
    print(f"{len(tiles)} tiles, cache in {CACHE}", flush=True)

    grid = np.zeros((N_ROWS, N_COLS))
    with cf.ProcessPoolExecutor(WORKERS) as ex:
        futures = {ex.submit(process_tile, t): t for t in tiles}
        for i, f in enumerate(cf.as_completed(futures), 1):
            rows, cols, km2 = f.result()
            np.add.at(grid, (rows, cols), km2)   # a cell can straddle two tiles
            print(f"[{i}/{len(tiles)}] {futures[f]}  {km2.sum():,.0f} km2", flush=True)

    r, c = np.nonzero(grid)
    out = pd.DataFrame({
        "row": r, "col": c,
        "lat": 90 - (r + 0.5) / CELLS_PER_DEG,
        "lon": -180 + (c + 0.5) / CELLS_PER_DEG,
        "forest2000_km2": grid[r, c].round(4),
    })
    out.to_csv(OUT, index=False)
    print(f"saved {OUT} ({len(out):,} cells, {out.forest2000_km2.sum():,.0f} km2 of forest)")


if __name__ == "__main__":
    main()
