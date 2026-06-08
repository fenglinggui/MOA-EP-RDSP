# Data Processing Scripts

This directory contains lightweight scripts for inspecting the released data and recomputing metrics from the released raw Pareto-front files.

The scripts are data-processing utilities only. They do not contain the implementation code of the compared optimization algorithms.

## Scripts

- `compute_hv_igd.py`: recompute per-run HV/IGD from released raw Pareto fronts.
- `summarize_metrics.py`: summarize per-run metric CSV files into mean/std tables.
- `inspect_product_instances.py`: inspect the released product-instance definitions.

## Metric Notes

- Experiment 1 HV is recomputed with the released `exp1_hv_boxes_all_algorithms_minmax_ref110.json` box file.
- Experiment 2 HV is recomputed with each product's four-algorithm Pareto-front min/max box expanded by 10% on both sides.
- Experiment 2 IGD uses the per-product reference front obtained by merging CMOEMT, TriP, ARACMO, and MOA-NSGAII final fronts and applying the same duplicate-preserving nondominated filtering as the formal experiment script.

## Example

From the repository root:

```powershell
python scripts/compute_hv_igd.py --experiment exp2 --out outputs/exp2_recomputed_metrics.csv
python scripts/summarize_metrics.py --metrics outputs/exp2_recomputed_metrics.csv --out outputs/exp2_recomputed_summary.csv
python scripts/inspect_product_instances.py --out outputs/product_instance_overview.csv
```
