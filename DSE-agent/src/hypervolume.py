#!/usr/bin/env python3
"""Read-only, fixed-reference formal-population hypervolume and status."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path

SUPPORTED = {"latency_ns", "ii_ns", "ii_cycles", "lut", "ff", "bram_36k", "dsp", "uram", "power_w"}
RESOURCES = ("lut", "ff", "bram_36k", "dsp", "uram")
UNITS = {key: ("ns" if key.endswith("_ns") else "cycles" if key == "ii_cycles"
               else "W" if key == "power_w" else "BRAM_36K equivalents" if key == "bram_36k"
               else "count") for key in SUPPORTED}


def number(value, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    try:
        value = float(value)
    except OverflowError:
        return None
    if not math.isfinite(value) or value < 0 or (positive and value == 0):
        return None
    return value


def measured(metrics):
    values = {key: number(metrics.get(key)) for key in SUPPORTED}
    clock = number(metrics.get("clock_ns"), positive=True)
    for duration, cycle_keys in (("latency_ns", ("latency_cycles", "cosim_latency_cycles")),
                                 ("ii_ns", ("ii_cycles",))):
        cycles = next((number(metrics[key]) for key in cycle_keys
                       if number(metrics.get(key)) is not None), None)
        if values[duration] is None and metrics.get(duration) is None and clock is not None and cycles is not None:
            values[duration] = number(cycles * clock)
    values["clock_ns"] = clock
    for key in ("latency_cycles", "cp_post_impl_ns"):
        values[key] = number(metrics.get(key))
    wns = metrics.get("wns")
    values["wns"] = (float(wns) if isinstance(wns, (int, float)) and not isinstance(wns, bool)
                     and number(abs(wns)) is not None else None)
    # No guessed BRAM units, implicit II, clock defaults, or Fmax extrapolation.
    values["transactions_per_second"] = (1e9 / values["ii_ns"]
                                           if values["ii_ns"] is not None and values["ii_ns"] > 0 else None)
    return values


def config_check(config):
    if not isinstance(config, dict):
        return "No fixed hv_config is available"
    if config.get("algorithm") != "pymoo_exact_nd" or config.get("population") != "formal":
        return "Only explicitly configured pymoo_exact_nd on the formal population is supported"
    objectives = config.get("objectives")
    if (not isinstance(objectives, list) or not objectives
            or not all(isinstance(x, str) and x in SUPPORTED for x in objectives)
            or len(set(objectives)) != len(objectives)):
        return "Objectives must be a nonempty unique list of supported measured metrics"
    reference = config.get("reference_point")
    if not isinstance(reference, dict) or set(reference) != set(objectives):
        return "reference_point must match the objective keys exactly"
    if any(number(reference[key], positive=True) is None for key in objectives):
        return "Reference coordinates must be finite and positive"
    return None


def exact_backend():
    try:
        import numpy as np
        from pymoo.indicators.hv import HV
        version = importlib.metadata.version("pymoo")
    except ImportError as exc:
        raise ImportError("Optional NumPy/pymoo exact-HV backend is unavailable") from exc

    def calculate(points, reference):
        return float(HV(ref_point=np.asarray(reference, dtype=float))(
            np.asarray(points, dtype=float)))
    return calculate, {"pymoo": version, "numpy": np.__version__}


def evaluate(front, directive, backend_loader=exact_backend):
    result = {"status": "unavailable", "hypervolume": None,
              "hypervolume_normalized": None, "convergence_ready": False,
              "config_id": None, "algorithm": None, "points": [], "excluded": []}
    if not isinstance(front, list) or not isinstance(directive, dict):
        return {**result, "status": "invalid_state", "reason": "Expected a point array and a directive object"}
    result["num_points"] = len(front)
    benchmark, run_id = directive.get("benchmark"), directive.get("run_id")
    result.update(benchmark=benchmark, run_id=run_id)
    config = directive.get("hv_config")
    error = config_check(config)
    # Available point metrics are useful even when HV configuration/dependencies are missing.
    for index, point in enumerate(front):
        if isinstance(point, dict) and isinstance(point.get("metrics"), dict):
            result["points"].append({"id": point.get("id", f"index-{index}"),
                                     "metrics": measured(point["metrics"])})
        else:
            result["excluded"].append({"id": f"index-{index}", "reason": "Malformed point or metrics"})
    if error:
        return {**result, "reason": error}
    result.update(algorithm=config["algorithm"], population=config["population"],
                  objectives=config["objectives"], reference_point=config["reference_point"],
                  units={key: UNITS[key] for key in config["objectives"]})
    if not benchmark or not run_id:
        return {**result, "status": "invalid_state", "reason": "Missing benchmark/run identity"}
    objectives = config["objectives"]
    reference = [float(config["reference_point"][key]) for key in objectives]
    vectors, clocks = [], set()
    out_of_reference = []
    for index, point in enumerate(front):
        if not isinstance(point, dict) or not isinstance(point.get("metrics"), dict):
            continue
        identity = point.get("id", f"index-{index}")
        metrics = point["metrics"]
        values = measured(metrics)
        validation = point.get("validation", {})
        reason = None
        if point.get("benchmark") != benchmark or point.get("run_id") != run_id:
            reason = "Benchmark/run mismatch"
        elif (point.get("status") != "success" or not isinstance(validation, dict)
              or validation.get("formal_eligible") is not True):
            reason = "No Main-verified formal acceptance"
        elif number(metrics.get("wns")) is None:
            reason = "Missing/negative/nonfinite routed WNS"
        elif any(number(metrics.get(key)) is None for key in RESOURCES):
            reason = "Incomplete routed resource evidence"
        elif any(values[key] is None for key in objectives):
            reason = "Missing/invalid objective metric"
        elif "ii_cycles" in objectives and values["clock_ns"] is None:
            reason = "ii_cycles comparison requires a known common clock"
        if reason:
            result["excluded"].append({"id": identity, "reason": reason})
            continue
        vector = [values[key] for key in objectives]
        if any(x >= bound for x, bound in zip(vector, reference)):
            out_of_reference.append(identity)
        vectors.append(vector)
        if values["clock_ns"] is not None:
            clocks.add(values["clock_ns"])
    result["num_eligible_points"] = len(vectors)
    if out_of_reference:
        return {**result, "status": "invalid_reference", "out_of_reference": out_of_reference,
                "reason": "Reference point is fixed; start a new comparison series to change it"}
    if "ii_cycles" in objectives and len(clocks) > 1:
        return {**result, "status": "invalid_units",
                "reason": "Use ii_ns for cross-clock comparisons"}
    if not vectors:
        return {**result, "status": "empty" if not front else "no_eligible_points"}
    try:
        calculate, versions = backend_loader()
        definition = {"benchmark": benchmark, "run_id": run_id,
                      "hv_config": config, "backend_versions": versions,
                      "units": result["units"],
                      "cycle_clock_ns": next(iter(clocks)) if "ii_cycles" in objectives else None}
        config_id = hashlib.sha256(json.dumps(definition, sort_keys=True,
                                             separators=(",", ":"), allow_nan=False).encode()).hexdigest()
        result.update(config_id=config_id, backend_versions=versions)
        value = calculate(vectors, reference)
        if number(value) is None:
            raise ValueError("Backend returned an invalid hypervolume")
        maximum = math.prod(reference)
        if not math.isfinite(maximum) or maximum <= 0:
            raise ValueError("Reference volume is outside the supported finite numeric range")
        if value > maximum * (1 + 1e-12):
            raise ValueError("Backend returned hypervolume larger than the reference volume")
        result.update(status="partial" if result["excluded"] else "ok",
                      hypervolume=value, hypervolume_normalized=value / maximum,
                      convergence_ready=not result["excluded"])
    except ImportError as exc:
        result.update(status="unavailable", reason=str(exc))
    except (ValueError, TypeError, RuntimeError, OverflowError) as exc:
        result.update(status="backend_error", reason=str(exc))
    return result


def convergence(history, consecutive=3, threshold=0.02):
    """A helper for until-converged mode, never a fixed-round early-stop rule."""
    if len(history) < consecutive + 1:
        return False
    window = history[-consecutive - 1:]
    identity = window[0].get("config_id")
    if not identity:
        return False
    for item in window:
        if (not item.get("convergence_ready") or item.get("status") != "ok"
                or item.get("config_id") != identity
                or number(item.get("hypervolume"), positive=True) is None):
            return False
    for previous, current in zip(window, window[1:]):
        change = (current["hypervolume"] - previous["hypervolume"]) / previous["hypervolume"]
        if change < 0 or change >= threshold:
            return False
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pareto", nargs="?", default="state/pareto_front.json")
    parser.add_argument("--directive", help="Defaults to search_directive.json beside the Pareto file")
    args = parser.parse_args()
    pareto_path = Path(args.pareto)
    directive_path = Path(args.directive) if args.directive else pareto_path.with_name("search_directive.json")
    try:
        if not pareto_path.exists():
            output = {"status": "not_initialized", "hypervolume": None,
                      "convergence_ready": False, "reason": f"Missing {pareto_path}"}
        else:
            front = json.loads(pareto_path.read_text(encoding="utf-8"))
            directive = (json.loads(directive_path.read_text(encoding="utf-8"))
                         if directive_path.exists() else {})
            output = evaluate(front, directive)
        print(json.dumps(output, indent=2, allow_nan=False))
        return 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({"status": "invalid_state", "hypervolume": None,
                          "convergence_ready": False, "reason": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
