# Does the validation protocol change the conclusions? — code and data

Code, processed data, and numerical results for the article
*Does the Validation Protocol Change the Conclusions? A Multi-Dataset Study of Leakage-Safe Evaluation and Conformal Uncertainty for Small Machining Datasets* (MDPI *Information*, manuscript information-4707995, revised version).

Every number, table, and figure in the revised manuscript is produced by the scripts in this folder.

## Datasets

| ID | Process | Rows | Independent unit | Source |
|---|---|---|---|---|
| D1 | Hard turning of 51CrV4 | 81 | 27 specimens | Wittich et al., DaKS, https://doi.org/10.48662/daks-69 (CC BY-SA 4.0) |
| D2 | NASA face milling, flank wear | 145 | 16 tool-life cases | Agogino & Goebel, NASA Ames, https://data.nasa.gov/dataset/milling-wear |
| D3 | UMich SMART CNC milling, tool condition | 4387 | 18 experiments | https://www.kaggle.com/datasets/shasun/tool-wear-detection-in-cnc-mill |

`processed/D1.csv`, `processed/D2.csv`, and `processed/D3_experiments.csv` are included. `processed/D3.csv` is regenerated from the original Kaggle files with `prep.py` (step 1 below).

## How to reproduce

```bash
pip install -r requirements.txt
# 1. data preparation (raw files downloaded from the sources above)
python prep.py hardness_roughness_hard_turning.csv mill.mat tool-wear-detection-in-cnc-mill processed
# 2. analyses
python run_icc.py          # Table 6
python run_cv.py           # Table 7, Figures 3-4 (row-wise, grouped, LOGO CV)
python run_extra.py        # Wilcoxon tests, D3 diagnostics (Table 8, Figure 5), task variants (Table 9)
python run_nested.py       # Section 3.5 (nested vs non-nested selection)
python run_conformal.py    # Section 3.6, Figure 6
# 3. figures
python figs.py all         # Figures 1, 3-6 -> figures/
```

Run time on a laptop is about 1.5 h in total; `run_nested.py` takes most of it.
Environment used: Python 3.13, scikit-learn 1.9.1, NumPy 2.5.3, SciPy 1.18.1, pandas 3.0.5, statsmodels 0.15.0, matplotlib 3.11.2.

## Files

| File | Content |
|---|---|
| `prep.py` | Data preparation for D1–D3 (see METHODS.md) |
| `common.py` | Tasks, groups, the five model families and their hyperparameters, fold generators, metrics |
| `run_icc.py` | Unadjusted and conditional ICC (REML random-intercept models) |
| `run_cv.py` | Row-wise, grouped, and LOGO CV; saves per-repetition metrics and out-of-fold predictions |
| `run_extra.py` | Group-level Wilcoxon tests with Holm adjustment; D3 fold composition, confusion matrices, majority baseline, per-experiment predictions; leave-one-level-out (D1) and leave-one-condition-out (D2) |
| `run_nested.py` | Twelve candidate configurations; non-nested vs nested grouped selection |
| `run_conformal.py` | CV-based conformal intervals: row-wise, grouped row-level, grouped cluster-level calibration |
| `figs.py`, `figs_late.py` | Figures 1 and 3–6 (written to `figures/`) |
| `results/` | Summary results (CSV) behind Tables 6–9 and Sections 3.5–3.6. Per-repetition files (`cv_runs.csv`, `cv_predictions.json`, `conformal_detail.csv`, `nested_selected.csv`) are written by the scripts when they are run. |
| `METHODS.md` | Detailed description of preprocessing, groups, folds, and calibration |

## Citation

Please cite the article and the original data sources listed above.
