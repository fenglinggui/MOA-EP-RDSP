#!/usr/bin/env python3
"""Inspect released product-instance definitions and export a compact CSV overview."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--instances", type=Path, default=None)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    repo = Path(__file__).resolve().parents[1]
    instances = args.instances or repo / "input_data" / "product_instances" / "product_instances.json"
    data = json.loads(instances.read_text(encoding="utf-8-sig"))

    rows = []
    for product, rec in sorted(data.items(), key=lambda kv: int(kv[0].replace("product", ""))):
        deps = rec.get("dependencies", {})
        n_edges = sum(len(v) for v in deps.values())
        rows.append({
            "product": product,
            "component_products": ";".join(rec.get("component_products", [])),
            "n_screws": rec.get("n_screws", len(rec.get("screws", []))),
            "n_tables": rec.get("n_tables", len(rec.get("tables", []))),
            "n_operations": len(rec.get("screws", [])) + len(rec.get("tables", [])),
            "n_dependency_edges": n_edges,
        })

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {args.out}")


if __name__ == "__main__":
    main()
