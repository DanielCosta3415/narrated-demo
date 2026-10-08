# Capture and evidence

Cutaway v0.2.0 sources are vendored with MIT notice. Adapted capture preserves full Chromium channel, configurable locale, initial pointer seam, empty/date input handling and validationMessage logs. GerenciAr-specific API fixtures were removed. Do not put tokens/storage states in manifests.

Install external Node dependencies in a dedicated runtime (Node >=22, Playwright recovered 1.63.0). Install full Chromium, not just headless shell. Keep binaries external. Use:

```text
node scripts/capture.mjs PLAN.json OUTPUT_DIRECTORY NODE_RUNTIME_DIRECTORY pt-BR
```

NODE_RUNTIME_DIRECTORY must have package.json and resolvable playwright. Wrapper dynamically loads the vendored recorder; no invented Cutaway CLI flags. Plan is actual Cutaway plan schema; inspect scripts/cutaway/plan.mjs when constructing it. Standard click/type/scroll/wait/focus/press and expectations are available. No product startup or fixture API action is executed by the wrapper.

Inspect native validationMessage language before major capture. Use isolated generic HTML fixtures first. Confirm persisted outcomes beyond a visible success toast. Record simulated failures and real fixture concurrency distinctly. Storage state, authenticated capture and fixture mutation require explicit scoped operator handling, not config commands.

Recover partial capture by selecting completed steps only, retaining source hashes and seam state. Join monotonic timelines with explicit offsets, normalized slow-motion and file references. Do not reuse a segment after relevant product/data changes without validating its evidence.

Merge spec: schema_version1, segments array of objects with timeline path and optional completed_steps prefix count. scripts/merge_capture.py rejects incomplete prefixes and mismatched viewport/scale; the operator must verify state continuity and initial pointer seams. Install browser outside sandbox if required by permission policy; PLAYWRIGHT_BROWSERS_PATH can point to an existing authorized browser installation.

Pointer mapping: CSS position / viewport -> encoded source pixels -> aspect-preserving fit/pad -> output. Overlay arrow/I-beam and click halo, check bounds. Distinguish browser screencast cadence from final CFR encoding and reconstructed pointer cadence.
