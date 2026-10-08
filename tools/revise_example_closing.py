"""Create a separate corrected example without overwriting the reviewed original."""
import argparse
import importlib.util
import json
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config")
    parser.add_argument("destination")
    args = parser.parse_args()
    original = Path(args.config).resolve()
    config = json.loads(original.read_text(encoding="utf-8-sig"))
    units = json.loads(Path(config["units"]).read_text(encoding="utf-8"))
    spec = importlib.util.spec_from_file_location("example", Path(__file__).resolve().parents[1] / "plugins/narrated-demo/app/self_test.py")
    example = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(example)
    closing = example.closing_for(config["voice"])
    if len(units["units"]) != 1 or units["units"][0]["id"] != "save-order":
        raise ValueError("This utility only revises the fictional self-test example")
    units["units"][0]["after"] = dict(text_display=closing, text_tts=closing)
    destination = Path(args.destination).resolve()
    destination.mkdir(parents=True, exist_ok=False)
    unit_path = destination / "units.json"
    unit_path.write_text(json.dumps(units, ensure_ascii=False, indent=2), encoding="utf-8")
    config["units"] = str(unit_path)
    config["output_dir"] = str(destination / config["voice"])
    target = destination / "config.json"
    target.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    print(target)

if __name__ == "__main__":
    main()
