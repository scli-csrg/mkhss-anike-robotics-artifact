# SwarmGate Robotics Artifact

This repository contains the reproducibility package for the manuscript:

**SwarmGate: Privacy-Preserving Attribute-Gated Key Establishment for Robotic Fleets**

The package is intentionally lightweight. It contains the datasets used for the paper's evaluation tables and figures, standard-library Python scripts to validate and visualize those results, and a reference protocol scaffold for the SwarmGate key-management flow described in the R4 manuscript.

## Contents

- `data/`: CSV datasets extracted from the manuscript tables and text.
- `scripts/generate_figures.py`: standard-library SVG plotting code.
- `scripts/validate_results.py`: consistency checks for speedups and derived communication values.
- `src/swarmgate_protocol.py`: a non-cryptographic reference scaffold for the SwarmGate lifecycle.
- `figures/`: generated SVG figures.

## Quick Start

```bash
python3 scripts/validate_results.py
python3 scripts/generate_figures.py
```

The scripts use only the Python standard library. No external plotting packages are required.

## Reproducibility Scope

This artifact reproduces the paper's reported tables and figures from the supplied numeric data. It does not implement production MKHSS, Paillier-ElGamal, NIKE, or fuzzy PAKE. The file `src/swarmgate_protocol.py` is a readable protocol scaffold that documents attribute reports, public encodings, session identifiers, policy versions, epochs, revocation checks, and predicate-gated key derivation. It should not be used as a cryptographic library.

## Dataset Provenance

The values in `data/` are transcribed from the R4 manuscript. Communication baselines in `data/swarmgate_summary.csv` are derived from the reported optimized encoding sizes and the stated `3.0x` communication reduction. The transfer times in `data/network_budget.csv` are analytic lower bounds computed from public-encoding size and nominal link rate; they are not robot-network measurements.

## Regenerated Outputs

Running `scripts/generate_figures.py` writes:

- `figures/mkhss_core_runtime.svg`
- `figures/mkhss_core_speedup.svg`
- `figures/swarmgate_latency.svg`
- `figures/swarmgate_communication.svg`
- `figures/network_budget.svg`

Running `scripts/validate_results.py` writes:

- `validation_report.md`

## Suggested Citation

Please replace the placeholder author metadata before public release.
