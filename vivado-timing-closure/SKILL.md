---
name: vivado-timing-closure
description: Vivado FPGA timing closure and optimization assistant. Covers systematic timing analysis, constraint validation, implementation strategy selection (place_design/phys_opt_design/route_design directives), pblock-based area constraints, RapidWright-assisted netlist optimization, and iterative convergence workflows. Use when users mention timing closure, WNS/TNS violations, Fmax improvement, FPGA timing optimization, DCP optimization, or post-route ECO fixes. Also trigger for questions about check_timing, report_qor_assessment/suggestions, methodology DRC, clock interaction analysis, fanout optimization, LUT merging, or critical path analysis.
---

# Vivado Timing Closure & Optimization

Systematic FPGA timing convergence based on AMD UltraFast Design Methodology (UG949) and the XTP301 checklist, combined with practical optimization experience.

For explanation or report-only requests, analyze the available evidence and identify any missing verification without requiring a new build. Run optimization only when it is within the user's request, and reuse valid results for the current design. Existing authorization covers necessary in-scope follow-up; changing a strategy or consulting vivado-tcl does not require repeated confirmation. Preserve explicit limits on RTL, netlist, interfaces, constraints, target frequency, runtime, and hardware operations.

## Quick Decision Flow

```
Inspect current reports / open the relevant checkpoint when execution is in scope
  → Validate the existing constraint baseline and record all timing metrics
  → WNS >= 0 or high QoR score? → Full final acceptance checks
                                  → All checks and requested deliverables complete? → DONE
                                  → Otherwise: investigate the remaining gaps
  → Timing still failing? → Diagnose constraints, paths, congestion, and QoR
                           → Apply an evidence-backed, authorized strategy
                           → Compare results; preserve the best candidate
                           → Plateau? End this strategy's loop and reassess
```

## Timing Acceptance Criteria

| Metric | Requirement | Check Command |
|--------|-------------|---------------|
| Setup WNS/TNS | WNS > 0 ns, TNS = 0 ns | `report_timing_summary` |
| Hold WHS/THS | WHS > 0 ns, THS = 0 ns | `report_timing_summary -delay_type min_max` |
| Pulse Width WPWS/TPWS | WPWS > 0 ns, TPWS = 0 ns | `report_timing_summary` |
| Route Status | Design fully routed; 0 routing errors | `report_route_status` |
| Fmax | `1000 / (clock_period - WNS)` MHz | WNS is negative for failing paths |

For a timing-closure task, apply these checks to the same final design with the full intended constraints, including I/O timing. Verify zero unconstrained internal endpoints, intended exception coverage, and applicable CDC, DRC, and methodology findings. Run `report_bus_skew` separately when bus-skew constraints exist. Resolve findings or use justified waivers only within the task's authorization; do not weaken constraints to produce a pass.

WNS >= 0 or a high QoR score starts final verification; neither is a completion condition. Keep the positive-margin requirements above unless the user has explicitly specified a different acceptance policy. Missing metrics or checks remain unverified, not passed. Timing closure is complete only after the applicable checks pass and the requested artifacts and validation results are delivered; bitstream generation or hardware programming is not an automatic next stage.

**Important**: Fmax is NOT explicitly shown in Vivado reports. Always calculate it: `Fmax = 1000 / (period - WNS)` where WNS is the value from the timing summary (negative means failing).

## Layer 1: Constraint Validation (ALWAYS START HERE)

Before any optimization, verify the design is properly constrained. Skipping this wastes hours optimizing paths that aren't the real problem.

### Essential checks (in priority order):

```
report_timing_summary          → WNS/TNS/WHS/THS/WPWS baseline
check_timing                   → Unconstrained paths (internal endpoints MUST be 0)
report_clock_interaction       → Clock relationships, identify unsynchronized crossings
report_methodology             → TIMING + XDC rule violations
report_qor_assessment          → Overall design health score (1-5)
```

### Interpreting QoR Assessment:

- **Score 1-2**: Major constraint or methodology issues — fix these first
- **Score 3**: Design has timing challenges but constraints are reasonable
- **Score 4-5**: Good design quality, remaining issues are fine-grained

Read `references/methodology-checklist.md` for specific DRC checks mapped from XTP301.

## Layer 2: Tool-Managed Implementation Optimization (May Change the Netlist)

This is where the biggest gains come from. The directives below are ordered by typical impact.

Built-in physical optimization can replicate cells, restructure logic, or move registers even when RTL source is unchanged. Honor explicit restrictions on netlist changes; this layer does not exempt tool-managed changes from those restrictions. Preserve a baseline checkpoint and compare the candidate's timing, resources, and applicable functional checks.

