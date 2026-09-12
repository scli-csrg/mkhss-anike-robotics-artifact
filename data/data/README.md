# Dataset Notes

The CSV files in this folder are the numeric data used by the R4 manuscript figures, tables, and validation checks.

- `mkhss_core_performance.csv`: core MKHSS procedure timing and speedup values for `lg(B)=1`.
- `geolocation_swarmgate.csv`: procedure-level geolocation SwarmGate timing.
- `fuzzy_pake.csv`: procedure-level fuzzy PAKE timing.
- `swarmgate_summary.csv`: end-to-end SwarmGate latency and public-encoding communication values.
- `key_exchange_comparison.csv`: qualitative comparison table from the deployment discussion.
- `network_budget.csv`: analytic lower-bound transfer times for public encodings over nominal link rates.
- `swarmgate_state_machine.csv`: lifecycle states and fail-closed checks from the R4 key-management section.

All times are reported in milliseconds or seconds as specified in each header. Derived fields are labeled explicitly. Network-budget rows are analytic estimates and do not include packet headers, retransmission, middleware scheduling, contention, or discovery traffic.
