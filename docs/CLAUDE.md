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
- Do not change existing notebooks (`1-Forest-Loss.ipynb`, `2-Bivariate-Data.ipynb`, `Commodities.ipynb`)
  unless I ask. New work goes in a new notebook (see below).
- Before running anything long or downloading data, tell me what you will do.

## Data rules
- Every dataset is merged on `iso3` + `year`.
- In notebooks, load data through raw GitHub URLs, never local paths, so the grader can run the notebook
  top to bottom:
  `BASE = "https://raw.githubusercontent.com/AndrewEberhardt/DataScienceProject/main/data/"`
- New raw files go in `data/raw/...`, derived files in `data/processed/...`. Log every new source in
  `docs/data_log.md` (source, URL, download date, variables, units).
- Python packages are listed in `requirements.txt` (pandas, numpy, linearmodels, statsmodels, matplotlib,
  wbgapi, geopandas, rasterstats).

## Sample (fixed, do not change)
62 countries with at least 30% of their territory between 30N and 30S (Natural Earth borders,
equal-area projection ESRI:54034) and at least 1 Mha of tree cover in 2000. Excluded: Algeria, Chile,
New Caledonia, South Sudan. Three regions: Latin America & Caribbean, Africa, Asia-Pacific
(from the Natural Earth continent field). List of countries: `data/processed/shock_panel.csv`.

## Research design (new, decided after the midterm)

### Question
How do world palm oil price shocks affect deforestation across tropical countries, and does the effect
depend on how exposed a country is? Soybeans follow the same design later. Beef is set aside for now
(world beef prices barely reach local markets: 0 of 21 countries show a correlation above 0.5).

### Design: exposure design (continuous-intensity difference-in-differences)
One commodity, so this is NOT a Bartik / shift-share design. The world price is the common shock,
the country's baseline exposure is the dose:

```
Y_palm[i,t] = beta * Exposure_palm[i] * p_palm[t-1] + alpha[i] + delta[t] + e[i,t]
```

- `alpha[i]` country fixed effects, `delta[t]` year fixed effects. They absorb exposure alone and the
  price alone, so only the interaction is estimated.
- Standard errors clustered by country (62 clusters).
- Estimate with `linearmodels.PanelOLS` (`EntityEffects + TimeEffects`, `cov_type="clustered",
  cluster_entity=True`).

### Variables
- Outcome `Y_palm[i,t]`: deforestation attributed to oil palm (DeDuCE, `data/processed/
  deduce_selected_commodities.csv`, commodity "Oil palm fruit", column `defor_ha`), divided by tree
  cover in 2000 (`extent_2000_ha`), times 100. Many zeros (about 17% of country-years): use
  `asinh` of the rate as main transform, report `log(1 + rate)` as a check. DeDuCE covers 2001-2023, so
  the period is 2001-2023. Robustness outcome: agricultural tree cover loss rate from GFW
  (`log_agri_loss_rate`, current Y).
- Exposure `Exposure_palm[i]` (fixed, baseline, no forest in it):
  `mean oil palm area harvested 1996-2000 (ha) / country land area (ha)`.
  - Area harvested: FAOSTAT, domain "Crops and livestock products", item "Oil palm fruit",
    element "Area harvested", years 1996-2000. NOT in the repo yet: if the file is missing, stop and ask
    me to download it (CSV, normalized format) into `data/raw/crops/faostat_palm_area_1996_2000.csv`.
  - Land area: World Bank indicator `AG.LND.TOTL.K2` (km2, use the 2000 value, x 100 for ha) via
    `wbgapi`, or the equal-area land area already computed from Natural Earth in `1-Forest-Loss.ipynb`.
  - Countries with no palm area get exposure 0 (they stay in the sample as controls).
- Price `p_palm[t]`: log of the real world palm oil price, World Bank Pink Sheet
  (`data/processed/commodity_prices_annual.csv`, commodity "Palm oil", column `log_price_real`).
  Use it lagged one year in the main specification.

### Threats and how we handle them
- Indonesia and Malaysia move the world price themselves: robustness without both.
- Palm oil co-moves with other vegetable oils and crude oil (biodiesel): add
  `Exposure_palm * log(real crude oil price)` (Pink Sheet "Crude oil, average") as a control.
- Non-producers may differ from producers: add region x year fixed effects as a robustness check.
- Plantations take years to develop: lags 1, 2 and 3 of the price.
- Continuous dose with TWFE is hard to interpret under heterogeneous effects (Callaway,
  Goodman-Bacon and Sant'Anna, NBER WP 32117): also report a binned version (high vs low exposure,
  above vs below the median among producers).

## Task list (one step at a time, wait for my go between steps)
1. Create `notebooks/3-Palm-Exposure-Design.ipynb`. Load the 62-country sample, DeDuCE (oil palm),
   GFW panel and Pink Sheet prices from raw GitHub URLs. Build `Y_palm` (rate, asinh). Show a short
   summary table (mean, median, share of zeros, by region).
2. Build `Exposure_palm` (needs the FAOSTAT area file, see above). Save
   `data/processed/palm_exposure.csv` (iso3, country, region, area_1996_2000_ha, land_area_ha,
   exposure_palm). Plot the top 15 countries and give the number of countries with exposure > 0.
3. Main regression: `Y_palm[i,t]` on `Exposure_palm[i] * p_palm[t-1]` with country and year FE,
   clustered SE. Then lags 1, 2, 3 (separately and together). Results table with coefficient, SE,
   p-value, 95% CI, N.
4. Event study (pre-trend check): replace the interaction with `Exposure_palm[i] x year dummies`
   (omit 2001 as reference). Plot the yearly coefficients with 95% CI next to the palm price path.
5. Placebos: (a) next year's price `p_palm[t+1]` instead of `t-1`; (b) a price unrelated to palm oil
   (Pink Sheet "Wheat, US HRW") interacted with `Exposure_palm`. Both should give effects close to 0.
6. Robustness: without Indonesia and Malaysia; with the crude oil control; with region x year FE;
   GFW agricultural loss as outcome; binned exposure (high vs low).
7. Summary figure: coefficient plot of all specifications (main, lags, placebos, robustness).

## Later (not now)
- Soybeans with the same design (FAOSTAT "Soya beans" area harvested).
- Alternative exposure: FAO GAEZ suitability share (more exogenous).
- Heterogeneity: interaction with export share (exports / production) and governance in 2000 (QoG).

## Key references
- Berman, Couttenier, Leblois, Soubeyran (2023), "Crop prices and deforestation in the tropics", JEEM
  (HAL hal-04093064): crop suitability x world prices, tropics-wide grid.
- "Palm oil and the politics of deforestation in Indonesia", JEEM 2021 (doi 10.1016/j.jeem.2021.102453):
  palm suitability x world prices at district level. Check the author list before citing.
- Pierce and Schott (2016), AER 106(7): fixed baseline exposure x common shock, falsification test.
- Callaway, Goodman-Bacon and Sant'Anna, "Difference-in-Differences with a Continuous Treatment"
  (NBER WP 32117): interpretation of continuous-dose TWFE.
- Goldsmith-Pinkham, Sorkin and Swift (2020), AER; Adao, Kolesar and Morales (2019), QJE: only needed
  if we later combine several commodities in a shift-share variable.
- Singh and Persson (2026), DeDuCE: deforestation attributed to commodities.

## Deadline
Final deliverable: December 19 at 16:00. Medium-style notebook article, max 3,000 words, technical
parts in an appendix. The notebook must run top to bottom from GitHub data.
