"""Aggregate Hansen Global Forest Change (v1.13, 2001-2025) to the GAEZ 5 arc-minute grid.

This script is run once, locally, by the team. It is NOT run by the notebooks:
the raw Hansen tiles are about 30 GB, far above the GitHub limit. The notebooks
load the aggregated output from GitHub.

For every 5 arc-minute cell (about 9 km at the equator, same grid as GAEZ v4),
it counts the 30 m Hansen pixels that were forest in 2000 and the pixels lost
in each year 2001-2025, for several canopy cover thresholds.

Grid convention (GAEZ v4, 2160 rows x 4320 columns, EPSG:4326):
    row = floor((90 - lat) * 12), col = floor((lon + 180) * 12)
    cell_id = row * 4320 + col
Hansen tiles are 10 x 10 degrees with 40000 x 40000 pixels (1/4000 degree).
10 degrees = 120 GAEZ cells, so a cell never crosses a tile border. A pixel is
assigned to the cell that contains its center.

Usage:
    python scripts/build_grid_panel.py --tiles 20N_090W     # one tile (test)
    python scripts/build_grid_panel.py --all                # every tile of the sample
"""

import argparse
import glob
import os
import shutil
import time
import urllib.request
import zipfile
from pathlib import Path

import numpy as np

HANSEN_VERSION = "GFC-2025-v1.13"
HANSEN_URL = f"https://storage.googleapis.com/earthenginepartners-hansen/{HANSEN_VERSION}/Hansen_{HANSEN_VERSION}_{{layer}}_{{tile}}.tif"
LAYERS = ["treecover2000", "lossyear"]
N_YEARS = 25                  # lossyear values 1..25 = 2001..2025
CELLS_PER_DEG = 12            # GAEZ 5 arc-minute grid
PIX_PER_DEG = 4000            # Hansen 1 arc-second grid
TILE_DEG = 10
TILE_PIX = TILE_DEG * PIX_PER_DEG          # 40000
TILE_CELLS = TILE_DEG * CELLS_PER_DEG      # 120
N_COLS_GLOBAL = 360 * CELLS_PER_DEG        # 4320
# Canopy cover thresholds: pixel is forest if treecover2000 > threshold.
# 25 = Berman et al. (2023) baseline, 50 = their robustness, 30 = GFW default (validation).
THRESHOLDS = [25, 30, 50]
BLOCK_ROWS = 1000

REPO = Path(__file__).resolve().parents[1]
DATA_DIR = Path.home() / "Data" / "hansen_gfc_v1.13"
RAW_DIR = DATA_DIR / "raw"
CELL_DIR = DATA_DIR / "cells"


def tile_origin(tile):
    """Return (top latitude, left longitude) of a Hansen tile name like '20N_090W'."""
    lat_s, lon_s = tile.split("_")
    lat = int(lat_s[:-1]) * (1 if lat_s[-1] == "N" else -1)
    lon = int(lon_s[:-1]) * (1 if lon_s[-1] == "E" else -1)
    return lat, lon


def sample_tiles():
    """Hansen tiles that intersect at least one of the 62 sample countries (GADM borders)."""
    import geopandas as gpd
    import pandas as pd
    from shapely.geometry import box

    files = sorted(glob.glob(str(REPO / "data/raw/gadm/gadm41_*_1.json.zip")))
    gadm = pd.concat([gpd.read_file(f"zip://{f}!{zipfile.ZipFile(f).namelist()[0]}") for f in files])
    region = gadm.union_all()
    tiles = []
    for lat in range(80, -60, -TILE_DEG):
        for lon in range(-180, 180, TILE_DEG):
            if box(lon, lat - TILE_DEG, lon + TILE_DEG, lat).intersects(region):
                tiles.append(f"{abs(lat):02d}{'N' if lat >= 0 else 'S'}_{abs(lon):03d}{'E' if lon >= 0 else 'W'}")
    return tiles


