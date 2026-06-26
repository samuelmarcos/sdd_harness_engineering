import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SESSION_MODULE_PATH = (
    Path(__file__).parents[2] / ".claude" / "knowledge" / "session_manager.py"
)
SPEC = importlib.util.spec_from_file_location(
    "session_manager", SESSION_MODULE_PATH
)
SESSION = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SESSION)


class SessionManagerTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        templates = (
            Path(__file__).parents[2] / ".claude" / "session-context" / "_templates"
        )
        session_dir = self.root / ".claude" / "session-context"
        session_dir.mkdir(parents=True)
        if templates.is_dir():
            shutil_copy_tree(templates, session_dir / "_templates")
        self.manager = SESSION.SessionManager(
            self.root,
            {"sessionMemory": {"tokenThreshold": 50, "approxCharsPerToken": 4}},
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_bootstrap_creates_metadata_and_global(self):
        metadata = self.manager.bootstrap()
        self.assertIn("sessionId", metadata)
        self.assertTrue(self.manager.metadata_path().is_file())
        self.assertTrue(self.manager.global_working_path().is_file())

    def test_feature_context_created_on_demand(self):
        self.manager.bootstrap()
        path = self.manager.ensure_feature_context("001-login")
        self.assertTrue(path.is_file())
        self.assertIn("001-login", path.read_text(encoding="utf-8"))

    def test_token_estimate_grows_with_content(self):
        self.manager.bootstrap()
        before = self.manager.refresh_token_estimate()
        self.manager.write_text(
            self.manager.global_working_path(),
            "x" * 400,
        )
        after = self.manager.refresh_token_estimate()
        self.assertGreater(after, before)

    def test_checkpoint_archives_when_threshold_exceeded(self):
        self.manager.bootstrap()
        self.manager.write_text(
            self.manager.global_working_path(),
            "linha\n" * 200,
        )
        self.assertTrue(self.manager.should_checkpoint())
        archived = self.manager.checkpoint_all(force=False)
        self.assertTrue(archived)
        metadata = self.manager.read_metadata()
        self.assertEqual(len(metadata.get("checkpoints", [])), 1)

    def test_merged_context_includes_global_and_feature(self):
        self.manager.bootstrap()
        (self.root / ".claude" / "session-context" / "active-feature").write_text(
            "001-login\n", encoding="utf-8"
        )
        self.manager.write_text(
            self.manager.global_working_path(),
            "## Foco\nImplementar login",
        )
        self.manager.ensure_feature_context("001-login")
        merged = self.manager.get_merged_context()
        self.assertIn("Foco", merged)
        self.assertIn("001-login", merged)


def shutil_copy_tree(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        target = dst / item.name
        if item.is_dir():
            shutil_copy_tree(item, target)
        else:
            target.write_text(item.read_text(encoding="utf-8"), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
