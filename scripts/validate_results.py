#!/usr/bin/env python3
"""Validate reported SwarmGate result tables.

The checks intentionally avoid third-party dependencies so the artifact can run
on a clean Python installation.
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REPORT = ROOT / "validation_report.md"


def read_csv(name: str):
    with (DATA / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def close(a: float, b: float, tolerance: float) -> bool:
    return abs(a - b) <= tolerance


def validate_speedups(rows, ours_key="ours_ms", baseline_key="baseline_ms", label_key="procedure"):
    findings = []
    for row in rows:
        ours = float(row[ours_key])
        baseline = float(row[baseline_key])
        reported = float(row["reported_speedup"])
        computed = baseline / ours
        ok = close(computed, reported, max(0.15, reported * 0.04))
        findings.append((row[label_key], computed, reported, ok))
    return findings


def main() -> int:
    lines = ["# Validation Report", ""]
    exit_code = 0

    core = read_csv("mkhss_core_performance.csv")
    lines.append("## Core MKHSS Speedups")
    for label, computed, reported, ok in validate_speedups(core):
        status = "OK" if ok else "CHECK"
        if not ok:
            exit_code = 1
        lines.append(f"- {status}: {label}: computed {computed:.2f}x, reported {reported:.2f}x")
    lines.append("")

    fuzzy = read_csv("fuzzy_pake.csv")
    lines.append("## Fuzzy PAKE Speedups")
    for label, computed, reported, ok in validate_speedups(fuzzy):
        status = "OK" if ok else "CHECK"
        if not ok:
            exit_code = 1
        lines.append(f"- {status}: {label}: computed {computed:.2f}x, reported {reported:.2f}x")
    lines.append("")

    geolocation = read_csv("geolocation_swarmgate.csv")
    lines.append("## Geolocation Implied Baselines")
    for row in geolocation:
        ours = float(row["ours_ms"])
        speedup = float(row["reported_speedup"])
        implied = float(row["baseline_ms_implied"])
        computed = ours * speedup
        ok = close(computed, implied, 0.02)
        status = "OK" if ok else "CHECK"
        if not ok:
            exit_code = 1
        lines.append(f"- {status}: {row['procedure']}: implied baseline {implied:.2f} ms")
    lines.append("")

    summary = read_csv("swarmgate_summary.csv")
    lines.append("## Communication Baselines")
    for row in summary:
        ours = float(row["ours_encoding_kb"])
        baseline = float(row["baseline_encoding_kb"])
        computed = ours * 3.0
        ok = close(computed, baseline, 0.05)
        status = "OK" if ok else "CHECK"
        if not ok:
            exit_code = 1
        lines.append(f"- {status}: {row['policy']}: {ours:.1f} kB -> {baseline:.1f} kB baseline")
    lines.append("")

    network = read_csv("network_budget.csv")
    lines.append("## Network-Budget Transfer Times")
    for row in network:
        encoding_kb = float(row["encoding_kb"])
        link_kbps = float(row["link_kbps"])
        reported = float(row["transfer_s"])
        computed = encoding_kb * 8.0 / link_kbps
        ok = close(computed, reported, 0.0005)
        status = "OK" if ok else "CHECK"
        if not ok:
            exit_code = 1
        lines.append(
            f"- {status}: {row['policy']} over {row['link_label']}: "
            f"computed {computed:.5f} s, reported {reported:.5f} s"
        )
    lines.append("")

    expected_states = {"Enroll", "Encode", "Fetch", "Derive", "Refresh"}
    states = {row["state"] for row in read_csv("swarmgate_state_machine.csv")}
    missing = sorted(expected_states - states)
    extra = sorted(states - expected_states)
    lines.append("## SwarmGate State Machine")
    if missing or extra:
        exit_code = 1
        if missing:
            lines.append(f"- CHECK: missing states: {', '.join(missing)}")
        if extra:
            lines.append(f"- CHECK: unexpected states: {', '.join(extra)}")
    else:
        lines.append("- OK: required lifecycle states are present")
    lines.append("")

    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {REPORT}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
