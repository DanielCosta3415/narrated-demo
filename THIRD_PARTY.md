# Componentes de terceiros

O código adaptado de Cutaway v0.2.0 mantém a licença e o copyright em `plugins/narrated-demo/skills/narrated-demo/scripts/cutaway/LICENSE`.

Os downloads do instalador não passam a ser MIT: uv e Node têm suas licenças próprias; Playwright e ONNX Runtime são Apache-2.0/MIT conforme o componente; Kokoro-82M declara Apache-2.0. Consulte também os termos e as atribuições das vozes na origem. FFmpeg compilado com libx264 pode ser GPL. Não redistribua os binários sob a licença deste código.

- https://github.com/half144/cutaway
- https://github.com/astral-sh/uv
- https://nodejs.org/en/about/previous-releases
- https://github.com/microsoft/playwright
- https://github.com/thewh1teagle/kokoro-onnx
- https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md
- https://ffmpeg.org/legal.html

FFmpeg e FFprobe da candidata: build Gyan 9.0.2 essentials, GPLv3. Download e licença/source provenance: https://github.com/GyanD/codexffmpeg/releases/tag/9.0.2 e https://www.gyan.dev/ffmpeg/builds/ . O ZIP baixado mantém LICENSE e documentação; não incluímos esses binários na distribuição MIT.

Kokoro e vetores Dora (`pf_dora`)/Alex (`pm_alex`) são baixados da release upstream e ficam fora do pacote de código. Consulte o model card e VOICES.md: MIT do wrapper não substitui termos do modelo e seus componentes. Phonemizer/espeak-ng têm componentes GPL e permanecem separados, com seus metadados/licenças no ambiente baixado. Segoe UI é uma fonte do Windows e não está incluída.

Documentação técnica não substitui parecer jurídico. Não prometemos direitos sobre pessoas, dados de treinamento ou uso indevido de vozes.