### The Golden Sequence (proven 20-45% Fmax improvement):

```tcl
# Step 1: Re-place with exploration (the single biggest lever)
place_design -directive Explore

# Step 2: Physical optimization after placement
phys_opt_design -directive Explore

# Step 3: Route with timing effort
route_design

# Step 4: Check and iterate if needed
report_timing_summary

# Step 5: Aggressive follow-up (if still failing)
phys_opt_design -directive AggressiveExplore
route_design -directive NoTimingRelaxation -tns_cleanup
```

### Directive Reference:

| Directive | Tool | Use When | Expected Impact |
|-----------|------|----------|-----------------|
| `Explore` | place_design | Always first choice | **20-45% Fmax** |
| `ExtraTimingOpt` | place_design | Still failing after Explore | +0-5% additional |
| `Explore` | phys_opt_design | After placement, before routing | +2-10% |
| `AggressiveExplore` | phys_opt_design | Close to closure, last push | +0.5-2% |
| `NoTimingRelaxation` | route_design | Final routing push | ±1% (prevents degrade) |
| `AlternateReplication` | phys_opt_design | Multiple failing paths, high fanout | variable |

### Iteration Pattern:

After each applicable phys_opt/routing cycle, compare WNS, TNS, failing endpoints, hold, pulse width, route status, and any stated resource limits on a consistent constraint baseline. TNS or endpoint improvements can be meaningful progress even when WNS is unchanged. Preserve the best candidate, including candidates that would otherwise be lost to a later regression.

- If WNS >= 0, run the full Timing Acceptance Criteria above and investigate any remaining failures or missing checks.
- End the **current strategy's repeated loop** after 3 consecutive rounds without material progress, or when WNS improvement per round is < 0.005 ns with no meaningful progress in the other relevant metrics.
- At a plateau, re-examine the limiting paths and continue another evidence-backed strategy within the existing scope and overall attempt, runtime, and resource limits. Do not request confirmation merely to switch an already-authorized strategy.
- If no feasible in-scope next step remains, or an overall limit is reached, report that closure is incomplete, retain the best result, and identify the remaining violations and concrete constraint or missing decision. Do not treat a plateau as success or restart the search indefinitely.

**Stage rule**: Post-place `phys_opt_design` can run after placement. Post-route optimization requires the appropriate routed design state. Check the actual design state and tool requirements; do not impose the post-route prerequisite on post-place optimization. See vivado-impl for stage-specific options.

### Using ML Strategy Suggestions:

```tcl
report_qor_suggestions
```
Outputs RQS_STRAT strategies recommended by Vivado's ML analysis. The top 3 strategies are auto-generated for your specific design. Each includes specific directives for opt_design/place_design/phys_opt_design/route_design.

## Layer 3: Pblock Area Constraints

Use when critical-path analysis shows substantial physical spread; Manhattan distance > 70 tiles on 5+ critical paths is a heuristic, not a required output from a specific helper.

### Pblock Flow:

1. Use `report_design_analysis`, `get_timing_paths`, and cell placement properties to inspect critical-path spread and select the affected logic.
2. Use `report_utilization` for that logic and inspect device sites/clock regions to size a region with resource headroom.
3. If available, the environment-specific helpers `analyze_critical_path_spread`, `report_utilization_for_pblock`, `analyze_fabric_for_pblock`, and `convert_fabric_region_to_pblock` can assist. They are not built-in Vivado commands and their implementations are not included here; inspect the available tool or script interface before use. Check whether a helper already includes sizing headroom.
4. Without those helpers or RapidWright, use the native reports, object queries, and manual sizing guidance below. An unavailable optional tool does not block the rest of the task or authorize its installation. If a particular result cannot be verified, state that limitation and continue unaffected work.

Apply the chosen constraint to the selected logic in a candidate design and compare it with the baseline. Adapt the following Non-Project Mode example to the current flow:

```tcl
# Use observed target cells and device ranges; evaluate on a candidate copy.
place_design -unplace
create_pblock pblock_opt
add_cells_to_pblock pblock_opt [get_cells <target_cell_patterns>]
resize_pblock pblock_opt -add <RANGES>
set_property IS_SOFT false [get_pblocks pblock_opt]
place_design
phys_opt_design -directive Explore
route_design
```

**Rules of thumb for manual pblock sizing**:
- Compute centroid of critical path cells (average X/Y coordinates)
- Size region to ~2x the needed SLICE count (aim for 50% utilization)
- Expand to cover the critical cell bounding box + 20% margin
- Clamp to device SLICE bounds (xcvu3p: X[0:168], Y[0:299])
- Avoid expanding to entire chip — that negates the constraint effect

