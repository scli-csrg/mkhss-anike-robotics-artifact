#!/usr/bin/env python3
"""Generate SVG figures from the artifact CSV files using only stdlib Python."""

from __future__ import annotations

import csv
import math
from pathlib import Path
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
FIGURES = ROOT / "figures"

BLUE = "#0072B2"
ORANGE = "#E69F00"
GREEN = "#009E73"
GRAY = "#666666"
LIGHT = "#F2F2F2"
BLACK = "#222222"


def read_csv(name: str):
    with (DATA / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def text(x, y, body, size=12, anchor="middle", rotate=None, color=BLACK):
    transform = f' transform="rotate({rotate} {x} {y})"' if rotate else ""
    return (
        f'<text x="{x:.2f}" y="{y:.2f}" font-family="Arial, sans-serif" '
        f'font-size="{size}" fill="{color}" text-anchor="{anchor}"{transform}>'
        f"{escape(str(body))}</text>"
    )


def rect(x, y, w, h, fill, stroke="none"):
    return f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{fill}" stroke="{stroke}"/>'


def line(x1, y1, x2, y2, stroke=GRAY, width=1):
    return f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{stroke}" stroke-width="{width}"/>'


def write_svg(path: Path, width: int, height: int, body):
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        rect(0, 0, width, height, "white"),
        *body,
        "</svg>",
    ]
    path.write_text("\n".join(svg) + "\n", encoding="utf-8")


def grouped_bar_chart(path, title, categories, series, ylabel, log_scale=False, ymax=None):
    width, height = 920, 520
    left, right, top, bottom = 92, 32, 58, 108
    plot_w = width - left - right
    plot_h = height - top - bottom
    body = [text(width / 2, 30, title, size=18)]

    values = [v for _, vals, _ in series for v in vals]
    if log_scale:
        min_v = max(1.0, min(values))
        max_v = ymax or max(values) * 1.2
        log_min = math.log10(min_v)
        log_max = math.log10(max_v)

        def ymap(v):
            return top + plot_h - ((math.log10(max(v, min_v)) - log_min) / (log_max - log_min)) * plot_h

        ticks = [1, 3, 10, 30, 100, 300]
    else:
        min_v = 0.0
        max_v = ymax or max(values) * 1.18

        def ymap(v):
            return top + plot_h - ((v - min_v) / (max_v - min_v)) * plot_h

        step = max_v / 5
        ticks = [round(i * step, 2) for i in range(6)]

    body.append(line(left, top, left, top + plot_h, BLACK, 1.2))
    body.append(line(left, top + plot_h, left + plot_w, top + plot_h, BLACK, 1.2))

    for tick in ticks:
        if tick <= 0:
            continue
        y = ymap(tick)
        body.append(line(left, y, left + plot_w, y, "#D9D9D9", 1))
        label = f"{tick:g}"
        body.append(text(left - 10, y + 4, label, size=11, anchor="end"))

    n = len(categories)
    group_w = plot_w / n
    bar_gap = 4
    bar_w = min(26, (group_w - 22) / max(1, len(series)) - bar_gap)

    for i, cat in enumerate(categories):
        cx = left + i * group_w + group_w / 2
        body.append(text(cx, top + plot_h + 42, cat, size=11, rotate=-35))
        for j, (_, vals, color) in enumerate(series):
            x = cx - (len(series) * (bar_w + bar_gap)) / 2 + j * (bar_w + bar_gap)
            y = ymap(vals[i])
            h = top + plot_h - y
            body.append(rect(x, y, bar_w, h, color))
            if not log_scale:
                body.append(text(x + bar_w / 2, y - 5, f"{vals[i]:g}", size=10, color=color))

    legend_x = left + 10
    legend_y = top + 10
    for idx, (name, _, color) in enumerate(series):
        y = legend_y + idx * 20
        body.append(rect(legend_x, y - 10, 13, 13, color))
        body.append(text(legend_x + 20, y + 1, name, size=12, anchor="start"))

    body.append(text(24, top + plot_h / 2, ylabel, size=13, rotate=-90))
    write_svg(path, width, height, body)


def main() -> int:
    FIGURES.mkdir(exist_ok=True)

    core = read_csv("mkhss_core_performance.csv")
    core_labels = ["CRS", "KeyGen", "Share", "Init A", "Init B", "Sync S", "Sync R", "Mult", "Convert"]
    ours = [float(row["ours_ms"]) for row in core]
    baseline = [float(row["baseline_ms"]) for row in core]
    speedup = [float(row["reported_speedup"]) for row in core]

    grouped_bar_chart(
        FIGURES / "mkhss_core_runtime.svg",
        "Core MKHSS Backend Procedure Latency",
        core_labels,
        [("Optimized", ours, BLUE), ("Baseline", baseline, ORANGE)],
        "Time (ms, log scale)",
        log_scale=True,
        ymax=400,
    )
    grouped_bar_chart(
        FIGURES / "mkhss_core_speedup.svg",
        "Core MKHSS Procedure Speedup",
        core_labels,
        [("Speedup", speedup, GREEN)],
        "Speedup over baseline (x)",
        ymax=50,
    )

    summary = read_csv("swarmgate_summary.csv")
    policies = [row["policy"] for row in summary]
    laptop = [float(row["laptop_s"]) for row in summary]
    avx = [float(row["avx512_s"]) for row in summary]
    enc_ours = [float(row["ours_encoding_kb"]) for row in summary]
    enc_base = [float(row["baseline_encoding_kb"]) for row in summary]

    grouped_bar_chart(
        FIGURES / "swarmgate_latency.svg",
        "End-to-End SwarmGate Latency",
        policies,
        [("Laptop", laptop, BLUE), ("AVX512", avx, GREEN)],
        "End-to-end time (s)",
        ymax=8.5,
    )
    grouped_bar_chart(
        FIGURES / "swarmgate_communication.svg",
        "SwarmGate Public Encoding Communication",
        policies,
        [("Optimized", enc_ours, BLUE), ("Baseline", enc_base, ORANGE)],
        "Public encoding size (kB)",
        ymax=1800,
    )

    network = read_csv("network_budget.csv")
    network_policies = []
    link_labels = []
    by_link = {}
    for row in network:
        policy = row["policy"]
        link = row["link_label"]
        if policy not in network_policies:
            network_policies.append(policy)
        if link not in link_labels:
            link_labels.append(link)
        by_link.setdefault(link, {})[policy] = float(row["transfer_s"])

    colors = [BLUE, GREEN, ORANGE]
    network_series = []
    for i, link in enumerate(link_labels):
        vals = [by_link[link][policy] for policy in network_policies]
        network_series.append((link, vals, colors[i % len(colors)]))
    grouped_bar_chart(
        FIGURES / "network_budget.svg",
        "Public-Encoding Transfer Lower Bound",
        network_policies,
        network_series,
        "Transfer time (s)",
        ymax=40,
    )

    for path in sorted(FIGURES.glob("*.svg")):
        print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
