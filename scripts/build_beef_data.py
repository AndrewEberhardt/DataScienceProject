"""Build the two small input files of notebook 5 (beef) from raw data kept outside the repository.

1. data/processed/grid_cattle.csv.gz
   Cattle density in 2000 (heads per km2) on the GAEZ 5 arc-minute grid, for every cell of grid_cells.csv.gz.
   Source: AGLW, Du et al. (2025), ESSD 17, 5543-5556, Zenodo 10.5281/zenodo.17128483, file
   LivestockMap/Cattl_2000.tif (about 5 km grid, heads per km2). Only this file is needed: it can be extracted
   from the 7.4 GB archive with HTTP range requests (see extract_cattle_2000 below).
   The 5 km pixels are averaged onto each 5 arc-minute cell (rasterio, Resampling.average, sea = no data).

2. data/processed/beef_export_share.csv
   Beef and buffalo meat (FAOSTAT item 1806) exports and production per sample country, in tonnes, and the
   export share (exports / production, capped at 1) over 1996-2000 and 2001-2023.
   Sources: FAOSTAT Trade (TCL) regional bulk files (Americas, Africa, Asia, Oceania) and FAOSTAT
   Production (QCL) bulk file.

Run once from the repository root:  python scripts/build_beef_data.py
"""
import glob
import io
import urllib.request
import zipfile
from pathlib import Path

import country_converter as coco
import numpy as np
import pandas as pd
import rasterio
from rasterio.transform import from_origin
from rasterio.warp import Resampling, reproject

REPO = Path(__file__).resolve().parents[1]
DATA = Path.home() / "Data"
AGLW_URL = "https://zenodo.org/records/17128483/files/LivestockMap.zip?download=1"
AGLW_FILE = DATA / "aglw/LivestockMap/Cattl_2000.tif"
TCL_FILES = DATA / "faostat_tcl"            # Trade_CropsLivestock_E_{Americas,Africa,Asia,Oceania}_NOFLAG.csv
QCL_FILE = DATA / "faostat_qcl/Production_Crops_Livestock_E_All_Data_(Normalized).csv"


class RangeFile(io.RawIOBase):
    """Read-only remote file that fetches only the bytes asked for (HTTP range requests)."""

    def __init__(self, url):
        r = urllib.request.urlopen(urllib.request.Request(url, method="HEAD"))
        self.url, self.size, self.pos = r.geturl(), int(r.headers["Content-Length"]), 0

    def seekable(self):
        return True

    def readable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, off, whence=0):
        self.pos = off if whence == 0 else self.pos + off if whence == 1 else self.size + off
        return self.pos

    def readinto(self, b):
        if self.pos >= self.size:
            return 0
        end = min(self.pos + len(b), self.size) - 1
        req = urllib.request.Request(self.url, headers={"Range": f"bytes={self.pos}-{end}"})
        data = urllib.request.urlopen(req).read()
        b[:len(data)] = data
        self.pos += len(data)
        return len(data)


def extract_cattle_2000():
    """Extract LivestockMap/Cattl_2000.tif (26 MB) from the AGLW archive without downloading the archive."""
    if AGLW_FILE.exists():
        return
    z = zipfile.ZipFile(io.BufferedReader(RangeFile(AGLW_URL), buffer_size=1 << 20))
    z.extract("LivestockMap/Cattl_2000.tif", AGLW_FILE.parents[1])


def build_grid_cattle():
    extract_cattle_2000()
    cells = pd.read_csv(REPO / "data/processed/grid_cells.csv.gz", usecols=["cell_id", "row", "col"])
    grid = np.full((2160, 4320), np.nan, np.float32)
    with rasterio.open(AGLW_FILE) as src:
        reproject(rasterio.band(src, 1), grid, src_nodata=np.nan, dst_nodata=np.nan,
                  dst_transform=from_origin(-180, 90, 1 / 12, 1 / 12), dst_crs="EPSG:4326",
                  resampling=Resampling.average)
    out = pd.DataFrame({"cell_id": cells.cell_id, "cattle2000": grid[cells.row, cells.col].round(3)})
    out.to_csv(REPO / "data/processed/grid_cattle.csv.gz", index=False)
    print(f"grid_cattle.csv.gz: {len(out):,} cells, {out.cattle2000.isna().mean():.1%} without a value, "
          f"median {out.cattle2000.median():.1f} heads/km2")


def to_iso3(m49):
    """FAOSTAT 'Area Code (M49)' ('076 etc.) to ISO3; regions and former countries give None."""
    return coco.convert(names=[int(str(m).strip("'")) for m in m49], src="UNnumeric", to="ISO3", not_found=None)


def build_export_share():
    sample = pd.read_csv(REPO / "data/processed/shock_panel.csv").drop_duplicates("iso3")[["iso3", "country"]]
    years = [f"Y{y}" for y in range(1996, 2024)]

    trade = pd.concat(pd.read_csv(f, encoding="latin-1") for f in sorted(glob.glob(str(TCL_FILES / "*_NOFLAG.csv"))))
    trade = trade[(trade["Item Code"] == 1806) & (trade.Element == "Export quantity")]
    trade = trade.drop_duplicates("Area Code")        # countries appear in only one regional file
    exp = trade.set_index("Area Code (M49)")[years]

    prod = pd.concat(c[(c["Item Code"] == 1806) & (c.Element == "Production")]
                     for c in pd.read_csv(QCL_FILE, encoding="latin-1", chunksize=2_000_000,
                                          usecols=["Area Code (M49)", "Item Code", "Element", "Year", "Value"]))
    prod = prod.pivot_table(index="Area Code (M49)", columns="Year", values="Value")
    prod.columns = [f"Y{c}" for c in prod.columns]

    exp.index, prod.index = to_iso3(exp.index), to_iso3(prod.index)
    exp = exp[exp.index.notna()].groupby(level=0).sum(min_count=1)
    prod = prod[prod.index.notna()].groupby(level=0).sum(min_count=1)

    out = sample.copy()
    for label, (y0, y1) in {"9600": (1996, 2000), "0123": (2001, 2023)}.items():
        cols = [f"Y{y}" for y in range(y0, y1 + 1)]
        e = exp.reindex(out.iso3)[cols].sum(axis=1, min_count=1).fillna(0).to_numpy()
        p = prod.reindex(out.iso3)[cols].sum(axis=1).to_numpy()
        out[f"exports_t_{label}"] = e.round(0)
        out[f"production_t_{label}"] = p.round(0)
        out[f"share_{label}"] = np.where(p > 0, np.clip(e / np.where(p > 0, p, 1), 0, 1), np.nan).round(4)
    out.to_csv(REPO / "data/processed/beef_export_share.csv", index=False)
    print(f"beef_export_share.csv: {len(out)} countries, {out.share_0123.isna().sum()} without production data")
    print(out.sort_values("share_0123", ascending=False).head(10)[["country", "share_9600", "share_0123"]]
          .to_string(index=False))


if __name__ == "__main__":
    build_grid_cattle()
    build_export_share()