def download(tile, layer):
    """Download one Hansen layer for one tile, skipping files already complete."""
    url = HANSEN_URL.format(layer=layer, tile=tile)
    path = RAW_DIR / os.path.basename(url)
    with urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=60) as r:
        size = int(r.headers["Content-Length"])
    if path.exists() and path.stat().st_size == size:
        return path
    tmp = path.with_suffix(".part")
    # Timeout so that a stalled connection fails instead of blocking the run forever
    with urllib.request.urlopen(url, timeout=120) as r, open(tmp, "wb") as f:
        shutil.copyfileobj(r, f, length=1 << 20)
    if tmp.stat().st_size != size:
        raise IOError(f"incomplete download: {url}")
    tmp.rename(path)
    return path


def process_tile(tile):
    """Count forest 2000 and yearly loss pixels per GAEZ cell in one tile; save a .npz file."""
    import rasterio

    out = CELL_DIR / f"{tile}.npz"
    if out.exists():
        return out
    paths = {layer: download(tile, layer) for layer in LAYERS}
    lat0, lon0 = tile_origin(tile)

    # Local GAEZ cell row / column (0..119) of each pixel row / column, from pixel centers
    pix = (np.arange(TILE_PIX) + 0.5) * CELLS_PER_DEG / PIX_PER_DEG
    cell_of_pix = np.floor(pix).astype(np.int32)
    n_local = TILE_CELLS * TILE_CELLS

    tc_hist = np.zeros(n_local * 101, dtype=np.int64)   # forest 2000: cell x treecover value 0..100
    loss = {t: np.zeros(n_local * (N_YEARS + 1), dtype=np.int64) for t in THRESHOLDS}

    with rasterio.open(paths["treecover2000"]) as tc_src, rasterio.open(paths["lossyear"]) as ly_src:
        assert tc_src.width == TILE_PIX and tc_src.height == TILE_PIX
        assert abs(tc_src.transform.c - lon0) < 1e-9 and abs(tc_src.transform.f - lat0) < 1e-9
        for i0 in range(0, TILE_PIX, BLOCK_ROWS):
            win = rasterio.windows.Window(0, i0, TILE_PIX, BLOCK_ROWS)
            tc = tc_src.read(1, window=win)
            ly = ly_src.read(1, window=win)
            lid = (cell_of_pix[i0:i0 + BLOCK_ROWS, None] * TILE_CELLS + cell_of_pix[None, :]).ravel()
            tc = tc.ravel()
            ly = ly.ravel()
            tc_hist += np.bincount(lid * 101 + tc, minlength=n_local * 101)
            lost = ly > 0
            for t in THRESHOLDS:
                m = lost & (tc > t)
                loss[t] += np.bincount(lid[m] * (N_YEARS + 1) + ly[m], minlength=n_local * (N_YEARS + 1))

    # Global GAEZ cell ids of the local cells
    row0 = int(round((90 - lat0) * CELLS_PER_DEG))
    col0 = int(round((lon0 + 180) * CELLS_PER_DEG))
    local_r, local_c = np.divmod(np.arange(n_local), TILE_CELLS)
    cell_id = (row0 + local_r) * N_COLS_GLOBAL + (col0 + local_c)

    tc_hist = tc_hist.reshape(n_local, 101)
    keep = tc_hist[:, 1:].sum(axis=1) > 0               # cells with any tree cover in 2000
    np.savez_compressed(
        out,
        cell_id=cell_id[keep],
        tc_hist=tc_hist[keep].astype(np.int32),
        **{f"loss_{t}": loss[t].reshape(n_local, N_YEARS + 1)[keep, 1:].astype(np.int32) for t in THRESHOLDS},
    )
    return out


def run_tile(tile):
    """Process one tile and report the outcome instead of raising, so one failure does not stop the others."""
    t0 = time.time()
    try:
        process_tile(tile)
        return tile, f"done in {time.time() - t0:.0f} s"
    except Exception as e:  # noqa: BLE001
        return tile, f"FAILED: {e!r}"


def main():
    from multiprocessing import Pool

    parser = argparse.ArgumentParser()
    parser.add_argument("--tiles", nargs="*", default=[])
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    CELL_DIR.mkdir(parents=True, exist_ok=True)

    tiles = sample_tiles() if args.all else args.tiles
    print(f"{len(tiles)} tiles, {args.workers} workers", flush=True)
    with Pool(args.workers) as pool:
        for k, (tile, status) in enumerate(pool.imap_unordered(run_tile, tiles), 1):
            print(f"[{k}/{len(tiles)}] {tile} {status}", flush=True)


if __name__ == "__main__":
    main()
