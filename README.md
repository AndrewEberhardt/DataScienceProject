# Commodity Prices and Deforestation

**Do commodity booms destroy tropical forests, and can good governance protect them?**

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
│   ├── raw/            # original downloads (large files are NOT committed, see below)
│   └── processed/      # cleaned CSVs used by the notebooks (committed, small)
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

The final notebook `notebooks/article.ipynb` loads its data **by URL** from this repository, so it runs from top to bottom without any local file:

```python
BASE = "https://raw.githubusercontent.com/AndrewEberhardt/datascienceproject/main/data/processed/"
panel = pd.read_csv(BASE + "panel.csv")
```

---

## Team workflow

1. **Never work directly on `main`.** Create a branch per task:
   `git checkout -b eda-prices`
2. **Commit often** with clear messages:
   `git commit -m "Add price index by country"`
3. **Push and open a Pull Request**; one teammate reviews before merging.
4. **One notebook = one owner at a time.** Notebooks merge badly, so agree on who edits which notebook. Shared code goes in `src/utils.py`.
5. **Pull before you start working:** `git pull origin main`
6. **Large files:** GitHub blocks files over 100 MB and warns above 50 MB. Keep raw downloads in `data/raw/` (ignored by git) and commit only filtered, cleaned CSVs in `data/processed/`.

---

## Timeline

| Date | Milestone |
|---|---|
| Oct 15 | Midterm presentation (max 8 slides, EDA + causality issues) |
| Dec 19, 16:00 | Final notebook uploaded to Moodle |

---

## Use of AI tools

We used AI assistants for brainstorming and coding help. All text is written by the team, and every claim is checked against the cited sources.
