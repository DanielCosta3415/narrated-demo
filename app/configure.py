"""Resolve dependency paths without requiring a user's manual JSON editing."""
import argparse
import json
import os
from pathlib import Path


def resolve(runtime, recording, units, output, voice):
    if voice not in ("Dora", "Alex"):
        raise ValueError("Escolha Dora ou Alex")
    required = ("model", "voices", "ffmpeg", "ffprobe", "python", "node")
    for key in required:
        if not Path(runtime[key]).is_file():
            raise ValueError(f"Dependência ausente: {key}")
    return dict(schema_version=1, mode="tutorial", project="Software", module="Tutorial",
                recording=str(Path(recording).resolve()), units=str(Path(units).resolve()),
                output_dir=str(Path(output).resolve()), voice=voice,
                **{key: runtime[key] for key in ("model", "voices", "ffmpeg", "ffprobe")},
                width=1920, height=1080, fps=60, subtitle_mode="both",
                font="Segoe UI", font_size=30, lufs=-16, true_peak=-1, lexicon={}, coverage=[])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", default=str(Path(os.environ.get("LOCALAPPDATA", ".")) / "NarratedDemo/runtime/runtime.json"))
    parser.add_argument("--recording", required=True)
    parser.add_argument("--units", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--voice", choices=("Dora", "Alex"), default="Dora")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    runtime = json.loads(Path(args.runtime).read_text(encoding="utf-8-sig"))
    config = resolve(runtime, args.recording, args.units, args.output, args.voice)
    target = Path(args.config)
    if target.exists():
        parser.error("O arquivo de configuração já existe; escolha outro caminho.")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    print(target.resolve())


if __name__ == "__main__":
    main()
