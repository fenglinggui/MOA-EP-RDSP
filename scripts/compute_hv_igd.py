#!/usr/bin/env python3
"""Recompute 2D minimization HV and IGD from released Pareto-front JSON files.

The script is intentionally self-contained and uses only the Python standard library.
It supports the raw Pareto-front files released in this repository.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from statistics import mean, pstdev


PRODUCT_HV_BOXES = {
    "product1": {"ideal_time": 65.0, "ref_time": 150.0, "ideal_energy": 1000.0, "ref_energy": 1600.0},
    "product2": {"ideal_time": 95.0, "ref_time": 250.0, "ideal_energy": 1450.0, "ref_energy": 2200.0},
    "product3": {"ideal_time": 50.0, "ref_time": 120.0, "ideal_energy": 850.0, "ref_energy": 1700.0},
    "product4": {"ideal_time": 80.0, "ref_time": 250.0, "ideal_energy": 1250.0, "ref_energy": 1800.0},
    "product5": {"ideal_time": 105.0, "ref_time": 200.0, "ideal_energy": 1800.0, "ref_energy": 2300.0},
    "product6": {"ideal_time": 180.0, "ref_time": 440.0, "ideal_energy": 2600.0, "ref_energy": 4000.0},
    "product7": {"ideal_time": 140.0, "ref_time": 300.0, "ideal_energy": 2200.0, "ref_energy": 3500.0},
    "product8": {"ideal_time": 160.0, "ref_time": 350.0, "ideal_energy": 2550.0, "ref_energy": 3500.0},
    "product9": {"ideal_time": 165.0, "ref_time": 420.0, "ideal_energy": 2800.0, "ref_energy": 4200.0},
    "product10": {"ideal_time": 170.0, "ref_time": 300.0, "ideal_energy": 2700.0, "ref_energy": 3300.0},
    "product11": {"ideal_time": 195.0, "ref_time": 450.0, "ideal_energy": 2850.0, "ref_energy": 4300.0},
    "product12": {"ideal_time": 190.0, "ref_time": 320.0, "ideal_energy": 2700.0, "ref_energy": 3700.0},
    "product13": {"ideal_time": 245.0, "ref_time": 530.0, "ideal_energy": 3700.0, "ref_energy": 5500.0},
    "product14": {"ideal_time": 410.0, "ref_time": 650.0, "ideal_energy": 6400.0, "ref_energy": 8000.0},
    "product15": {"ideal_time": 450.0, "ref_time": 900.0, "ideal_energy": 7500.0, "ref_energy": 9000.0},
}


def method_aliases(method):
    aliases = {method}
    label_to_internal = {
        "RVEA": "pure_rvea",
        "MOA-RVEA": "moa_rvea",
        "SMSEMOA": "pure_smsemoa",
        "MOA-SMSEMOA": "moa_smsemoa",
        "CTAEA": "pure_ctaea",
        "MOA-CTAEA": "moa_ctaea",
        "NSGAII": "pure_nsgaii",
        "MOA-NSGAII": "moa_nsgaii",
    }
    internal_to_label = {v: k for k, v in label_to_internal.items()}
    if method in label_to_internal:
        aliases.add(label_to_internal[method])
    if method in internal_to_label:
        aliases.add(internal_to_label[method])
    if method == "MOA(ours)":
        aliases.add("MOA-NSGAII")
    if method == "MOA-NSGAII":
        aliases.add("MOA(ours)")
    return aliases


def product_hv_box(product):
    box = PRODUCT_HV_BOXES.get(product)
    if not box:
        return None
    return (
        [float(box["ideal_time"]), float(box["ideal_energy"])],
        [float(box["ref_time"]), float(box["ref_energy"])],
    )


def load_json(path: Path):
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def objectives_from_point(point):
    if isinstance(point, dict):
        if "objectives" in point and len(point["objectives"]) >= 2:
            return [float(point["objectives"][0]), float(point["objectives"][1])]
        if "F" in point and len(point["F"]) >= 2:
            return [float(point["F"][0]), float(point["F"][1])]
        if "time" in point and "energy" in point:
            return [float(point["time"]), float(point["energy"])]
    if isinstance(point, (list, tuple)) and len(point) >= 2:
        return [float(point[0]), float(point[1])]
    return None


def front_objectives(record):
    pts = []
    for point in record.get("pareto_front", []) or []:
        obj = objectives_from_point(point)
        if obj is not None and all(math.isfinite(v) for v in obj):
            pts.append(obj)
    return pts


def nondominated(points):
    unique = sorted(set((float(x), float(y)) for x, y in points))
    keep = []
    for i, p in enumerate(unique):
        dominated = False
        for j, q in enumerate(unique):
            if i == j:
                continue
            if q[0] <= p[0] and q[1] <= p[1] and (q[0] < p[0] or q[1] < p[1]):
                dominated = True
                break
        if not dominated:
            keep.append([p[0], p[1]])
    return keep


def nondominated_keep_duplicates(points):
    """Match the formal experiment script: keep duplicate nondominated points."""
    pts = [[float(x), float(y)] for x, y in points]
    keep = []
    for p in pts:
        dominated = False
        for q in pts:
            if q[0] <= p[0] and q[1] <= p[1] and (q[0] < p[0] or q[1] < p[1]):
                dominated = True
                break
        if not dominated:
            keep.append(p)
    return keep


def normalize(points, ideal, ref):
    out = []
    dx = ref[0] - ideal[0]
    dy = ref[1] - ideal[1]
    if dx <= 0 or dy <= 0:
        return out
    for x, y in points:
        out.append([(x - ideal[0]) / dx, (y - ideal[1]) / dy])
    return out


def hypervolume_2d_min(points, ref=(1.0, 1.0)):
    """2D dominated hypervolume for minimization after normalization."""
    pts = nondominated([p for p in points if 0.0 < p[0] < ref[0] and 0.0 < p[1] < ref[1]])
    if not pts:
        return 0.0
    pts = sorted(pts, key=lambda p: p[0])
    hv = 0.0
    prev_y = ref[1]
    for x, y in pts:
        if y < prev_y:
            hv += max(ref[0] - x, 0.0) * max(prev_y - y, 0.0)
            prev_y = y
    return hv


def euclidean(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def igd(points, reference_points):
    if not points or not reference_points:
        return float("nan")
    return mean(min(euclidean(r, p) for p in points) for r in reference_points)


def grouped_reference_front(records):
    by_product = {}
    for rec in records:
        by_product.setdefault(rec["product"], []).extend(front_objectives(rec))
    return {prod: nondominated(points) for prod, points in by_product.items()}


def grouped_reference_front_normalized(records, box_by_product):
    """Build IGD references using the same duplicate-preserving rule as the formal scripts."""
    by_product = {}
    for rec in records:
        product = rec["product"]
        ideal, ref = box_by_product(product)
        if ideal is None or ref is None:
            continue
        by_product.setdefault(product, []).extend(normalize(front_objectives(rec), ideal, ref))
    return {prod: nondominated_keep_duplicates(points) for prod, points in by_product.items()}


def infer_box(record, all_product_points=None):
    ideal = record.get("ideal_point")
    ref = record.get("ref_point")
    if ideal and ref:
        return [float(ideal[0]), float(ideal[1])], [float(ref[0]), float(ref[1])]
    points = all_product_points or front_objectives(record)
    if not points:
        return [0.0, 0.0], [1.0, 1.0]
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return [min(xs), min(ys)], [max(xs), max(ys)]


def default_raw_path(repo: Path, experiment: str) -> Path:
    if experiment == "exp1":
        return repo / "results" / "experiment1_moa_vs_moea_same_hv" / "raw_pareto_fronts" / "experiment1_per_run_pareto_fronts.json"
    if experiment == "exp2":
        return repo / "results" / "experiment2_moa_vs_frameworks_same_time" / "raw_pareto_fronts" / "experiment2_per_run_pareto_fronts.json"
    raise ValueError(experiment)


def default_summary_path(repo: Path, experiment: str) -> Path | None:
    if experiment == "exp1":
        return repo / "results" / "experiment1_moa_vs_moea_same_hv" / "summaries" / "experiment1_moa_vs_moea_same_hv_summary.json"
    if experiment == "exp2":
        return repo / "results" / "experiment2_moa_vs_frameworks_same_time" / "summaries" / "experiment2_moa_vs_frameworks_same_time_summary.json"
    return None


def load_summary_records(path: Path | None):
    if path is None or not path.exists():
        return {}, {}, {}
    data = load_json(path)
    run_boxes = {}
    run_metrics = {}
    product_boxes = {}
    for rec in data.get("records", []) if isinstance(data, dict) else []:
        methods = set(method_aliases(rec.get("method")))
        if rec.get("method_label"):
            methods.update(method_aliases(rec.get("method_label")))
        keys = [(method, rec.get("product"), rec.get("run_id")) for method in methods]
        if rec.get("hv_ideal_point") and rec.get("hv_ref_point"):
            box = ([float(x) for x in rec["hv_ideal_point"]], [float(x) for x in rec["hv_ref_point"]])
            for key in keys:
                run_boxes[key] = box
            product_boxes[rec.get("product")] = box
        for key in keys:
            run_metrics[key] = rec
    for product, box in (data.get("hv_boxes", {}) if isinstance(data, dict) else {}).items():
        if isinstance(box, dict) and box.get("ideal") and box.get("ref"):
            product_boxes[product] = ([float(x) for x in box["ideal"]], [float(x) for x in box["ref"]])
    return run_boxes, product_boxes, run_metrics


def load_exp1_hv_boxes(repo: Path):
    path = repo / "results" / "experiment1_moa_vs_moea_same_hv" / "summaries" / "exp1_hv_boxes_all_algorithms_minmax_ref110.json"
    if not path.exists():
        return {}
    data = load_json(path)
    boxes = {}
    for product, box in data.items():
        if not isinstance(box, dict):
            continue
        boxes[product] = (
            [float(box["ideal_time"]), float(box["ideal_energy"])],
            [float(box["ref_time"]), float(box["ref_energy"])],
        )
    return boxes


def fill_missing_run_ids(records):
    """Released exp1 raw files may contain repeated run_id=0; recover run order by group."""
    counts = {}
    seen = {}
    for rec in records:
        key = (rec.get("method"), rec.get("product"))
        counts[key] = counts.get(key, 0) + 1
    for rec in records:
        key = (rec.get("method"), rec.get("product"))
        if counts.get(key, 0) <= 1:
            continue
        current = rec.get("run_id")
        if current not in (None, "", 0, "0"):
            continue
        idx = seen.get(key, 0)
        rec["run_id"] = idx
        seen[key] = idx + 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--experiment", choices=["exp1", "exp2"], required=True)
    ap.add_argument("--raw", type=Path, default=None, help="Path to per-run raw Pareto-front JSON.")
    ap.add_argument("--summary", type=Path, default=None, help="Optional released summary JSON for official HV boxes.")
    ap.add_argument("--out", type=Path, required=True, help="Output CSV path.")
    args = ap.parse_args()

    repo = Path(__file__).resolve().parents[1]
    raw_path = args.raw or default_raw_path(repo, args.experiment)
    summary_path = args.summary or default_summary_path(repo, args.experiment)
    records = load_json(raw_path)
    fill_missing_run_ids(records)
    run_boxes, product_boxes, run_metrics = load_summary_records(summary_path)
    if args.experiment == "exp1":
        product_boxes.update(load_exp1_hv_boxes(repo))
    ref_fronts = grouped_reference_front(records)
    igd_refs = {}
    if args.experiment == "exp2":
        igd_refs = grouped_reference_front_normalized(records, product_hv_box)
    all_by_product = {}
    for rec in records:
        all_by_product.setdefault(rec["product"], []).extend(front_objectives(rec))

    rows = []
    for rec in records:
        points = front_objectives(rec)
        product = rec["product"]
        key = (rec.get("method"), product, rec.get("run_id"))
        if key in run_boxes:
            hv_ideal, hv_ref = run_boxes[key]
        elif product in product_boxes:
            hv_ideal, hv_ref = product_boxes[product]
        else:
            hv_ideal, hv_ref = infer_box(rec, all_by_product.get(product))
        igd_ideal, igd_ref = product_hv_box(product) or (hv_ideal, hv_ref)

        norm_points_hv = normalize(points, hv_ideal, hv_ref)
        norm_points_igd = normalize(points, igd_ideal, igd_ref)
        if args.experiment == "exp2" and product in igd_refs:
            norm_ref_igd = igd_refs[product]
        else:
            norm_ref_igd = normalize(ref_fronts.get(product, []), igd_ideal, igd_ref)
        official = run_metrics.get(key, {})
        rows.append({
            "experiment": args.experiment,
            "method": rec.get("method"),
            "product": product,
            "run_id": rec.get("run_id"),
            "seed": rec.get("seed"),
            "n_pareto": len(points),
            "hv": hypervolume_2d_min(norm_points_hv),
            "igd": igd(norm_points_igd, norm_ref_igd),
            "official_hv": official.get("final_hv", ""),
            "official_igd": official.get("igd", ""),
            "elapsed_s": rec.get("elapsed_s"),
            "n_gen": rec.get("n_gen"),
            "stop_reason": rec.get("stop_reason"),
        })

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {args.out}")


if __name__ == "__main__":
    main()
