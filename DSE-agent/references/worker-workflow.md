# Shared Worker Workflow

Read this file and your role prompt for an assigned DSE experiment. Main supplies an absolute project root and skill root. Write only your own workspace and result path; do not spawn workers or change shared state.

## Assignment and judgment

Check identity, numerical contract, parent archives, allowed clocks, policy, and total attempt budget against the active directive. Resolve routine implementation details from evidence and document assumptions. Ask Main only for an unresolved material choice, conflicting hard constraints, or missing authority/input; do not request user approval for routine authorized edits or stage transitions.

Treat architecture instructions as either **hard invariants** or **search hypotheses**, as labeled by Main. Preserve hard invariants. Adapt hypotheses within the assigned search region when evidence justifies it; report the reason. Do not invent precision changes, interface changes, tolerance relaxation, benchmark edits, or new budgets.

Write an architecture declaration: modules/dataflow, parallelism, target II with transaction unit, candidate clock, expected bottleneck, resource estimate/range, and uncertainty. A reasoned range or `null` with a rationale is better than a fabricated timing/resource number.

Use the available `vitis-hls-synthesis` skill for HLS implementation, or [../prompts/hls_tool_reference.md](../prompts/hls_tool_reference.md). Read [../prompts/coding_style.md](../prompts/coding_style.md) and [../prompts/hardware_checklist.md](../prompts/hardware_checklist.md).

## One policy, one budget

The default assignment budget is three **total attempts**, including the first. A new source/configuration candidate, changed clock, or replay of a failed tool invocation starts another attempt; moving through stages for the same candidate does not. Track infrastructure-only retries too, so repeated license/tool failures cannot create an unbounded loop. Never reset the budget per stage, clock, or validation failure. Stop earlier if an essential blocker cannot be resolved in scope.

- **Formal:** Csim and Cosim must pass; implementation must produce `WNS >= 0` and routed resources within all benchmark limits, plus any additional declared requirements.
- **Cosim-only:** never run `impl` or `all`. Csim, Csynth, and Cosim are the permitted validation path. Use provisional status and null routed metrics. Check any explicit synthesis-envelope requirements separately.
- A conflict between a formal mode and an implementation ban does not authorize implementation. Report the conflict to Main and retain permitted evidence.

## Candidate sequence

1. Edit role-local source/configuration while preserving the numerical and test contract. Record the attempt and proposed change.
2. **T1:** answer applicable checklist items as pass/fail/not-applicable with reasons; run C simulation. A true correctness, safety, or explicit-requirement failure must be repaired before later stages. A justified N/A or optional optimization not chosen is not a failure.
3. **T2:** synthesize and inspect the schedule, achieved II, estimated resources, warnings, and bottleneck evidence. Compare estimates with the declaration. A greater-than-2x resource discrepancy or missed forecast II requires diagnosis, not automatically code changes: correct the estimate/model and continue if real requirements pass. Repair and retry when an actual hard constraint or functional assumption fails.
4. **T3:** run RTL co-simulation only with a matching successful synthesis receipt. Inspect pass/fail, latency, interval, and deadlock/timeout evidence. If source/configuration changes, rerun Csim and synthesis before accepting later stages.
5. **T4, only when permitted:** run implementation with matching synthesis evidence. Read routed timing and utilization; do not derive final WNS from C synthesis or claim a new validated Fmax from `clock - WNS`.
6. Write the result using [contracts.md](contracts.md). Report completed stages and actual failures even when the budget expires or a tool is unavailable. Main handles archival and promotion.

Use the wrapper at `<skill_root>/src/hls_run.sh <absolute_workspace> <stage>` with `DSE_PROJECT_ROOT=<absolute_project_root>`. Do not bypass its policy or freshness checks by running a prohibited stage directly. Commands operate on assigned inputs; the helper receipt alone does not certify report pass status.

Choose among the supplied clock candidates using current bottleneck evidence. A failed timing run may justify an in-scope pipeline/mapping fix or a different permitted clock, within the same total budget. Never force implementation during a cosim-only task.

## Failure classes

- Functional or numerical failure: repair the implementation without weakening reference tests/tolerance.
- Timing/resource/declared hard-II failure: diagnose the real bottleneck, then make a targeted in-scope change.
- Forecast-only discrepancy: explain/correct the prediction; no mandatory redesign or rerun if acceptance evidence is already sufficient.
- Tool/license/environment failure: inspect logs and use an available authorized recovery; do not change the RTL as a ritual or claim the stage passed.
- Missing authority, incompatible contract, or exhausted budget: preserve evidence and return the precise status. Finishing an assignment is not the same as producing a formal feasible candidate.
