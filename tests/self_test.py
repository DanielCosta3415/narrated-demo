"""Source-checkout entry point for the self-contained plugin self-test."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).resolve().parents[1] / "plugins/narrated-demo/app/self_test.py"), run_name="__main__")
