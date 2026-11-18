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
| Natural Earth land area for Taiwan | https://github.com/nvkelso/natural-earth-vector | 09.11.2026, read when the notebook runs | Andrew | `ne_50m_admin_0_countries.geojson`, projected to ESRI:54034, unit ha. Used in the palm oil and soybean notebooks because the World Bank indicator has no value for Taiwan |
| World Bank land area | https://data.worldbank.org/indicator/AG.LND.TOTL.K2 | 09.11.2026, read through `wbgapi` when the notebook runs | Andrew | Indicator `AG.LND.TOTL.K2`, year 2000, unit km2 (x 100 for ha) |
| GAEZ v4 crop suitability, high input | https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/CRUTS32/Hist/6190H/ | 18.11.2026 | Andrew | `data/raw/gaez/sxHr_{olp,soy}.tif`. Theme 4 (res05), climate CRU TS 3.2, historical 1961-1990, high input, rainfed (`Hr`), crops oil palm (`olp`) and soybean (`soy`). GeoTIFF, EPSG:4326, 5 arc-minutes (2160 x 4320). Suitability index 0-10000 (nodata -9) |
| GAEZ v4 wheat suitability, high input | https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/CRUTS32/Hist/6190H/sxHr_whe.tif | 18.11.2026 | Andrew | `data/raw/gaez/sxHr_whe.tif`. Same settings as the palm and soy rasters (1961-1990, rainfed, high input), crop wheat (`whe`) |
| GADM 4.1 province borders (level 1) | https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_{ISO3}_1.json.zip | 18.11.2026 | Andrew | `data/raw/gadm/gadm41_{ISO3}_1.json.zip`, one file per sample country (62), GeoJSON in zip, EPSG:4326. Same version as the GFW subnational tables (GFW ReadMe). Disputed areas (GID_0 Z01-Z09, Kashmir and Himalayan states) are inside the India file and kept with India |
