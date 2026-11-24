"""Compare our replication of Berman et al. (2023) with their own replication data.

Run once, locally. Berman et al.'s Stata files (Zenodo 7044013, 56 MB) stay outside the repo in
~/Data/berman_replication/. Outputs (committed to GitHub, read by notebook 4):
    data/processed/berman_comparison.csv : beta of asinh(loss) on the log price index, cell and
        country x year fixed effects, SE clustered by cell, 2001-2018, 15 crops, for combinations of
        their / our outcome, suitability weights and price series, on the 0.5 degree cells we share.
    data/processed/berman_prices.csv : their and our real price series (base 2000 = 100) for the crops
        whose series differ (banana, sugar).

Our side is built as in notebook 4 (0.5 degree blocks of the 9 km cells, mean GAEZ v4 suitability over
the block, World Bank Pink Sheet real prices). Cells are matched on their center coordinates.
"""

import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import pyfixest as pf
import rasterio

REPO = Path(__file__).resolve().parents[1]
BERMAN = Path.home() / "Data/berman_replication"
YEARS = list(range(2001, 2019))

# Crop: (GAEZ v4 codes, Pink Sheet series, name in Berman et al.'s files)
CROPS = {
    "banana": (["ban"], ["Banana, US"], "banana"), "cocoa": (["coc"], ["Cocoa"], "cocoa"),
    "coconut": (["con"], ["Coconut oil"], "coconut"),
    "coffee": (["cof"], ["Coffee, Arabica", "Coffee, Robusta"], "coffee"),
    "cotton": (["cot"], ["Cotton, A Index"], "cotton"), "maize": (["mze"], ["Maize"], "maize"),
    "oil palm": (["olp"], ["Palm oil"], "oilpalm"), "rice": (["rcd", "rcw"], ["Rice, Thai 5%"], "rice"),
    "soybean": (["soy"], ["Soybeans"], "soybean"), "sugarcane": (["suc"], ["Sugar, world"], "sugar"),
    "tea": (["tea"], ["Tea, avg 3 auctions"], "tea"), "tobacco": (["tob"], ["Tobacco, US import u.v."], "tobacco"),
    "wheat": (["whe"], ["Wheat, US HRW"], "wheat"), "barley": (["brl"], ["Barley"], "barley"),
    "sorghum": (["srg"], ["Sorghum"], "sorghum"),
}
CROP_LIST = list(CROPS)


