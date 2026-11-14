"""Test harness semantics; mocks here do not constitute product acceptance."""
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from checks import acceptance

ROOT = Path(__file__).resolve().parents[1]


class HarnessTests(unittest.TestCase):
    def test_exit_codes(self):
        for statuses, expected in ((["PASS"], 0), (["BLOCKED"], 3), (["PASS", "BLOCKED"], 3), (["FAIL", "BLOCKED"], 1)):
            with self.subTest(statuses=statuses):
                self.assertEqual(acceptance.exit_code([{"result": status} for status in statuses]), expected)

    def test_main_continues_after_unexpected_scenario_exception(self):
        def fake_run(scenario):
            if scenario == "AC-1":
                raise RuntimeError("harness experiment")
            return {"scenario": scenario, "result": "BLOCKED" if scenario == "AC-3" else "PASS"}
        output = io.StringIO()
        with patch.object(acceptance, "run", side_effect=fake_run), redirect_stdout(output):
            code = acceptance.main([])
        rows = json.loads(output.getvalue())
        self.assertEqual(code, 1)
        self.assertEqual([row["scenario"] for row in rows], list(acceptance.SCENARIOS))
        self.assertEqual(rows[0]["actual"]["exception"], "RuntimeError")
        self.assertEqual(rows[-1]["result"], "PASS")

    def test_run_captures_product_exception(self):
        with patch.object(acceptance.storage, "connect", side_effect=RuntimeError("test-only storage failure")):
            row = acceptance.run("AC-1")
        self.assertEqual(row["result"], "FAIL")
        self.assertEqual(row["actual"]["exception"], "RuntimeError")

    def test_guard_records_even_a_swallowed_network_attempt(self):
        def fake_case(scenario, path, row):
            try:
                acceptance.socket.create_connection(("localhost", 1))
            except RuntimeError:
                pass
        with patch.object(acceptance, "local_case", side_effect=fake_case):
            row = acceptance.run("LOCAL-no-network")
        self.assertEqual(row["result"], "FAIL")
        self.assertEqual(row["actual"]["network_attempts"], 1)

    def test_guard_is_restored(self):
        original = acceptance.socket.socket.connect
        with acceptance.network_guard([]):
            self.assertIsNot(acceptance.socket.socket.connect, original)
        self.assertIs(acceptance.socket.socket.connect, original)

    def test_single_scenario_cli_and_fixed_runner(self):
        for scenario, expected in (("AC-1", 0), ("AC-3", 3)):
            with self.subTest(scenario=scenario):
                result = subprocess.run([sys.executable, "-B", str(ROOT / "checks/integration_runner.py"), "--scenario", scenario], capture_output=True, text=True, cwd=ROOT)
                self.assertEqual(result.returncode, expected, result.stderr)
                rows = json.loads(result.stdout)
                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0]["scenario"], scenario)
                self.assertIn("expected", rows[0])
                self.assertIn("actual", rows[0])
                self.assertIn("intermediate_states", rows[0])


if __name__ == "__main__":
    unittest.main()
