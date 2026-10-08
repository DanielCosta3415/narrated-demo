---
name: setup
description: Prepare the isolated Windows runtime for the Narrated Demo plugin when the user requests installation or repair.
---

# Set up Narrated Demo

Check Windows x64 and whether `%LOCALAPPDATA%/NarratedDemo/runtime/runtime.json` exists. Do not overwrite a working installation without diagnosing it.

Explain that setup downloads Python, Node, Chromium, FFmpeg and local speech weights. Obtain authorization for downloads and local installation; no credentials or admin privileges should normally be needed. Do not modify the user's application repository or global PATH.

The installed plugin is self-contained: locate its root by going two levels up from this setup skill directory. Inspect `installer/Install.ps1` at that plugin root before executing; no extra source checkout or Git installation is required. Run `Install.ps1 -AcceptDownloads` only after authorization. A failed command is not a completed installation. Existing unowned destinations are deliberately refused: keep a beta installation intact and use a new empty destination, rather than forcing adoption.

After setup, use the runtime's Python to execute `app/self_test.py RUNTIME_JSON OUTPUT_DIRECTORY` at the plugin root, with an output directory outside the application repository and outside the managed runtime. This uses fictional data, actual capture, Dora and Alex, technical validation and resume checks. Report failures and distinguish technical success from listening/visual approval. Do not publish generated outputs automatically.

Use `app/runtime.py doctor --runtime RUNTIME_JSON` for diagnostics. Repeat the bundled installer to repair dependencies; versioned directories preserve previous versions. `installer/Maintain.ps1 -Action Rollback -ConfirmAction` verifies the prior configuration before switching. `-Action Uninstall -ConfirmAction` archives the owned runtime instead of recursively deleting it. Both accept an explicit `-Destination`. Obtain authorization for maintenance; do not delete the archived files or alter the user's other plugins.