## Layer 4: Netlist-Level Optimization (Use with Caution)

Only proceed when physical optimization (Layers 2-3) is exhausted. These modify the netlist and can degrade timing if misapplied.

Evaluate the applicable physical strategies; lack of an optional helper alone is not evidence that those strategies are exhausted. The RapidWright calls below are examples of optional helper interfaces, not guaranteed package APIs. Use them only when an installed tool exposes the operation. Prefer available Vivado capabilities for equivalent work when suitable, and preserve explicit limits on netlist editing.

Always test manual netlist changes on a copy first. Use a tool's documented dry-run or `--test` option only if that tool supports it. Otherwise perform appropriate structural/functional validation on the candidate and re-check routing, timing, and resources. Do not adopt an unverified candidate merely because a specific test option is unavailable; report that limitation while continuing other feasible work.

### Fanout Splitting:

When fanout > 100 on critical path nets:

```python
# In RapidWright:
optimize_fanout(net_name="<net>", split_factor=<3-8>)
# split_factor: fanout/100, min 3, max 8
```

**Warning**: Fanout splitting replicates source drivers, adding cells. This can cause placement congestion. On designs with inherently high fanout architecture (e.g., neural network accelerators), it may degrade WNS by 0.5+ ns. Always compare before/after.

### LUT Input Cone Merging:

When paths have chains of small LUTs (LUT2-LUT5 feeding each other):

```python
# Find candidate pins: iterate nets where source cell is a LUT
# and sink cell is also a LUT
optimize_lut_input_cone(hierarchical_pin_names=[
    "cell_name/A1",  # Format: hierarchical_cell_name/pin_name
    ...
])
```

**Pre-check**: Count LUT types. If LUT6 dominates (>80%) with few LUT2-LUT5, merging has no targets and won't help.

### Cell Re-placement (ECO):

When `report_qor_suggestions` shows route delay > 60% on specific paths:

```python
# In RapidWright:
# 1. Read DCP
# 2. Identify cells on worst paths
# 3. Unplace target cells
# 4. Place at centroid of their connected cells
# 5. Write DCP
# 6. In Vivado: route_design only (keep placement)
```

## Congestion Analysis & Resolution

Congestion is the #1 cause of timing degradation between placement and routing. Use these tools systematically.

### Identifying Congestion

```tcl
# Primary congestion analysis
report_design_analysis -congestion

# Complexity analysis (predictive — can run before implementation)
report_design_analysis -complexity

# Check router log for congestion levels during route_design
```

### Congestion Severity Levels (from router log):

| Level | Area Size | Impact on QoR |
|-------|-----------|---------------|
| 0-3 | < 32x32 tiles | Usually manageable |
| 4 | Any | May affect routability |
| 5 | > 32x32 tiles | **Likely to degrade QoR and routability** |

### Congestion Types and Their Meanings:

- **Global Congestion**: All interconnect types combined — overall picture
- **Long Congestion**: Long-distance interconnect only — high values cause longer routing delays as router falls back to short wires
- **Short Congestion**: All other interconnect — high values (>5% tile%) cause longer runtime and potential QoR degradation
- **CLB Routing Congestion**: Local hot-spots that can cause routing failure even when global/long/short levels are acceptable. Look for `INFO: [Route 35-443] CLB routing congestion detected` in the log

### Router Behavior During Congestion:

When congestion prevents routing convergence during Global Iterations, the router:
1. Stops timing optimization
2. Prioritizes finding ANY valid routing solution (no overlaps)
3. Once valid routing is found, re-enables timing optimization

This can cause intermediate WNS to spike. Don't panic if intermediate routing WNS looks bad — judge by the final result.

### Congestion Warning Signs:

```
WARNING: [Place 46-14] The placer has determined that this design is highly
congested and may have difficulty routing.
```
→ Immediately run `report_design_analysis -congestion` before proceeding to routing.

```
CRITICAL WARNING: [Route 35-162] N signals failed to route due to routing congestion.
```
→ Design is unroutable. Reduce congestion before retrying.

### Congestion Mitigation Strategies:

1. **Placement-level fixes:**
   - `place_design -directive ExtraNetDelay_low` — reduces congestion by lowering net delay emphasis
   - `CELL_BLOAT_FACTOR` property on congested modules — spreads cells to reduce local density

2. **Logic-level fixes:**
   - `opt_design` to reduce MUXF*/CARRY*/SRL* in congested regions
   - Remove LUT combining attributes (LUTNM, HLUTNM) before place_design
   - Reduce control set diversity (fewer unique reset/CE combinations)