def our_blocks():
    """0.5 degree blocks: summed loss (threshold 25), mean GAEZ v4 suitability, center coordinates."""
    cells = pd.read_csv(REPO / "data/processed/grid_cells.csv.gz")
    cells["block"] = (cells.row // 6) * 720 + cells.col // 6
    b = cells.groupby("block")[[f"loss25_{y}" for y in YEARS] + ["forest25_px"]].sum()
    suit = {}
    for crop, (codes, _, _) in CROPS.items():
        layers = []
        for c in codes:
            with rasterio.open(REPO / f"data/raw/gaez/sxHr_{c}.tif") as src:
                layers.append(src.read(1).astype(np.float32))
        a = np.max(layers, axis=0)
        a[a < 0] = np.nan
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)          # blocks entirely at sea
            suit[crop] = np.nanmean(a.reshape(360, 6, 720, 6), axis=(1, 3)).ravel()
    b = b.join(pd.DataFrame(suit), how="left")
    b["lat"] = 90 - ((b.index // 720) * 6 + 3) / 12
    b["lon"] = -180 + ((b.index % 720) * 6 + 3) / 12
    return b.rename_axis("block").reset_index()


def our_prices():
    pr = pd.read_csv(REPO / "data/processed/commodity_prices_annual.csv")
    P = pd.DataFrame({c: pr[pr.commodity.isin(s)].groupby("year").price_real.mean() for c, (_, s, _) in CROPS.items()})
    return 100 * P / P.loc[2000]


def berman_prices():
    w = pd.read_stata(BERMAN / "wb_prices_annual.dta")
    w["year"] = w.year.astype(int)
    P = w.pivot(index="year", columns="M3filename", values="price_wb_real")[[v[2] for v in CROPS.values()]]
    P.columns = CROP_LIST
    return P


def log_index(S, P):
    """Log price index: rows of S are cells, columns crops (in CROP_LIST order)."""
    S = np.asarray(S, float)
    return np.log((S / S.sum(axis=1, keepdims=True)) @ P.loc[YEARS, CROP_LIST].to_numpy().T)


def main():
    d = pd.read_stata(BERMAN / "Replication_data.dta")
    d = d[d.cover_t25_2000 > 0].copy()                    # final sample of the paper
    d["year"] = d.year.astype(int)
    rows = []

    def add(name, data, y, x, sample):
        f = pf.feols(f"{y} ~ {x} | gid + id_iso_year", data.dropna(subset=[y, x]), vcov={"CRV1": "gid"})
        rows.append({"sample": sample, "model": name, "beta": f.coef().iloc[0], "se": f.se().iloc[0], "N": f._N})
        print(f"{name}: {f.coef().iloc[0]:.3f}")

    add("Berman et al. data and index", d, "sine_t25_y01", "lprice_gaez_ag", "all Berman cells")

    # Match cells on center coordinates (both grids have centers at .25 / .75 degrees)
    blocks = our_blocks()
    for t in (d, blocks):
        lon, lat = ("xcoord", "ycoord") if t is d else ("lon", "lat")
        t["xk"], t["yk"] = (t[lon] * 4).round().astype(int), (t[lat] * 4).round().astype(int)
    key = d.drop_duplicates("gid")[["gid", "xk", "yk"]].merge(blocks[["block", "xk", "yk"]], on=["xk", "yk"])
    print(f"{len(key):,} common cells out of {d.gid.nunique():,} (Berman et al.)")
    L = d.merge(key[["gid", "block"]], on="gid")
    t = L.year.to_numpy() - YEARS[0]
    B = blocks.set_index("block")
    L["y_ours"] = np.arcsinh(B.loc[L.block, [f"loss25_{y}" for y in YEARS]].to_numpy()[np.arange(len(L)), t])

    # Suitability: Berman et al. (GAEZ v3, column "mean") and ours (GAEZ v4), on the common cells
    s = pd.read_stata(BERMAN / "suit_crop_gid_gaez.dta")
    S_b = s[s.crop.isin([v[2] for v in CROPS.values()])].pivot(index="gid", columns="crop", values="mean")
    S_b = S_b[[v[2] for v in CROPS.values()]].reindex(key.gid).to_numpy()
    S_o = B.loc[key.block, CROP_LIST].to_numpy()
    P_o, P_b = our_prices(), berman_prices()
    # Berman et al.'s banana price is missing in 2018: extend it with the growth of our series
    P_b.loc[2018, "banana"] = P_b.loc[2017, "banana"] * P_o.loc[2018, "banana"] / P_o.loc[2017, "banana"]

    row = pd.Series(np.arange(len(key)), index=key.gid).loc[L.gid].to_numpy()
    def put(name, S, P):
        L[name] = log_index(S, P)[row, t]

    put("x_ours", S_o, P_o)
    put("x_rebuilt", S_b, P_b)
    put("x_suitB_pricesO", S_b, P_o)
    put("x_suitO_pricesB", S_o, P_b)
    common = "common cells"
    add("Berman et al. outcome, Berman et al. index", L, "sine_t25_y01", "lprice_gaez_ag", common)
    add("Our outcome, Berman et al. index", L, "y_ours", "lprice_gaez_ag", common)
    add("Berman et al. outcome, our index", L, "sine_t25_y01", "x_ours", common)
    add("Our outcome, our index", L, "y_ours", "x_ours", common)
    add("Our outcome, index rebuilt from Berman et al. files", L, "y_ours", "x_rebuilt", common)
    add("Our outcome, Berman et al. suitability, our prices", L, "y_ours", "x_suitB_pricesO", common)
    add("Our outcome, our suitability, Berman et al. prices", L, "y_ours", "x_suitO_pricesB", common)
    for crop in CROP_LIST:                                 # our index with one price series replaced
        P = P_o.copy()
        P[crop] = P_b[crop]
        put("x_one", S_o, P)
        add(f"Our index, Berman et al. price for {crop}", L, "y_ours", "x_one", "common cells, one price swapped")

    out = pd.DataFrame(rows)
    out.round(4).to_csv(REPO / "data/processed/berman_comparison.csv", index=False)
    prices = pd.concat({"Berman et al.": P_b.loc[YEARS, ["banana", "sugarcane"]],
                        "ours": P_o.loc[YEARS, ["banana", "sugarcane"]]}, axis=1)
    prices.columns = [f"{c}_{who}" for who, c in prices.columns]
    prices.round(2).rename_axis("year").to_csv(REPO / "data/processed/berman_prices.csv")
    print(out.round(3).to_string())


if __name__ == "__main__":
    main()
