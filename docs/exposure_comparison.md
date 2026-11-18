# Choosing the exposure measure: FAOSTAT area vs GAEZ suitability

Working document for the team. Goal: decide which exposure measure we use in the final article for palm oil and soybeans.
Every number below comes from `notebooks/3-Palm-Exposure-Design.ipynb` and `notebooks/4-Soy-Exposure-Design.ipynb` (run of November 2026).

---

## 1. What we are deciding

The design stays the same whatever we choose. Only `Exposure[i]` changes:

```
Y[i,t] = beta * Exposure[i] * log p[t-1] + alpha[i] + delta[t] + e[i,t]
```

- `Y[i,t]`: asinh of deforestation attributed to the crop (DeDuCE) as % of tree cover in 2000
- `p[t-1]`: real world price of the crop (Pink Sheet), lagged one year
- `alpha[i]`, `delta[t]`: country and year fixed effects, SE clustered by country (62 countries, 2001-2023, N = 1,426)

The whole identification rests on one assumption: **without the price change, highly exposed and weakly exposed countries would have followed the same deforestation path.** The exposure measure decides whether this assumption is believable.

Four options:

| | Option | Exposure[i] | Status |
|---|---|---|---|
| A | FAOSTAT area (current) | harvested area 1996-2000 / land area | done (notebooks 3 and 4) |
| B | GAEZ suitability | share of land suitable for the crop / land area | not started |
| C | GAEZ suitability x forest | suitable land that was forested in 2000 / land area | not started |
| D | IV: A instrumented by B | A, with `B * p[t-1]` as instrument for `A * p[t-1]` | not started, needs B |

---

## 2. Option A: FAOSTAT harvested area 1996-2000 (current)

**Definition.** Mean harvested area of the crop in 1996-2000 (FAOSTAT QCL, "Oil palm fruit" or "Soya beans", element "Area harvested") divided by World Bank land area in 2000 (`AG.LND.TOTL.K2`, Natural Earth for Taiwan). Countries with no area get 0.

**Meaning of beta.** Effect of a 1 log point higher world price on deforestation, per unit of share of land already planted with the crop before 2001.

**What we found.**

| | Palm oil | Soybeans |
|---|---|---|
| Countries with exposure > 0 | 37 of 62 | 43 of 62 |
| Most exposed | Malaysia 9.35%, Nigeria 3.28%, Guinea 1.26%, Indonesia 0.93% | Argentina 2.64%, Paraguay 2.62%, India 2.06%, Brazil 1.48% |
| Median producer | 0.11% | 0.03% |
| Main beta (t-1), clustered p | +2.15, p < 0.001 | -2.84, p = 0.004 |
| Wild cluster bootstrap p | 0.058 | 0.165 |
| Without the 3 most influential countries | -1.25, p = 0.46 | +0.39, p = 0.34 |
| Placebo wheat price (should be 0) | +0.88, p = 0.012 (fails) | -1.74, p = 0.002 (fails) |
| Placebo price t+1 (should be 0) | +0.22, p = 0.68 (passes) | -0.87, p = 0.052 (borderline) |
| Adding exposure x linear trend | beta halves to 1.00, p = 0.045 | beta becomes +1.48, p = 0.44 |

**Strengths.**
- Very intuitive: "countries that already grew palm oil".
- Measures where the crop really is, so the link between price and local supply response is strong (high relevance).
- Data already in the repo, everything runs.
- Same logic as Pierce and Schott (2016): baseline exposure fixed before the period x common shock.

**Weaknesses.**
- **Exposure is chosen, not given.** A country planted palm in 1996-2000 because of past clearing, plantation policies, investors, roads. These factors also create its own deforestation trend after 2001. The exposure trend test and the event study (coefficients rising steadily 2005-2017 for palm, switching sign after 2013 for soy) show exactly this problem.
- For soy, high exposure = Brazil, Argentina, Paraguay, where deforestation fell for policy reasons (PPCDAm 2004, Soy Moratorium 2006). The negative beta most likely captures these policies, not prices.
- Very concentrated: 3 countries carry the result in both crops.
- Data quality: Nigeria (3.28%) has 0 of 5 official FAOSTAT values (estimates only). Ghana, Malawi, Mozambique get soy exposure 0 because FAOSTAT has no row, although DeDuCE shows soy deforestation there (0.9% of sample soy deforestation).
- Placebo wheat fails in both crops: with prices correlated at 0.85, we cannot separate a palm or soy price effect from a general commodity boom effect.