3. **Physical constraints:**
   - Pblock to isolate congested modules and give them dedicated area
   - Adjust floorplan to spread high-connectivity modules apart

## Design Complexity Analysis (Pre-Implementation)

Before running implementation, assess whether the design itself is "difficult" using complexity metrics. This predicts routing challenges before spending implementation time.

### Rent Exponent (`report_design_analysis -complexity`):

| Rent Exponent | Meaning |
|---------------|---------|
| 0.0 – 0.65 | Normal — design should route without major issues |
| 0.65 – 0.85 | High — likely routing challenges, especially with >15K instances |
| > 0.85 | Very high — design may fail implementation, needs restructuring |

High Rent exponent = tightly connected logic groups that connect densely to other groups → high global routing demand.

### Average Fanout:

| Average Fanout | Meaning |
|----------------|---------|
| < 4 | Normal |
| 4 – 5 | High — congestion likely; SSI designs with >100K instances may fail to fit in one SLR |
| > 5 | Very high — design may fail implementation |

**Important**: Always cross-reference Rent exponent and Average Fanout with Total Instances. Small modules (< 15K instances) can have high metrics but still implement easily. Use `-hierarchical_depth` to drill into problematic submodules.

## Clock Skew Reduction

Clock skew directly eats into timing budget. Intra-clock skew is typically < 300 ps; synchronous clock pairs < 500 ps. Unbalanced trees can have skew of several nanoseconds — making timing closure nearly impossible.

### Identifying Skew Problems:

1. Review paths with unexpectedly high clock uncertainty in timing reports
2. `report_clock_interaction` — check if async clocks are incorrectly being timed
3. Paths crossing SLR or I/O columns often have elevated skew

### Skew Reduction Techniques:

**For all architectures:**
- Remove cascaded clock buffers — connect them in parallel instead
- Merge parallel clock buffers into a single buffer; use CE pins for gating
- Remove LUTs/combinational logic from clock paths (migrate gating to CE pins)
- Never use `CLOCK_DEDICATED_ROUTE=FALSE` in production — it routes clocks on general interconnect, causing high skew and noise sensitivity

**For UltraScale/UltraScale+:**
- Use `BUFG_GT` for simple clock division instead of MMCM/PLL — saves resources and balances clock trees
- Apply `CLOCK_DELAY_GROUP` on critical synchronous clocks to enforce matched routing
- Use `ANY_CMT_COLUMN` instead of `FALSE` for clock routing exceptions — keeps clocks on dedicated resources
- Place MMCM/PLL near the center of clock loads to reduce network delay
- Pblock source and target into the same SLR to avoid cross-SLR clock skew
- Restrict BUFR/BUFIO/BUFH to a single clock region

## Clock Interaction Report Deep-Dive

`report_clock_interaction` uses a color-coded matrix. Understanding it prevents over-constraining and under-constraining:

| Color | Label | Meaning | Action |
|-------|-------|---------|--------|
| Black | No path | No interaction between clock domains | Reference only |
| Green | Timed | Paths timed, clocks are synchronous | Reference — verify this is intended |
| Cyan | Partial False Path | Some paths excluded by user exceptions | Verify exceptions are correct |
| **Red** | **Timed (unsafe)** | **Paths timed but clocks appear asynchronous** | **Add set_clock_groups or set_false_path** |
| **Orange** | **Partial False (unsafe)** | **Async clocks but only partially excluded** | **Check for missed exception coverage** |
| Blue | User Ignored | Paths excluded by clock_groups/false_path | Verify async circuit is correct (CDC) |
| Light blue | Max Delay Datapath | Constrained by set_max_delay -datapath_only | Verify delay value is correct |

**Workflow**: Before adding exceptions, the matrix should only show Black, Red, and Green. The goal is to convert all Red (unsafe timed) → Blue (user ignored) for truly async clocks.

### Clock Pair Requirement Analysis:

Sort `report_clock_interaction` by "Path Req (WNS)" column to find overly tight requirements. Vivado expands each clock to 1000 cycles to find the tightest alignment. If "Not Expanded" appears, the clocks MUST be treated as asynchronous.

### Clock Domain Crossing (CDC) Validation:

```tcl
report_cdc
```
Analyzes async clock crossing circuits for correctness. Run after each major block update. Waive violations only after confirming the CDC circuit is safe.

## Detailed Baseline Setting Process (from UG949)

The default workflow preserves the existing constraints and reuses the appropriate checkpoint for the task:

