"""Province (admin-1) borders of our 62 countries, from GADM 4.1.

Run once, from the repository root:

    python src/build_gadm_admin1.py

GADM 4.1 is the version Global Forest Watch uses for its subnational statistics (GADM 3.6
lacks e.g. the 2018 regions of Ghana), so the province names match the "Subnational 1" sheets of data/raw/forest/global.xlsx.

For each country of data/processed/shock_panel.csv it downloads the GADM 4.1 GeoPackage
(2.3 GB in total), keeps level 1 only, simplifies the borders to about 500 m (enough for
the 5' grid, about 9 km) and deletes the download.

Output: data/raw/boundaries/gadm41_admin1_sample.gpkg
    iso3, gid_1, name_1, geometry (EPSG:4326)
Disputed areas that GADM codes Z01-Z09 are given to the country file they come from.
"""

import tempfile
import time
import urllib.request
from pathlib import Path

import geopandas as gpd
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "data/processed/shock_panel.csv"
OUT = ROOT / "data/raw/boundaries/gadm41_admin1_sample.gpkg"
URL = "https://geodata.ucdavis.edu/gadm/gadm4.1/gpkg/gadm41_{iso3}.gpkg"
TOLERANCE_DEG = 0.005   # about 500 m at the equator


CACHE = Path(tempfile.gettempdir()) / "gadm41_admin1_cache"   # one small file per country, to restart


def admin1(iso3, tmp):
    cached = CACHE / f"{iso3}.gpkg"
    if cached.exists():
        return gpd.read_file(cached)
    path = Path(tmp) / f"{iso3}.gpkg"
    for attempt in range(5):          # the GADM server sometimes resets the connection
        try:
            urllib.request.urlretrieve(URL.format(iso3=iso3), path)
            break
        except OSError:
            if attempt == 4:
                raise
            time.sleep(10)
    gdf = gpd.read_file(path, layer="ADM_ADM_1")
    path.unlink()
    gdf = gdf.rename(columns={"GID_0": "iso3", "GID_1": "gid_1", "NAME_1": "name_1"})
    gdf["geometry"] = gdf.geometry.simplify(TOLERANCE_DEG, preserve_topology=True)
    gdf = gdf[["iso3", "gid_1", "name_1", "geometry"]]
    gdf.to_file(cached, driver="GPKG")
    return gdf


def main():
    countries = sorted(pd.read_csv(SAMPLE)["iso3"].unique())
    CACHE.mkdir(exist_ok=True)
    parts = []
    with tempfile.TemporaryDirectory() as tmp:
        for i, iso3 in enumerate(countries, 1):
            part = admin1(iso3, tmp)
            # GADM files disputed areas under codes Z01-Z09 (e.g. parts of Indian states):
            # they belong to the country file they come from, and pieces of one province are merged
            part = part.assign(iso3=iso3).dissolve(by="name_1", aggfunc="first", as_index=False)
            parts.append(part[["iso3", "gid_1", "name_1", "geometry"]])
            print(f"[{i}/{len(countries)}] {iso3}: {len(parts[-1])} provinces", flush=True)
    out = gpd.GeoDataFrame(pd.concat(parts, ignore_index=True), crs="EPSG:4326")
    out.to_file(OUT, driver="GPKG")
    print(f"saved {OUT} ({len(out)} provinces, {OUT.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
