"""Package committed source only, reproducibly, with file and archive hashes."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def git(*arguments):
    return subprocess.check_output(["git", *arguments], cwd=ROOT)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="release-output")
    args = parser.parse_args()
    if git("status", "--porcelain").strip():
        raise ValueError("Commit reviewed changes before packaging")
    commit = git("rev-parse", "HEAD").decode().strip()
    plugin = json.loads(git("show", "HEAD:plugins/narrated-demo/plugin.json"))
    version = plugin["version"]
    timestamp = datetime.fromtimestamp(int(git("show", "-s", "--format=%ct", "HEAD")), timezone.utc)
    zip_time = (timestamp.year, timestamp.month, timestamp.day, timestamp.hour, timestamp.minute, timestamp.second // 2 * 2)
    output = (ROOT / args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    files = git("ls-tree", "-r", "--name-only", "-z", "HEAD").decode().rstrip("\0").split("\0")
    manifest = {}
    archive = output / f"narrated-demo-v{version}.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as stream:
        for name in sorted(files):
            if Path(name).suffix.lower() in (".exe", ".onnx", ".bin", ".mp4", ".m4a", ".wav", ".pyc") or any(p in name for p in (".runtime", "test-output", "__pycache__")):
                raise ValueError(f"Private/runtime artifact is tracked: {name}")
            data = git("show", f"HEAD:{name}")
            if b"C:" + b"/Users/" in data or b"C:" + b"\\Users\\" in data:
                raise ValueError(f"Machine-specific path in source: {name}")
            manifest[name] = hashlib.sha256(data).hexdigest()
            info = zipfile.ZipInfo(name, zip_time)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            stream.writestr(info, data)
    record = {"schema_version": 1, "commit": commit, "version": version, "files": manifest, "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest()}
    (output / "FILES.json").write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    (output / "SHA256SUMS.txt").write_text(f"{record['archive_sha256']}  {archive.name}\n", encoding="utf-8")
    print(json.dumps({"archive": str(archive), "commit": commit, "sha256": record["archive_sha256"], "files": len(manifest)}, indent=2))

if __name__ == "__main__":
    main()
