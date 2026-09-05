<a name="top"></a>

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/fpga-agent-icon-dark.png">
  <source media="(prefers-color-scheme: light)" srcset="assets/fpga-agent-icon.png">
  <img src="assets/fpga-agent-icon.png" alt="FPGA-Agent logo" width="144" height="144">
</picture>

<h1>FPGA-Agent</h1>

<p><strong>From HLS and RTL to timing closure — with skills built for agent-driven FPGA work.</strong></p>
<p>AMD Vivado / Vitis engineering skills &nbsp;·&nbsp; Multi-agent design-space exploration</p>

<p>
  <a href="#skills"><img src="https://img.shields.io/badge/FPGA_skills-9-0F766E?style=flat-square" alt="9 FPGA skills"></a>
  <a href="#dse"><img src="https://img.shields.io/badge/Agentic--DSE-3_worker_roles-4F46E5?style=flat-square" alt="Agentic-DSE: 3 worker roles"></a>
  <a href="#workflow"><img src="https://img.shields.io/badge/AMD-Vivado_%2F_Vitis-334155?style=flat-square" alt="AMD Vivado and Vitis"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-GPL--2.0-A16207?style=flat-square" alt="GPL-2.0 license"></a>
</p>

<p><strong>English</strong> &nbsp;|&nbsp; <a href="README.zh-CN.md">简体中文</a></p>

<p>
  <a href="#start">Quick start</a> &nbsp;·&nbsp;
  <a href="#skills">Skill library</a> &nbsp;·&nbsp;
  <a href="#workflow">Workflows</a> &nbsp;·&nbsp;
  <a href="#dse">Agentic-DSE</a> &nbsp;·&nbsp;
  <a href="#resources">Resources</a>
</p>

</div>

---

## Two ways to work

