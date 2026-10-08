# Contracts v1

All owned JSON uses schema_version: 1. External Cutaway v0.2.0 timeline uses version: 1; adapt deliberately, do not relabel it as a skill contract.

Config: assets/config.example.json; paths relative to configuration file. Executables are explicit paths or PATH names, never shell strings. No credentials or arbitrary startup hooks. Resolved configuration and hashes are persisted per run. Mode enum: demo/tutorial/revise-narration/select-voice/resume/validate.

Units: assets/units.example.json. Unique id, chapter, title, nonempty ordered step indexes. before/during/after each has text_display and text_tts. Optional phases may be empty in demo. Tutorial requires before and after; useful long-action commentary is authored, not generic filler. Every unit has grounding entries: claim, status (confirmed/supported_with_limits/unverified), evidence. Never narrate an unverified claim as fact.

Coverage statuses: demonstrated, blocked, not_implemented, out_of_scope, not_applicable. demonstrated references valid unit IDs. Record missing flows; do not fabricate completeness.

Capture: frames with t/file; pointer points t/x/y in CSS pixels; clicks; cursors; steps start/expectationEnd; viewport width/height; capture scale; duration and complete status. External version checked. All times in seconds without early rounding; FFmpeg concat timebase 1ms. No frame duplication claim as native compositor 60fps.

Output timeline contains parts, source spans, holds, global speech/caption windows and total duration. Before speech must finish before motion starts. Speech/captions ordered and nonoverlapping. Time mapping normalizes explicit Cutaway slowdown only; not arbitrary speed-up.

Manifest: exact tool versions, input/output hashes, config, stage signatures and status. Cache hit requires input signature AND output hash. Model/voice/text => audio; capture => source; pacing/text => composition; subtitles/output => final QA. A changed final file invalidates all prior whole-file QA.

QA status enum: pass/fail/not_verified. Categories: technical integrity, visual sampling, continuous audiovisual review, perceptual listening, user approval. Technical success never upgrades other categories. Reuse visual review only with identical visual-clips/layout hashes and disclose reuse.
