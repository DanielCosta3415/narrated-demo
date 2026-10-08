"""Local launcher and verified runtime diagnostics. No remote synthesis API."""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys

PLUGIN = Path(__file__).resolve().parents[1]
SKILL = PLUGIN / "skills/narrated-demo"
BINARY_HASHES = {
    "ffmpeg": "3256173f3f8bffd7df12227c68adf68025edb1832273a9530688a7bb1ed8edec",
    "ffprobe": "f0d36ecbbdd3bcfac3efa078c96c7271c2e68b3810595552ac3b7f17e9a65c52",
}

def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()

def load(path):
    data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if data.get("schema_version") != 1:
        raise ValueError("Unsupported runtime schema")
    for key in ("python", "node", "ffmpeg", "ffprobe", "model", "voices"):
        if not isinstance(data.get(key), str) or not Path(data[key]).is_file():
            raise ValueError(f"Missing dependency: {key}. Run setup/repair.")
    return data

def doctor(runtime):
    voices = json.loads((SKILL / "assets/voices.json").read_text(encoding="utf-8"))
    for key in ("model", "voices"):
        if digest(runtime[key]) != voices[key + "_sha256"]:
            raise ValueError(f"Corrupt or unsupported {key}")
    for key, expected in BINARY_HASHES.items():
        if digest(runtime[key]) != expected:
            raise ValueError(f"Unsupported {key} build")
    versions = {}
    for key, option in (("python", "--version"), ("node", "--version"), ("ffmpeg", "-version"), ("ffprobe", "-version")):
        result = subprocess.run([runtime[key], option], capture_output=True, text=True, check=True)
        versions[key] = result.stdout.splitlines()[0]
    if "3.12.10" not in versions["python"] or versions["node"] != "v24.11.0":
        raise ValueError("Unsupported Python/Node version")
    imports = "import kokoro_onnx,soundfile,numpy,PIL,onnxruntime; from importlib.metadata import version; assert version('kokoro-onnx')=='0.6.1'"
    subprocess.run([runtime["python"], "-c", imports], check=True)
    browser_root = Path(runtime["browsers"])
    if not list(browser_root.glob("chromium-1243/**/chrome.exe")):
        raise ValueError("Chromium 1243 missing")
    result = subprocess.run([runtime["node"], "-e", "console.log(require(process.argv[1]).version)",
                             str(Path(runtime["node_deps"]) / "node_modules/playwright/package.json")], capture_output=True, text=True, check=True)
    if result.stdout.strip() != "1.63.0":
        raise ValueError("Unsupported Playwright version")
    return {"status": "pass", "versions": versions, "models_sha256": "verified", "binaries_sha256": "verified", "scope": "dependencies; audiovisual review remains separate"}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("doctor", "capture", "build", "validate", "review", "sample"))
    parser.add_argument("--runtime", default=str(Path(os.environ.get("LOCALAPPDATA", ".")) / "NarratedDemo/runtime/runtime.json"))
    parser.add_argument("--config")
    parser.add_argument("--plan")
    parser.add_argument("--output")
    args = parser.parse_args()
    runtime = load(args.runtime)
    if args.command == "doctor":
        print(json.dumps(doctor(runtime), ensure_ascii=False, indent=2))
        return
    env = dict(os.environ, PLAYWRIGHT_BROWSERS_PATH=runtime["browsers"])
    if args.command == "capture":
        if not args.plan or not args.output:
            parser.error("capture requires --plan and --output")
        command = [runtime["node"], str(SKILL / "scripts/capture.mjs"), args.plan, args.output, runtime["node_deps"], "pt-BR"]
    else:
        if not args.config:
            parser.error("command requires --config")
        command = [runtime["python"], str(SKILL / "scripts/review.py"), args.config] if args.command == "review" else [runtime["python"], str(SKILL / "scripts/pipeline.py"), args.command, args.config]
    subprocess.run(command, env=env, check=True)

if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f"Runtime error: {error}", file=sys.stderr)
        sys.exit(1)
