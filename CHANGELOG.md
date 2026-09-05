# Changelog

## 2026-09-06 — High-Capability Model Instruction Refresh

This update adapts the FPGA skill suite for more capable reasoning models, including intended users of GPT-6 and Claude Fable 5.1. It reduces unnecessary procedural friction while retaining explicit approval requirements and evidence-based completion criteria. It does not claim measured improvements in model capability, runtime, Fmax, or design quality.

### Added

- A ninth skill, [vivado-timing-closure](vivado-timing-closure/SKILL.md), with constraint-baseline validation, iterative optimization, diagnosis, advanced-optimization references, methodology guidance, and English evaluation fixtures.
- `agents/openai.yaml` UI metadata for all nine skills without pinning a model or changing runtime permissions.
- A focused [debug troubleshooting reference](vivado-debug/references/debug-troubleshooting.md), retaining detailed guidance outside the main skill entrypoint.

### Changed

1. **Execution and analysis cooperate.** The TCL skill can inspect exit status, logs, reports, and requested artifacts, and consult related skills while completing an authorized task. A handoff between skills is not a new approval gate.
2. **Completion requires full acceptance.** WNS reaching zero or a favorable QoR score starts final verification; it does not establish closure or automatically authorize bitstream generation. Setup, hold, pulse width, routing, full constraints, applicable design checks, and requested deliverables must all be accounted for.
3. **A plateau ends a strategy loop, not the task.** Progress includes TNS and failing endpoints as well as WNS. Preserve the best candidate, reassess evidence-backed alternatives within existing limits, and explicitly report incomplete closure when no feasible authorized path remains.
4. **Routine context is inferred before asking.** Reuse the established Project/Non-Project flow and infer HLS settings from files and prior instructions. Ask only for consequential missing information; do not invent required device or clock values for execution.
5. **The existing constraint baseline is preserved.** `reset_timing` is no longer a default diagnostic step. Any isolated reduced-I/O experiment is provisional and must restore the full intended constraints before acceptance. IP constraints remain protected.
6. **Physical-optimization stages are distinguished.** Post-place optimization is not blocked by a post-route prerequisite. Tool-managed optimization is correctly identified as potentially modifying the netlist, even when RTL is unchanged.
7. **Workflows match the requested outcome.** Report review, script generation, simulation, implementation, export, and hardware programming are separate scopes. GUI wizards, additional strategies, and parallel runs are not universal prerequisites.
8. **Optional helpers have explicit fallbacks.** Native Vivado analysis remains available when custom helpers or RapidWright are absent. Use documented dry-run/test options only when supported, and validate manual netlist changes on a copy before adopting them.
9. **Overwrite behavior is scoped.** `-force` examples assume replaceable task-owned outputs or an already-authorized overwrite. Otherwise prefer a fresh path; request approval only when an unauthorized overwrite is necessary.
10. **Synthesis attribute guidance is consistent.** `KEEP` is distinguished from `DONT_TOUCH`; the latter supports RTL and XDC, with RTL placement needed when the object could disappear before XDC processing.

### Packaging and Language

- Updated the README for the nine-skill layout, intended model audience, usage examples, and verification limits.
- Translated the remaining Chinese skill documentation and evaluation text into English. Timing-diagnosis expectations distinguish hypotheses from confirmed causes and retain request-scoped execution.
- Replaced a machine-specific simulation evaluation-runner path with a configurable location. The runner remains an optional external dependency; no model evaluation is triggered by installing or reading the skills.
- Preserved existing HDL/HLS examples without line-ending-only rewrites, the DSE agent prompt set, and the repository license.
- Kept workstation-specific workspace instructions and local paths out of the published package.

### Authorization Boundaries Retained

More procedural autonomy does not mean broader authority. Explicit limits on RTL, netlist, interfaces, constraints, clock targets, runtime, resources, overwrite operations, tool installation, external actions, and hardware programming remain binding. Read-only requests do not authorize design changes. Missing verification is reported as unverified, never passed.

### Validation

- Skill frontmatter, names, descriptions, and UI metadata checked across all nine skills.
- Local documentation links, Markdown fences, JSON evaluation fixtures, and English-language text checked in the updated package.
- Simulation evaluation-wrapper shell syntax and non-executing CLI paths checked.
- Fenced TCL snippet completeness checked, with success/failure behavior tested for the revised error-handler examples.
- No live model benchmarks, Vivado/Vitis builds, timing-closure experiments, bitstream generation, or hardware operations performed for this release.
