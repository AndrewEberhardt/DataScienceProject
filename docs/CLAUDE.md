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
2. Done (18.11.2026): Hansen aggregation to 5 arc-minute cells. 121 tiles (5 ocean tiles do not exist,
   HTTP 404). `grid_cells.csv.gz`: 511,427 cells, 62 countries, 30 MB. Validation vs GFW (threshold 25):
   sample totals 1.002 (extent) and 1.001 (loss), every country within 3% except Suriname (loss 1.05,
   border cells with French Guiana). Raw tiles (29 GB) kept in `~/Data/hansen_gfc_v1.13/`.
3. Done (18.11.2026): `notebooks/3-Crop-Price-Index.ipynb` runs top to bottom (1.5 min). Within-country
   share of suitability variance 54-74% (Berman: 50-74%). SD of ln index after cell + country x year FE:
   0.047 (13 crops, 2001-2025), 0.038 (15 crops, 2001-2018). Output `grid_suitability.csv.gz` (11 MB).
   Done (19.11.2026): weight maps of the 13 crops (same colour scale, `crop_weight_maps.png`) and of the
   4 forest-risk crops for the article (cocoa, oil palm, soybean, coffee, `crop_weight_maps_article.png`).
4. Done (18.11.2026): `notebooks/4-Grid-Regressions.ipynb` runs top to bottom (9 min, peak 9.7 GB RAM).
   OLS asinh: replication 0.5 deg 2001-2018 beta 1.97 (Berman 1.27); 9 km 2001-2018 1.07;
   MAIN 9 km 2001-2025 0.96 (+0.31 after 2018); 0.5 deg 2001-2025 1.66. Significant with block, country
   and Conley SE. Permutation of prices across crops (1,000 draws, exact closed-form demeaning, balanced
   panel): p = 0.10 (replication), 0.06 (9 km 2001-2018), 0.03 (0.5 deg 2001-2025), 0.006 (MAIN).
   Possible thesis: Berman's design does not pass the permutation test on its own period and resolution;
   finer cells and the post-2018 shocks (cocoa, coffee) make the result credible.
   PPML elasticities: 0.5 deg 1.50 / 9 km 1.06 (2001-2018, 15 crops); 0.5 deg 1.07 / 9 km 0.84
   (2001-2025, 13 crops): about 30% smaller at 9 km. Robustness stable (canopy 50: 0.95, t-1: 0.69,
   t-2: 0.81, avg suitability x year: 1.19, tropics only: 1.07). Contribution of prices (share of predicted deforestation due to price changes, as Berman: "responsible
   for 35% of predicted forest loss"): MAIN 44%, replication 0.5 deg 2001-2018 56% (Berman 35%).
   (19.11.2026: contribution was (obs-cf)/cf = 77%, now (obs-cf)/obs. Decile model, contribution and avg suitability x year corrected; they were misaligned
   because pyfixest with copy_data=False resets the DataFrame index. Use `panel_pos()`, never `d.index`.)
   (a) Done (19.11.2026), section 9: 2001-2018 with 13 crops gives 2.07 (0.5 deg) and 1.12 (9 km), close
   to 15 crops (1.97 / 1.07): the crop set barely moves beta, the lower beta over 2001-2025 comes from the
   period. But permutation p drops to 0.022 (0.5 deg) and 0.004 (9 km) with 13 crops: the weak p of the
   replication comes from barley and sorghum, so the thesis above must be nuanced.
   (b) Done (19.11.2026), section 10: adding the price index of neighbouring land (rings 9-18, 18-30,
   30-55 km and a far ring 60-110 km) moves the effect to the neighbours (own cell 0.97 -> 0.16-0.18);
   the far ring absorbs everything (1.27-1.30), total 1.43. Not local spillovers: deforestation responds
   to the crop mix of the whole region (about 100 km). Neighbour indices explain 91% of the within
   variation of the own index.
   Protected areas Done (19.11.2026), section 11 (WDPA Nov 2026, `scripts/build_protected_areas.py`,
   `grid_protected.csv.gz`): interaction lnP x share protected before 2001. Raw +0.06 (ns); with forest
   deciles x lnP -0.30; strict (IUCN I-IV) -0.33, with deciles -0.63; share protected 2001-2025 +0.26
   (new areas created where pressure was high: selection, not causal).
   (c) Done (19.11.2026), section 12, `scripts/compare_berman.py` -> `berman_comparison.csv`, `berman_prices.csv`.
   Berman replication data (Zenodo 7044013, in ~/Data/berman_replication/). His regression in Python on his data: 1.267 (0.088), exact. Matched
   0.5 deg cells: 11,856 common; deforestation identical (corr 1.00, totals 0.997), forest 2000 0.993.
   Our outcome + his index: 1.315; our outcome + our index: 2.19 on the same cells. The whole gap is the
   price index: (1) price series: his banana and sugar differ from ours (his sugar is not "Sugar, world";
   his banana alone moves 2.19 to 1.79, his sugar alone to 2.05); (2) GAEZ v3 vs v4 weights (rice 18% vs
   11%, corr of weights 0.7-0.9); (3) an undocumented step: his index rebuilt from his own files gives 1.69
   (within corr 0.996 with his index), not 1.27. Sign and significance hold in every variant (1.2 to 2.2).
   (d) Done (19.11.2026): switch RECOMPUTE (default False) in notebook 4. 9 km models are in `if RECOMPUTE:`
   blocks; their results are read from `data/processed/results/` (10 CSV, 76 KB). Default run: 75 s,
   about 3 GB RAM (0.5 deg models estimated live). RECOMPUTE = True: about 15 min, 10 GB, rewrites the CSV
   (identical numbers checked). Any change to a 9 km model needs a RECOMPUTE run and a commit of results/.
   NEXT: plan of the final article (task 6).
5. New notebook `notebooks/5-Beef-Exports.ipynb`: beef section (David: FAOSTAT beef exports).
6. Final article notebook (Medium style, max 3,000 words, technical parts in an appendix).
   Skeleton done (19.11.2026): `notebooks/6-Article.ipynb`, 8 sections + appendix, 9 figures/tables, all code
   reads small files (results/summary.csv, inference.csv, contribution.csv exported by notebook 4); runs in
   about 6 s. Every prose block is a "To write (Andrew)" placeholder with the points and numbers to cite.
   A word count cell checks the 3,000 word limit. Section 7 (beef) waits for task 5.
7. After merging into `main`: switch `BRANCH` to "main" in notebooks 3 and 4.

Pushing: git in the Claude Code terminal has no GitHub credentials. Commit there, push with GitHub Desktop.

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
