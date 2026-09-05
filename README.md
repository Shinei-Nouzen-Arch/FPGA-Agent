# FPGA-Agent

Reusable skills and agent prompts for AMD Vivado/Vitis FPGA development, from HLS and RTL through implementation, timing closure, simulation, and hardware debug.

> **My Claude account got banned.** 😅 If you find this project useful, consider sponsoring me to get a GPT Pro 20× subscription — I'd love to keep building.

The repository includes two complementary components:

1. **FPGA development skills** — nine skills for individual tasks and coordinated engineering workflows.
2. **[Agentic-DSE](#agentic-dse--multi-agent-hls-design-space-exploration)** — the existing multi-agent HLS design-space exploration prompts in [DSE-agent/](DSE-agent/).

## High-Capability Model Update

This update revises the skill instructions for more capable reasoning models, such as **GPT-6** and **Claude Fable 5.1**. The emphasis is on giving capable models room to make evidence-backed decisions within the user's request, while preserving explicit approvals and engineering safeguards.

- Infer routine details from the existing project and conversation; ask only when a consequential missing decision cannot be resolved from available evidence.
- Coordinate analysis, scripting, and implementation without repeatedly asking for permission to continue work that is already authorized.
- Select the stages needed for the requested outcome instead of treating every task as a full build, export, or programming workflow.
- Treat a strategy plateau as a reason to reassess within the existing limits, not as successful completion.
- Verify the complete result: positive setup, hold, and pulse-width margins; routing and constraint coverage; applicable design checks; and the requested deliverables.
- Preserve original constraints, IP protections, explicit RTL/netlist restrictions, candidate validation, output ownership, and hardware authorization boundaries.

These are instruction and workflow changes, not a model-specific API integration or a measured claim of better model accuracy, runtime, or FPGA performance. The named models describe the intended audience; no cross-model benchmark results are claimed. See [CHANGELOG.md](CHANGELOG.md) for the detailed changes and validation scope.

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

The existing [DSE-agent/](DSE-agent/) prompt set is retained unchanged by the high-capability skill refresh.

An agentic FPGA HLS design space exploration system. A Main Agent (architect + evolution scheduler) coordinates 3 Worker Agents to explore the Pareto-optimal frontier of FPGA designs through iterative refinement.

## How It Works

```
Main Agent (agent.md)
├── Explorer Worker     — large-step mutation, explores new architecture/parameter space
├── Exploiter Worker    — small-step fine-tuning, incremental optimization
└── Innovator Worker    — feature-level crossover, fuses two parent designs
     ↓
T1 (checklist) → T2 (synthesis) → T3 (co-simulation) → T4 (implementation)
     ↓
Pareto front update → Hypervolume check → Self-evolving knowledge base
```

Each round: the Main Agent analyzes bottlenecks, assigns tasks to all 3 Workers in parallel, collects validated results, and updates the Pareto frontier. The process converges when Hypervolume improvement drops below a threshold.

## What's In This Repo

| File | Purpose |
|------|--------|
| [DSE-agent/agent.md](DSE-agent/agent.md) | Main Agent instructions — full orchestration protocol (`init req` → `run dse` → convergence) |
| [DSE-agent/prompts/architect.md](DSE-agent/prompts/architect.md) | Hardware Architect Agent — selects architectures, analyzes critical paths, guides DSE direction |
| [DSE-agent/prompts/explorer.md](DSE-agent/prompts/explorer.md) | Explorer Worker — large-step mutation, bold architectural changes |
| [DSE-agent/prompts/exploiter.md](DSE-agent/prompts/exploiter.md) | Exploiter Worker — small-step parameter/microarchitecture fine-tuning |
| [DSE-agent/prompts/innovator.md](DSE-agent/prompts/innovator.md) | Innovator Worker — feature-level crossover of two parent designs |
| [DSE-agent/prompts/req_parser.md](DSE-agent/prompts/req_parser.md) | Requirement Parser Agent — converts user requirements into structured DSE configuration |
| [DSE-agent/prompts/coding_style.md](DSE-agent/prompts/coding_style.md) | HLS C++ coding style guide based on AMD UG1399, with anti-patterns and templates |
| [DSE-agent/prompts/hardware_checklist.md](DSE-agent/prompts/hardware_checklist.md) | Pre-synthesis hardware checklist (A1–F5) + co-simulation quick diagnostic |

## Quick Start

1. **Prepare your design** — Create `designs/<name>/` with `spec.json`, `src/kernel.cpp`, and `tb/testbench.cpp`
2. **Initialize** — Run `init req <name>` with your requirements
3. **Explore** — Run `run dse <name> [N]` to execute N rounds of DSE iteration

## What's NOT Included (Must Be Created by You or the AI Agent)

The DSE component contains **agent prompt configuration**, not a bundled execution runtime. The following are intentionally excluded and must be supplied or created when needed:

| Component | Description | How to Get |
|-----------|-------------|------------|
| **HLS synthesis skill** | Vitis HLS tool knowledge (commands, pragma reference, report analysis) | Use the `vitis-hls-synthesis` skill from this repo, or create your own |
| **Knowledge base** | `knowledge/core/` (architecture catalog, platform specs) and `knowledge/learned/` (success/failure cases) | Auto-generated by the Architect Agent at runtime using its own knowledge, or pre-populated manually |
| **Hypervolume script** | `hypervolume.py` for Pareto frontier HV computation (pymoo-based) | Generate via AI or write your own; Mode A is optional — Mode B (simplified) and Mode C (manual) work without it |
| **Benchmarks** | Reference designs and test vectors | Provide your own `designs/<name>/` directory with kernel source and testbench |
| **Runtime state** | `state/`, `results/`, `tmp/` directories | Auto-created by agents during execution |

## Agent Platform Compatibility

The prompts are platform-agnostic. Use with any AI agent system that supports:

- Reading files (`Read`)
- Writing files (`Write`)
- Spawning subagents (`sessions_spawn` or equivalent)
- Shell execution (for HLS synthesis commands)

## License

The repository's [GPL-2.0 license](LICENSE) is unchanged. Preserve the copyright and license notices in bundled third-party examples.
