# FPGA-Agent

Reusable skills and agent prompts for AMD Vivado/Vitis FPGA development, from HLS and RTL through implementation, timing closure, simulation, and hardware debug.

> **My Claude account got banned.** 😅 If you find this project useful, consider sponsoring me to get a GPT Pro 20× subscription — I'd love to keep building.

The repository includes two complementary components:

1. **FPGA development skills** — nine skills for individual tasks and coordinated engineering workflows.
2. **[Agentic-DSE](#agentic-dse--multi-agent-hls-design-space-exploration)** — multi-agent HLS design-space exploration with orchestration, worker prompts, and execution helpers in [DSE-agent/](DSE-agent/).

## Vivado/Vitis FPGA Development Skills

The skills use AMD Vivado/Vitis 2025.2 documentation as their primary baseline. Check command support, device applicability, and installed tool versions before executing a design flow.

## FPGA Development Flow

```
HLS C/C++ → RTL → Synthesis → Implementation → Timing Verification

Constraints and validation: vivado-constraints + vivado-analysis
Iterative timing closure:   vivado-timing-closure
Simulation throughout:     vivado-sim
TCL automation:            vivado-tcl
Hardware debug:            vivado-debug (when requested and authorized)
```

## Skills Overview

| Skill | Documentation | Focus | Core Content |
|-------|--------------|-------|--------------|
| [vitis-hls-synthesis](vitis-hls-synthesis/SKILL.md) | UG1399 | HLS Synthesis | Pragmas, interfaces, dataflow/pipeline, burst optimization, stage-specific validation |
| [vivado-synth](vivado-synth/SKILL.md) | UG901 | Synthesis | Strategies, resource inference, attributes, FSM encoding, OOC/incremental synthesis |
| [vivado-constraints](vivado-constraints/SKILL.md) | UG903 | Constraints | Clocks, I/O delays, timing exceptions, CDC, physical constraints, XDC debugging |
| [vivado-impl](vivado-impl/SKILL.md) | UG904 | Implementation | Optimization, placement, routing, congestion, incremental implementation, ECO tactics |
| [vivado-analysis](vivado-analysis/SKILL.md) | UG906 | Report Analysis | Timing paths, QoR assessment, methodology, utilization, diagnosis and acceptance evidence |
| [vivado-timing-closure](vivado-timing-closure/SKILL.md) | UG949, UG1292, XTP301 | Timing Closure | Constraint baselines, iterative optimization, best-candidate preservation, full final acceptance |
| [vivado-debug](vivado-debug/SKILL.md) | UG908 | Hardware Debug | ILA/VIO/JTAG-to-AXI, debug insertion, clock requirements, hardware troubleshooting |
| [vivado-sim](vivado-sim/SKILL.md) | UG900 | Simulation | Behavioral/netlist/timing simulation, xsim, third-party simulators, SAIF/VCD |
| [vivado-tcl](vivado-tcl/SKILL.md) | UG835, UG892 | TCL Automation | Script generation/review, authorized batch execution, result verification, requested output generation |

## Architecture

Each skill has a `SKILL.md` entrypoint. Supporting resources vary by skill:

```
skill-name/
├── SKILL.md           Decision guidance, scope, and workflow
├── agents/openai.yaml UI metadata for compatible hosts
├── REFERENCE.md       Command and attribute reference, when present
├── references/        Focused guidance, when present
├── examples/          HDL/HLS examples, when present
└── evals/             Evaluation fixtures or runner wrapper, when present
```

- Read the selected `SKILL.md` first, then load the references and examples relevant to the task. Supporting references are not universal prerequisites.
- Keep each skill folder intact so its relative references remain usable.
- The Markdown instructions are reusable across file-capable agent hosts. `agents/openai.yaml` supplies optional host-specific metadata; it does not configure or select a model.

## Using the Skills

Add the selected folders through your agent platform's skill mechanism, or make their instructions and resources available to the agent. Preserve any existing installation unless replacing it is part of your request. Related skills can be used together for a single authorized task.

Example requests:

- "Review this timing report and explain the likely bottleneck. Do not change the design."
- "Generate a batch TCL script for the existing project, but do not run it."
- "Run the existing implementation flow and verify the requested outputs. Preserve the current constraints and do not program hardware."
- "Improve timing within the current RTL and clock target, keep the best candidate, and report any remaining acceptance failures."

Vivado/Vitis installations, device licenses, hardware access, and optional tools such as RapidWright are not bundled. Missing optional helpers should not prevent work that available native tools can complete.

## Cross-References Between Skills

```
vitis-hls-synthesis ──→ vivado-impl (implementation), vivado-analysis (timing), vivado-constraints (top-level)
                    ──→ vivado-sim (RTL simulation), vivado-debug (hardware debug), vivado-tcl (automation)

vivado-synth ──→ vivado-tcl (execution)
vivado-constraints ──→ vivado-tcl (execution), vivado-analysis (report interpretation)
vivado-impl ──→ vivado-tcl (execution), vivado-synth (synthesis), vivado-constraints (constraints), vivado-analysis (analysis)
              ──→ vitis-hls-synthesis (HLS-level optimization)
vivado-analysis ──→ vivado-tcl (execution), vivado-constraints (constraint modification), vivado-impl (strategy adjustment)
vivado-timing-closure ──→ vivado-analysis (evidence), vivado-constraints (baseline), vivado-impl (tactics), vivado-tcl (execution)
vivado-debug ──→ vivado-tcl (execution), vivado-impl (strategy), vivado-analysis (timing)
              ──→ vitis-hls-synthesis (HLS debug options)
vivado-sim ──→ vivado-tcl (execution), vitis-hls-synthesis (co-simulation)
vivado-tcl ──→ vivado-debug (debug decisions), vivado-analysis (analysis), vitis-hls-synthesis (IP integration)
```

## Examples Directory

| Skill | Directory | Content |
|-------|-----------|---------|
| vivado-synth | `examples/` | 64 Verilog/SV files — UG901 HDL coding templates (RAM/DSP/ROM/SRL/FSM) |
| vivado-impl | `examples/ug906/` | 3 sets of before/after RTL — report_qor_suggestions optimization examples |
| vitis-hls-synthesis | `examples/` | Design/Feature/Introductory tutorials — Official AMD HLS reference implementations |

---

## Agentic-DSE — Multi-Agent HLS Design Space Exploration

[Agentic-DSE](DSE-agent/SKILL.md) coordinates a Main Agent and three specialized workers to explore architecture, pragma, parameter, and clock choices for a selected HLS benchmark.

- **Explorer:** broad architecture and parameter exploration.
- **Exploiter:** local refinement of a baseline or validated parent.
- **Innovator:** feature-level crossover, with explicit seed variants for zero- or one-parent populations.

Main handles requirement parsing, architecture proposals, assignments, evidence checks, immutable archives, Pareto selection, and learned knowledge. Each round uses fresh worker identities and isolated workspaces; limited concurrency is handled by batching the three roles.

### Capabilities

- Read-only requirement review, architecture advice, Pareto inspection, and convergence diagnosis.
- Project initialization and continuation with existing benchmark inputs and runtime state.
- Fixed-round execution or bounded until-converged search, with one total retry budget per assignment.
- Formal Csim/Csynth/Cosim/implementation workflows, or explicitly requested cosim-only exploration with separate provisional results.
- Input fingerprints and stage receipts that bind source, headers, test data, configuration, tool identity, and reports to each candidate.
- Immutable candidate archives and parent references that survive workspace reuse.
- Fixed-reference, exact N-dimensional hypervolume with explicit objective units, configuration identity, and separate latency/throughput metrics.
- Scoped architecture guidance and historical case evidence for reusable experiment planning.

### Package Structure

| Path | Purpose |
| --- | --- |
| [DSE-agent/SKILL.md](DSE-agent/SKILL.md) | Main workflow, task routing, and stopping rules |
| [DSE-agent/AGENTS.md](DSE-agent/AGENTS.md) | Ownership, delegation, and execution boundaries |
| [DSE-agent/agent.md](DSE-agent/agent.md) | Compatibility entry point |
| [DSE-agent/prompts/](DSE-agent/prompts/) | Parser, Architect, worker, coding, and checklist guidance |
| [DSE-agent/references/](DSE-agent/references/) | Shared worker workflow, state, result, and evidence contracts |
| [DSE-agent/src/hls_run.sh](DSE-agent/src/hls_run.sh) | Policy-aware HLS stage execution |
| [DSE-agent/src/artifacts.py](DSE-agent/src/artifacts.py) | Input/receipt verification and candidate archival |
| [DSE-agent/src/hypervolume.py](DSE-agent/src/hypervolume.py) | Read-only formal-population metrics and hypervolume |
| [DSE-agent/knowledge/](DSE-agent/knowledge/) | Architecture families, named example platform, and scoped cases |

### Using Agentic-DSE

Keep the `DSE-agent` directory intact. Its skill invocation name is `$run-agentic-dse`; hosts that load prompts directly can start at `SKILL.md` or the compatibility `agent.md`.

1. Select a project containing a benchmark's source, testbench/test vectors, target configuration, and objectives or specification. Existing `benchmarks/<name>/` and legacy `designs/<name>/` layouts are supported.
2. Ask the agent to initialize the selected benchmark and requirements. Main prepares missing state and isolated worker inputs without replacing existing work.
3. Request a bounded search or read-only analysis, for example:

   - "Run three DSE rounds for this benchmark, preserving its numerical contract."
   - "Run two cosim-only rounds; do not run implementation."
   - "Continue until converged, for at most six rounds."
   - "Show the Pareto front and explain the current bottleneck without changing files."

These are natural-language requests, not shell commands. The skill-resource directory and active project directory may be different; runtime files belong to the selected project.

The execution helpers use Python 3.10+ and the configured Vitis command-line tools. Exact hypervolume uses NumPy and pymoo; status reporting remains available without the optional numerical backend. An agent host needs file access, shell execution, and worker delegation for multi-agent rounds.

### Project Runtime Layout

```
project/
├── benchmarks/<name>/       Reference source, tests, and requirements
├── workspace/<role>/        Isolated candidate inputs and HLS output
├── results/<role>.json      Worker result and evidence references
├── state/                  Main-owned directive, population, and lineage
├── knowledge/learned/       Main-owned, evidence-linked experiment lessons
├── tmp/<run_id>/            Parser and Architect proposals
└── archive/<run_id>/        Immutable round and candidate snapshots
```

## License

The repository's [GPL-2.0 license](LICENSE) is unchanged. Preserve the copyright and license notices in bundled third-party examples.
