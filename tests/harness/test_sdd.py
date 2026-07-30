import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[2] / ".sdd" / "sdd.py"
SPEC = importlib.util.spec_from_file_location("sdd", MODULE_PATH)
SDD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SDD)


class SddHarnessTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / ".sdd").mkdir()
        (self.root / ".sdd" / "config.json").write_text(
            json.dumps({"protectedPaths": ["src"]}), encoding="utf-8"
        )
        (self.root / ".claude" / "session-context").mkdir(parents=True)
        (self.root / "specs" / "features").mkdir(parents=True)
        (self.root / "src").mkdir()
        (self.root / "tests").mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def create_feature(self, status="awaiting_approval"):
        feature_id = "001-login"
        directory = self.root / "specs" / "features" / feature_id
        directory.mkdir()
        (directory / "requirements.md").write_text(
            "- **F001-R1**: O sistema DEVE autenticar.\n", encoding="utf-8"
        )
        (directory / "design.md").write_text(
            "# Design\n\nImplementar em src/login.py.\n", encoding="utf-8"
        )
        (directory / "tasks.md").write_text(
            "- [ ] F001-T1 — Entregar login via RED → GREEN → REFACTOR (F001-R1)\n",
            encoding="utf-8",
        )
        payload = {
            "id": feature_id,
            "title": "Login",
            "status": status,
            "created": "2026-06-23",
            "updated": "2026-06-23",
            "approval": None,
            "reviews": {
                "qa": {"status": "pending", "report": None},
                "traceability": {"status": "pending", "report": None},
            },
        }
        (directory / "status.json").write_text(
            json.dumps(payload), encoding="utf-8"
        )
        return feature_id

    def activate(self, feature_id):
        (
            self.root / ".claude" / "session-context" / "active-feature"
        ).write_text(feature_id + "\n", encoding="utf-8")

    def approve(self, feature_id):
        SDD.approve_feature(self.root, feature_id, "human@example.com")

    def assert_blocked(self, payload):
        allowed, _ = SDD.guard(payload, self.root)
        self.assertFalse(allowed)

    def test_blocks_absolute_path_without_active_feature(self):
        self.assert_blocked(
            {"tool_input": {"file_path": str(self.root / "src" / "a.py")}}
        )

    def test_blocks_relative_protected_path(self):
        self.assert_blocked({"tool_input": {"file_path": "src/a.py"}})

    def test_blocks_multi_edit_when_any_target_is_protected(self):
        self.assert_blocked(
            {
                "tool_input": {
                    "edits": [
                        {"file_path": "specs/note.md"},
                        {"file_path": "src/a.py"},
                    ]
                }
            }
        )

    def test_blocks_markdown_inside_protected_directory(self):
        self.assert_blocked({"tool_input": {"file_path": "src/unsafe.md"}})

    def test_blocks_payload_without_recognized_path(self):
        self.assert_blocked({"tool_input": {"content": "x"}})

    def test_blocks_invalid_active_feature_id(self):
        (
            self.root / ".claude" / "session-context" / "active-feature"
        ).write_text("../../outside\n", encoding="utf-8")
        allowed, message = SDD.guard(
            {"tool_input": {"file_path": "src/a.py"}}, self.root
        )
        self.assertFalse(allowed)
        self.assertIn("ID inválido", message)

    def test_allows_non_protected_path(self):
        allowed, _ = SDD.guard(
            {"tool_input": {"file_path": "specs/note.md"}}, self.root
        )
        self.assertTrue(allowed)

    def test_awaiting_approval_does_not_unlock_code(self):
        feature_id = self.create_feature()
        self.activate(feature_id)
        self.assert_blocked({"tool_input": {"file_path": "src/login.py"}})

    def test_persisted_approval_unlocks_code(self):
        feature_id = self.create_feature()
        self.activate(feature_id)
        self.approve(feature_id)
        allowed, message = SDD.guard(
            {"tool_input": {"file_path": "src/login.py"}}, self.root
        )
        self.assertTrue(allowed, message)

    def test_spec_change_invalidates_approval(self):
        feature_id = self.create_feature()
        self.activate(feature_id)
        self.approve(feature_id)
        path = (
            self.root
            / "specs"
            / "features"
            / feature_id
            / "requirements.md"
        )
        path.write_text(path.read_text(encoding="utf-8") + "\nMudança.\n")
        allowed, message = SDD.guard(
            {"tool_input": {"file_path": "src/login.py"}}, self.root
        )
        self.assertFalse(allowed)
        self.assertIn("obsoleta", message)

    def test_checking_task_does_not_invalidate_approval(self):
        feature_id = self.create_feature()
        self.activate(feature_id)
        self.approve(feature_id)
        path = self.root / "specs" / "features" / feature_id / "tasks.md"
        path.write_text(
            path.read_text(encoding="utf-8").replace("- [ ]", "- [x]"),
            encoding="utf-8",
        )
        allowed, message = SDD.guard(
            {"tool_input": {"file_path": "src/login.py"}}, self.root
        )
        self.assertTrue(allowed, message)

    def test_rejects_unqualified_ids(self):
        feature_id = self.create_feature()
        directory = self.root / "specs" / "features" / feature_id
        (directory / "requirements.md").write_text(
            "- **R1**: requisito sem prefixo\n", encoding="utf-8"
        )
        errors = SDD.validate_feature(self.root, feature_id)
        self.assertTrue(any("sem prefixo" in error for error in errors))

    def test_requires_status_metadata(self):
        feature_id = self.create_feature()
        path = self.root / "specs" / "features" / feature_id / "status.json"
        status = json.loads(path.read_text(encoding="utf-8"))
        del status["reviews"]
        path.write_text(json.dumps(status), encoding="utf-8")
        errors = SDD.validate_feature(self.root, feature_id)
        self.assertTrue(any("reviews" in error for error in errors))

    def test_reapproval_resets_review_results(self):
        feature_id = self.create_feature()
        path = self.root / "specs" / "features" / feature_id / "status.json"
        status = json.loads(path.read_text(encoding="utf-8"))
        status["status"] = "changes_requested"
        status["reviews"]["qa"] = {
            "status": "approved",
            "report": "old-report.md",
        }
        path.write_text(json.dumps(status), encoding="utf-8")
        self.approve(feature_id)
        updated = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(updated["reviews"]["qa"]["status"], "pending")
        self.assertIsNone(updated["reviews"]["qa"]["report"])

    def test_review_requires_tasks_and_coverage(self):
        feature_id = self.create_feature()
        self.approve(feature_id)
        (self.root / "tests" / "README.md").write_text(
            "Exemplo documental: @covers F001-R1\n", encoding="utf-8"
        )
        (self.root / "src" / "login.py").write_text(
            "# comentário de produção: @covers F001-R1\n", encoding="utf-8"
        )
        path = self.root / "specs" / "features" / feature_id / "status.json"
        status = json.loads(path.read_text(encoding="utf-8"))
        status["status"] = "in_review"
        path.write_text(json.dumps(status), encoding="utf-8")
        errors = SDD.validate_feature(self.root, feature_id)
        self.assertTrue(any("não concluídas" in error for error in errors))
        self.assertTrue(any("sem @covers" in error for error in errors))

    def test_verified_requires_persisted_review_reports(self):
        feature_id = self.create_feature()
        self.approve(feature_id)
        directory = self.root / "specs" / "features" / feature_id
        tasks = directory / "tasks.md"
        tasks.write_text(
            tasks.read_text(encoding="utf-8").replace("- [ ]", "- [x]"),
            encoding="utf-8",
        )
        (self.root / "tests" / "login.spec.py").write_text(
            "# @covers F001-R1\n", encoding="utf-8"
        )
        status_path = directory / "status.json"
        status = json.loads(status_path.read_text(encoding="utf-8"))
        status["status"] = "verified"
        status_path.write_text(json.dumps(status), encoding="utf-8")
        errors = SDD.validate_feature(self.root, feature_id)
        self.assertTrue(any("review 'qa'" in error for error in errors))

        reviews_dir = directory / "reviews"
        reviews_dir.mkdir()
        qa_report = reviews_dir / "qa.md"
        trace_report = reviews_dir / "traceability.md"
        qa_report.write_text("QA aprovado\n", encoding="utf-8")
        trace_report.write_text("Rastreabilidade aprovada\n", encoding="utf-8")
        status["reviews"] = {
            "qa": {
                "status": "approved",
                "report": str(qa_report.relative_to(self.root)),
            },
            "traceability": {
                "status": "approved",
                "report": str(trace_report.relative_to(self.root)),
            },
        }
        status_path.write_text(json.dumps(status), encoding="utf-8")
        self.assertEqual(SDD.validate_feature(self.root, feature_id), [])

    def test_record_review_report_path_resolves_for_validate(self):
        """Regressão: `record_review` grava `report` relativo à pasta da
        feature (specs/features/<id>/reviews/...) — `validate` precisa
        resolver esse caminho na mesma base, não na raiz do repo. O teste
        acima (`test_verified_requires_persisted_review_reports`) não pega
        esse bug porque constrói `report` manualmente relativo à raiz (o
        contorno manual, não o caminho real que `record_review` produz) —
        este teste chama `record_review` de verdade."""
        feature_id = self.create_feature()
        self.approve(feature_id)
        directory = self.root / "specs" / "features" / feature_id
        tasks = directory / "tasks.md"
        tasks.write_text(
            tasks.read_text(encoding="utf-8").replace("- [ ]", "- [x]"),
            encoding="utf-8",
        )
        (self.root / "tests" / "login.spec.py").write_text(
            "# @covers F001-R1\n", encoding="utf-8"
        )

        reviews_dir = directory / "reviews"
        reviews_dir.mkdir()
        (reviews_dir / "qa.md").write_text("QA aprovado\n", encoding="utf-8")
        (reviews_dir / "traceability.md").write_text(
            "Rastreabilidade aprovada\n", encoding="utf-8"
        )

        SDD.record_review(self.root, feature_id, "qa", "approved", "reviews/qa.md")
        SDD.record_review(
            self.root, feature_id, "traceability", "approved", "reviews/traceability.md"
        )

        self.assertEqual(SDD.validate_feature(self.root, feature_id), [])
        status = json.loads((directory / "status.json").read_text(encoding="utf-8"))
        self.assertEqual(status["status"], "verified")

    def test_appending_resultado_real_does_not_invalidate_approval(self):
        # Um implementer pode marcar a task [x] e anexar
        # "**Resultado real:** ..." na mesma linha/bloco — texto legítimo de
        # evidência, não mudança de escopo — mas sem normalização isso muda
        # o conteúdo de tasks.md e invalida approval.specRevision (digest)
        # mesmo com QA + reviewer já aprovados.
        feature_id = self.create_feature()
        self.activate(feature_id)
        self.approve(feature_id)
        path = self.root / "specs" / "features" / feature_id / "tasks.md"
        original = path.read_text(encoding="utf-8")
        path.write_text(
            original.replace("- [ ]", "- [x]").rstrip("\n")
            + " **Resultado real:** medição feita, 3 arquivos, zero regressão.\n",
            encoding="utf-8",
        )
        allowed, message = SDD.guard(
            {"tool_input": {"file_path": "src/login.py"}}, self.root
        )
        self.assertTrue(allowed, message)

    def test_resultado_real_stops_at_next_task_bullet(self):
        feature_id = self.create_feature()
        directory = self.root / "specs" / "features" / feature_id
        tasks_path = directory / "tasks.md"
        tasks_path.write_text(
            "- [x] F001-T1 — Entregar login (F001-R1) "
            "**Resultado real:** ok, funcionou.\n"
            "- [ ] F001-T2 — Segunda task (F001-R1)\n",
            encoding="utf-8",
        )
        digest_before = SDD.spec_digest(self.root, feature_id)
        tasks_path.write_text(
            tasks_path.read_text(encoding="utf-8").replace(
                "ok, funcionou.", "ok, funcionou, medi de novo e confirmei."
            ),
            encoding="utf-8",
        )
        digest_after = SDD.spec_digest(self.root, feature_id)
        self.assertEqual(digest_before, digest_after)

    def test_coverage_scan_dirs_config_extends_scan(self):
        (self.root / ".sdd" / "config.json").write_text(
            json.dumps(
                {
                    "protectedPaths": ["src"],
                    "coverageScanDirs": ["tests", "src", "scripts"],
                }
            ),
            encoding="utf-8",
        )
        scripts_dir = self.root / "scripts"
        scripts_dir.mkdir()
        (scripts_dir / "test_extract.py").write_text(
            "# @covers F001-R1\n", encoding="utf-8"
        )
        covered = SDD.coverage_markers(self.root, "F001")
        self.assertIn("F001-R1", covered)

    def test_coverage_scan_dirs_defaults_when_config_omits_key(self):
        # Sem "coverageScanDirs" no config.json, comportamento idêntico ao de
        # antes (só tests/ e src/) — não quebra projetos já configurados.
        covered = SDD.coverage_markers(self.root, "F001")
        self.assertEqual(covered, set())
        (self.root / "tests" / "example.spec.ts").write_text(
            "// @covers F001-R1\n", encoding="utf-8"
        )
        covered = SDD.coverage_markers(self.root, "F001")
        self.assertIn("F001-R1", covered)


if __name__ == "__main__":
    unittest.main()
