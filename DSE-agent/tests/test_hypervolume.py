"""Unit tests use an independent tiny-population exact oracle."""
from copy import deepcopy
from itertools import combinations
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import hypervolume as hv


def test_backend():
    def exact(points, reference):
        value = 0
        for count in range(1, len(points) + 1):
            for subset in combinations(points, count):
                corner = [max(p[d] for p in subset) for d in range(len(reference))]
                volume = math.prod(r - p for r, p in zip(reference, corner))
                value += volume if count % 2 else -volume
        return value
    return exact, {"test_oracle": "inclusion-exclusion-v1"}


def unavailable_backend():
    raise ImportError("test dependency unavailable")


class HypervolumeTests(unittest.TestCase):
    def setUp(self):
        self.directive = {"benchmark": "test", "run_id": "run",
                          "hv_config": {"algorithm": "pymoo_exact_nd", "population": "formal",
                                        "objectives": ["latency_ns", "ii_ns"],
                                        "reference_point": {"latency_ns": 100, "ii_ns": 100}}}
        self.point = {"id": "p1", "benchmark": "test", "run_id": "run", "status": "success",
                      "validation": {"formal_eligible": True},
                      "metrics": {"latency_cycles": 4, "ii_cycles": 2, "clock_ns": 5,
                                  "lut": 10, "ff": 10, "bram_36k": 0, "dsp": 0,
                                  "uram": 0, "wns": 0}}

    def evaluate(self, points=None):
        return hv.evaluate([self.point] if points is None else points, self.directive, test_backend)

    def test_exact_nd_inputs_and_fixed_normalization(self):
        output = self.evaluate()
        self.assertEqual(output["hypervolume"], 80 * 90)
        self.assertEqual(output["hypervolume_normalized"], 0.72)
        self.assertTrue(output["convergence_ready"])
        self.assertEqual(output["backend_versions"]["test_oracle"], "inclusion-exclusion-v1")

    def test_nulls_are_not_zero_or_reference_defaults(self):
        for key in ("latency_cycles", "ii_cycles", "clock_ns", "lut", "wns"):
            with self.subTest(key=key):
                point = deepcopy(self.point)
                point["metrics"][key] = None
                output = self.evaluate([point])
                self.assertIsNone(output["hypervolume"])
                self.assertEqual(output["status"], "no_eligible_points")
                self.assertFalse(output["convergence_ready"])

    def test_unknown_clock_and_ii_remain_unknown(self):
        values = hv.measured({"latency_cycles": 10, "clock_ns": None, "ii_cycles": None})
        self.assertIsNone(values["latency_ns"])
        self.assertIsNone(values["ii_ns"])
        self.assertIsNone(values["transactions_per_second"])

    def test_invalid_metrics_and_overflow_are_not_measurements(self):
        for value in (False, "10", -1, float("nan"), float("inf"), 10 ** 10000):
            self.assertIsNone(hv.number(value))
        self.assertIsNone(hv.measured({"latency_cycles": 1e308, "clock_ns": 1e308})["latency_ns"])

    def test_real_zero_resources_and_zero_wns_pass(self):
        self.assertEqual(self.evaluate()["status"], "ok")

    def test_provisional_legacy_and_foreign_points_are_not_formal(self):
        for edit in ({"status": "provisional_pass"}, {"validation": {}},
                     {"benchmark": "other"}, {"run_id": "other"}):
            point = {**self.point, **edit}
            output = self.evaluate([point])
            self.assertEqual(output["status"], "no_eligible_points")

    def test_negative_wns_is_not_formal(self):
        self.point["metrics"]["wns"] = -0.001
        self.assertEqual(self.evaluate()["status"], "no_eligible_points")

    def test_partial_population_never_implies_convergence(self):
        missing = deepcopy(self.point)
        missing["id"] = "missing"
        missing["metrics"]["ii_cycles"] = None
        output = self.evaluate([self.point, missing])
        self.assertEqual(output["status"], "partial")
        self.assertIsNotNone(output["hypervolume"])
        self.assertFalse(output["convergence_ready"])

    def test_reference_never_grows_and_invalidation_is_explicit(self):
        original = deepcopy(self.directive)
        self.point["metrics"]["latency_cycles"] = 20
        output = self.evaluate()
        self.assertEqual(output["status"], "invalid_reference")
        self.assertEqual(self.directive, original)
        self.assertIsNone(output["hypervolume"])

    def test_clock_units_use_interval_ns(self):
        slower = deepcopy(self.point)
        slower.update(id="p2")
        slower["metrics"]["clock_ns"] = 10
        values = self.evaluate([self.point, slower])["points"]
        self.assertEqual([p["metrics"]["ii_ns"] for p in values], [10, 20])
        self.directive["hv_config"].update(objectives=["ii_cycles"], reference_point={"ii_cycles": 100})
        self.assertEqual(self.evaluate([self.point, slower])["status"], "invalid_units")

    def test_config_changes_create_different_series(self):
        baseline = self.evaluate()["config_id"]
        for key, value in (("run_id", "new-run"), ("benchmark", "new-benchmark")):
            original = self.directive[key]
            self.directive[key] = value
            self.point[key] = value
            self.assertNotEqual(self.evaluate()["config_id"], baseline)
            self.directive[key] = original
            self.point[key] = original
        self.directive["hv_config"]["reference_point"]["ii_ns"] = 120
        self.assertNotEqual(self.evaluate()["config_id"], baseline)

    def test_cycle_objective_clock_changes_comparison_series(self):
        self.directive["hv_config"].update(objectives=["ii_cycles"], reference_point={"ii_cycles": 100})
        first = self.evaluate()["config_id"]
        self.point["metrics"]["clock_ns"] = 10
        self.assertNotEqual(self.evaluate()["config_id"], first)

    def test_failed_timing_still_visible_in_status(self):
        self.point["metrics"]["wns"] = -1.5
        self.assertEqual(self.evaluate()["points"][0]["metrics"]["wns"], -1.5)

    def test_backend_version_changes_comparison_series(self):
        calculate, _ = test_backend()
        changed = hv.evaluate([self.point], self.directive,
                              lambda: (calculate, {"test_oracle": "version-2"}))
        self.assertNotEqual(changed["config_id"], self.evaluate()["config_id"])

    def test_missing_dependency_preserves_status_details_without_fallback(self):
        output = hv.evaluate([self.point], self.directive, unavailable_backend)
        self.assertEqual(output["status"], "unavailable")
        self.assertIsNone(output["hypervolume"])
        self.assertEqual(output["points"][0]["metrics"]["latency_ns"], 20)
        self.assertFalse(output["convergence_ready"])

    def test_empty_and_missing_config_do_not_imply_convergence(self):
        self.assertEqual(self.evaluate([])["status"], "empty")
        self.directive.pop("hv_config")
        self.assertIsNone(self.evaluate()["hypervolume"])
        self.assertTrue(self.evaluate()["points"])

    def test_missing_brambasis_is_not_guessed(self):
        self.point["metrics"].pop("bram_36k")
        self.point["metrics"]["bram"] = 10
        self.assertEqual(self.evaluate()["status"], "no_eligible_points")

    def test_convergence_requires_four_valid_comparable_positive_values(self):
        baseline = self.evaluate()
        history = [{**baseline, "hypervolume": value} for value in (100, 101, 102, 103)]
        self.assertTrue(hv.convergence(history))
        self.assertFalse(hv.convergence(history[:3]))
        for edit in ({"status": "empty"}, {"hypervolume": None}, {"hypervolume": 0},
                     {"config_id": "different"}, {"convergence_ready": False},
                     {"hypervolume": 101}, {"hypervolume": 110}):
            self.assertFalse(hv.convergence([*history[:3], {**history[3], **edit}]))

    def test_cli_missing_state_is_read_only(self):
        with tempfile.TemporaryDirectory(prefix="dse-hv-status-") as folder:
            script = Path(hv.__file__).resolve()
            result = subprocess.run([sys.executable, str(script)], cwd=folder,
                                    text=True, capture_output=True, check=True)
            self.assertEqual(json.loads(result.stdout)["status"], "not_initialized")
            self.assertEqual(list(Path(folder).iterdir()), [])

    def test_optional_real_backend_matches_oracle(self):
        try:
            calculate, _ = hv.exact_backend()
        except ImportError:
            self.skipTest("Optional numerical backend is not installed")
        oracle, _ = test_backend()
        points = [[1, 4, 3], [2, 2, 1]]
        reference = [5, 6, 7]
        self.assertAlmostEqual(calculate(points, reference), oracle(points, reference))


if __name__ == "__main__":
    unittest.main()