---

## 3. Option B: GAEZ crop suitability

**Definition.**

```
Exposure_GAEZ[i] = land area of country i with suitability "medium or better" for the crop / land area of country i
```

(alternative: mean suitability index over the country, 0 to 1). Source: FAO and IIASA, Global Agro-Ecological Zones v4 (https://gaez.fao.org/), theme "Suitability and Attainable Yield".

GAEZ gives, for each grid cell of about 9 km (5 arc-minutes), a suitability index from 0 to 10,000 computed **only from climate, soil and terrain**: temperature, rainfall, length of growing period, soil type, slope. It says where the crop *could* grow, not where it *is* grown.

GAEZ suitability classes (index): very high > 8,500; high 7,000-8,500; good 5,500-7,000; medium 4,000-5,500; moderate 2,500-4,000; marginal 1,000-2,500; very marginal < 1,000; not suitable 0. "Medium or better" = index >= 4,000. We test 2,500 and 5,500 as robustness.

**Meaning of beta.** Effect of a 1 log point higher world price on deforestation, per unit of share of land agronomically suited to the crop. This is an **intention to treat**: it includes countries that are suitable but did not respond (for example Central Africa for palm).

**Strengths.**
- **Much more exogenous.** Climate and soil were not chosen by governments or investors and do not depend on past clearing. The parallel trends assumption is far easier to defend: highly suitable countries have no obvious reason to follow a different deforestation path *except* through the crop.
- **Reference method of the literature**: Berman, Couttenier, Leblois and Soubeyran (2023, JEEM), suitability x world prices across the tropics; the Indonesia palm paper (JEEM 2021), suitability x prices at district level. Graders will recognise it.
- Removes the FAOSTAT data problems (estimates, missing rows, Nigeria, Ghana).
- Exposure is spread over many more countries, so results depend less on 3 countries.
- Answers directly the main weakness of Option A, which is what the course grades most (causal identification).

**Weaknesses.**
- **Suitability is not production.** Congo basin countries are very suitable for palm but produce little (no infrastructure, weak institutions, land tenure). The link with the real supply response is weaker, so estimates will be less precise and possibly closer to 0. A null result is possible and must be written honestly.
- **Few true controls.** Almost every tropical country is somewhat suitable for palm and soy: few countries at 0. This is fine for a continuous dose design but the binned version (high vs low) must use a median split, not producer vs non producer.
- **Suitability can still correlate with other things** that drive deforestation trends: tropical rainforest climate, remoteness. Region x year fixed effects and the exposure trend test remain necessary.
- **Prices still co-move.** If wheat suitability correlates with palm suitability, the wheat placebo can still fail. Better placebo with GAEZ: use the suitability of a crop that grows in other climates (wheat suitability x wheat price), which is a cleaner test than in Option A.
- **More work**: download rasters, compute zonal statistics per country, check small islands.

**Choices to fix before computing** (and to write in `docs/data_log.md`):

| Parameter | Recommended choice | Why |
|---|---|---|
| Variable | Crop suitability index (0-10,000) | continuous, allows any threshold |
| Crop | Oil palm; Soybean | our two commodities |
| Water supply | Rainfed | irrigation depends on investment, so it is endogenous |
| Input level | High input (robustness: low input) | decided 18.11.2026: with low input, soy is rated marginal in Mato Grosso and Parana, while soy and palm deforestation is driven by commercial, mechanised farms |
| Climate period | earliest historical baseline available (1961-1990 if offered, else 1981-2010) | must be determined before our sample |
| Climate data | historical observed (CRU), not a future scenario | |
| Threshold | index >= 4,000 (robustness: 2,500 and 5,500, and mean index) | standard GAEZ classes |
| Borders | Natural Earth 50m, as in the rest of the project | same sample definition |
| Area weighting | reproject to ESRI:54034 (equal area) before counting cells | cells in degrees have unequal area by latitude |

**How to compute** (new notebook, about 1 day of work):
1. Download the two rasters (GeoTIFF) from the GAEZ data portal and save them in `data/raw/gaez/` (files are a few MB, under the 100 MB limit).
2. Load them from GitHub URLs with `rasterio`, reproject to ESRI:54034.
3. With `rasterstats.zonal_stats` and Natural Earth borders, compute for each of the 62 countries the suitable area and the land area. Use `all_touched=True` or 10m borders for small islands (Vanuatu, Solomon Islands, Fiji) and check them by hand.
4. Save `data/processed/gaez_exposure.csv` (iso3, country, region, suitable_area_ha, land_area_ha, exposure_gaez_palm, exposure_gaez_soy).
5. Plot the top 15 and the correlation with Option A (scatter, one point per country).
6. Rerun sections 3 to 8 of notebooks 3 and 4 with the new exposure.

---

## 4. Option C: GAEZ suitability x forest in 2000

**Definition.**

```
Exposure_C[i] = area that is suitable for the crop AND forested in 2000 / land area
```

Requires the Hansen tree cover 2000 raster, or a GFW country table by suitability zone (not available).

**Idea.** A price boom can only cause deforestation where there is suitable land still covered by forest. This is closest to what Berman et al. do at grid cell level.

**Strengths.** Measures the land that can actually be converted; likely the strongest relevance among exogenous measures.

**Weaknesses.**
- **Contradicts a choice we already made**: "no forest in the exposure" (`docs/CLAUDE.md`). Forest in 2000 depends on past deforestation, which may have its own dynamics, and our outcome is already divided by forest in 2000.
- Mixes two mechanisms (price response and forest availability) into one number; harder to interpret.
- Needs the Hansen 30 m raster for the tropics: very heavy (several GB), not compatible with the 100 MB repo rule unless we aggregate it outside the notebook.

**Verdict.** Not worth it for the deadline. Better: keep forest in 2000 as a **heterogeneity variable** (Option B x high vs low forest cover), which the README already plans.

---

## 5. Option D: instrumental variable (A instrumented by B)

**Definition.** Two stage least squares with country and year fixed effects:

```
First stage:  Exposure_FAO[i] * p[t-1] = pi * Exposure_GAEZ[i] * p[t-1] + alpha[i] + delta[t] + u[i,t]
Second stage: Y[i,t] = beta * (fitted Exposure_FAO * p[t-1]) + alpha[i] + delta[t] + e[i,t]
```

Option B is then the **reduced form** of Option D: running B is required anyway.

**Meaning of beta.** Same units and meaning as Option A (per unit of planted share), but using only the part of planted area explained by geography.

**Strengths.**
- Keeps the intuitive interpretation of A while using the exogeneity of B.
- Standard and elegant; shows graders we understand endogeneity of exposure.

**Weaknesses.**
- **Weak instrument risk.** With 62 countries and suitability that predicts production poorly in Africa, the first stage may be weak (rule of thumb: first stage F > 10 with clustered SE). If weak, the IV estimate is biased and its CI is huge.
- Exclusion restriction: suitability must affect deforestation only through planted area in 1996-2000. Arguable: suitable countries can expand the crop *after* 2000 without having planted it before, which is precisely the effect we want to measure. This makes the IV less natural than B alone.
- `linearmodels.PanelOLS` does not do IV. Need `pyfixest` (`feols("y ~ 1 | iso3 + year | x ~ z")`) or a manual within transformation with `linearmodels.IV2SLS`. Add `pyfixest` to `requirements.txt` if chosen.

**Verdict.** Worth reporting only if the first stage is strong. Cheap once B exists (half a day).

---

## 6. Side by side

| Criterion | A: FAOSTAT area | B: GAEZ suitability | C: GAEZ x forest | D: IV |
|---|---|---|---|---|
| Exogeneity (parallel trends credible?) | weak: shown by trend test and placebos | good | medium (forest 2000 endogenous) | good if exclusion holds |
| Relevance (link to real supply response) | strong | medium, weak in Central Africa | medium to strong | depends on first stage |
| Interpretation | very simple | simple (intention to treat) | harder | simple, same as A |
| Precision expected | high but driven by 3 countries | lower | lower | lowest |
| Data quality | FAOSTAT estimates and gaps | homogeneous global model | heavy raster | inherits both |
| Support in the literature | Pierce and Schott 2016 (trade) | Berman et al. 2023; Indonesia JEEM 2021 | Berman et al. (grid level) | common in shift share papers |
| Extra work | none | about 1 day + rerun | several days, heavy data | half a day after B |
| Fits our current rules | yes | yes | no (forest in exposure) | yes |
| Risk for the article | results not credible as causal | null result possible | deadline | weak instrument |

---

## 7. Diagnostics that will decide (to run once B exists)

Decide the rules **before** seeing the results, so the choice is not driven by significance.

1. **Relevance**: correlation between Exposure_FAO and Exposure_GAEZ across the 62 countries, and first stage F of Option D. If F > 10: D is usable.
2. **Trend test**: add `Exposure x linear trend`. The exposure that keeps beta stable is the more credible one.
3. **Placebos**: price t+1, and wheat (price x wheat suitability for B). They should give 0.
4. **Influence**: drop the 3 most influential countries; wild cluster bootstrap p values.
5. **Event study**: yearly coefficients should follow the price path, not a smooth trend.

**Decision rule we propose:**
- B passes the trend test and placebos better than A: **B is the main specification**, A goes to the appendix as comparison, D reported if F > 10.
- B and A both fail: we keep B as main (more defensible) and write the article as a **credible null result** with a clear discussion of why identification is hard at country level.
- B gives nothing and A gives an effect that fails placebos: we do **not** present A as causal.

---

## 8. Our recommendation

**Compute Option B now, run D as a by-product, drop C (keep forest 2000 for heterogeneity), keep A as a comparison.**

Reasons:
- Option A fails the two tests that matter for the causal part of the grade (wheat placebo in both crops, exposure trend for soy and half of palm). Keeping it as the main result means presenting something we already know is not credible.
- Option B is the standard answer of the literature to exactly this problem and costs about one day.
- Even if B gives a null result, the article becomes stronger: "the naive exposure gives an effect, the exogenous exposure does not, here is why" is a clear causal inference story.

---

## 9. Timeline (deadline December 19, 16:00)

| Week | Task |
|---|---|
| Nov 18-24 | Download GAEZ rasters, compute `gaez_exposure.csv`, log in `data_log.md` |
| Nov 25-Dec 1 | Rerun palm and soy with B, run D and the diagnostics of section 7, apply the decision rule |
| Dec 2-8 | Heterogeneity (forest 2000), final figures, literature review |
| Dec 9-17 | Write the article (max 3,000 words) and technical appendix, test the notebook top to bottom from GitHub |
| Dec 18-19 | Buffer, upload to Moodle |

---

## 10. References

- Berman, Couttenier, Leblois and Soubeyran (2023), "Crop prices and deforestation in the tropics", *JEEM* (HAL hal-04093064).
- "Palm oil and the politics of deforestation in Indonesia" (2021), *JEEM*, doi 10.1016/j.jeem.2021.102453 (check author list before citing).
- Pierce and Schott (2016), *AER* 106(7).
- Callaway, Goodman-Bacon and Sant'Anna, "Difference-in-Differences with a Continuous Treatment", NBER WP 32117.
- FAO and IIASA (2021), Global Agro-Ecological Zones v4 (GAEZ v4), https://gaez.fao.org/.
- Singh and Persson (2026), DeDuCE, *Nature Food*.
