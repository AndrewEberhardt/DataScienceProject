# Project: Do commodity price shocks increase deforestation?

EPFL master course project (MGT-499, Data Science & Causal Inference for Sustainability), group of 3
(Andrew Eberhardt, David Rodrigues Melo, Pelin Koç). Repository: `AndrewEberhardt/DataScienceProject`.

## How to work with me
- Go step by step: do one step of the task list below, show the result, then stop and wait for my go.
- Answer me in French. Code comments, notebook text and figure labels in English.
- Never use long dashes in any text.
- Every graph: title, axis labels, legend (when there is more than one series), data source under it.
- Course rule: AI-generated text must not be copy-pasted into the report. For notebook prose, explain
  what to write and let me write it.
- Do not change existing notebooks (`1-Forest-Loss.ipynb`, `2-Bivariate-Data.ipynb`, `Commodities.ipynb`,
  `david/*`) unless I ask. New work goes in a new notebook (see below).
- Before running anything long or downloading data, tell me what you will do.

## Data rules
- Country-level datasets are merged on `iso3` + `year`; grid-level datasets on `cell_id` + `year`.
- In notebooks, load data through raw GitHub URLs, never local paths, so the grader can run the notebook
  top to bottom:
  `BASE = "https://raw.githubusercontent.com/AndrewEberhardt/DataScienceProject/main/data/"`
- New raw files go in `data/raw/...`, derived files in `data/processed/...`. Log every new source in
  `docs/data_log.md` (source, URL, download date, variables, units). Files must stay under 100 MB.
- Heavy preprocessing that cannot run in a notebook (Hansen tiles, about 30 GB) lives in `scripts/`, is run
  once locally, and only its aggregated output is committed.
- Python packages are listed in `requirements.txt` (pandas, numpy, linearmodels, statsmodels, matplotlib,
  wbgapi, geopandas, rasterstats, rasterio, pyfixest).

## Sample (fixed, do not change)
62 countries with at least 30% of their territory between 30N and 30S (Natural Earth borders,
equal-area projection ESRI:54034) and at least 1 Mha of tree cover in 2000. Excluded: Algeria, Chile,
New Caledonia, South Sudan. Three regions: Latin America & Caribbean, Africa, Asia-Pacific
(from the Natural Earth continent field). List of countries: `data/processed/shock_panel.csv`.
Grid cells: every GAEZ 5 arc-minute cell of the 62 countries (GADM 4.1 borders) with forest in 2000.
A flag `in_tropics` marks cells within 23.44 N / S (the band of Berman et al.).

## Story of the project (for the article)
1. Midterm: three commodities (palm oil, soybeans, beef), country-level price shocks.
2. Beef set aside: world beef prices barely reach local markets (0 of 21 countries show a correlation
   above 0.5 between world and local prices, `david/david.com.price.ipynb`).
3. Country-level exposure designs for palm and soy (FAOSTAT area, then GAEZ suitability, then provinces)
   were tried and dropped: placebos and trend tests failed, national policies confound the result.
   The code is kept under the git tag `pre-cleanup` (notebooks 3 to 6).
4. Final design: replicate and extend Berman et al. (2023) at a finer resolution and over a longer period.

## Research design: Berman et al. (2023), finer and longer

### Question
Do increases in world crop prices cause deforestation in the tropics, and does the answer of
Berman et al. (2023) hold at a finer resolution (9 km instead of 55 km) and after 2018 (until 2025)?

### Equation (shift-share reduced form, as in Berman et al. 2023, eq. 3)
```
asinh(Defor[c,t]) = beta * ln(Price[c,t]) + eta[c] + nu[country, t] + e[c,t]
```
- `c` grid cell, `t` year. `eta[c]` cell fixed effects, `nu[country,t]` country x year fixed effects
  (absorb national policies, macro shocks and the common price trend).
- `Defor[c,t]`: number of Hansen pixels lost in cell c in year t among pixels with tree cover in 2000
  above 25 percent (50 percent as robustness).
- Price index: `Price[c,t] = sum_i alpha[i,c] * P[i,t]`, with relative suitability
  `alpha[i,c] = S[i,c] / sum_j S[j,c]` (GAEZ v4 suitability index) and `P[i,t]` the real world price of
  crop i (World Bank Pink Sheet, base 100 in 2000). Contemporaneous price in the baseline,
  lags t-1 and t-2 as robustness.
- Estimation: `pyfixest.feols` (three-way fixed effects are not possible in `linearmodels`).
  PPML (`pyfixest.fepois`) on pixel counts as robustness.
