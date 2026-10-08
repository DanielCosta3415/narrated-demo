---
name: setup
description: Prepare the isolated Windows runtime for the Narrated Demo plugin when the user requests installation or repair.
---

# Set up Narrated Demo

Check Windows x64 and whether `%LOCALAPPDATA%/NarratedDemo/runtime/runtime.json` exists. Do not overwrite a working installation without diagnosing it.

Explain that setup downloads Python, Node, Chromium, FFmpeg and local speech weights. Obtain authorization for downloads and local installation; no credentials or admin privileges should normally be needed. Do not modify the user's application repository or global PATH.

Use a source checkout of `https://github.com/DanielCosta3415/narrated-demo`, outside the application repository. Inspect `installer/Install.ps1` before executing. Prefer a tagged release when available; this beta has not been independently certified. Run `Install.ps1 -AcceptDownloads` only after authorization. A failed command is not a completed installation.

After setup, use the runtime's Python to execute `tests/self_test.py RUNTIME_JSON OUTPUT_DIRECTORY` with an output directory outside the application repository. This uses fictional data, actual capture, Dora and Alex, technical validation and resume checks. Report failures and distinguish technical success from listening/visual approval. Do not publish generated outputs automatically.
