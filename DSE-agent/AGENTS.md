# Agentic-DSE Project Instructions

The detailed workflow is in [SKILL.md](SKILL.md), invoked as `$run-agentic-dse`. These instructions apply to DSE execution; ordinary code, documentation, review, or diagnostic tasks do not automatically start DSE or create workers.

## Acceptance and authority

A formal Pareto candidate must pass C simulation and RTL co-simulation, have post-implementation `WNS >= 0`, and satisfy the benchmark's routed LUT, FF, BRAM, DSP, and URAM limits and other hard requirements. Synthesis estimates, missing reports, and tool exit codes alone are not formal success.

An explicit `cosim_only_user_override` or implementation ban forbids `impl` and `all`. Complete the requested permitted work with provisional status and null post-implementation metrics. Never ask to bypass this restriction as a routine step or silently promote a provisional point.

Honor explicit approvals, hardware restrictions, finite budgets, and the benchmark's numerical contract. Routine choices and retries inside an authorized task need no repeated confirmation. A material change to scope, precision, interfaces, test vectors, tolerance, external state, or resource authority needs the corresponding user authorization.

## Roots and ownership

Resource paths are relative to the skill root; experiment paths below are relative to the explicitly selected project root. Installing or editing this package does not initialize a DSE project.

Project designs, knowledge bases, experiment results, reports, manifests, archives, and machine-specific configuration are private runtime data, not publishable skill resources. Copying or publishing a skill does not authorize disclosure of those artifacts. Keep them outside the distributed package, use synthetic fixtures, and review an explicit file allowlist before any publication. Disclosure of project-derived material requires the user's approval of the specific artifacts and destination.

- `benchmarks/` or legacy `designs/`: read-only references during exploration; edit only when the user requests a benchmark change.
- `workspace/<role>/` and `results/<role>.json`: the corresponding worker's only writable paths.
- `state/`: Main is the sole writer.
- `knowledge/`: Main is the sole writer; verified experimental lessons must retain evidence and scope. Hypotheses are labeled separately.
- `tmp/<run_id>/`: Parser and Architect may write only their assigned proposal files. Main checks and promotes proposals; these roles never directly edit shared state or learned knowledge.
- `archive/`: Main adds immutable snapshots; do not overwrite existing ones. Preserve candidate sources, configuration, test inputs, reports, receipts, and results before workspace reuse or a requested reset.

## Delegation during actual DSE

This file explicitly authorizes three role workers for an actual DSE round, not for unrelated maintenance tasks.

- Create fresh Explorer, Exploiter, and Innovator identities for each round. Retire completed workers after collection and archival; do not retrigger them for later rounds.
- Parser and Architect have a data dependency: run them sequentially or complete both locally.
- Worker assignments must be self-contained, with absolute resource/project paths, benchmark/run/candidate IDs, inputs, architecture constraints, numerical contract, parents, allowed clocks, validation policy, total attempt budget, and output contract.
- Workers may run in parallel because their write paths do not overlap. If capacity is limited, batch all three roles; do not remove a role or share workspaces.
- Workers do not write shared state, learned knowledge, other workers' paths, or nested worker outputs, and do not spawn subagents.
- Main waits for every worker before validating, archiving, and updating the population and knowledge.

## Tools and checks

Use the tools actually provided by the host; do not assume a particular vendor's tool-call syntax. Prefer targeted searches and patch-based edits.

Run the wrapper with an absolute workspace path and the selected project root:

```bash
DSE_PROJECT_ROOT=/absolute/project /absolute/skill/DSE-agent/src/hls_run.sh /absolute/project/workspace/explorer csynth
```

Use the available `vitis-hls-synthesis` skill for kernel or tool-specific work; otherwise read `prompts/hls_tool_reference.md` and the relevant coding guidance. Check uncertain or version-dependent technical facts against installed tools or primary AMD documentation. Do not install tools or dependencies merely to answer status.

For package maintenance, run relevant unit tests, Python syntax checks, and `bash -n src/hls_run.sh`. Validate touched JSON files; do not require a live `state/` directory or launch HLS for ordinary documentation edits. For experiments, follow the policy-specific report gates in `references/worker-workflow.md`.
