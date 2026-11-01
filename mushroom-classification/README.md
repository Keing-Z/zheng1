# Mushroom Toxicity Classification — End-to-End Data Science Project

A complete machine-learning workflow on the UCI Mushroom dataset: exploratory analysis,
multi-method feature-importance comparison, six-model benchmarking, and an interactive
HTML dashboard for exploring the results.

**Stack:** Python · pandas · NumPy · scikit-learn · Matplotlib · Seaborn · Chart.js

---

## What this project does

| Stage | Content |
|---|---|
| Data preparation | Loads the UCI Agaricus/Lepiota dataset, maps the 22 categorical features to Chinese labels, handles missing values (`stalk-root` encoded as `?`) |
| Exploratory analysis | Class balance, feature–class relationships, correlation heatmap across encoded features |
| Feature importance | **Three independent methods** — Random Forest impurity importance, chi-square test, mutual information — compared for agreement |
| Model benchmark | Six classifiers trained and evaluated under identical preprocessing |
| Evaluation | Accuracy / Precision / Recall / F1, **5-fold cross-validation**, ROC curves with AUC, confusion matrix |
| Reporting | Auto-generated figures, a written report, and an interactive dashboard |

---

## Results

Six models, evaluated on a held-out test set with 5-fold cross-validation:

| Model | Accuracy | Precision | Recall | F1 | CV Mean | CV Std |
|---|---|---|---|---|---|---|
| Logistic Regression | 0.9625 | 0.9616 | 0.9604 | 0.9610 | 0.9546 | 0.0066 |
| Random Forest | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| Gradient Boosting | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| SVM (RBF) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.9994 | 0.0012 |
| KNN (k=5) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.9994 | 0.0012 |
| Decision Tree | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |

### Why almost every model reaches 100% — and why that is not the interesting result

Reporting "100% accuracy" as an achievement would misrepresent the finding. The dataset
is, by construction, almost linearly separable: the `odor` feature alone carries nearly all
of the class signal. The feature-importance analysis shows this directly — `odor` scores
**mutual information = 1.0**, meaning it is perfectly informative about the label on its own.

So the model comparison is not measuring model quality; it is measuring how easy this
particular dataset is. Every tree-based model converges to the same ceiling.

**The useful conclusions are elsewhere:**

1. **Feature importance converges across methods.** Random Forest importance, chi-square
   and mutual information all rank `odor` first by a wide margin, followed by
   `spore-print-color`, `gill-color` and `bruises`. Agreement between three methodologically
   different approaches is stronger evidence than any single ranking.
2. **Cross-validation exposes the one model that isn't saturated.** Logistic Regression
   scores 0.9546 ± 0.0066 in 5-fold CV — the only model whose errors are large enough to
   observe, which makes it the only one where the preprocessing actually matters.
3. **A harder dataset is required to discriminate between models.** If the goal were model
   selection rather than analysis, this dataset would need to be replaced with one that has
   a non-trivial Bayes error.

This distinction — knowing when a metric is informative and when it is an artefact of the
data — is the part of the project I would emphasise in a review.

---

## Repository layout

```
mushroom-classification/
├── src/
│   ├── mushroom_analysis.py        # Main pipeline (772 lines, 9 methods)
│   ├── data_entry.py               # Dataset acquisition / conversion
│   └── fix_feature_importance.py   # Feature-importance comparison utility
├── data/
│   ├── agaricus-lepiota.data       # Raw UCI data
│   ├── agaricus-lepiota.names      # Attribute documentation
│   ├── mushroom_data.csv           # Cleaned, Chinese-labelled dataset
│   ├── model_results.csv           # Benchmark output
│   └── feature_importance.csv      # Three-method importance scores
├── figures/                        # 11 generated visualisations
├── dashboard/
│   └── dashboard.html              # Interactive results dashboard (Chart.js)
└── report/                         # Written report and slide deck
```

---

## Usage

```bash
pip install pandas numpy scikit-learn matplotlib seaborn

cd src
python mushroom_analysis.py
```

The pipeline prints a staged progress log and writes figures plus CSV result tables.

To open the dashboard, serve the `dashboard/` folder over HTTP (the Chart.js CDN requires
a network connection) and open `dashboard.html` in a browser.

---

## Design notes

- **Class-based pipeline.** The analysis is a single `MushroomAnalysis` class with one
  method per stage (`load_data`, `basic_statistics`, `visualization`,
  `feature_importance_analysis`, `prepare_data`, `build_models`, `evaluate_models`,
  `generate_report`). Each stage is independently re-runnable and the orchestration in
  `run()` stays readable.
- **Reproducibility.** `random_state=42` is fixed for every model and every split, so the
  benchmark table is stable across runs.
- **Scaling without leakage.** `StandardScaler` is fitted on the training split only
  (`fit_transform` on train, `transform` on test), so no test information reaches the
  model during preprocessing.
- **Known limitation.** Label encoding of the categorical columns is currently fitted on
  the full dataset before the train/test split. For this dataset it has no practical
  effect — the encoder only maps categories to integers with no dependence on the target —
  but the strictly correct approach is to fit the encoder on the training split alone and
  map unseen categories to a reserved value. This is the first thing I would change in a
  productionised version of the pipeline.
- **Figures use a headless backend.** `matplotlib.use('Agg')` is set before importing
  pyplot so the pipeline runs on a server with no display.
