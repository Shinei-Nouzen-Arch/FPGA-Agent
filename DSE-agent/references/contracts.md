# Runtime and Evidence Contracts

## Directive and assignments

Main records the effective directive once from the authorized task. Preserve existing equivalent schemas by explicitly mapping fields; do not silently reinterpret a restriction.

A directive contains:

- `benchmark`, `run_id`, absolute `project_root`, selected benchmark paths, target part, and the numerical contract (types, rounding/overflow behavior, interfaces, tolerance, and reference-test identity).
- `validation_policy.mode`: `formal` or `cosim_only_user_override`; `implementation_allowed`: a Boolean. Formal execution requires implementation authorization. Any explicit implementation ban wins over a contradictory mode until Main resolves the directive from the user's instructions.
- `execution.mode`: `fixed_rounds` or `until_converged`; finite `max_rounds`; `max_attempts_per_assignment` (default 3 total, not 3 retries); any wall-time, concurrency, license, or compute limits.
- `clock_preference`: existing permitted periods in ns, ordered by the current objective. A frequency requirement uses `clock_ns = 1000 / frequency_mhz` without coarse rounding.
- Benchmark hard constraints and soft objectives, kept distinct. Resource ceilings cover LUT, FF, BRAM_36K, DSP, and URAM; a verified unsupported resource may have a zero ceiling. Do not invent missing device capacities.
- Optional `hv_config`: a fixed benchmark-specific comparison definition, not an adaptive normalization.

Before assigning work, Main creates `workspace/<role>/.dse/assignment.json` with:

```json
{
  "benchmark": "selected-benchmark",
  "run_id": "unique-run-id",
  "candidate_id": "round-001-explorer",
  "role": "explorer",
  "validation_policy": {
    "mode": "formal",
    "implementation_allowed": true
  },
  "max_attempts": 3,
  "input_paths": ["src", "tb", "config.cfg"]
}
```

This is an illustrative shape, not permission to choose the example policy. Copy the actual policy from the directive. Include all source/header/test-data/configuration dependencies in `input_paths`; use role-local copies of benchmark inputs. Exclude generated tool output. Every listed path must stay inside the role workspace. Arbitrary external includes or data files must first be brought into the assigned input tree by Main when authorized; do not silently read an untracked dependency.

The wrapper hashes the assignment context, complete listed input trees, and configuration. It requires unchanged successful synthesis evidence before cosim or implementation. A receipt proves command completion against those bytes, not functional correctness or formal acceptance; inspect the reports as well. A configuration/source/header/test-data change invalidates the evidence. A stage with missing or stale output cannot produce a successful receipt.

## Candidate result

Every result has `id`, `benchmark`, `run_id`, `role`, `status`, `parent` (always an array), `operator`, `attempts`, `architecture_declaration`, `changes`, `rationale`, `iteration_log`, `metrics`, `estimated_metrics`, `validation`, and `artifacts`.

Status is one of:

- `success`: all formal gates passed for this exact candidate.
- `failed`: the formal flow completed enough to establish a failed gate.
- `provisional_pass` or `provisional_fail`: the requested cosim-only validation passed or failed.
- `blocked`: an essential input, capability, or authority is unavailable; retain completed evidence.
- `budget_exhausted`: an assignment ended at its limit before acceptance.

Canonical measured metrics (unknown values remain null):

```json
{
  "latency_cycles": null,
  "clock_ns": null,
  "latency_ns": null,
  "ii_cycles": null,
  "ii_ns": null,
  "lut": null,
  "ff": null,
  "bram_36k": null,
  "dsp": null,
  "uram": null,
  "wns": null,
  "cp_post_impl_ns": null,
  "power_w": null
}
```

Use measured co-simulation cycles/interval and the recorded clock to derive latency and interval in ns. State the transaction unit for II/throughput. An absent II is not automatically equal to latency. BRAM_18K is converted to BRAM_36K equivalents explicitly; an ambiguous legacy `bram` field needs unit metadata before conversion. Zero is legitimate only when measured or explicitly confirmed, never a placeholder.

Routed LUT/FF/BRAM/DSP/URAM, WNS, post-implementation critical path, and power are null when implementation did not run. Put synthesis resources and architecture predictions under `estimated_metrics` with their source/stage. Cosim-only constraints on synthesis estimates do not turn them into measured routed resources.

`validation` records policy, each stage status, report paths, input digest, and Main's acceptance checks. `artifacts` records the workspace manifest and receipts initially, then immutable archive paths after collection. Main verifies the wrapper receipts using `artifacts.py verify`, checks report contents and acceptance, and records `validation.formal_eligible: true` only after all formal checks. Never import an old point as formal merely because it lacks a status field.

## Archive and shared-state promotion

Main archives every result before reusing the role workspace, even failed/provisional attempts with useful evidence. Use:

```bash
python3 /absolute/skill/DSE-agent/src/artifacts.py archive /absolute/project/workspace/explorer /absolute/project/results/explorer.json /absolute/project/archive/run-id/round-001/explorer
```

The archive contains a snapshot manifest and copied workspace evidence/result. Existing destinations are rejected. Treat an interrupted/incomplete archive as incomplete; use a fresh destination after investigating, never overwrite it. The helper rejects symlinks so an archive cannot silently retain mutable external files.

Before promoting a successful candidate, verify its input digest and each stage receipt/report hash, the numerical/test contract, measured metrics, hard constraints, and archival completeness. Store candidate references in the population and lineage using the archive location. Keep current best and nondominated candidates even when later attempts fail.

Parser and Architect write temporary proposals only. Main validates types, limits, identity, consistency, and user authority before writing shared files. Learned lessons cite their experiment and stage; catalog ideas and historical proposals remain hypotheses until current evidence supports them.

## Hypervolume

All configured objectives are minimized. Default objective suggestions are latency_ns, ii_ns, LUT, BRAM_36K, and DSP; only enable objectives with meaningful, available measurements. Use **ii_ns**, not ii_cycles, when comparing clocks. An explicit ii_cycles objective is valid only for a population with one known common clock.

`hv_config` fields:

```json
{
  "algorithm": "pymoo_exact_nd",
  "population": "formal",
  "objectives": ["latency_ns", "ii_ns", "lut", "bram_36k", "dsp"],
  "reference_point": {
    "latency_ns": 100000,
    "ii_ns": 10000,
    "lut": 10000,
    "bram_36k": 100,
    "dsp": 100
  }
}
```

Numbers above illustrate the schema only. Main selects and records an appropriate fixed reference from actual benchmark limits or an explicitly documented baseline, before comparing rounds. It must be finite, positive, and worse than the intended population. The script does not choose or grow it. Out-of-reference points invalidate that comparison and are reported; do not silently drop them and call the remainder converged.

A changed benchmark, run, objective order/units, population, reference, algorithm, or backend version starts a new comparison series. Record the returned `config_id` with each HV value. No approximation may be labeled exact. If NumPy/pymoo is unavailable, HV is null and status remains readable; do not install anything without the relevant authority.

Missing or invalid objective values exclude that point with a reason and make the result partial, not convergence-ready. Unknown metrics are never replaced with zeros, clock defaults, or reference-point values. Empty formal populations and zero-baseline histories are not convergence evidence.
