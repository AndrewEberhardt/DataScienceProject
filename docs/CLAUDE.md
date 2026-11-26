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
5. Beef tested directly (notebook 5): with world prices its effect cannot be identified (it is confounded
   with the trend of cattle areas), which is why the index keeps the 13 crops.
6. After the meeting with the professor (25.11.2026: interpret the results in numbers, think about
   controls, so causality): the Berman design fails a leads test (the index of t+2 predicts deforestation
   as well as the index of t), so its effect mixes prices with regional deforestation trends. Controls for
   characteristics of 2000 x year and province x year fixed effects divide it by about 3 (main model 0.37,
   lower bound 0.12 with cell trends). New message: crop prices do raise deforestation, about 16% of tree
   cover loss over 2001-2025 (45 Mha), against 36% with the Berman design.

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

### Main model (since 25.11.2026, notebook 4 section 14, step 4 of the controls ladder)
```
asinh(Defor[c,t]) = beta * ln(Price[c,t]) + eta[c] + nu[province, t] + mu[forest decile, t]
                    + gamma_t * (share protected 2000, ln(1 + cattle 2000), average suitability)[c] + e[c,t]
```
- `nu[province,t]`: GADM 4.1 level-1 province x year (1,275 provinces), assigned in notebook 4
  (`assign_provinces`, cell center, else nearest province of the same country).
- Controls: only characteristics measured in 2000, interacted with year. Nothing measured after 2000
  (roads, population, farm area): prices may have changed it (bad controls).
- Lower bound: + a linear trend for each cell (`cell_id[t]` in pyfixest). The Berman design (cell +
  country x year only) is kept as the comparison.
- Sample: cells with a cattle density and a protected share (474,721 of 511,427).

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

### Beef (separate section, done in notebook 5)
Cell level: `asinh(Defor[c,t]) = beta ln Price[c,t] + gamma ln P_beef[t] x ln(1 + Cattle2000[c])`
+ average suitability x year + cell FE + country x year FE. Cattle density in 2000 from AGLW (Du et al.
2025), a map that is not shaped by our period (within-country correlation 0.19 with crop suitability).
Country level: DeDuCE "Cattle meat" deforestation on ln P_beef x export share (FAOSTAT trade, exports /
production of item 1806), and on local producer prices (FAOSTAT PP). Berman et al. only add meat to their
index in an appendix (1.27 -> 1.54 on their data; the two indices have a within correlation of 0.98), they
never estimate a beef effect on its own.
Tried and dropped: GAEZ Napier grass (`nap`) as pasture suitability (within-country correlation 0.83 with
crop suitability, gave an unstable negative sign); Berman's `meat` layer (undocumented, 0.88 correlated with
his `energy` layer).

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
   11%, corr of weights 0.7-0.9; our weights + his prices 1.69, his weights + our prices 2.11: prices matter
   more); (3) an undocumented step: his index rebuilt from his own files gives 1.75 (within corr 0.996 with
   his index), not 1.31 (his index on the common cells). Sign and significance hold in every variant (1.2 to 2.2).
   (d) Done (19.11.2026): switch RECOMPUTE (default False) in notebook 4. 9 km models are in `if RECOMPUTE:`
   blocks; their results are read from `data/processed/results/` (10 CSV, 76 KB). Default run: 75 s,
   about 3 GB RAM (0.5 deg models estimated live). RECOMPUTE = True: about 15 min, 10 GB, rewrites the CSV
   (identical numbers checked). Any change to a 9 km model needs a RECOMPUTE run and a commit of results/.
   NEXT: plan of the final article (task 6).
5. Done (20.11.2026): `notebooks/5-Beef-Exports.ipynb` runs top to bottom from GitHub (20 s, 1.8 GB RAM;
   RECOMPUTE = True: about 4 min, 10 GB, rewrites `results/beef_grid_9km.csv`). Inputs built once by
   `scripts/build_beef_data.py` from raw data outside the repo (AGLW `Cattl_2000.tif` extracted alone from the
   7.4 GB Zenodo archive with HTTP range requests, in `~/Data/aglw/`; FAOSTAT trade in `~/Data/faostat_tcl/`):
   `grid_cattle.csv.gz`, `beef_export_share.csv`. Export for the article: `results/beef_summary.csv`.
   Cell level (9 km, 2001-2025, SE by country): beef term -0.26 (0.06), the same with 3- and 5-year moving
   averages and 5-year periods; forest 2000 x year: -0.21; + cattle x linear trend: -0.03 (0.11); + trend and
   forest: -0.01; beef price without its trend: -0.03. By region: Latin America -0.35 without trend, +0.09
   (0.12) with regional trends. The negative sign is a trend: deforestation moved away from old cattle areas
   while the real beef price doubled (114 -> 244, 2000 = 100). The crop index stays at 0.94-1.23.
   Country level: export share x beef price on cattle deforestation, nothing in any version (SE 1.5 to 7);
   placebo on crop deforestation significant once (-10.1, p = 0.04): noise. Brazil is 68% of cattle
   deforestation (31.9 of 46.9 Mha) and only became an exporter after 2000 (share 2% in 1996-2000, 20% in
   2001-2023). Local producer prices: the 14 countries with 10+ years make 6% of cattle deforestation
   (Brazil 2001-2006 only), coefficient negative (reverse causality), not causal.
