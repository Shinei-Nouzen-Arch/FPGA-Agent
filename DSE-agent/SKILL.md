---
name: run-agentic-dse
description: Initialize, run, resume, and inspect FPGA HLS design-space exploration with Explorer, Exploiter, and Innovator workers. Also use for read-only requirement review, architecture advice, Pareto analysis, and convergence diagnosis without automatically launching experiments.
---

# Agentic-DSE

Use capable-model judgment to choose evidence-backed experiments within the user's objective, numerical contract, validation policy, and budget. A request to explain or inspect does not authorize an experiment.

## Roots and routing

- **Skill root** is the directory containing this file: generic prompts, references, scripts, and synthetic tests are resources, not the active experiment.
- **Project root** is the user's selected DSE project: benchmark inputs, runtime state, worker workspaces, results, and archives live there. Resolve both roots to absolute paths before acting; do not assume they coincide.
- Read [AGENTS.md](AGENTS.md) for ownership and delegation rules. For initialization or execution also read [references/contracts.md](references/contracts.md).
- `init req`, `run dse`, and `show pareto` are natural-language intent labels, not shell commands. Keep the package directory named `DSE-agent`; its compatible invocation name is `$run-agentic-dse`.

| Intent | Scope |
| --- | --- |
| Review requirements, suggest architecture, diagnose convergence | Read available inputs and relevant prompts; return analysis or proposals without writing state or running HLS |
| Initialize or prepare a run | Create missing, authorized project state and workspace inputs; no experiments unless requested |
| Run or continue DSE | Execute the authorized round budget, including routine in-scope fixes and validation |
| Show status or Pareto | Read state and reports; optional read-only HV calculation; no initialization or repair |
| Reset or switch benchmark | Archive existing state and evidence first; reset only the user-requested scope |

Missing runtime files are not a reason to refuse read-only advice. State what can be established and which evidence is absent. Do not silently turn a diagnostic request into a repair.

## Publication boundary

Keep project-specific designs, benchmark inputs, experiment records, learned knowledge, reports, input manifests, archives, and local environment details in the private project directory. This skill package does not bundle a project's knowledge base or target configuration.

A request to copy, update, or publish the skill authorizes generic skill resources, not disclosure of local development content. Review an explicit file allowlist before publication. Use synthetic examples and placeholders; publish project-derived material only when the user explicitly approves those specific artifacts for that destination. This boundary does not prevent authorized local experiments or read-only analysis.

## Initialize or reconcile an authorized run

1. Identify the benchmark from the request and project context. Support an existing `benchmarks/<name>/` or legacy `designs/<name>/` layout; do not rename it. Read its source, testbench, configuration, and `objectives.json` or `spec.json`. Preserve reference implementations, test vectors, interfaces, arithmetic behavior, and tolerances.
2. Use [prompts/req_parser.md](prompts/req_parser.md) with [src/req_parser_schema.json](src/req_parser_schema.json). First resolve facts from the conversation and selected project. Distinguish blocking decisions from optional preferences. Ask at most three real blockers at a time, retaining the rest; uncertainty in an estimate is not an approval gate.
3. Run the Parser and then [prompts/architect.md](prompts/architect.md) sequentially, normally locally. Their outputs are proposals under `tmp/<run_id>/`; only Main promotes checked proposals into shared state.
4. Main records one validation policy and execution budget for the assignment chain. A requested formal DSE run authorizes its normal synthesis, simulation, and implementation stages unless restricted by the user or host. An explicit implementation ban takes precedence. Do not ask again for stages already authorized; do not expand authority to hardware programming, external publication, installations, paid services, or semantic changes.
5. For a new authorized run, create only missing runtime files, with consistent benchmark and run identity:
   - `state/search_directive.json` and `state/architecture_decisions.json`;
   - `state/pareto_front.json` and `state/lineage.json` as empty arrays;
   - `state/agent_contributions.json` as an empty object;
   - `knowledge/learned/successful_configs.json` and `failure_cases.json` as empty arrays, and `learned_hints.json` as an empty object;
   - `results/`, `tmp/`, and separate `workspace/<role>/src` and `tb` trees, seeded from the selected benchmark with a usable role-local `config.cfg`.
