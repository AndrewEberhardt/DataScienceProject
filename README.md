# Commodity Prices and Deforestation

**Do commodity booms destroy tropical forests?**

Group project for the course *Data Science & Causal Inference for Sustainability* (EPFL).

Team: Andrew, David, Pelin

---

## Research question

We study whether increases in world agricultural commodity prices (soybeans, palm oil, cocoa, coffee, beef, etc.) cause more deforestation in tropical countries.

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
│   ├── raw/            # original downloads (NOT committed, see "Where to put the data")
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

## Where to put the data

Data files are **never pushed to GitHub**: everything in `data/` (and any CSV, Excel, Parquet, zip... file) is ignored by `.gitignore`. We share data through the team [SharePoint folder](https://epflch-my.sharepoint.com/:f:/r/personal/andrew_eberhardt_epfl_ch/Documents/DataScienceProject?d=w784b1bac4ebe4103a11e659f2aae055c&csf=1&web=1&e=mt8f2b) instead.

| What | Where on your computer |
|---|---|
| Original downloads (Global Forest Watch, World Bank, FAO, QoG...) | `data/raw/` |
| Cleaned files used by the notebooks | `data/processed/` |

**When you start:** download the files from SharePoint and copy them into the same folders on your computer.

**When you add or update a data file:** save it in the right folder above, then upload it to SharePoint so the others get it too. Also note the source and download date in `docs/data_log.md`.

In the notebooks, load the data from the local folder:

```python
panel = pd.read_csv("../data/processed/panel.csv")
```

To rebuild the processed files from scratch, download the raw data from the sources above and run `notebooks/01_data_cleaning.ipynb`.

---

## Team workflow

We use **GitHub Desktop** to share code and **PyCharm** to write it. Follow these steps every time and nobody will overwrite anyone else's work.

### The 4 golden rules

1. **Never work on `main`.** Always work on your own branch.
2. **One notebook = one person.** Never edit a notebook that belongs to someone else. If you need their results, read the CSV file they saved.
3. **Pull before you start, push when you stop.**
4. **Never push data files.** Data goes on SharePoint (see above).

### Every time you work

**1. Before you start**
- In GitHub Desktop, click **Current Branch** and choose `main`.
- Click **Fetch origin**, then **Pull origin**. You now have everyone's latest work.
- Click **Current Branch → New Branch**, give it a clear name (for example `david-prices`), then **Create Branch** and **Publish branch**.

**2. While you work**
- Write your code in PyCharm as usual.
- Every time you finish a small step, go to GitHub Desktop: write a short summary at the bottom left (for example "Clean forest loss data"), click **Commit**, then **Push origin**.

**3. When your task is finished**
- Click **Create Pull Request**. This opens GitHub in your browser: click **Create pull request**.
- Tell the group. Someone else checks it and clicks **Merge pull request**.
- Back in GitHub Desktop, go back to `main` and click **Pull origin**. Start your next task with a new branch.

### Who works on what

| Person | Task | Their files |
|---|---|---|
| Andrew | | |
| David | | |
| Pelin | | |

Write your name next to a file before you start working on it. Shared functions go in `src/utils.py`: tell the group before changing it.

### If something goes wrong

- **GitHub Desktop says there is a conflict:** don't click anything you are not sure about. Send a screenshot to the group.
- **For a notebook conflict:** choose **Use the version from main**, then redo your changes in that version.
- **Never** use "force push", and never click "Discard changes" on a file you did not write.

---

## Timeline

| Date | Milestone |
|---|---|
| Oct 15 | Midterm presentation (max 8 slides, EDA + causality issues) |
| Dec 19, 16:00 | Final notebook uploaded to Moodle |

---

## Use of AI tools

We used AI assistants for brainstorming and coding help. All text is written by the team, and every claim is checked against the cited sources.
