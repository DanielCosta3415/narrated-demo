# Provenance and licensing

Cutaway source v0.2.0: https://github.com/half144/cutaway ; MIT, Copyright (c)2026 half144. Full notice preserved in scripts/cutaway/LICENSE. Local modifications include full Chromium locale, date/empty input, validation logs and pointer seams; product-specific API hooks removed.

Five v5 scripts were inspected; local synthesis, millisecond mapping, caption splitting, pointer drawing, two-pass loudness, full decode and sampled review informed scripts/pipeline.py. Original copies and hashes remain in extraction provenance outside the skill; they are not executable defaults.

External dependencies, not bundled: kokoro-onnx (MIT; verify installed dist metadata), Kokoro-82M v1.0 weights (Apache-2.0 model card), ONNX model/voice-vector release model-files-v1.1, Playwright (Apache-2.0), NumPy (BSD), SoundFile (BSD), Pillow (HPND). Check transitive components including phonemizer/espeak-ng and ONNX Runtime before redistribution. Voice-vector licensing must be checked separately against release/model attribution; do not assume runtime license covers voices/training data.

https://github.com/thewh1teagle/kokoro-onnx
https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.1
https://huggingface.co/hexgrad/Kokoro-82M
https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md

FFmpeg license depends on build configuration; local libx264-enabled build is GPL, not assumed LGPL. FFprobe also inspect -version build flags. No FFmpeg binaries bundled. Windows Segoe UI is proprietary installed font, not redistributed; a freely licensed installed font may be configured instead.