6. Preserve existing state and user edits. Infer or migrate unambiguous legacy metadata without inventing validation. Reconcile missing files from existing evidence; do not erase a population merely because one file is absent. A conflicting active benchmark needs the requested switch/archive procedure, not silent replacement.
7. Record target facts from the selected project or installed tools in private project state. Do not package a real project's platform profile as a public default. Missing optional HV configuration or architecture estimates need not block an otherwise executable run.

## Execute rounds

1. Read the current directive, architecture decisions, population, lineage, and contributions. Validate their benchmark, policy, and numerical-contract consistency. Check required tools and input files without launching expensive work just to inspect status.
2. Main selects parents from immutable, evidence-backed candidates and defines one bounded assignment per role. With zero parents, use three explicitly labeled seed assignments; with one parent, Innovator uses a single-parent seed variant. Only call an operation crossover when it actually has two parents.
3. For **each actual DSE round**, create fresh Explorer, Exploiter, and Innovator workers using [prompts/explorer.md](prompts/explorer.md), [prompts/exploiter.md](prompts/exploiter.md), and [prompts/innovator.md](prompts/innovator.md). Include the shared [references/worker-workflow.md](references/worker-workflow.md), absolute input/output paths, identities, numerical contract, policy, allowed clocks, parents, goals, and total attempt budget. Batch roles if concurrency is limited; do not omit a role or start nested workers.
4. Workers run only policy-permitted stages in their own workspaces. Default to **three total attempts per assignment: initial attempt plus two retries**, shared across all clocks, edits, and stages. Use a different explicit task budget when supplied.
5. Wait for all three workers to finish. Main checks reports against the candidate input digest and stage receipts, functional pass evidence, clock and metric units, and the selected policy. An exit code or synthesis estimate alone is not formal acceptance.
6. Before reusing any worker workspace, archive its result, source/header/test data, configuration, input manifest, stage receipts, and reports under a new round/candidate path. Use [src/artifacts.py](src/artifacts.py) or an equivalent checked snapshot. Never overwrite an existing archive. Pareto and parent references must point to immutable archives, not mutable workspace files.
7. Main alone updates state, lineage, contributions, and learned knowledge. Admit only fully validated formal successes to the formal Pareto population. Keep cosim-only results in a separate provisional population; do not promote them or mix their metrics into formal HV.
8. If a fixed, benchmark-specific HV configuration is available, run [src/hypervolume.py](src/hypervolume.py). Record the actual algorithm, configuration ID, population, reference point, result status, and value. Keep missing metrics as `null`; never substitute a platform limit or a guessed clock.
9. Apply the stopping mode below. For the next authorized round, archive the previous round and retire its workers before creating fresh identities. No per-round reapproval is needed within the existing scope and budget.
10. Report actual rounds, accepted/rejected/provisional candidates, best validated metrics, preserved artifacts, remaining failures, and the termination reason. Task completion and engineering success are separate: a requested cosim-only or fixed-budget run can finish without producing a formal feasible design.

## Stopping and completion

- **Fixed rounds:** `run dse <benchmark> N` means exactly N rounds unless a user stop, exhausted execution limit, unavailable essential capability, or authority/input blocker prevents continuation. Without N, run one round. A low HV improvement alone does not truncate a fixed-round request.
- **Until converged:** requires a finite maximum-round budget. Use an existing project budget; if none exists, obtain that consequential limit before starting an open-ended run. The default criterion is three consecutive relative improvements below 2%, computed over comparable, valid, nonempty formal populations with the same HV configuration ID.
- Compute relative improvement against the preceding positive HV. Missing, empty, invalid, zero-baseline, unavailable, or differently configured values do not count as low improvement. A decrease requires consistency/regression diagnosis, not a convergence claim.
- When convergence cannot be measured, continue safe work within the authorized budget using available engineering evidence; report that convergence is undetermined.
- Distinguish `fixed_rounds_complete`, `converged`, `budget_exhausted`, `blocked`, and `user_stopped`. Separately record whether there is a `formal_feasible_point`, `provisional_only`, or `no_feasible_point`. Do not call a plateau, failed run, or incomplete report set successful closure.

## Status and recovery

Read only the evidence that exists. The HV helper returns structured unavailable/error states and does not install dependencies or write state. Its absence or missing optional numerical libraries must not hide the benchmark, completed rounds, available points, failures, or missing reports.

Use host-provided tools and respect their sandbox/approval decisions. If an essential command is denied, complete unaffected in-scope work and report the precise blocker. Preserve the best candidate and archive before any requested reset; never reset or modify an unrelated project or installed skill.
