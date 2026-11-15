"""Regression checks for the harness, separate from product acceptance results."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from checks import acceptance, integration_runner


class CheckToolsTests(unittest.TestCase):
    def invoke(self, entry, *arguments, cwd=ROOT):
        completed = subprocess.run([sys.executable, "-B", *entry, *arguments],
                                   cwd=cwd, text=True, capture_output=True, timeout=20)
        self.assertEqual(completed.stderr, "", completed.stderr)
        return completed.returncode, json.loads(completed.stdout)

    def test_real_ci_reports_all_scenarios_and_failure_precedes_blocked(self):
        code, rows = self.invoke(["checks/integration_runner.py"])
        self.assertEqual([row["scenario"] for row in rows], list(acceptance.SCENARIOS))
        # These are actual product results, not a requirement that the product passes.
        self.assertEqual(rows, [acceptance.run(item) for item in acceptance.SCENARIOS])
        self.assertEqual(code, 1)
        outcomes = {row["scenario"]: row["result"] for row in rows}
        self.assertEqual(outcomes["AC-2"], "FAIL")
        self.assertEqual(outcomes["ERR-2-PAY"], "FAIL")
        self.assertEqual(outcomes["AC-3"], "BLOCKED")
        self.assertEqual(len(rows), 16)

    def test_real_ci_exit_codes_and_scenario_selection(self):
        for scenario, expected_code, expected_result in (
            ("AC-1", 0, "PASS"), ("AC-2", 1, "FAIL"),
            ("ERR-2-PAY", 1, "FAIL"), ("AC-3", 3, "BLOCKED"),
        ):
            with self.subTest(scenario=scenario):
                code, rows = self.invoke(["checks/integration_runner.py"], "--scenario", scenario)
                self.assertEqual(code, expected_code)
                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0]["scenario"], scenario)
                self.assertEqual(rows[0]["result"], expected_result)

    def test_module_and_import_entry_points(self):
        self.assertIs(integration_runner.run_acceptance, acceptance.main)
        for module in ("checks.integration_runner", "checks.acceptance"):
            with self.subTest(module=module):
                code, rows = self.invoke(["-m", module], "--scenario", "PAY-1")
                self.assertEqual(code, 0)
                self.assertEqual(rows[0]["persisted_status"], "paid")

    def test_absolute_scripts_work_from_unrelated_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            for script in ("integration_runner.py", "acceptance.py"):
                with self.subTest(script=script):
                    code, rows = self.invoke([str(ROOT / "checks" / script)],
                                             "--scenario", "STATE-1", cwd=directory)
                    self.assertEqual(code, 0)
                    self.assertEqual(rows[0]["persisted_status"], "pending")

    def test_real_ci_repeat_runs_are_isolated(self):
        first = self.invoke(["checks/integration_runner.py"])
        second = self.invoke(["checks/integration_runner.py"])
        self.assertEqual(first, second)

    def test_unexpected_product_error_does_not_stop_remaining_scenarios(self):
        # Only this harness resilience test substitutes one product operation.
        # The integration subprocess tests above always use the real src modules.
        with patch.object(acceptance.ui, "mark_paid", side_effect=RuntimeError("injected tool regression fault")):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = acceptance.main([])
        rows = json.loads(output.getvalue())
        by_id = {row["scenario"]: row for row in rows}
        self.assertEqual(code, 1)
        self.assertEqual(len(rows), 16)
        self.assertEqual(by_id["PAY-1"]["exception"], "RuntimeError")
        self.assertEqual(by_id["ERR-3-PAY"]["actual_exception"], "OperationalError")
        self.assertEqual(by_id["ERR-3-SUBMIT"]["result"], "PASS")
        self.assertEqual(by_id["AC-3"]["result"], "BLOCKED")

    def test_external_scenario_never_attempts_network(self):
        # Guard both common socket entry paths; no success response is simulated.
        with patch("socket.create_connection", side_effect=AssertionError("network forbidden")) as connect, \
             patch("socket.socket.connect", side_effect=AssertionError("network forbidden")) as socket_connect:
            result = acceptance.run("AC-3")
        self.assertEqual(result["result"], "BLOCKED")
        connect.assert_not_called()
        socket_connect.assert_not_called()


if __name__ == "__main__":
    unittest.main()
