# Commodity Prices and Deforestation

**Do commodity booms destroy tropical forests?**

Group project for the course *Data Science & Causal Inference for Sustainability* (EPFL).

Team: Andrew, David, Pelin

---

## Research question

We study whether increases in world agricultural commodity prices (soybeans, palm oil, cocoa, coffee, beef, etc.) cause more deforestation in tropical countries, and whether this effect is weaker where governance is stronger.

- **Outcome:** tree cover loss / primary forest loss (Global Forest Watch)
- **Main explanatory variable:** country-specific commodity price index (world prices weighted by pre-period crop shares or crop suitability)
- **Heterogeneity:** governance quality (Quality of Government dataset)
- **Method:** panel regression with country and year fixed effects, lagged prices

---

## Repository structure

```
.
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── raw/            # original downloads (NOT committed, see "Getting the data")
│   └── processed/      # cleaned CSVs used by the notebooks (NOT committed)
├── notebooks/
│   ├── 01_data_cleaning.ipynb   # download + clean + merge (not graded)
│   ├── 02_eda.ipynb             # detailed exploratory analysis (not graded)
│   ├── 03_analysis.ipynb        # regressions and robustness checks
│   └── article.ipynb            # FINAL graded article (max 3,000 words)
├── src/
│   └── utils.py        # shared functions (loading, plotting style, price index)
├── figures/            # exported graphs for slides and article
└── docs/
    ├── literature.md   # literature review notes
    └── midterm/        # midterm slides
```

---

## Data sources

| Role | Source | Link |
|---|---|---|
| Deforestation | Global Forest Watch, tree cover loss (Hansen et al.) | https://www.globalforestwatch.org/dashboards/global/ |
| Commodity prices | World Bank Commodity Price Data (Pink Sheet) | https://www.worldbank.org/en/research/commodity-markets |
| Crop weights | FAOSTAT, Crops and livestock products (QCL) | https://www.fao.org/faostat/en/#data/QCL |
| Crop suitability | FAO GAEZ v4 | https://gaez.fao.org/ |
| Governance | Quality of Government, Standard Time-Series | https://www.gu.se/en/quality-government/qog-data |
| Controls | World Bank World Development Indicators | https://data.worldbank.org/ |

Download date and version of each file must be written in `docs/data_log.md`.

---

## How to run

```bash
git clone https://github.com/AndrewEberhardt/datascienceproject.git
cd datascienceproject
pip install -r requirements.txt
jupyter lab
```

### Getting the data

Data files are **not stored in this repository** (they are ignored by `.gitignore`). Before running the notebooks:

1. Download the processed files from the team's shared folder: [SharePoint folder](https://epflch-my.sharepoint.com/:f:/r/personal/andrew_eberhardt_epfl_ch/Documents/DataScienceProject?d=w784b1bac4ebe4103a11e659f2aae055c&csf=1&web=1&e=mt8f2b)
2. Put them in `data/processed/` (and any raw downloads in `data/raw/`).

Notebooks then load the data from the local folder:

```python
from src.utils import DATA_DIR
panel = pd.read_csv(DATA_DIR / "panel.csv")
```

To rebuild the processed files from scratch, download the raw data from the sources above and run `notebooks/01_data_cleaning.ipynb`.

---

## Team workflow

1. **Never work directly on `main`.** Create a branch per task:
   `git checkout -b eda-prices`
2. **Commit often** with clear messages:
   `git commit -m "Add price index by country"`
3. **Push and open a Pull Request**; one teammate reviews before merging.
4. **One notebook = one owner at a time.** Notebooks merge badly, so agree on who edits which notebook. Shared code goes in `src/utils.py`.
5. **Pull before you start working:** `git pull origin main`
6. **Large files:** GitHub blocks files over 100 MB and warns above 50 MB. No data is committed: keep raw downloads in `data/raw/` and cleaned files in `data/processed/` (both ignored by git), and share them through the team folder.

---

## Timeline

| Date | Milestone |
|---|---|
| Oct 15 | Midterm presentation (max 8 slides, EDA + causality issues) |
| Dec 19, 16:00 | Final notebook uploaded to Moodle |

---

## Use of AI tools

We used AI assistants for brainstorming and coding help. All text is written by the team, and every claim is checked against the cited sources.
