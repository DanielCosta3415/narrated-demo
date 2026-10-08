"""Behavioral packaging, path and recoverable-uninstall tests without downloads."""
import json
import importlib.util
from pathlib import Path
import subprocess
import shutil
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/narrated-demo"

class Distribution(unittest.TestCase):
    def test_narrator_closing_agreement(self):
        spec = importlib.util.spec_from_file_location("demo_self_test", PLUGIN / "app/self_test.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(module.closing_for("Dora"), "O pedido foi salvo. Obrigada por acompanhar.")
        self.assertEqual(module.closing_for("Alex"), "O pedido foi salvo. Obrigado por acompanhar.")
        with self.assertRaises(KeyError):
            module.closing_for("Unknown")
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="narrated-owned-ação ")
        self.root = Path(self.temp.name)
    def tearDown(self):
        # Test-only deletion of the exact owned temporary directory. The
        # extended path is needed on hosts with long-path policy disabled.
        self.assertEqual(self.root.parent.resolve(), Path(tempfile.gettempdir()).resolve())
        self.assertTrue(self.root.name.startswith("narrated-owned-"))
        shutil.rmtree("\\\\?\\" + str(self.root))
        self.temp.cleanup()
    def shell(self, command, succeeds=True):
        result = subprocess.run(["powershell.exe", "-NoProfile", "-Command", command], capture_output=True, text=True, errors="replace")
        if succeeds:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
        return result
    def common(self, body):
        return f". '{PLUGIN / 'installer/Common.ps1'}'; {body}"
    def test_broad_roots_rejected(self):
        self.shell(self.common("Get-SafeRoot $env:USERPROFILE"), False)
        self.shell(self.common("Get-SafeRoot 'C:\\'"), False)
    def test_unowned_directory_preserved(self):
        (self.root / "important.txt").write_text("keep")
        self.shell(self.common(f"Assert-Owned '{self.root}'"), False)
        self.assertEqual((self.root / "important.txt").read_text(), "keep")
    def test_unsafe_zip_rejected(self):
        archive = self.root / "bad.zip"
        with zipfile.ZipFile(archive, "w") as stream:
            stream.writestr("../escaped.txt", "bad")
        self.shell(self.common(f"Expand-SafeArchive '{archive}' '{self.root / 'inside'}'"), False)
        self.assertFalse((self.root / "escaped.txt").exists())
    def test_safe_zip_spaces(self):
        archive = self.root / "good.zip"
        with zipfile.ZipFile(archive, "w") as stream:
            stream.writestr("folder/file.txt", "good")
        destination = self.root / "safe space"
        self.shell(self.common(f"Expand-SafeArchive '{archive}' '{destination}'"))
        self.assertEqual((destination / "folder/file.txt").read_text(), "good")
    def test_zip_extended_paths(self):
        archive = self.root / "long.zip"
        with zipfile.ZipFile(archive, "w") as stream:
            stream.writestr("folder/file.txt", "long path")
        destination = self.root / ("a" * 90) / ("b" * 90)
        self.shell(self.common(f"Expand-SafeArchive '{archive}' '{destination}'"))
        self.assertEqual(Path("\\\\?\\" + str(destination / "folder/file.txt")).read_text(), "long path")
    def test_wrong_marker_rejected(self):
        (self.root / ".narrated-demo-owner.json").write_text(json.dumps({"app": "other", "root": str(self.root)}))
        self.shell(self.common(f"Assert-Owned '{self.root}'"), False)
    def test_recoverable_uninstall(self):
        owned = self.root / "runtime"
        owned.mkdir()
        (owned / ".narrated-demo-owner.json").write_text(json.dumps({"app": "narrated-demo", "root": str(owned)}))
        (owned / "video.mp4").write_bytes(b"preserved fixture")
        script = PLUGIN / "installer/Maintain.ps1"
        self.shell(f"& '{script}' -Action Uninstall -Destination '{owned}' -ConfirmAction")
        archived = list(self.root.glob("runtime.archived-*"))
        self.assertEqual(len(archived), 1)
        self.assertFalse(owned.exists())
        self.assertEqual((archived[0] / "video.mp4").read_bytes(), b"preserved fixture")
    def test_plugin_self_contained(self):
        manifest = json.loads((PLUGIN / "plugin.json").read_text())
        self.assertTrue((PLUGIN / manifest["extensions"]["com.openai"]["onboardingSkill"]).is_file())
        for path in ("app/runtime.py", "app/configure.py", "installer/Install.ps1", "dependencies/requirements.lock", "dependencies/package-lock.json"):
            self.assertTrue((PLUGIN / path).is_file(), path)
        self.assertEqual((ROOT / "installer/Install.ps1").read_bytes(), (PLUGIN / "installer/Install.ps1").read_bytes())

if __name__ == "__main__":
    unittest.main()
