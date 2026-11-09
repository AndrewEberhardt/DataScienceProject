# Data log

| Dataset | Source URL | Version / date downloaded | Who    | Notes |
|---|---|---------------------------|--------|---|
| Tree cover loss | https://www.globalforestwatch.org/dashboards/global/ | 30.09.2026                | Andrew | 30% canopy threshold |
| Commodity prices (Pink Sheet) | https://www.worldbank.org/en/research/commodity-markets |                           |        | |
| FAOSTAT crops (QCL) | https://www.fao.org/faostat/en/#data/QCL |                           |        | |
| FAOSTAT producer prices (PP) | https://www.fao.org/faostat/en/#data/PP |                           | David  | `data/raw/crops/FAOSTAT_2.0.csv`. Indonesia palm oil 2001–2023 and Argentina beef 2001–2019 typed in by hand in `david.com.price.ipynb`: source TODO |
| GAEZ v4 suitability | https://gaez.fao.org/ |                           |        | |
| QoG Standard Time-Series | https://www.gu.se/en/quality-government/qog-data |                           |        | |
| World Bank WDI | https://data.worldbank.org/ |                           |        | |
| DeDuCE deforestation attributed to commodities | https://github.com/chandrakant6492/DeDuCE | 2001-2023 version, 08.10.2026 | Andrew | `data/raw/crops/`, sheet "Deforestation attribution". Singh & Persson, Nature Food 2026, doi:10.1038/s43016-026-01305-4 |
|trase.earth     |https://trase.earth/open-data/datasets/spatial-metrics-brazil-soy-soy-deforestation-5-year-total  |                           |        | |
| FAOSTAT oil palm area harvested | https://www.fao.org/faostat/en/#data/QCL | 09.11.2026 | Andrew | `data/raw/crops/faostat_palm_area_1996_2000.csv`. Domain QCL, item "Oil palm fruit", element "Area harvested", 1996-2000, unit ha. Panama 1996 is missing (flag M) |
| FAOSTAT soybean area harvested | https://www.fao.org/faostat/en/#data/QCL | 09.11.2026 | Andrew | `data/raw/crops/faostat_soy_area_1996_2000.csv`. Domain QCL, item "Soya beans", element "Area harvested", 1996-2000, unit ha. Missing values have flag M |
| Natural Earth land area for Taiwan | https://github.com/nvkelso/natural-earth-vector | 09.11.2026, read when the notebook runs | Andrew | `ne_50m_admin_0_countries.geojson`, projected to ESRI:54034, unit ha. Used in the palm oil and soybean notebooks because the World Bank indicator has no value for Taiwan |
| World Bank land area | https://data.worldbank.org/indicator/AG.LND.TOTL.K2 | 09.11.2026, read through `wbgapi` when the notebook runs | Andrew | Indicator `AG.LND.TOTL.K2`, year 2000, unit km2 (x 100 for ha) |
