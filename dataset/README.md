# Dataset annotation: 51CrV4 hard turning

This directory preserves the experimental input and the transparent modeling contracts used by the six notebooks. The study predicts axial surface roughness (`Ra`) and post-process Vickers hardness (`HV30`) from machining settings and initial hardness. It uses one experimental dataset; no synthetic observations are added.

## Source, attribution, and scope

| Field | Value |
|---|---|
| Dataset title | Surface layer state after hard turning of 51CrV4 |
| Creators | Felix Wittich, Thomas Wegener, Alexander Liehr, Wolfgang Zinn, Thomas Niendorf, Andreas Kroll |
| Publisher | DaKS, University of Kassel |
| Issued | 3 March 2025 |
| Persistent identifier | [10.48662/daks-69](https://doi.org/10.48662/daks-69) |
| Official record | [DaKS dataset record](https://daks.uni-kassel.de/entities/dataset/14ec53e8-1bf9-42d2-b653-5d54b3962364) |
| Source license | [Creative Commons Attribution-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-sa/4.0/) |
| Included source file | [`raw/hardness_roughness_hard_turning.csv`](raw/hardness_roughness_hard_turning.csv) |
| Prediction unit | One machined section |
| Independent grouping unit | One physical specimen |
| Sample structure | 81 sections, 27 specimens, three sections per specimen |

The deposit also provides residual-stress depth-profile data. Those observations are outside this repository's two-target task and are not included. Measured roughness `Rz` is preserved in the raw and unified tables but excluded from modeling. The related micromagnetic study supplies experimental context; micromagnetic signals are not predictors in this project.

The source metadata describe quenched-and-tempered 51CrV4, a Weiler C30 lathe, PCBN inserts with a fixed 0.8 mm corner radius, axial roughness measured with a Mitutoyo SJ-210, and hardness measured with a Struers DuraScan-70 at 294.2 N (HV30). See the [main README references](../README.md#related-peer-reviewed-sources) for the associated publications.

## Experimental hierarchy and verified data quality

The four measured factors each have three observed levels. The CSV contains all `3⁴ = 81` factor combinations exactly once. A specimen has one initial-hardness/feed/speed combination and three sections with different depths. There are nine specimens for each initial-hardness level.

Section labels are identifiers: section 1 corresponds to 0.50 mm depth, section 2 to 0.25 mm, and section 3 to 0.05 mm. The labels are not additional independent predictors. The three section responses from one specimen must remain together during validation and specimen-level resampling.

Checks of the included CSV and modeling table found:

- 81 complete measurement records and 27 distinct specimen identifiers;
- exactly three sections per specimen;
- no missing measured values or duplicate complete records;
- one observation for each four-factor combination; and
- nine outer folds, each containing nine sections from three complete specimens.

**Metadata discrepancy:** the DaKS narrative includes a reference to two initial-hardness levels. The deposited CSV contains 400, 500, and 600 HV30. The modeling contract follows these three measured levels and preserves the source file unchanged.

## Raw format and column mapping

The UTF-8 raw CSV is semicolon-separated and has three header rows:

1. descriptive measurement labels;
2. variable symbols; and
3. measurement units.

Data begin on line 4. The processed CSV files are comma-separated with one English column-name row. Do not interpret the two supplementary header rows as observations.

| Raw position | Raw symbol or field | Unified column | Role | Unit | Observed levels or range |
|---:|---|---|---|---|---|
| 1 | Specimen | `specimen_id` | Physical-specimen grouping key | — | 27 identifiers, preserved as strings |
| 2 | Section | `section_id` | Section identifier; excluded feature | — | 1, 2, 3 |
| 3 | `HV_init` | `HV_init_HV30` | Measured predictor | HV30 | 400, 500, 600 |
| 4 | `v_c` | `cutting_speed_m_min` | Measured predictor | m/min | 100, 175, 250 |
| 5 | `f` | `feed_mm_rev` | Measured predictor | mm/rev | 0.05, 0.25, 0.50 |
| 6 | `a_p` | `depth_of_cut_mm` | Measured predictor | mm | 0.05, 0.25, 0.50 |
| 7 | `HV` | `post_process_hardness_HV30` | Target | HV30 | 480–639 |
| 8 | `Ra` | `surface_roughness_Ra_um` | Target | µm | 0.122–3.614 |
| 9 | `Rz` | `surface_roughness_Rz_um` | Measured outcome; excluded feature | µm | 0.797–14.393 |

The raw feed header uses `mm`; the project represents the turning feed as `mm/rev`. The Vickers headers use `kgf/mm²`, and the project retains the HV30 designation. No hardness conversion to Brinell (`HB`) is applied. Specimen identifiers such as `03-008` are labels, not numeric measurements.

Target summaries calculated from the 81 included observations are:

| Target | Mean | Sample SD (`ddof=1`) | Minimum | Maximum |
|---|---:|---:|---:|---:|
| `Ra` (µm) | 1.050877 | 0.852611 | 0.122 | 3.614 |
| Post-process hardness (HV30) | 539.802469 | 45.624944 | 480 | 639 |

The full feature and target contracts are in [`unified/feature_dictionary.csv`](unified/feature_dictionary.csv) and [`unified/target_definition.csv`](unified/target_definition.csv).

## Deterministic derived predictors

Notebook 02 computes three process proxies from the measured inputs. They use no target values and introduce no additional experimental measurements.

| Modeling column | Formula | Output unit |
|---|---|---|
| `uncut_chip_section_mm2` | `f × a_p` | mm² |
| `material_removal_proxy_mm3_min` | `1000 × v_c × f × a_p` | mm³/min |
| `theoretical_roughness_Ra_um` | `1000 × f² / (32 × r_e)`, with `r_e = 0.8 mm` | µm |

Here, `f` and `a_p` are in millimetres and `v_c` is in metres per minute. The factor 1000 converts units. The fixed corner radius is experimental metadata, not a varying predictor. The theoretical roughness is a kinematic proxy, not measured `Ra`. These derived columns are deterministic and are not statistically independent of their source factors.

The four measured and three derived predictor columns are available before response measurement. Neither measured target nor `Rz` may be used as an inference-time input. `specimen_id` supplies grouping metadata to the line-profile implementation without encoding the identifier as a learned feature.

## File inventory and generation

| File | Records or definitions | Purpose | Generated by |
|---|---:|---|---|
| [`raw/hardness_roughness_hard_turning.csv`](raw/hardness_roughness_hard_turning.csv) | 81, after three header rows | Unmodified source measurements | Official DaKS deposit |
| [`unified/unified_dataset.csv`](unified/unified_dataset.csv) | 81 | English names; retains `Rz` and source identifiers | Notebook 01 |
| [`unified/modeling_dataset.csv`](unified/modeling_dataset.csv) | 81 | Predictors, targets, derived features, stable row IDs, outer folds | Notebook 02 |
| [`unified/split_assignments.csv`](unified/split_assignments.csv) | 81 | Immutable specimen-group outer-fold assignments | Notebook 02 |
| [`unified/feature_dictionary.csv`](unified/feature_dictionary.csv) | 13 | Roles, units, and inference availability | Notebook 02 |
| [`unified/target_definition.csv`](unified/target_definition.csv) | 2 | Two modeled response variables | Notebook 02 |
| [`unified/preprocessing_summary.csv`](unified/preprocessing_summary.csv) | 9 | Frozen design and preprocessing decisions | Notebook 02 |

The modeling table omits `Rz`, adds `sample_id`, three derived columns, `outer_fold`, and the label `split = nested_group_cv`. `outer_fold` is a validation assignment, not a model predictor or a separate external test set. No rows are imputed, synthetically expanded, or removed from the modeling table.

## Minimal loading example

For modeling and inspection, load the documented English-column table:

```python
from pathlib import Path
import pandas as pd

root = Path.cwd()  # repository root
data = pd.read_csv(
    root / "dataset/unified/modeling_dataset.csv",
    dtype={"specimen_id": "string"},
)
assert len(data) == 81
assert data["specimen_id"].nunique() == 27
```

To parse the raw measurements directly, skip all three header rows and supply unique names:

```python
columns = [
    "specimen_id", "section_id", "HV_init_HV30", "cutting_speed_m_min",
    "feed_mm_rev", "depth_of_cut_mm", "post_process_hardness_HV30",
    "surface_roughness_Ra_um", "surface_roughness_Rz_um",
]
raw = pd.read_csv(
    root / "dataset/raw/hardness_roughness_hard_turning.csv",
    sep=";", skiprows=3, header=None, names=columns,
    dtype={"specimen_id": "string"},
)
assert raw.shape == (81, 9)
```

## Integrity, validation, and limitations

The unchanged source CSV has SHA-256:

```text
04dbebf049fc94e6208688580e2376c7b4c2ee92f69dd37a2ab3126572a706b7
```

Notebook 01 checks this value before parsing. The repository-wide [`SHA256SUMS`](../SHA256SUMS) also covers the processed contracts and saved evidence. Verify the snapshot from the repository root with `shasum -a 256 -c SHA256SUMS` before rerunning notebooks.

Validation uses nine specimen-group outer folds and four specimen-group inner folds. Scaling and model selection belong within training partitions. The final comparison uses 81 OOF predictions per model and target; bootstrap resampling treats the 27 specimens as clusters.

The design contains one section per factorial combination and one specimen per initial-hardness/feed/speed combination. It provides no independent replication of those combinations and no external dataset. Results describe prediction within the observed 51CrV4 experimental domain; they do not establish transfer to other alloys, tools, or machining ranges.

## Citation and reuse

Wittich, F., Wegener, T., Liehr, A., Zinn, W., Niendorf, T., & Kroll, A. (2025). *Surface layer state after hard turning of 51CrV4* [Data set]. DaKS, University of Kassel. [https://doi.org/10.48662/daks-69](https://doi.org/10.48662/daks-69).

The [main README](../README.md#recommended-dataset-citation) supplies BibTeX. Retain the source attribution and CC BY-SA 4.0 terms when redistributing the measurements. The modeling tables are project-derived representations of those measurements; the prediction and statistical artifacts are results of the notebook workflow, not additional official DaKS data.
