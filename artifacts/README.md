# Compact scientific artifacts

This directory intentionally contains only the CSV evidence needed to inspect or reconstruct the final scientific comparisons without shipping hundreds of intermediate files.

- `Tables/Predictions/`: matched outer-OOF predictions for baselines, modern models, FA-ATF, ablations, retained experts, and uncertainty intervals.
- `Tables/Metrics/`: final ranking, target-wise performance, ablations, uncertainty, target-specific weights, fold-assignment sensitivity, and measured latency.
- `Tables/Statistics/`: paired comparisons, multiplicity-aware tests, rank stability, leave-one-specimen influence, ablation tests, and the specimen-profile permutation test.

All values are copied from the executed primary run `FA_ATF_DaKS69_Exploratory_20260820`. Model binaries, training caches, manifests, duplicate figure-source tables, and administrative reports are deliberately excluded.

## Location and prediction schema

All retained tables are under [`FA_ATF_DaKS69_Exploratory_20260820/Tables/`](FA_ATF_DaKS69_Exploratory_20260820/Tables/). The run label identifies the historical experiment; it is not the publication date or proof of a new execution.

| Prediction file | Rows | Meaning |
|---|---:|---|
| `baseline_oof_predictions.csv` | 1,620 | Ten baseline models × two targets × 81 sections |
| `modern_oof_predictions.csv` | 1,134 | Seven modern comparators × two targets × 81 sections |
| `fa_atf_oof_predictions.csv` | 162 | Proposed model × two targets × 81 sections |
| `fa_atf_ablation_oof_predictions.csv` | 1,134 | Seven controlled variants, including full FA-ATF, × two targets × 81 sections |
| `fa_atf_uncertainty_oof.csv` | 162 | Target-wise predictions and nominal 90% residual intervals |
| `fa_atf_expert_outer_oof.csv` | 180 | Outputs of branches retained in each target/fold; branch coverage varies with selection |

The primary prediction key is `(model, target, sample_id)`; ablations use `(variant, target, sample_id)`. `y_true` contains the measured target and `y_pred` its outer-held-out prediction in physical units. `specimen_id` and `outer_fold` must match the [modeling contract](../dataset/unified/modeling_dataset.csv). Classical-model rows in the modern prediction table have no neural `seed_prediction_sd`; a blank value in that field is expected.

## Results and inference

- [Full model ranking](FA_ATF_DaKS69_Exploratory_20260820/Tables/Metrics/final_dimensionless_model_ranking.csv): 18 models ranked by mean target-wise NRMSE.
- [Target-wise metrics](FA_ATF_DaKS69_Exploratory_20260820/Tables/Metrics/final_target_metrics_with_group_bootstrap_ci.csv): 36 model-target pairs with specimen-cluster bootstrap intervals.
- [Paired comparisons](FA_ATF_DaKS69_Exploratory_20260820/Tables/Statistics/paired_fa_atf_comparisons.csv): FA-ATF versus 17 comparators; negative error differences favor FA-ATF; Holm correction applies across the comparisons.
- [Rank stability](FA_ATF_DaKS69_Exploratory_20260820/Tables/Statistics/cluster_bootstrap_rank_stability.csv): 2,000 cluster-bootstrap resamples of the 27 specimens.
- [Ablation statistics](FA_ATF_DaKS69_Exploratory_20260820/Tables/Statistics/fa_atf_ablation_statistical_comparisons.csv): bootstrap differences and multiplicity-adjusted tests for component removal.
- [Uncertainty diagnostics](FA_ATF_DaKS69_Exploratory_20260820/Tables/Metrics/fa_atf_uncertainty_summary_with_ci.csv): coverage, widths, and interval scores, including whole-specimen profiles.
- [Accuracy and latency](FA_ATF_DaKS69_Exploratory_20260820/Tables/Metrics/accuracy_latency_comparison.csv): observed accuracy and timings from the original execution environment.

The snapshot permits inspection and verification of the point metrics without fitting models. All CSV inputs read by Notebook 06 are included, allowing replay of the final statistical analysis from the stored predictions. That replay does not refit models or remeasure latency. A full sequential rerun regenerates omitted intermediate selection tables, convergence records, and model bundles. See [REPRODUCIBILITY.md](../REPRODUCIBILITY.md).