| Focused FPGA engineering | Multi-agent exploration |
| --- | --- |
| Nine reusable skills covering HLS, synthesis, constraints, implementation, analysis, timing closure, simulation, TCL, and hardware debug. | A Main Agent coordinates Explorer, Exploiter, and Innovator workers to search architecture, pragma, parameter, and clock choices. |
| **Start with:** a design, report, script, or engineering question. | **Start with:** a benchmark, numerical contract, objectives, and a bounded search budget. |
| [Browse the skills →](#skills) | [Explore Agentic-DSE →](#dse) |

<a name="start"></a>

## Quick start

1. **Choose an entry point.** Pick a skill from the library below, or use [DSE-agent](DSE-agent/SKILL.md) for design-space exploration.
2. **Make the folder available to your agent.** Use your platform's skill mechanism, or provide its `SKILL.md` and supporting resources directly. Keep the folder intact and preserve existing installations unless replacing them is part of your request.
3. **Describe the outcome and boundaries.** Specify whether you want analysis, script generation, execution, or optimization. Related skills can work together within the same authorized task.

| Your goal | Example request |
| --- | --- |
| Understand a report | "Review this timing report and explain the likely bottleneck. Do not change the design." |
| Prepare automation | "Generate a batch TCL script for the existing project, but do not run it." |
| Run implementation | "Run the existing implementation flow and verify the requested outputs. Preserve the constraints and do not program hardware." |
| Improve timing | "Improve timing within the current RTL and clock target, keep the best candidate, and report any remaining acceptance failures." |

The skills use AMD Vivado/Vitis **2025.2 documentation** as their primary baseline. Use the commands and device support available in your installed toolchain.

<a name="skills"></a>

## Skill library

| Skill | What it covers | AMD guides |
| --- | --- | --- |
| [vitis-hls-synthesis](vitis-hls-synthesis/SKILL.md) | C/C++ to RTL, pragmas, interfaces, dataflow, pipelining, burst optimization, and stage-specific checks | UG1399 |
| [vivado-synth](vivado-synth/SKILL.md) | Synthesis strategies, resource inference, attributes, FSM encoding, hierarchy, and OOC/incremental synthesis | UG901 |
| [vivado-constraints](vivado-constraints/SKILL.md) | Clocks, I/O delays, timing exceptions, CDC, physical constraints, and XDC debugging | UG903 |
| [vivado-impl](vivado-impl/SKILL.md) | Placement, routing, physical optimization, congestion, incremental implementation, and ECO tactics | UG904 |
| [vivado-analysis](vivado-analysis/SKILL.md) | Timing paths, QoR, methodology, utilization, diagnosis, and acceptance evidence | UG906 |
| [vivado-timing-closure](vivado-timing-closure/SKILL.md) | Constraint baselines, iterative optimization, best-candidate preservation, and final timing acceptance | UG949 · UG1292 · XTP301 |
| [vivado-sim](vivado-sim/SKILL.md) | Behavioral/netlist/timing simulation, xsim, third-party simulators, and SAIF/VCD | UG900 |
| [vivado-tcl](vivado-tcl/SKILL.md) | Script generation and review, authorized batch execution, result verification, and requested outputs | UG835 · UG892 |
| [vivado-debug](vivado-debug/SKILL.md) | ILA, VIO, JTAG-to-AXI, debug insertion, clock requirements, and hardware troubleshooting | UG908 |

<a name="workflow"></a>

## Engineering workflows

```text
HLS C/C++  →  RTL  →  Synthesis  →  Implementation  →  Timing verification
```

| Along the flow | Skills to use |
| --- | --- |
| Constraints and report analysis | `vivado-constraints` + `vivado-analysis` |
| Iterative timing improvement | `vivado-timing-closure` + `vivado-impl` |
| Simulation throughout development | `vivado-sim` |
| TCL automation across stages | `vivado-tcl` |
| Hardware debug, when requested and authorized | `vivado-debug` |

<details>
<summary><strong>How the skills connect</strong></summary>

Select the supporting skill for the next required activity; these connections do not require every task to run the full flow.

| Starting point | Supporting skills |
| --- | --- |
| `vitis-hls-synthesis` | Implementation: `vivado-impl`; timing: `vivado-analysis`; constraints: `vivado-constraints`; RTL simulation: `vivado-sim`; debug: `vivado-debug`; automation: `vivado-tcl` |
| `vivado-synth` | Execution: `vivado-tcl` |
| `vivado-constraints` | Execution: `vivado-tcl`; report interpretation: `vivado-analysis` |
| `vivado-impl` | Scripting: `vivado-tcl`; synthesis: `vivado-synth`; constraints: `vivado-constraints`; analysis: `vivado-analysis`; HLS changes: `vitis-hls-synthesis` |
| `vivado-analysis` | Commands: `vivado-tcl`; constraint changes: `vivado-constraints`; implementation tactics: `vivado-impl` |
| `vivado-timing-closure` | Evidence: `vivado-analysis`; constraints: `vivado-constraints`; tactics: `vivado-impl`; automation: `vivado-tcl` |
| `vivado-debug` | Scripting: `vivado-tcl`; implementation: `vivado-impl`; timing: `vivado-analysis`; HLS debug options: `vitis-hls-synthesis` |
| `vivado-sim` | Automation: `vivado-tcl`; HLS co-simulation: `vitis-hls-synthesis` |
| `vivado-tcl` | Debug decisions: `vivado-debug`; analysis: `vivado-analysis`; HLS IP integration: `vitis-hls-synthesis` |

</details>

<a name="dse"></a>

## Agentic-DSE

**Explore the design space, preserve the evidence, and retain the best candidates.**

[Agentic-DSE](DSE-agent/SKILL.md) separates orchestration from candidate implementation. Main handles requirements, architecture proposals, assignments, evidence checks, archival, Pareto selection, and learned knowledge.

| Worker | Search behavior | Cold-start behavior |
| --- | --- | --- |
| **Explorer** | Broad architecture and parameter exploration | Implements a new seed from the benchmark |
| **Exploiter** | Local refinement of a baseline or validated parent | Establishes or refines the baseline |
| **Innovator** | Feature-level crossover of compatible parents | Uses an explicit seed or single-parent variant |

Each round uses fresh worker identities and isolated workspaces. Limited concurrency is handled by batching all three roles.

### Core capabilities

- **Flexible task routing:** requirement review, architecture advice, Pareto inspection, and convergence diagnosis can remain read-only.
- **Bounded search:** fixed-round or until-converged execution, with a finite round limit and one total attempt budget per assignment.
- **Two validation modes:** formal Csim/Csynth/Cosim/implementation workflows, or explicitly requested cosim-only exploration with separate provisional results.
- **Traceable candidates:** input fingerprints and stage receipts bind source, headers, test data, configuration, tool identity, and reports.
- **Preserved results:** immutable candidate archives and parent references survive workspace reuse.
- **Comparable metrics:** fixed-reference, exact N-dimensional hypervolume records objective units, configuration identity, and separate latency/throughput metrics.
- **Private project knowledge:** learned knowledge and experiment evidence stay in the selected project, outside the published skill package.

### Start a search

Keep the `DSE-agent` directory intact. Its skill invocation name is **`$run-agentic-dse`**. Hosts that load prompts directly can start at [SKILL.md](DSE-agent/SKILL.md) or the compatibility [agent.md](DSE-agent/agent.md).

1. **Select a benchmark.** Supply source, testbench/test vectors, target configuration, and objectives or a specification. Both `benchmarks/<name>/` and legacy `designs/<name>/` layouts are supported.
2. **Initialize the project.** Ask the agent to prepare the selected benchmark and requirements. Main creates missing state and isolated worker inputs while preserving existing work.
3. **Choose the search scope.** For example:

   - "Run three DSE rounds for this benchmark, preserving its numerical contract."
   - "Run two cosim-only rounds; do not run implementation."
   - "Continue until converged, for at most six rounds."
   - "Show the Pareto front and explain the current bottleneck without changing files."

These are natural-language requests, not shell commands. Runtime files belong to the selected project, which may be separate from the skill-resource directory.

<details>
<summary><strong>DSE package guide</strong></summary>

| Path | Purpose |
| --- | --- |
| [DSE-agent/SKILL.md](DSE-agent/SKILL.md) | Main workflow, routing, and stopping rules |
| [DSE-agent/AGENTS.md](DSE-agent/AGENTS.md) | Ownership, delegation, and execution boundaries |
| [DSE-agent/agent.md](DSE-agent/agent.md) | Compatibility entry point |
| [DSE-agent/prompts/](DSE-agent/prompts/) | Parser, Architect, workers, coding guidance, and checklist |
| [DSE-agent/references/](DSE-agent/references/) | Shared workflow, state, result, and evidence contracts |
| [DSE-agent/src/hls_run.sh](DSE-agent/src/hls_run.sh) | Policy-aware HLS stage execution |
| [DSE-agent/src/artifacts.py](DSE-agent/src/artifacts.py) | Input/receipt verification and candidate archival |
| [DSE-agent/src/hypervolume.py](DSE-agent/src/hypervolume.py) | Read-only formal-population metrics and hypervolume |

</details>

<details>
<summary><strong>Project runtime layout</strong></summary>

```text
project/
├── benchmarks/<name>/       Reference source, tests, and requirements
├── workspace/<role>/        Isolated candidate inputs and HLS output
├── results/<role>.json      Worker result and evidence references
├── state/                  Main-owned directive, population, and lineage
├── knowledge/learned/       Main-owned, evidence-linked experiment lessons
├── tmp/<run_id>/            Parser and Architect proposals
└── archive/<run_id>/        Immutable round and candidate snapshots
```

</details>

<a name="resources"></a>

## Resources and setup

**FPGA tools.** Use your installed Vivado/Vitis toolchain, device licenses, and any required hardware access. Optional helpers such as RapidWright are not bundled; available native tools can still be used for tasks that do not require them.

**DSE helpers.** Execution uses Python 3.10+ and the configured Vitis CLI. Exact hypervolume uses NumPy and pymoo; status reporting remains available without that optional backend. Multi-agent rounds require an agent host with file access, shell execution, and worker delegation.

**Agent hosts.** The Markdown instructions are reusable across file-capable hosts. `agents/openai.yaml` provides optional UI metadata; it does not configure or select a model.

### Bundled examples

| Location | Content |
| --- | --- |
| [vivado-synth/examples/](vivado-synth/examples/) | UG901 RTL templates for RAM, DSP, ROM, SRL, and FSM designs, with companion data files |
| [vivado-impl/examples/ug906/](vivado-impl/examples/ug906/) | Three before/after RTL example sets for QoR suggestions |
| [vitis-hls-synthesis/examples/](vitis-hls-synthesis/examples/) | AMD HLS design, feature, and introductory tutorials |

<details>
<summary><strong>Anatomy of a skill folder</strong></summary>

```text
skill-name/
├── SKILL.md            Scope, decision guidance, and workflow
├── agents/openai.yaml  UI metadata for compatible hosts
├── REFERENCE.md        Command and attribute reference, when present
├── references/         Focused guidance, when present
├── examples/           HDL/HLS examples, when present
└── evals/              Evaluation fixtures or runner wrapper, when present
```

Read the selected `SKILL.md` first, then load the references and examples relevant to the task. Supporting resources are not universal prerequisites.

</details>

## Support

> **My Claude account got banned.** 😅 If you find this project useful, consider sponsoring me to get a GPT Pro 20× subscription — I'd love to keep building.

## License

Licensed under [GPL-2.0](LICENSE). Preserve the copyright and license notices in bundled third-party examples.

---

<p align="center"><a href="#top">Back to top ↑</a> &nbsp;·&nbsp; <strong>English</strong> &nbsp;|&nbsp; <a href="README.zh-CN.md">简体中文</a></p>
