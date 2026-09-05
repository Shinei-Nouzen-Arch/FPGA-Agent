"""Deterministic adapter tests with a fake HLS process, not FPGA experiments."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
import artifacts
import hls_driver


class HlsArtifactsTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="dse-tests-")
        self.addCleanup(self.temporary.cleanup)
        self.project = Path(self.temporary.name)
        self.workspace = self.project / "workspace/explorer"
        for relative in ("src", "tb", ".dse"):
            (self.workspace / relative).mkdir(parents=True)
        (self.project / "state").mkdir()
        (self.workspace / "src/kernel.cpp").write_text("void kernel() {}\n")
        (self.workspace / "src/helper.cpp").write_text("void helper() {}\n")
        (self.workspace / "src/types.h").write_text("using value_t = int;\n")
        (self.workspace / "tb/testbench.cpp").write_text("int main() { return 0; }\n")
        (self.workspace / "tb/vectors.dat").write_text("1 2 3\n")
        self.config = self.workspace / "config.cfg"
        self.config.write_text("[hls]\npart=example-part\nclock=5\nsyn.top=kernel\n"
                               "syn.file=src/kernel.cpp\nsyn.file=src/helper.cpp\n"
                               "tb.file=tb/testbench.cpp\n")
        self.policy = {"mode": "formal", "implementation_allowed": True}
        self.assignment = {"benchmark": "test", "run_id": "test-run",
                           "candidate_id": "r1-explorer", "role": "explorer",
                           "validation_policy": self.policy, "max_attempts": 3,
                           "input_paths": ["src", "tb", "config.cfg"]}
        self.directive = {"benchmark": "test", "run_id": "test-run",
                          "validation_policy": self.policy}
        self.save_context()
        self.calls = []
        self.emit_reports = True
        self.fail = False
        self.mutate_inputs = False
        self.which = patch("shutil.which", return_value=sys.executable)
        self.which.start()
        self.addCleanup(self.which.stop)
        self.process = patch("hls_driver.subprocess.run", side_effect=self.fake_process)
        self.process.start()
        self.addCleanup(self.process.stop)

    def save_context(self):
        (self.workspace / ".dse/assignment.json").write_text(json.dumps(self.assignment))
        (self.project / "state/search_directive.json").write_text(json.dumps(self.directive))

    def fake_process(self, args, **kwargs):
        self.calls.append(args)
        stage = "csynth" if args[0] == "v++" else next(s for s in hls_driver.STAGES if f"--{s}" in args)
        names = {"csim": "hls_project/csim/report/kernel_csim.log",
                 "csynth": "hls_project/hls/syn/report/kernel_csynth.rpt",
                 "cosim": "hls_project/hls/sim/report/kernel_cosim.rpt",
                 "impl": "hls_project/hls/impl/report/export_impl.rpt"}
        if self.emit_reports:
            report = self.workspace / names[stage]
            report.parent.mkdir(parents=True, exist_ok=True)
            report.write_text(f"fake {stage} output {len(self.calls)}\n")
            if stage == "csynth":
                rtl = self.workspace / "hls_project/hls/syn/verilog/kernel.v"
                rtl.parent.mkdir(parents=True, exist_ok=True)
                rtl.write_text("module kernel; endmodule\n")
        if self.mutate_inputs:
            (self.workspace / "src/types.h").write_text("using value_t = short;\n")
        return subprocess.CompletedProcess(args, 1 if self.fail else 0)

    def stage(self, stage):
        hls_driver.run_stage(self.project, self.workspace, stage, self.config)

    def test_full_sequence_has_matching_receipts_and_multiple_sources(self):
        for stage in hls_driver.STAGES:
            self.stage(stage)
        check = artifacts.verify(self.workspace)
        self.assertEqual(check["verified_receipts"], list(hls_driver.STAGES))
        manifest = artifacts.read_json(self.workspace / ".dse/input_manifest.json")
        self.assertIn("src/helper.cpp", manifest["files"])
        self.assertIn("src/types.h", manifest["files"])
        self.assertIn("tb/vectors.dat", manifest["files"])
        self.assertIn(str(self.config), self.calls[1])
        self.assertIn("--part", self.calls[1])

    def test_implementation_ban_precedes_tool_launch(self):
        self.policy.update(mode="cosim_only_user_override", implementation_allowed=False)
        self.save_context()
        for mode in ("impl", "all"):
            with self.assertRaisesRegex(ValueError, "forbidden"):
                hls_driver.policy_check(self.project, self.workspace, mode)
        self.assertEqual(self.calls, [])
        for stage in ("csim", "csynth", "cosim"):
            self.stage(stage)
        self.assertFalse((self.workspace / ".dse/impl.json").exists())

    def test_formal_mode_does_not_override_explicit_ban(self):
        self.policy["implementation_allowed"] = False
        self.save_context()
        with self.assertRaisesRegex(ValueError, "forbidden"):
            self.stage("impl")

    def test_assignment_policy_and_identity_must_match(self):
        self.directive["benchmark"] = "different"
        self.save_context()
        with self.assertRaisesRegex(ValueError, "mismatch"):
            self.stage("csim")
        self.assertEqual(self.calls, [])

    def test_directory_without_receipt_is_not_synthesis_evidence(self):
        (self.workspace / "hls_project/hls/syn").mkdir(parents=True)
        with self.assertRaises(OSError):
            self.stage("cosim")
        self.assertEqual(self.calls, [])

    def test_header_and_test_data_changes_invalidate_synthesis(self):
        for relative in ("src/types.h", "tb/vectors.dat"):
            with self.subTest(relative=relative):
                self.stage("csynth")
                (self.workspace / relative).write_text("changed\n")
                before = len(self.calls)
                with self.assertRaisesRegex(ValueError, "Stale"):
                    self.stage("cosim")
                self.assertEqual(len(self.calls), before)

    def test_clock_change_invalidates_synthesis(self):
        self.stage("csynth")
        self.config.write_text(self.config.read_text().replace("clock=5", "clock=3"))
        with self.assertRaisesRegex(ValueError, "Stale"):
            self.stage("impl")

    def test_changed_report_and_rtl_are_rejected(self):
        for relative in ("hls_project/hls/syn/report/kernel_csynth.rpt",
                         "hls_project/hls/syn/verilog/kernel.v"):
            with self.subTest(relative=relative):
                self.stage("csynth")
                (self.workspace / relative).write_text("changed\n")
                with self.assertRaisesRegex(ValueError, "Changed or missing"):
                    self.stage("cosim")

    def test_failed_or_stale_output_cannot_retain_success_receipt(self):
        self.stage("csynth")
        self.emit_reports = False
        with self.assertRaisesRegex(ValueError, "no fresh"):
            self.stage("csynth")
        self.assertFalse((self.workspace / ".dse/csynth.json").exists())
        self.emit_reports = True
        self.fail = True
        with self.assertRaisesRegex(ValueError, "failed"):
            self.stage("csynth")
        self.assertFalse((self.workspace / ".dse/csynth.json").exists())

    def test_inputs_changing_during_run_are_rejected(self):
        self.mutate_inputs = True
        with self.assertRaisesRegex(ValueError, "changed while"):
            self.stage("csynth")
        self.assertFalse((self.workspace / ".dse/csynth.json").exists())

    def test_missing_dependency_and_symlink_are_rejected(self):
        (self.workspace / "src/helper.cpp").unlink()
        with self.assertRaisesRegex(ValueError, "missing from"):
            self.stage("csynth")
        (self.workspace / "src/helper.cpp").symlink_to(self.workspace / "src/kernel.cpp")
        with self.assertRaisesRegex(ValueError, "Symlinks"):
            self.stage("csynth")

    def test_archive_preserves_bytes_and_rejects_overwrite(self):
        for stage in hls_driver.STAGES:
            self.stage(stage)
        result = self.project / "result.json"
        result.write_text(json.dumps({"id": "r1-explorer", "status": "success"}))
        destination = self.project / "archive/run/round-1/explorer"
        output = artifacts.archive(self.workspace, result, destination)
        self.assertIn("snapshot_digest", output)
        original = (self.workspace / "src/kernel.cpp").read_text()
        (self.workspace / "src/kernel.cpp").write_text("new candidate\n")
        self.assertEqual((destination / "workspace/src/kernel.cpp").read_text(), original)
        with self.assertRaises(FileExistsError):
            artifacts.archive(self.workspace, result, destination)
        self.assertEqual(artifacts.verify(destination / "workspace")["verified_receipts"],
                         list(hls_driver.STAGES))

    def test_failed_candidate_can_be_archived_without_formal_promotion(self):
        result = self.project / "result.json"
        result.write_text(json.dumps({"id": "r1-explorer", "status": "blocked"}))
        output = artifacts.archive(self.workspace, result, self.project / "archive/blocked")
        self.assertIn("verification_error", output)
        self.assertTrue((self.project / "archive/blocked/snapshot.json").exists())

    def test_wrong_role_path_and_external_inputs_are_rejected(self):
        self.assignment["role"] = "innovator"
        self.save_context()
        with self.assertRaisesRegex(ValueError, "Workspace does not match"):
            self.stage("csim")
        with self.assertRaises(ValueError):
            artifacts.local_path(self.workspace, "../outside")
        with self.assertRaises(ValueError):
            artifacts.local_path(self.workspace, self.project / "outside")

    def test_cli_ban_all_is_nonmutating(self):
        self.policy.update(mode="cosim_only_user_override", implementation_allowed=False)
        self.save_context()
        before = artifacts.snapshot_files(self.workspace)
        self.process.stop()
        self.which.stop()
        output = subprocess.run(
            [str(SRC / "hls_run.sh"), "workspace/explorer", "all"],
            cwd=SRC, env={**os.environ, "DSE_PROJECT_ROOT": str(self.project)},
            capture_output=True, text=True, check=False)
        self.assertEqual(output.returncode, 2)
        self.assertIn("forbidden", output.stderr)
        self.assertEqual(artifacts.snapshot_files(self.workspace), before)

    def test_cli_root_is_project_not_skill(self):
        with patch.dict(os.environ, {"DSE_PROJECT_ROOT": str(self.project)}):
            with patch.object(sys, "argv", ["hls_driver.py", "workspace/explorer", "all"]):
                self.assertEqual(hls_driver.main(), 0)
        self.assertEqual(len(self.calls), 4)


if __name__ == "__main__":
    unittest.main()
