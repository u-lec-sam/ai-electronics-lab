"""Guard critical AI Electronics Lab repository and operating contracts."""
from pathlib import Path
import csv
import unittest

ROOT = Path(__file__).resolve().parents[1]


class RepositoryContractTests(unittest.TestCase):
    def test_canonical_operating_documents_exist(self):
        required = [
            "README.md",
            "docs/ARCHITECTURE.md",
            "docs/ENGINEERING_RULES.md",
            "docs/RECURSIVE_IMPROVEMENT.md",
            "docs/RESEARCH_NOTES.md",
            "docs/ONE_BUTTON_OPERATOR_LOOP.md",
            "memory/README.md",
            "memory/PROJECT_STATE.md",
            "evals/README.md",
        ]
        for relative in required:
            with self.subTest(path=relative):
                self.assertTrue((ROOT / relative).is_file(), relative)

    def test_recursive_loop_and_evidence_gates_are_documented(self):
        protocol = (ROOT / "docs/RECURSIVE_IMPROVEMENT.md").read_text(
            encoding="utf-8"
        ).lower()
        for stage in (
            "read", "baseline", "diagnose", "propose",
            "test", "review", "integrate", "record",
        ):
            with self.subTest(stage=stage):
                self.assertIn(stage, protocol)
        self.assertIn("must not be self-approved", protocol)
        self.assertIn("model weights", protocol)

    def test_one_button_contract_has_single_active_next_task(self):
        operator = (ROOT / "docs/ONE_BUTTON_OPERATOR_LOOP.md").read_text(
            encoding="utf-8"
        ).lower()
        for required in (
            "run next task", "active next task", "acceptance criteria",
            "refresh github", "not background execution",
            "do not access the user's local device",
        ):
            with self.subTest(text=required):
                self.assertIn(required, operator)
        self.assertEqual(operator.count("### ael-001:"), 1)

    def test_public_repo_secret_boundary_is_documented(self):
        rules = (ROOT / "docs/ENGINEERING_RULES.md").read_text(
            encoding="utf-8"
        ).lower()
        self.assertIn("secrets", rules)
        self.assertIn("public", rules)

    def test_active_project_tables_have_headers_and_data(self):
        csv_paths = [
            "projects/001-stm32g0b1-sensor-io/hardware/BOM_DRAFT.csv",
            "projects/001-stm32g0b1-sensor-io/hardware/INTERFACE_PLAN.csv",
        ]
        for relative in csv_paths:
            with self.subTest(path=relative):
                with (ROOT / relative).open(
                    newline="", encoding="utf-8"
                ) as stream:
                    rows = list(csv.reader(stream))
                self.assertGreaterEqual(len(rows), 2)
                self.assertGreaterEqual(len(rows[0]), 4)
                self.assertTrue(all(cell.strip() for cell in rows[0]))

    def test_preliminary_hardware_status_is_not_misrepresented(self):
        project = (ROOT / "projects/001-stm32g0b1-sensor-io/README.md").read_text(
            encoding="utf-8"
        ).lower()
        self.assertIn("preliminary", project)
        self.assertIn("no native kicad schematic/pcb", project)


if __name__ == "__main__":
    unittest.main()
