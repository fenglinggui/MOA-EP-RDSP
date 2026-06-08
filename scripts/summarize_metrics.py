#!/usr/bin/env python3
"""Summarize per-run metric CSV files into mean/std tables."""
from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev


def to_float(value):
    try:
        return float(value)
    except Exception:
        return None


def fmt_mean_std(vals):
    vals = [v for v in vals if v is not None and math.isfinite(v)]
    if not vals:
        return ""
    if len(vals) == 1:
        return f"{vals[0]:.6g} (0)"
    return f"{mean(vals):.6g} ({stdev(vals):.6g})"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--metrics", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    rows = list(csv.DictReader(args.metrics.open("r", encoding="utf-8-sig")))
    groups = defaultdict(lambda: {"hv": [], "igd": [], "elapsed_s": []})
    for row in rows:
        key = (row.get("experiment"), row.get("product"), row.get("method"))
        for metric in ["hv", "igd", "elapsed_s"]:
            groups[key][metric].append(to_float(row.get(metric)))

    out_rows = []
    for (exp, product, method), vals in sorted(groups.items()):
        out_rows.append({
            "experiment": exp,
            "product": product,
            "method": method,
            "hv_mean_std": fmt_mean_std(vals["hv"]),
            "igd_mean_std": fmt_mean_std(vals["igd"]),
            "elapsed_s_mean_std": fmt_mean_std(vals["elapsed_s"]),
            "runs": len(vals["hv"]),
        })

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        writer.writeheader()
        writer.writerows(out_rows)
    print(f"Wrote {len(out_rows)} rows to {args.out}")


if __name__ == "__main__":
    main()
