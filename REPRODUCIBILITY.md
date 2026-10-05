# Reproducibility and snapshot verification

This repository publishes notebook source, saved executed outputs, and a compact evidence snapshot from `FA_ATF_DaKS69_Exploratory_20260820`. Inspection of the snapshot and a new end-to-end experiment have different requirements.

## Inspect the published evidence

No model fitting is required to read the dataset, executed notebook outputs, saved predictions, tables, or the 36 numbered PNG figures. Start with the [main README](README.md), [dataset annotation](dataset/README.md), and [artifact index](artifacts/README.md).

From the repository root, verify all files covered by the integrity manifest:

```bash
shasum -a 256 -c SHA256SUMS
```

On systems using GNU coreutils, `sha256sum -c SHA256SUMS` is equivalent. The manifest excludes itself and Git's internal metadata. Notebook execution changes files, so verify the unmodified snapshot first.

## What was checked for publication

The checks performed on 5 October 2026 covered:

- raw-data SHA-256 equality with the checksum enforced by Notebook 01;
- 81 complete records, 27 specimens, three sections per specimen, and one record per factorial combination;
- nine outer folds containing complete specimens and matching the saved prediction assignments;
- all 2,916 primary prediction records: 18 models × two targets × 81 uniquely matched observations;
- independent numerical verification of all 36 model-target MAE, RMSE, R², and NRMSE point estimates and all 18 joint-ranking values from the stored predictions;
- unique ablation/uncertainty keys and finite predictions;
- six readable notebook files with executed code-cell outputs and no stored exception outputs;
- presence of every CSV input read by Notebook 06, allowing analysis replay from the bundled evidence;
- documentation links, figure inventory, and file-integrity checks.

The data, numerical results, figures, and notebook contents were preserved during documentation preparation. These checks verify the saved snapshot; they do not constitute a new clean-kernel execution, a fresh environment installation, or an independent external validation. Model fitting, bootstrap inference, and latency measurement were not rerun for publication.

## Reconstruct the full workflow

Use a separate clone when rerunning so that the published snapshot remains available for comparison:

```bash
git clone https://github.com/nurgulsmakova5-gif/fa-atf-51crv4-hard-turning.git
cd fa-atf-51crv4-hard-turning
conda env create -f environment.yml
conda activate fa-atf-51crv4
python -m ipykernel install --user --name fa-atf-51crv4 --display-name "Python (fa-atf-51crv4)"
jupyter lab
```

The exact dependency pins are in [environment.yml](environment.yml). They are supplied as an environment specification, not a tested platform-independent lock file. Availability and numerical behavior can depend on the operating system and package channel. A new installation was not validated during publication.

Choose **Python (fa-atf-51crv4)** in every notebook. Open Jupyter from the repository root; the notebooks also recognize a working directory immediately inside `notebooks/`. Restart the kernel for each notebook, execute substantive cells in sequence, inspect each output, and proceed in order **01 → 02 → 03 → 04 → 05 → 06**.

| Stage | Input requirement | Main regenerated outputs |
|---|---|---|
| 01 | Preserved raw CSV | Unified measurements, audit/EDA outputs |
| 02 | Notebook 01 contract | Derived features and specimen-group folds |
| 03 | Modeling contract | Baseline fitted bundles, OOF predictions, selection and timing tables |
| 04 | Modeling contract and Notebook 03 outputs | Modern fitted bundles, neural histories, OOF predictions, selection and timing tables |
| 05 | Modeling contract | FA-ATF bundles, selected branches, ablations, intervals, fold-assignment sensitivity |
| 06 | Modeling contract and CSV evidence from Notebooks 03–05, also included in this snapshot | Final statistical comparisons, robustness summaries, scientific tables and figures |

Notebooks 03–04 reuse a previous local run only when their expected bundles and supporting tables are complete. A fresh clone does not include those bundles and therefore enters the fitting path. To force fitting in those stages after a prior local run, launch Jupyter with:

```bash
RECOMPUTE_MODELS=1 jupyter lab
```

Notebook 05 fits the proposed model when executed. Model binaries are intentionally absent from the publication snapshot and ignored by Git.

## Replay the final analysis without training

After creating the environment, Notebook 06 can be run directly from a fresh clone because all of its CSV inputs are bundled. Use a clean kernel and execute the cells sequentially. It recomputes the final metrics, bootstrap/statistical comparisons, uncertainty summaries, and within-domain analyses from the stored predictions, and regenerates the associated figures. The retained inputs include the modeling dataset, baseline/modern/proposed/ablation/uncertainty/expert predictions, fold weights, alternative-fold summary, and the three model-family timing tables.

This replay verifies analysis of a frozen prediction snapshot. It does not reconstruct the training history or validate how those predictions were fitted. It reads the original timing values rather than measuring new inference latency. To refit models and reconstruct training-side selection, run all six notebooks in order. Replay execution was not performed during this publication task; input completeness was checked statically and the point metrics were independently verified.

Notebook 04 uses Apple MPS when available and otherwise CPU. Install Times New Roman before regenerating figures: the notebook font contract may fail if the required font is absent. Regenerated figures are written to the run's `Figures/PNG` and `Figures/PDF` directories; the root `figures/` directory contains the curated publication copies indexed by [figure_manifest.csv](figures/figure_manifest.csv).

## Numerical comparison and evidence boundaries

The final NRMSE divides each target's OOF RMSE by its full-sample observed standard deviation (`ddof=1`). The joint ranking averages the two dimensionless target scores. Keep physical-unit errors separate. The fixed evaluation standard deviations are 0.8526105996 µm for `Ra` and 45.6249437679 HV30 for hardness.

Match results using stable `sample_id`, `specimen_id`, target, model/variant, and `outer_fold`, rather than CSV row order. Never replace the specimen-group folds with a random section-level split when comparing against this snapshot.

Re-execution may produce numerical differences from library versions, neural backends, or hardware; timings are especially environment-dependent. Confirmatory superiority over the focal model-family leaders remains inconclusive in the published tables. The experiment contains no independent external test set or independent experimental replication at each factor combination.
