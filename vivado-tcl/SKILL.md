---
name: vivado-tcl
description: Generate, review, explain, and execute Vivado/Vitis TCL scripts for FPGA design flows, and verify their execution results. Covers project and non-project flows, synthesis, implementation, simulation, constraints, IP integration, and hardware programming. Use for explicit TCL requests or when scripting is needed to complete an already-authorized FPGA task; the user need not name TCL again. For pure report interpretation, strategy selection, constraint theory, or debug planning, use the relevant analysis, synthesis, implementation, constraints, or debug skill as the primary guide. Combine those skills with this one when execution and verification are needed.
---

# Vivado TCL Script Generation Guide

## Overview

This skill generates and reviews Vivado TCL scripts and, when execution is part of the user's request, runs them via `vivado -mode batch` and verifies the results. It covers project creation, synthesis, implementation, bitstream generation, hardware programming, IP integration, debug, and simulation. For the complete command reference, see REFERENCE.md.

## Critical Rules

1. **NEVER mix Project Mode and Non-Project Mode commands** — they are incompatible flows
2. **Project Mode**: uses `create_project`, `add_files`, `launch_runs`, `wait_on_run`, `open_run`
3. **Non-Project Mode**: uses `read_verilog`, `synth_design`, `opt_design`, `place_design`, `route_design`
4. **Determine the mode from existing evidence first**: inspect the project, scripts, configuration, and prior user instructions. Preserve an established flow. For a new flow, choose a suitable mode and state the assumption unless the choice materially changes the requested deliverable or execution scope. Ask only for consequential information that cannot be established from available evidence; do not re-ask answered questions or invent a target device needed for execution.
5. **Verify execution as part of this skill**: inspect exit status, run status, relevant logs/reports, and requested artifacts. Use vivado-analysis or other relevant skills for deeper design decisions while continuing the same task; switching skills does not require the user to repeat authorization.
6. **Match the requested action**: review or script generation ends with the requested analysis or checked script, not an automatic execution. An execution or fix request includes its necessary in-scope validation and follow-up. Existing authorization remains valid; skill selection does not authorize additional design changes, hardware programming, or hardware writes.

## Execution Model

### How to run a TCL script
```bash
# Batch mode (recommended for automation)
vivado -mode batch -source <script.tcl>

# With arguments
vivado -mode batch -source script.tcl -tclargs "ARG1=value1"

# Interactive TCL shell
vivado -mode tcl
```

### Key output files
- `vivado.log` — full session log
- `vivado.jou` — journal of TCL commands (reusable as script)
- `*.dcp` — design checkpoints (snapshots of design state)
- `*.bit` — bitstream files
- `*.xsa` — hardware platform for Vitis
- `*.ltx` — debug probes file

## Quick Reference: Project Mode Flow

```tcl
# 1. Create project
create_project <name> <dir> -part <part>

# 2. Add sources
add_files {./src/top.v ./src/sub.v}
add_files -fileset constrs_1 ./constraints/timing.xdc
update_compile_order -fileset sources_1

# 3. Synthesis
launch_runs synth_1
wait_on_run synth_1

# 4. Open synth results & reports
open_run synth_1 -name netlist_1
report_timing_summary -file syn_timing.rpt
report_power -file syn_power.rpt

# 5. Implementation through routing
launch_runs impl_1 -to_step route_design
wait_on_run impl_1

# 6. Reports
open_run impl_1
report_timing_summary -delay_type min_max -file imp_timing.rpt
report_route_status -file imp_route_status.rpt
check_timing -file imp_check_timing.rpt
report_drc -file imp_drc.rpt
report_utilization -file imp_util.rpt
report_power -file imp_power.rpt
```

Inspect the run status and reports against the task's acceptance criteria before the output stage. When bitstream generation is in scope and those checks pass, continue without another confirmation:

```tcl
launch_runs impl_1 -to_step write_bitstream
wait_on_run impl_1
```

## Quick Reference: Non-Project Mode Flow

```tcl
# 0. Setup
set outputDir ./output
file mkdir $outputDir

# 1. Read sources
read_verilog {./src/top.v ./src/sub.v}
read_xdc ./constraints/timing.xdc

# 2. Synthesis
synth_design -top <top_module> -part <part>
write_checkpoint -force $outputDir/post_synth.dcp
report_timing_summary -file $outputDir/post_synth_timing.rpt

# 3. Implementation
opt_design
place_design
# Optional: phys_opt_design
route_design
write_checkpoint -force $outputDir/post_route.dcp

# 4. Reports
report_timing_summary -file $outputDir/post_route_timing.rpt
report_route_status -file $outputDir/post_route_status.rpt
check_timing -file $outputDir/post_route_check_timing.rpt
report_utilization -file $outputDir/post_route_util.rpt
report_power -file $outputDir/post_route_power.rpt
report_drc -file $outputDir/post_route_drc.rpt
```