- Standard errors: clustered at a level coarser than the 9 km cell (0.5 degree block or GADM province),
  because neighbouring cells are strongly correlated; Conley (500 and 1000 km) as robustness.
  Berman et al. cluster by 0.5 degree cell.

### Variables and choices
- Cells: GAEZ v4 grid, 5 arc-minutes (about 9.2 km at the equator), 2160 x 4320, EPSG:4326.
  `cell_id = row * 4320 + col`. File: `data/processed/grid_cells.csv.gz` (one row per cell, wide in years).
- Deforestation: Hansen Global Forest Change v1.13, 2001-2025. Validated against GFW country tables.
- Crops (13): banana, cocoa, coconut, coffee, cotton, maize, oil palm, rice, soybean, sugarcane, tea,
  tobacco, wheat. Barley and sorghum (in Berman's 15) are dropped: the Pink Sheet stops them in 2020.
- Suitability: GAEZ v4, CRU TS 3.2 1961-1990, high input, rainfed, index 0-10000
  (`data/raw/gaez/sxHr_{crop}.tif`). Rice = max(dryland `rcd`, wetland `rcw`).
  Berman et al. use GAEZ v3 (percentage of maximum attainable yield): the closest v4 equivalent.
- Prices: `data/processed/commodity_prices_annual.csv` (`price_real`). Pink Sheet series:
  Banana US, Cocoa, Coconut oil, Coffee (Arabica and Robusta averaged), Cotton A Index, Maize, Palm oil,
  Rice Thai 5%, Soybeans, Sugar world, Tea avg 3 auctions, Tobacco US import u.v., Wheat US HRW.

### Steps of the results
1. Replication: 0.5 degree cells, 2001-2018, 15 crops (barley and sorghum exist until 2018), in the
   tropics band. Target: beta close to 1.27 (Berman et al., Figure 1, Model 1). Also compare our cell
   counts with their replication data (Zenodo 7044013).
2. Finer: 9 km cells, same period and crops.
3. Longer: 9 km cells, 2001-2025, 13 crops. Does the effect hold after 2018 (2021-2022 price spike)?
4. Heterogeneity as in Berman et al.: deciles of forest cover in 2000; distance to port, distance to
   capital, night lights in 2000 (if time allows).
5. Contribution of prices to deforestation: predicted deforestation with observed prices vs prices
   fixed at their 2001 level (Berman et al., footnote 10).
6. Robustness: canopy 50 percent, PPML, lags, average suitability x year FE, without large producers,
   Conley SE, regions separately.

### Beef (separate section)
World beef prices reach local markets only in exporting countries. Show that the link between the beef
price and cattle-driven deforestation (DeDuCE, "Cattle meat") appears only where the export share
(FAOSTAT trade, exports / production) is high (Brazil, Paraguay, Argentina...). This explains why beef
is not in the crop price index. Berman et al. treat beef in their appendix (pasture suitability x beef
price).

## Task list (one step at a time, wait for my go between steps)
1. Done: clean the repository (tag `pre-cleanup`), branch `andrew-cleanup-berman`.
2. Hansen aggregation to 5 arc-minute cells: `scripts/build_grid_panel.py` (tiles), then
   `scripts/assemble_grid_panel.py` (countries, validation, `grid_cells.csv.gz`).
3. GAEZ suitability for the 13 crops (done: rasters in `data/raw/gaez/`). New notebook
   `notebooks/3-Crop-Price-Index.ipynb`: suitability per cell, alpha, price index, maps.
4. New notebook `notebooks/4-Grid-Regressions.ipynb`: steps 1 to 6 of the results above.
5. New notebook `notebooks/5-Beef-Exports.ipynb`: beef section.
6. Final article notebook (Medium style, max 3,000 words, technical parts in an appendix).

## Key references
- Berman, Couttenier, Leblois, Soubeyran (2023), "Crop prices and deforestation in the tropics", JEEM 119
  (working paper: FAERE WP 2022.08; replication files: Zenodo 7044013). The reference design.
- Hansen et al. (2013), "High-resolution global maps of 21st-century forest cover change", Science 342(6160).
- FAO and IIASA (2021), Global Agro-Ecological Zones v4 (GAEZ v4).
- Goldsmith-Pinkham, Sorkin and Swift (2020), AER: shift-share identification from the shares.
- Harding et al. (2021): commodity prices and deforestation in Brazil (cited by Berman et al.).
- Singh and Persson (2026), DeDuCE: deforestation attributed to commodities (beef section).

## Deadline
Final deliverable: December 19 at 16:00. Medium-style notebook article, max 3,000 words, technical
parts in an appendix. The notebook must run top to bottom from GitHub data.
