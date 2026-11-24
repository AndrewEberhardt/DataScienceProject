"""Share of each sample country in world production of the 13 crops of the price index (1999-2001 mean).

Run once, locally. The FAOSTAT bulk file (Production_Crops_Livestock, about 545 MB unzipped) stays outside
the repo in ~/Data/faostat_qcl/. Output (committed to GitHub):
    data/processed/world_production_share.csv : iso3, crop, share of world production (quantity),
        mean over 1999-2001 (before our period, so not affected by the price shocks we study).

Used in notebook 4 to drop large producers: a country that produces a large share of a crop can move its
world price, so its deforestation could cause price changes (reverse causality). Berman et al. (2023)
run the same check with a market share variable that does not cover 16 of our 62 countries.
"""

from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
RAW = Path.home() / "Data/faostat_qcl/Production_Crops_Livestock_E_All_Data_(Normalized).csv"
OUT = REPO / "data/processed/world_production_share.csv"

ITEMS = {486: "banana", 661: "cocoa", 249: "coconut", 656: "coffee", 328: "cotton", 56: "maize",
         254: "oil palm", 27: "rice", 236: "soybean", 156: "sugarcane", 667: "tea", 826: "tobacco",
         15: "wheat"}                                     # FAOSTAT item code: crop (coconut: in shell)
PRODUCTION, WORLD = 5510, 5000
# FAOSTAT area codes whose name differs from ours
AREA_FIX = {"BOL": 19, "CIV": 107, "COG": 46, "LAO": 120, "MEX": 138, "TWN": 214, "TZA": 215, "VEN": 236,
            "VNM": 237}


def main():
    sample = pd.read_csv(REPO / "data/processed/shock_panel.csv")[["iso3", "country"]].drop_duplicates()
    areas = pd.read_csv(RAW.parent / "Production_Crops_Livestock_E_AreaCodes.csv")
    code = dict(zip(areas.Area, areas["Area Code"]))
    sample["area"] = [AREA_FIX.get(i, code.get(c)) for i, c in zip(sample.iso3, sample.country)]
    assert sample.area.notna().all(), sample[sample.area.isna()]

    d = pd.read_csv(RAW, usecols=["Area Code", "Item Code", "Element Code", "Year", "Value"])
    d = d[d["Element Code"].eq(PRODUCTION) & d["Item Code"].isin(ITEMS) & d.Year.between(1999, 2001)]
    prod = d.groupby(["Area Code", "Item Code"]).Value.mean()     # tonnes, mean 1999-2001
    world = prod.xs(WORLD, level="Area Code")

    rows = []
    for iso3, area in zip(sample.iso3, sample.area.astype(int)):
        for item, crop in ITEMS.items():
            q = prod.get((area, item), 0.0)
            rows.append({"iso3": iso3, "crop": crop, "share_world_production": q / world[item]})
    out = pd.DataFrame(rows)
    out.round(5).to_csv(OUT, index=False)

    top = out.loc[out.groupby("iso3").share_world_production.idxmax()].sort_values("share_world_production", ascending=False)
    print(top.head(20).round(3).to_string(index=False))
    print(f"countries with a share of 10% or more for at least one crop: {(top.share_world_production >= 0.10).sum()}")
    print(f"Written {OUT}")


if __name__ == "__main__":
    main()
