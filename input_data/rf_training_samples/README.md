# RF Training Samples

This folder contains the training samples used for the RF-based MOA guidance model.

## Files

- `grasp_training_rows.json`: training rows for grasping/removal operation-parameter guidance.
- `unscrew_training_rows.json`: training rows for unscrewing operation-parameter guidance.
- `training_summary.json`: summary of the RF training setup and dataset size.

The trained `.pkl` model files are intentionally not included because they are large. The released JSON files contain the training samples needed to inspect and reproduce the RF-guidance data construction.
