"""Exercise actual capture and both local voices using only a fictional fixture."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("runtime")
    parser.add_argument("output")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    skill = root / "plugins/narrated-demo/skills/narrated-demo"
    runtime = json.loads(Path(args.runtime).read_text(encoding="utf-8-sig"))
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    def write(name, content):
        path = output / name
        path.write_text(json.dumps(content, ensure_ascii=False), encoding="utf-8")
        return path
    plan = write("plan.json", {"url": (skill / "assets/fixture.html").as_uri(),
        "viewport": {"width": 1440, "height": 810}, "captureScale": 1,
        "steps": [{"action": "click", "selector": "#save", "validationAudit": True},
                  {"action": "type", "selector": "#description", "text": "Pedido fictício"},
                  {"action": "click", "selector": "#save", "expect": '#result:text-is("Pedido fictício salvo: Pedido fictício")'}]})
    env = dict(os.environ, PLAYWRIGHT_BROWSERS_PATH=runtime["browsers"])
    subprocess.run([runtime["node"], str(skill / "scripts/capture.mjs"), str(plan),
                    str(output / "recording"), runtime["node_deps"], "pt-BR"], env=env, check=True)
    sys.path.insert(0, str(root / "app"))
    from configure import resolve
    for voice in ("Dora", "Alex"):
        before = f"Olá, o meu nome é {voice} e neste vídeo irei demonstrar um pedido fictício."
        units = write(f"units-{voice}.json", {"schema_version": 1, "units": [{
            "id": "save-order", "chapter": "Exemplo", "title": "Pedido fictício", "steps": [0, 1, 2],
            "before": {"text_display": before, "text_tts": before},
            "during": {"text_display": "Preencho a descrição.", "text_tts": "Preencho a descrição."},
            "after": {"text_display": "O pedido foi salvo. Obrigado por acompanhar.", "text_tts": "O pedido foi salvo. Obrigado por acompanhar."},
            "grounding": [{"claim": "Pedido fictício salvo", "status": "confirmed", "evidence": "Expectativa de captura e fixture local"}]}]})
        config = resolve(runtime, output / "recording/timeline.json", units, output / voice, voice)
        cfg = write(f"config-{voice}.json", config)
        subprocess.run([runtime["python"], str(skill / "scripts/test_integration.py"), str(cfg)], check=True)
    print("Captura e validação técnica com Dora e Alex concluídas; revisão humana permanece separada.")

if __name__ == "__main__":
    main()