After the applicable acceptance checks pass, generate a bitstream if requested. For unattended automation, encode the checks as failure conditions before this output block; merely producing reports is not verification.

```tcl
# 5. Generate the requested bitstream in the selected task output location
write_bitstream -force $outputDir/top.bit
```

## IP Integrator (Block Design)

```tcl
# Create block design
create_bd_design "system"

# Add IP cores
create_bd_cell -type ip -vlnv xilinx.com:ip:<ip_name>:<version> <instance>

# Run automation (AXI connections, external ports)
apply_bd_automation -rule xilinx.com:bd_rule:processing_system7 \
    -config {make_external "FIXED_IO, DDR"} [get_bd_cells ps7_0]
apply_bd_automation -rule xilinx.com:bd_rule:axi4 \
    -config {Master "/ps7_0/M_AXI_GP0"} [get_bd_intf_pins peripheral/S_AXI]

# Validate, save, generate wrapper
assign_bd_address
validate_bd_design
save_bd_design
make_wrapper -files [get_files system.bd] -top
```

When a Vitis platform export is requested, first build the design and verify its applicable acceptance criteria and required bitstream using the relevant flow above. Then export to the selected output path:

```tcl
write_hw_platform -fixed -include_bit -force ./system_wrapper.xsa
```

## Hardware Programming

```tcl
open_hw_manager
connect_hw_server -url localhost:3121
open_hw_target

current_hw_device [get_hw_devices <device>]
set_property PROGRAM.FILE {<bitstream>.bit} [current_hw_device]
set_property PROBES.FILE {<probes>.ltx} [current_hw_device]
program_hw_devices [current_hw_device]

close_hw_target
disconnect_hw_server
close_hw_manager
```

## Debug Core Insertion (ILA)

```tcl
# After synthesis, before implementation
open_run synth_1

# Create ILA
create_debug_core u_ila_0 ila
set_property C_DATA_DEPTH 1024 [get_debug_cores u_ila_0]

# Connect clock
set_property port_width 1 [get_debug_ports u_ila_0/clk]
connect_debug_port u_ila_0/clk [get_nets clk]

# Add probes
set_property port_width <width> [get_debug_ports u_ila_0/probe0]
connect_debug_port u_ila_0/probe0 [get_nets {<signal_list>}]

# Implement and write probes
implement_debug_core
write_debug_probes -force ./output/top.ltx
```

## TCL Syntax Tips

### Object queries
```tcl
get_cells -hierarchical -filter "lib_cell =~ FD*"
get_pins -of [get_cells inst_1]
get_nets -of [get_pins inst_1/D]
get_property loc [get_cells inst_1]
set_property loc SLICE_X1Y27 [get_cells inst_1]
```

### Bus indexing
```tcl
add_wave {bus[4]}       ;# braces for square brackets
add_wave bus(4)         ;# parentheses work too
```

### Error handling
```tcl
if {[catch {<command>} result options]} {
    puts stderr "Error: $result"
    return -options $options $result
}
```

Propagate an unhandled stage failure to the batch caller; logging an error alone must not allow dependent stages to appear successful. When a fix is in scope, inspect the failure and make a relevant correction before retrying.

## Workflow Guidelines

1. **For batch execution, write TCL to a `.tcl` file first**, then run it with `vivado -mode batch -source`. For generation or review only, deliver the checked script or findings without executing the flow.
2. **Include `file mkdir` for output directories** to avoid errors
3. **Use `write_checkpoint`** at key stages in Non-Project Mode for recovery
4. **Verify the stages actually run**: check run status and relevant logs, reports, and artifacts. Include `report_timing_summary` after synthesis and routing when those stages are in scope. Apply the full [timing acceptance criteria](../vivado-timing-closure/SKILL.md#timing-acceptance-criteria) before claiming timing closure; otherwise report the validation appropriate to the requested stage.
5. **Limit `-force` to replaceable task outputs or already-authorized overwrites**. Establish ownership and replaceability from the task context, file provenance, and output paths; this is an evidence check, not a per-run user confirmation. Use a fresh output path for other existing files. Ask only when an overwrite is necessary and not already authorized. All `-force` examples here and in REFERENCE.md assume this output ownership check has been made.
6. **For IP Integrator flows**, always `validate_bd_design` before proceeding
7. **When programming hardware**, always check device connection before programming
8. **Complete the requested outcome**: a script launch, successful process exit, or generated report alone is not proof of success. Continue necessary authorized work; if a required step cannot be completed, identify the specific missing result and finish unaffected work without claiming the whole task is complete.

## Common Part Numbers (examples)

| Family | Part Example |
|--------|-------------|
| Kintex-7 | xc7k70tfbg484-2 |
| Zynq-7000 | xc7z020clg484-1 |
| Artix-7 | xc7a35tcpg236-1 |
| Kintex UltraScale+ | xcku5p-ffvb676-2-e |
| Zynq UltraScale+ | xczu9eg-ffvb1156-2-e |
| Versal | xcvm1802-vsva2197-2MP-e-S |