6. Final article notebook (Medium style, max 3,000 words, technical parts in an appendix).
   Skeleton done (19.11.2026): `notebooks/6-Article.ipynb`, 11 sections + appendix, all code reads small files
   (results/summary.csv, inference.csv, contribution.csv exported by notebook 4, beef_grid_9km.csv and
   beef_summary.csv exported by notebook 5); runs in about 1 min from GitHub. Every prose block is a
   "To write (Andrew)" placeholder with the points and numbers to cite. A word count cell checks the 3,000
   word limit. Section 9 (beef) done (20.11.2026): points to write, figure (beef term with and without the
   trend of cattle areas), Appendix A.5 (all beef estimates); AI tools and Reproducibility are now A.6 / A.7.
   Updated (25.11.2026): To write points of the hook and sections 4, 5, 10, 11 rewritten with the main model;
   code reads controls_9km.csv, identification_9km.csv and effect_size_9km.csv (ladder figure in section 4,
   share figure in section 5, full tables in A.3); contribution.csv (old 44%) is no longer used.
7. Done (25.11.2026), after the meeting with the professor, in notebook 4 (default run 84 s from GitHub):
   (a) Section 13, identification checks, `results/identification_9km.csv` (RECOMPUTE: about 4 min, 13 GB):
   province x year FE 0.38; leads of the index in the Berman design fail (t 1.04, t+1 -0.06, t+2 0.98);
   cell trends 0.13; first differences 0.22; leave one crop out 0.75 (banana) to 1.17 (cocoa). At 0.5 degree:
   cell trends 0.05 (ns), first differences 0.26. Figure `leave_one_crop_out.png`.
   (b) Section 14, controls ladder, `results/controls_9km.csv` (RECOMPUTE: about 30 min, more than 10 GB):
   1. cell + country x year 0.99; 2. + forest 2000 deciles x year 0.64; 3. + protected, cattle, average
   suitability (2000) x year 0.72; 4. province x year (MAIN) 0.37; 5. + cell trends 0.12. Detrended index
   (each crop price divided by its log-linear trend 2001-2025): 0.26, 0.27, 0.25, 0.15, 0.14, but unstable
   across periods (0.57 for 2001-2018, 0.06 for 2001-2023) and its t+1 lead is significant: a check only.
   Figures `controls_ladder.png`, `detrended_prices.png`.
   (c) Section 15, size of the effect, `results/effect_size_9km.csv`: sample loss 285.9 Mha (11.4 Mha per
   year). Main model: typical shock (SD of ln index after cell + province x year FE, 0.032) +1.2%; all prices
   +10% = +0.40 Mha per year; share of 2001-2025 loss due to prices 16% (45 Mha, CI 13-19%), Berman design 36%
   (104 Mha), lower bound 5%; 2024 cocoa spike (+121% real) +3.2% (0.73 Mha). Formula: loss x
   exp(-beta (lnP - lnP 2001)) with observed loss (not the decile model of section 6). GAEZ spreads cocoa over
   all humid forests (median weight 7%, max 21%), so no cocoa map by country. Figure `share_due_to_prices.png`.
   Shared doc for the professor (Claude Docs, English): https://claude.ai/artifact/QAi9Ak2BU776rzYqUDRjFw.
   NEXT: depending on the professor, rerun neighbours (section 10) and protected areas (section 11) with the
   main model; then the user writes the article text.
8. After merging into `main`: switch `BRANCH` to "main" in notebooks 3, 4, 5 and 6.

Pushing: git in the Claude Code terminal has no GitHub credentials. Commit there, push with GitHub Desktop.

## Key references
- Berman, Couttenier, Leblois, Soubeyran (2023), "Crop prices and deforestation in the tropics", JEEM 119
  (working paper: FAERE WP 2022.08; replication files: Zenodo 7044013). The reference design.
- Hansen et al. (2013), "High-resolution global maps of 21st-century forest cover change", Science 342(6160).
- FAO and IIASA (2021), Global Agro-Ecological Zones v4 (GAEZ v4).
- Goldsmith-Pinkham, Sorkin and Swift (2020), AER: shift-share identification from the shares.
- Harding et al. (2021): commodity prices and deforestation in Brazil (cited by Berman et al.).
- Singh and Persson (2026), DeDuCE: deforestation attributed to commodities (beef section).
- Du et al. (2025), "Annual global grided livestock mapping from 1961 to 2021", ESSD 17, 5543-5556 (AGLW,
  Zenodo 17128483): cattle density in 2000 (beef section).
- Assuncao, Gandour and Rocha (2015), Environment and Development Economics: in the Amazon, crop prices
  raise deforestation but the effect of cattle prices is mixed (supports our beef result).

## Deadline
Final deliverable: December 18 at 16:00 (MGT-499 guidelines, docs/MGT-499_Project-guidelines.docx.pdf). Medium-style notebook article, max 3,000 words, technical
parts in an appendix. The notebook must run top to bottom from GitHub data.
