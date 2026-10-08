# Validation and delivery

Validate metadata AND entire decode; inspect decoded-frame PTS, not r_frame_rate alone. Compare planned timing/audio duration and final duration; preserve ending, never -shortest a voice track. Validate speech/subtitle windows and pointer bounds. QA associates SHA256, config hash, UTC timestamp and exact output.

Inspect each settled unit and critical states/validation/scroll/cursor/first-last frames. Use continuous audiovisual review and actual listening only when supported; otherwise not_verified. Silent or duplicate frames may be deliberate holds; review map before labelling freezing. No unsupported probability scores.

Deliver MP4, SRT/VTT, timeline, manifest, QA and coverage. State mock scope, blocked/unimplemented integrations, sampled versus integral review and user approval state. Changed speech requires new audio/subtitle/final checks even if visuals reused.

Test scripts/test_pipeline.py plus a short fixture capture, local voice and render/decode. Tests do not authorize opening product services. Metadata validator is additional, not end-to-end proof. If discovery isn't visible, retry in a new chat/restart; don't claim a successful selector observation without evidence.
