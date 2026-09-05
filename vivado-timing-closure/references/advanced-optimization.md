# Vivado Timing Closure Advanced Optimization

Advanced SSI, constraint, environment, incremental implementation, and script-template notes split from SKILL.md.

## SSI Device-Specific Optimization (xcvu3p, xcvu9p, etc.)

Stacked Silicon Interconnect (SSI) devices partition logic across multiple Super Logic Regions (SLRs, i.e., separate dies). Cross-SLR paths use expensive SLL (Super Long Line) resources with higher and more variable delay.

### SLR Utilization Balance:

```tcl
# After placement, check per-SLR utilization
report_utilization -slr
report_qor_assessment  # includes SLR-specific table
```

Signs of imbalance: one SLR > 70% while others < 50%. Use `USER_SLR_ASSIGNMENT` to guide placement without over-constraining.

### SLR Crossing Optimization:

1. **USER_CROSSING_SLR**: Guides the placer to choose optimal SLR crossing points
2. **USER_SLL_REG** (UltraScale+): Maps register-to-register SLR crossings to dedicated Laguna TX_REG→RX_REG paths
   - Reduces congestion near SLR boundaries
   - Improves delay estimation accuracy
   - Higher and more consistent SLR crossing performance
   - UltraScale (non-Plus): can only use TX_REG or RX_REG, not both
3. **Laguna register manual placement**: For critical crossings, manually place registers at LAGUNA sites:
   ```tcl
   set_property BEL TX_REG3 [get_cells reg_A]
   set_property BEL RX_REG3 [get_cells reg_B]
   set_property LOC LAGUNA_X2Y480 [get_cells reg_A]
   set_property LOC LAGUNA_X2Y360 [get_cells reg_B]
   ```

### SLR Crossing Best Practices:
- Register ALL SLR boundary crossings (pipeline across dies)
- Use pblock to constrain critical logic to a single SLR
- `USER_SLL_REG` is preferred over manual placement — let the tool choose exact Laguna sites when possible
- Cross-SLR clock skew can be significantly higher than intra-SLR — check `report_clock_interaction` for SLR-aware clock planning

## Constraint Tips (from UG949 Chapter 4)

### Multi-Cycle Paths:
When clock enables activate every N cycles, apply multi-cycle exceptions. **Critical rule**: adjusting setup edge also moves the hold edge. Always add a second `-hold` constraint:

```tcl
set_multicycle_path -from [get_pins REGA/C] -to [get_pins REGB/D] -setup 3
set_multicycle_path -from [get_pins REGA/C] -to [get_pins REGB/D] -hold 2
```

**Always constrain PINS, not cells**: cells have multiple endpoints (D, EN, RST). Constraining the cell incorrectly applies the exception to all endpoints.

Exception: synchronous CDC paths with phase-shifted clocks only need setup modification (no hold adjustment needed).

## Environment Configuration

### Vivado Version Differences:
- Vivado 2025.2's `place_design` produces different (often better) results than 2025.1
- Always note the design's creation version when opening DCPs
- DCP integrity warnings (version mismatch) are expected and harmless

### RapidWright JVM Configuration:

These notes apply only when RapidWright is already available and useful for the authorized task. Check the actual installation and exposed APIs before using helper examples. Use available Vivado reports and operations for suitable alternatives; a missing optional dependency does not authorize installation or block unrelated work.

- **Java 11 recommended** (Java 21 has known G1 GC crashes with certain design operations)
- Use Vivado's bundled Java: `$VIVADO_ROOT/tps/lnx64/jre11*/bin/java`
- The pip `rapidwright` package includes a standalone JAR — use it directly:
  ```bash
  export RAPIDWRIGHT_PATH=<path>/RapidWright
  export CLASSPATH=$RAPIDWRIGHT_PATH/jars/rapidwright-standalone.jar
  ```
- RapidWright loads DCPs 3-5x faster than Vivado — use it for analysis, Vivado for implementation

### DCP Loading Time Reference (xcvu3p, ~37K cells):
- Vivado: ~10 seconds
- RapidWright: ~1.3 seconds

### Incremental Implementation (ECO Flow):
When making small changes to an already-implemented design, use incremental mode to preserve existing placement/routing:

```tcl
read_checkpoint -incremental <previous.dcp>
place_design   # only places newly unplaced cells
route_design   # only routes newly unrouted nets
```

This preserves ~95% of existing placement/routing and dramatically improves runtime. Ideal for:
- After RapidWright netlist modifications (fanout splitting, LUT merging)
- After manual cell relocation ECOs
- When only a few cells have been changed

## Complete Optimization Script Template

Adapt these stage blocks to the requested flow. They assume full intended constraints and candidate output paths that are new or known to be replaceable from task ownership and file provenance. Inspect execution status and reports at each decision point; for unattended execution, encode the applicable checks as failure conditions. Advancing after passing checks within an already-authorized run does not require another user confirmation.

```tcl
# Open and baseline
open_checkpoint <input.dcp>
report_timing_summary -delay_type min_max -file baseline.rpt

# Constraint check
check_timing
report_methodology

# QoR assessment
report_qor_assessment
report_qor_suggestions

# Layer 2: Implementation optimization
place_design -directive Explore
phys_opt_design -directive Explore
route_design

report_timing_summary -delay_type min_max -file candidate.rpt
report_route_status
```

If remaining violations and the diagnosis justify another pass, and the current design state supports post-route optimization, run the following stage within the existing limits. Otherwise proceed to final verification or reassess the strategy using the [Iteration Pattern](../SKILL.md#iteration-pattern).

```tcl
phys_opt_design -directive AggressiveExplore
route_design -directive NoTimingRelaxation -tns_cleanup
```

For final verification, first ensure the full intended constraints are active. Collect and inspect the applicable evidence against the [Timing Acceptance Criteria](../SKILL.md#timing-acceptance-criteria), including bus skew when constrained:

```tcl
config_timing_analysis -ignore_io_paths no
report_timing_summary -delay_type min_max
report_route_status
check_timing
report_exceptions -coverage
report_methodology
report_drc
report_cdc

# Save the candidate without implying that it passed acceptance.
write_checkpoint <candidate_output.dcp> -force
```

Report the candidate as timing-closed only if all applicable checks pass and the requested outputs are delivered. Otherwise retain the best candidate, identify failed or missing checks, and continue feasible authorized work; apply the strategy and overall stopping limits rather than declaring success.
