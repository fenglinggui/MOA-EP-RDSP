# MOA for Execution-Parameterized Robotic Disassembly Sequence Planning

This repository provides the input data and experimental results used in the paper:

**Meta-operation-assisted optimization for execution-parameterized robotic disassembly sequence planning**

The repository contains data only. It does not include implementation code for the compared algorithms.

## Contents

- `input_data/product_instances/`
  - Fifteen generated product instances represented by executable IK candidate libraries.
  - Candidate-count and validation summaries.
- `input_data/moa_rf_training_samples/`
  - RF training samples used by the meta-operation-assisted (MOA) framework.
  - Unscrewing and grasping-removal training rows.
- `results/experiment1_moa_vs_moea_same_hv/`
  - Experiment 1 results comparing four MOEAs with their MOA-assisted variants under the same HV target.
  - HV boxes, HV targets, summary workbook, processed JSON, and convergence figure.
- `results/experiment2_moa_vs_frameworks_same_time/`
  - Experiment 2 results comparing MOA with CMOEMT, TriP, and ARACMO under the same runtime budget.
  - HV/IGD summary workbook, processed JSON, and Pareto-front figure.
- `results/combined/`
  - Combined workbook for the two formal experiments.

## Naming

The paper uses **MOA** as the method abbreviation for the proposed meta-operation-assisted optimization framework.
Older local experiment folders may contain legacy names, but the released files are renamed according to the paper.

## Notes

- Experiment 1 and Experiment 2 use different HV normalization bounds because they answer different experimental questions.
- Experiment 1 evaluates the time needed to reach comparable HV levels.
- Experiment 2 evaluates final HV and IGD under equal runtime budgets.
