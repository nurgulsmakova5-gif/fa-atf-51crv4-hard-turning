# Methods document: preprocessing, groups, folds, and calibration

This document describes every step needed to reproduce the analyses without inferring anything from the code.

## 1. Data preparation (`prep.py`)

**D1 — hard turning of 51CrV4.** The raw DaKS file has three header rows (names, symbols, units) and `;` as separator. Columns used: specimen ID, section, initial hardness `HV_init` (400/500/600 HV30), cutting speed `v_c` (100/175/250 m/min), feed `f` (0.05/0.25/0.50 mm/rev), depth of cut `a_p` (0.05/0.25/0.50 mm), targets `Ra` (µm) and `HV30`. No rows removed, no imputation. 81 rows, 27 specimens × 3 sections. Each specimen is a unique combination of `HV_init`, `f`, `v_c`; the three sections differ in `a_p`.

**D2 — NASA milling.** `mill.mat` (167 records). Records without measured `VB` are removed (146 remain). Record index 17 (case 2) contains corrupted signal values (|x| up to 1.6·10^29) and is removed, giving **145 runs in 16 cases**. For each of the six signals (`smcAC`, `smcDC`, `vib_table`, `vib_spindle`, `AE_table`, `AE_spindle`) the middle half of the run (samples n/4 … 3n/4) is used to compute the RMS, standard deviation, and peak-to-peak value → 18 features. Added: `time`, `DOC`, `feed`, `material` (1 = cast iron, 2 = steel). Group = `case`.

**D3 — UMich CNC mill.** For each of the 18 experiments, only rows whose `Machining_Process` starts with `Layer` (six cutting stages) are kept, and every fourth row is retained (`iloc[::4]`) → **4387 samples**. Removed columns: all `*Position` variables, `M1_CURRENT_PROGRAM_NUMBER`, `M1_sequence_number`, `M1_CURRENT_FEEDRATE`, `Machining_Process`, and the five constant signals (`Z1_CurrentFeedback`, `Z1_DCBusVoltage`, `Z1_OutputCurrent`, `Z1_OutputVoltage`, `S1_SystemInertia`) → **31 features**. Target `worn` = 1 if `tool_condition == 'worn'` (10 experiments) else 0 (8). Group = experiment number.

## 2. Groups and prediction tasks

| Dataset | Group | Grouped CV / LOGO predicts … |
|---|---|---|
| D1 | specimen | a new specimen at an unseen combination of seen factor levels (no replicated specimens exist) |
| D2 | case (tool life) | a new tool; its setting is usually represented by the twin tool (8 settings × 2 tools) |
| D3 | experiment | the condition of a tool in a new experiment |

Additional tasks: D1 leave-one-level-out (one level of `HV_init`, `f`, or `v_c` held out; 3 folds per factor); D2 leave-one-condition-out (both cases of one DOC/feed/material setting held out; 8 folds).

## 3. Fold construction (`common.splits`)

| Protocol | D1 | D2 | D3 | Repetitions (seeds) |
|---|---|---|---|---|
| Row-wise | `KFold(9, shuffle=True)` | `KFold(8, shuffle=True)` | `StratifiedKFold(6, shuffle=True)` | 20, 20, 5 (seed = 0 … r−1) |
| Grouped | `GroupKFold(9, shuffle=True)` | `GroupKFold(8, shuffle=True)` | `StratifiedGroupKFold(6, shuffle=True)` | same |
| LOGO | 27 folds | 16 folds | 18 folds | 1 |

All preprocessing (standardization, polynomial expansion) is inside scikit-learn pipelines and is fitted on the training rows of each fold only. Metrics are computed on the pooled out-of-fold predictions of each repetition: NRMSE = RMSE / SD(y) (population SD); balanced accuracy and MCC for D3. Underestimation `U = 100 (NRMSE_grouped − NRMSE_row) / NRMSE_grouped` per repetition; mean and SD over repetitions are reported (SD = variability due to fold assignment, not a confidence interval).

## 4. Group-level tests (`run_extra.py`)

For each group: NRMSE (or accuracy, D3) from row-wise predictions, averaged over repetitions, and from LOGO predictions. Two-sided Wilcoxon signed-rank test over groups (27/16/18), Holm adjustment across the five models of each task.

## 5. Nested selection (`run_nested.py`)

Twelve configurations: RF (200 trees) with `max_features ∈ {1.0, sqrt}` × `min_samples_leaf ∈ {1, 3, 5}`; kNN with k ∈ {3, 7}; standardized degree-2 polynomial features + ridge with α ∈ {0.1, 10}; SVR (RBF, ε = 0.1, standardized target) with C ∈ {1, 10}. Outer: `GroupKFold(9 or 8, shuffle=True, random_state=100+rep)`, 10 repetitions. Non-nested: the configuration with the lowest outer grouped-CV NRMSE, reporting that NRMSE. Nested: in each outer fold, `GroupKFold(4, shuffle=True)` on the training groups selects the configuration, which is refitted on all training groups and predicts the held-out groups.

## 6. Conformal calibration (`run_conformal.py`)

Outer loop: LOGO (27 or 16 held-out groups). Model: RF of `common.py`, refitted on all G−1 training groups. Calibration scores from 5-fold out-of-fold predictions on the training groups:

* row-wise: `KFold(5)` on training rows, one score |y − ŷ| per row (78 scores for D1; 125–144 for D2);
* grouped row-level: `GroupKFold(5)` on training groups, one score per row;
* grouped cluster-level: `GroupKFold(5)`, one score per group = max |y − ŷ| over its rows (26 scores for D1; 15 for D2).

Quantile q̂ = the ⌈(m+1)(1−α)⌉-th smallest of m scores, α = 0.1 (25th of 26 for D1; 15th of 15 = maximum for D2); q̂ = ∞ if the index exceeds m (requires m ≥ 9). Interval ŷ ± q̂. Reported: marginal coverage, group-simultaneous coverage (all rows of the held-out group covered), and mean width 2q̂/SD(y). Per-group details are in `results/conformal_detail.csv`.