```
1. Inspect or open the relevant checkpoint with its existing complete constraints
2. Record the design version, constraint sources/scopes, and baseline timing metrics
3. report_clock_networks + report_clocks → verify clock definitions and propagation
4. check_timing + report_methodology → identify specific coverage or constraint issues
5. Correct supported issues within scope, using Tcl or the Timing Constraints Wizard
6. report_clock_interaction + report_cdc → verify relationships and crossing circuits
7. Apply justified exceptions only to the intended paths, preserving IP constraints
8. If optimization is requested, run the applicable implementation stages
9. Compare candidates under the same full constraint set, including I/O timing
10. Run the full Timing Acceptance Criteria before declaring closure
```

**Key constraint for IP**: All AMD IP XDC constraints must remain intact. Never remove or override IP timing constraints.

**Optional baseline reconstruction**: Use only when it is needed for an authorized constraint diagnosis. Work on an isolated copy, retain the original checkpoint and constraint sources, and ensure IP constraints are preserved or correctly reloaded with their original scope and ordering. `reset_timing` is not a default diagnostic step; any temporary reconstruction must restore the required IP constraints before measurements. If the necessary constraint sources are unavailable, keep the existing baseline and identify the specific gap instead of clearing it.

An experiment using `config_timing_analysis -ignore_io_paths yes` is a partial diagnostic result only. Before final verification, restore the full intended constraint set, set `config_timing_analysis -ignore_io_paths no`, and rerun the applicable reports. Do not adopt reduced constraints or a changed target clock as a timing-closure result.

## Diagnosing Violation Root Causes

Read `references/diagnosis-guide.md` for detailed patterns. Quick reference:

| Symptom | Likely Cause | Strategy |
|---------|-------------|----------|
| Route delay > 60% of path delay | Poor cell placement (spread) | Pblock or place_design Explore |
| Logic delay > 60% of path delay | Deep logic levels | LUT merging or pipeline (requires RTL change) |
| High fanout nets on critical paths | Driver overload | Fanout splitting (test carefully) |
| WNS degrades after routing | Congestion | `report_design_analysis -congestion` |
| Place 46-14 warning | Placer detects high congestion | Analyze congestion BEFORE routing |
| Route 35-443 CLB congestion | Local hot-spots despite OK global levels | Check generated txt file for congested CLBs |
| Many failing endpoints but small TNS | Isolated paths | phys_opt_design targeted passes |
| Few failing endpoints but large TNS | Systematic issue | Check constraints first |
| High Rent exponent (>0.65) | Inherent design complexity | Floorplan restructuring, SSI-aware partitioning |
| Clock skew > 500 ps on sync paths | Unbalanced clock trees | CLOCK_DELAY_GROUP, remove cascade buffers |

## Advanced Optimization Topics

Read `references/advanced-optimization.md` when the task involves SSI/SLR-specific optimization, Laguna register placement, UG949 multi-cycle-path details, Vivado/RapidWright environment tuning, incremental implementation, or a complete TCL optimization script template.

Quick reminders:
- For SSI devices, check `report_utilization -slr` and keep critical logic within one SLR when possible.
- Register SLR boundary crossings; prefer `USER_SLL_REG` over manual Laguna placement unless exact control is required.
- For multi-cycle paths, adjust hold after setup and constrain pins rather than whole cells.
- Use Vivado/RapidWright version notes in the reference before comparing DCP optimization results.

## Key Principles

1. **Start with constraints, not optimization**. An incorrectly constrained design wastes all optimization effort.
2. **`place_design -directive Explore` is the single biggest lever**. It consistently delivers 20-45% Fmax improvement.
3. **Separate a strategy plateau from task completion**. Use the Iteration Pattern above to compare all relevant metrics, preserve the best candidate, and reassess within the existing limits. Only full acceptance establishes closure.
4. **Physical optimizations have a ceiling**. Around 0.4 ns WNS residual typically means logic depth is the limit — physical changes alone won't help.
5. **Validate netlist changes on a copy first**. Follow the Layer 4 validation guidance; use a documented test mode only when the actual tool supports it. Changes that add cells (fanout splitting) can easily backfire.
6. **Version matters**. Vivado 2025.2 placement produces different results than 2025.1. Use what works best for each design.

## References

- `references/diagnosis-guide.md` — Detailed timing violation diagnosis patterns
- `references/methodology-checklist.md` — XTP301 checklist mapped to optimization workflow
- AMD UG949: UltraFast Design Methodology Guide for FPGA and SoC
- AMD UG1292: UltraFast Design Methodology Timing Closure Quick Reference Guide
- AMD XTP301: UltraFast Design Methodology Checklist
- [AMD UG835: phys_opt_design](https://docs.amd.com/r/2025.2-English/ug835-vivado-tcl-commands/phys_opt_design) — post-place/post-route operation and tool-managed netlist changes
