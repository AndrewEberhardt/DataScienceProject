# Midterm presentation: slide outline (October 15)

Format: max 8 slides, EDA + causality issues. **Draft:** the team rewrites the text in its own words before presenting (see "Use of AI tools" in the README). Every number below comes from the notebook named next to it.

| # | Slide | Figure | Notebook |
|---|---|---|---|
| 1 | Question and approach | none | README |
| 2 | Sample and outcome | `figures/sample_map.png` | `1-Forest-Loss.ipynb` |
| 3 | Which commodities | `figures/commodities_top15.png` | `Commodities.ipynb` |
| 4 | Do world prices reach farmers? | `figures/price_passthrough.png` | `david/david.com.price.ipynb` |
| 5 | Building X, the price shock | `figures/relative_prices.png` + formula | `david/david.com.price.ipynb` |
| 6 | Bivariate: raw vs within | `figures/bivariate_within.png` | `2-Bivariate-Data.ipynb` |
| 7 | Why the sign flips: trends | `figures/bivariate_trends.png` | `2-Bivariate-Data.ipynb` |
| 8 | Causality issues and next steps | table | `2-Bivariate-Data.ipynb`, section 6 |

---

## 1. Question and approach

- Do world commodity price booms cause more deforestation in tropical countries?
- Outcome: tree cover loss rate (Global Forest Watch). Explanatory variable: country-specific price shock X, lagged one year.
- Method (after the midterm): panel regressions with country and year fixed effects.
- Heterogeneity: is the effect stronger where more forest was left in 2000?
  *To decide:* `1-Forest-Loss.ipynb` also mentions governance as the heterogeneity variable. Pick one for the slide.

## 2. Sample and outcome

- Rule fixed in advance: at least 30% of the territory between 30°N and 30°S, and at least 1 Mha of tree cover in 2000 → 63 countries, 2001–2025, balanced panel.
- About 278 Mha lost: 129 Mha in Latin America & Caribbean, 80 Mha in Asia-Pacific, 69 Mha in Africa.
- Permanent agriculture explains 60.1% of the loss → second outcome: agricultural loss rate.
- Loss rates are very skewed → we use logs.

## 3. Which commodities

- DeDuCE (Singh & Persson 2026): cattle 38.6%, oil palm 8.4%, soybeans 5.1% of attributed deforestation; together 52.2% of all and 59.5% of agricultural deforestation.
- All three have a world price (World Bank Pink Sheet). Palm oil and soy are mostly exported, cattle mostly domestic.
- Cocoa (2.2%) and rubber (1.3%) left out: much smaller.

## 4. Do world prices reach farmers?

- Correlation of year-to-year changes in the local producer price (FAOSTAT) and the world price, country by country.
- Local price follows the world price (correlation > 0.5) in 15 of 53 country-commodity series (14 of 37 countries).
- Soybeans 12/26, palm oil 3/6 (Malaysia, Colombia, Indonesia), **beef 0/21**.
- → Price transmission is a causality issue for beef, our biggest commodity.

## 5. Building X, the price shock

- $X_{it} = \sum_c \log(1 + E_{ic}) \times \tilde p_{ct}$
- Exposure $E_{ic}$: value of 1996–2000 production per hectare of forest in 2000, fixed before the sample.
- Relative price $\tilde p_{ct}$: log real world price minus its 1996–2000 average.
- log(1 + x) because of extreme exposures; South Sudan dropped (no data before 2011); X lagged one year.
- 62 countries × 25 years = 1,550 observations.

## 6. Bivariate: raw vs within

- Raw correlation between loss rate and X(t−1): **+0.33**.
- Within countries (country and year averages removed): **−0.24**.
- Also removing each country's trend: **−0.02**; year-to-year changes: **−0.06**.
- Same picture for the agricultural loss rate (+0.35, −0.26, −0.08, −0.07).

## 7. Why the sign flips: trends

- X rises over time in exposed countries (world prices above their 1996–2000 level after 2003).
- The most exposed countries had flat or falling loss rates: correlation −0.50 between a country's average shock and the trend of its loss rate.
- The most exposed countries are beef producers with little forest (Zimbabwe, Argentina, South Africa, Nigeria), not the big frontiers.
- → Fixed effects alone are not enough: we need country trends or first differences.

## 8. Causality issues and next steps

| Issue | Answer |
|---|---|
| Reverse causality (Brazil, Indonesia, Malaysia move world prices) | world prices; robustness without the big producers |
| Exposure caused by deforestation | exposure fixed in 1996–2000 |
| Permanent differences between countries | country fixed effects |
| Common shocks (world demand, 2008 crisis) | year fixed effects |
| Different trends (Brazil's PPCDAm 2004, Soy Moratorium 2006, Indonesia moratorium 2011) | country trends, first differences |
| Prices may not reach farmers (beef) | robustness with soy and palm oil only |
| Non-agricultural loss (fires, logging) | agricultural loss rate as second outcome |
| Leakage between countries | limitation |

Next: panel regressions (fixed effects, country trends, first differences, clustered by country), heterogeneity by forest in 2000, controls (World Bank WDI).
