# Local voice quality

Approved profile evidence recovered from review.py: Kokoro ONNX 0.6.1, model v1.0, Dora pf_dora and Alex pm_alex, pt-br, speed1, trimFalse, sentence_pause0/clause_pause0. Zero configured pauses does not remove natural pauses. Faber is excluded from automatic choice. Profile preference approval is not full-video approval.

Model files remain external; expected SHA256 is in assets/voices.json. Inspect model/runtime versions and speaker availability; do not silently replace. Generate new comparable samples only on material profile/model change or user request. Native waveform plus processed audio duration measured, no phoneme-edge trim, crossfaded speech or header-only resampling.

Default new-run target -16 LUFS ±1LU, true peak <=-1dBTP; preserve project-approved overrides. v5 used -18 LUFS/-2dBTP and final check <=-1.5dBTP. Two-pass loudnorm then decode final AAC and measure again. STT/correlation cannot establish naturalness or pronunciation.

Subtitles: UTF-8 SRT/VTT separate; <=2 lines segmented by sense. external/selectable/burned-in/both configurable. v5 used burned ASS. Do not use licensed Windows fonts as redistributed assets; allow installed fallback. Confirm final legibility and reading time visually.
