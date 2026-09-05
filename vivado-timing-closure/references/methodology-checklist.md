# XTP301 Methodology Checklist — Timing-Relevant Items

Mapped from AMD XTP301 UltraFast Design Methodology Checklist to actionable verification steps. Organized by design phase.

Apply the checks relevant to the requested stage and reuse current evidence. Optimization techniques, GUI workflows, multiple strategies, and parallel runs are conditional methods, not universal prerequisites for answering a question or completing an already-passing design. Mark an inapplicable method as such; do not treat missing acceptance evidence as a pass. Use the [Timing Acceptance Criteria](../SKILL.md#timing-acceptance-criteria) for final closure.

## Design Creation Phase

### Clock Setup (XTP301 §4.2.1)
- [ ] All clocks defined via Clocking Wizard or explicit create_clock
- [ ] No gated clocks in design (use CE pins instead)
- [ ] Clock components at top level for sharing
- [ ] Clocks on dedicated clock routing (not local interconnect)
- [ ] UltraScale: Follow recommended clock topology in UG949
- [ ] Run `check_timing` + `report_methodology` after opt_design

### Reset Design (XTP301 §4.2.2)
- [ ] Minimize reset usage (control logic only, not datapath)
- [ ] Resets synchronized within their clock domain
- [ ] No global asynchronous reset unless essential for startup

### Constraints (XTP301 §4.2.3)
- [ ] Clock constraints are correct and complete, whether established through Tcl or the Timing Constraints Wizard
- [ ] All critical warnings in Messages tab resolved
- [ ] `report_timing_summary` shows no anomalies
- [ ] `report_clock_interaction` confirms correct clock relationships
- [ ] Existing complete constraints form the baseline; any reduced-I/O diagnostic experiment is isolated and its results are marked provisional

## Post-Synthesis Checks (XTP301 §4.3)

### Design Integrity (§4.3.1)
- [ ] Synthesis log reviewed: all critical warnings fixed
- [ ] `report_drc` + `report_methodology` run
- [ ] All DRC violations reviewed and resolved or waived

### Utilization (§4.3.2)
- [ ] `report_utilization` shows reasonable margins
- [ ] `report_qor_assessment` run
- [ ] High utilization blocks identified for optimization
- [ ] Synthesis strategy evaluated (PerfOptimized vs AreaOptimized)

### Performance (§4.3.3) — **KEY for timing**
- [ ] `report_timing_summary` shows internal paths approaching closure
- [ ] Clock and constraint issues resolved BEFORE implementation
- [ ] High fanout nets identified and monitored
- [ ] `report_qor_suggestions` reviewed for auto-fixable violations
- [ ] Block-level synthesis strategies applied to critical submodules

### Reliability (§4.3.4)
- [ ] `report_cdc` run after each major block update
- [ ] CDC violations reviewed and waived where safe

## Implementation Success (XTP301 §4.4)

### Design Integrity (§4.4.1)
- [ ] All warnings reviewed
- [ ] `report_drc` + `report_methodology` run post-implementation
- [ ] Violations reviewed and waived where appropriate

### Performance (§4.4.2) — **KEY for timing**
- [ ] Baseline setting and constraint validation process executed
- [ ] Timing errors analyzed at each implementation stage
- [ ] If timing is still failing and the diagnosis supports exploration, alternative implementation strategies evaluated within the existing scope and budget (including applicable ML suggestions)
- [ ] Failed timing paths analyzed in detail
- [ ] Intelligent Design Runs (IDR) considered when available and useful for unresolved timing issues

### Placement Issues (§4.4.3)
- [ ] `report_qor_assessment` control set issues reviewed
- [ ] Excessive control sets addressed (reduce set/reset/CE combinations)
- [ ] High fanout nets not causing placement distortion

### Routing Issues (§4.4.4)
- [ ] Congestion identified early via log file analysis
- [ ] Congestion severity level < 5
- [ ] `report_design_analysis` used for congestion analysis
- [ ] LUT combining / MUXF / CARRY / SRL options reviewed for congestion impact
- [ ] Hold time violations addressed BEFORE routing (via phys_opt_design)
- [ ] `CELL_BLOAT_FACTOR` applied to congested modules if needed

### Strategy Testing (§4.4.5)
- [ ] Alternative runs performed only while unresolved issues and diagnostic evidence justify another strategy
- [ ] Candidate runs compared using WNS, TNS, failing endpoints, hold, pulse width, route status, and applicable resource limits under consistent constraints
- [ ] Incremental implementation flow considered for small changes
- [ ] Parallel execution (OOC synthesis/implementation) considered when useful and within the existing resource budget

## Timing Convergence Specific (UG949 Chapter 6)

### Clock Interaction Report — Color Matrix Reference

| Color | Label | Meaning | Required Action |
|-------|-------|---------|-----------------|
| Black | No path | No interaction | Reference only |
| Green | Timed | Synchronous, paths timed | Verify intended |
| Cyan | Partial False Path | Some paths excluded | Verify exceptions correct |
| **Red** | **Timed (unsafe)** | **Timed but clocks async** | **Add clock_groups or false_path** |
| **Orange** | **Partial False (unsafe)** | **Async but incomplete exclusion** | **Fix exception coverage** |
| Blue | User Ignored | Excluded by constraints | Verify CDC circuit correct |
| Light blue | Max Delay Datapath | set_max_delay -datapath_only | Verify delay value |

### Baseline Setting Process (Full UG949 Workflow)

Follow the canonical [Detailed Baseline Setting Process](../SKILL.md#detailed-baseline-setting-process-from-ug949). Preserve the existing complete constraints and all AMD IP constraints. Reconstruct a baseline only when needed for an authorized diagnosis, using an isolated copy and correctly preserved or reloaded IP constraints before measurements.

An I/O-exclusion experiment is provisional. Restore the full intended constraints and `config_timing_analysis -ignore_io_paths no` before final verification. Do not restart a reduced-constraint flow after full-constraint verification, and do not treat baseline reconstruction as a prerequisite for routine analysis.

### Clock Skew Guidelines (from UG949)
- Intra-clock paths: skew typically < 300 ps
- Synchronous clock pairs: skew typically < 500 ps
- Unbalanced clock trees: skew can reach several ns → nearly impossible to close timing
- Cross-SLR or cross-I/O-column paths have elevated skew
- `CLOCK_DEDICATED_ROUTE=FALSE`: **never use in production** — routes clocks on general interconnect
- `ANY_CMT_COLUMN`: preferred over FALSE — keeps clocks on dedicated resources
- `CLOCK_DELAY_GROUP`: enforces matched routing for critical synchronous clocks
- Place MMCM/PLL near clock load center to minimize network delay

### Common Timing Convergence Techniques
- Track WNS, TNS, and failing endpoints together; verify hold and pulse width as well. Improving WNS alone does not establish closure.
- Check for severe WHS violations (< -1 ns) — indicates missing constraints
- Evaluate tradeoffs: design choices vs constraints vs architecture
- After timing is met, tools stop optimizing — no extra margin added

### Fmax Calculation
```
Fmax (MHz) = 1000 / (clock_period_ns - WNS_ns)
```
Where WNS is negative for failing paths. Example: period=1.5ns, WNS=-0.419ns → Fmax = 1000/(1.5-(-0.419)) = 1000/1.919 = 521.1 MHz.

### Final Verification for a Closure Task
- [ ] The same final design passes the [Timing Acceptance Criteria](../SKILL.md#timing-acceptance-criteria), including the stated positive margins and complete routing
- [ ] Full intended constraints and I/O analysis are active
- [ ] `check_timing` shows 0 unconstrained internal endpoints (acceptance quality)
- [ ] Timing exceptions reviewed: no unexpected paths in "User Ignored Paths"
- [ ] Applicable CDC, DRC, methodology, and separate bus-skew checks reviewed and resolved or justifiably waived within scope
- [ ] SSI designs: SLR utilization balanced, SLL crossings optimized
- [ ] Power numbers re-checked (timing fixes may have increased power)
- [ ] Requested artifacts and verification results delivered; unperformed checks explicitly identified rather than marked passed

## Methodology DRC Quick Reference (from UG949 Tables 6 & 7)

When `report_methodology` flags these violations, here's what they mean and what to do.

### Timing Convergence Impact DRCs (affect timing closure difficulty):

| DRC | Severity | Description | Action |
|-----|----------|-------------|--------|
| TIMING-6 | Critical | No common primary clock between related clocks | Add clock_groups or redesign clock topology |
| TIMING-7 | Critical | No common node between related clocks | Check clock tree; may need BUFG_GT or CLOCK_DELAY_GROUP |
| TIMING-8 | Critical | No common period between related clocks | Async clocks — add set_clock_groups |
| TIMING-14 | Critical | LUT on clock tree | Remove LUT from clock path; use CE pin for gating |
| TIMING-15 | Warning | Severe hold violation on inter-clock paths | Check CDC circuit; may need set_max_delay -datapath_only |
| TIMING-16 | Warning | Large setup violation | Standard timing closure — use Layer 2/3 strategies |
| TIMING-30 | Warning | Generated clock on sub-optimal master pin | Reassign generated clock to better master source |
| TIMING-31 | Critical | Inappropriate multicycle on phase-shifted clocks | Phase-shift sync CDC only needs setup MCP, not hold |
| TIMING-32/33 | Warning | Non-recommended bus skew constraint | Review bus skew requirements |
| TIMING-36 | Critical | Missing master clock edge propagation for generated clock | Check create_generated_clock -master_clock |
| TIMING-42 | Warning | Clock propagation blocked by path segmentation | Review clock path for segmenting constraints |
| TIMING-44 | Warning | Unreasonable user clock uncertainty | Review set_clock_uncertainty values |
| TIMING-48 | Advisory | set_max_delay -datapath_only on latch input | Typically safe; verify latch timing |
| TIMING-56 | Warning | Missing clock group exclusion (logical or physical) | Add set_clock_groups for independent async clocks |
| XDCH-1 | Warning | Missing -hold in multicycle path constraint | Add set_multicycle_path -hold N-1 |
| XDCV-1 | Warning | Incomplete constraint coverage due to missing replicated objects | Review -include_replicated_objects usage |
| XDCV-2 | Warning | Incomplete constraint coverage due to missing replicated objects | Review constraint scoping |

### Acceptance Quality DRCs (affect timing analysis accuracy — fix before signoff):

| DRC | Severity | Description | Action |
|-----|----------|-------------|--------|
| TIMING-1/2/5 | Critical | Non-recommended clock source definition | Redefine create_clock on proper source pin |
| TIMING-17 | Critical | Sequential cell without clock | Add clock constraint or set as false path |
| TIMING-18/20 | Warning | Missing clock or I/O delay | Add missing constraints |
| TIMING-25 | Critical | Unexpected clock waveform | Check create_clock waveform parameters |
| TIMING-35 | Critical | No common node on same-clock paths | Check clock buffer placement; reduce clock skew |
| TIMING-40/43 | Warning | Inappropriate clock topology or requirement | Review clock topology vs constraints |
| TIMING-41 | Warning | Invalid propagated clock on internal pin | Move clock definition to proper source |
| TIMING-47 | Warning | False path or async clock group between synchronous clocks | Verify clocks are truly async; remove exception if not |
| TIMING-51 | Critical | No common phase between parallel MMCM/PLL clocks | Review MMCM/PLL configuration |
| TIMING-52 | Critical | No common phase between spread-spectrum MMCM clocks | Check SSMOD configuration |
| TIMING-54 | Critical | Scoped false path/clock group/max_delay between clocks | Review constraint scoping; prefer unscoped |
| TIMING-55 | Critical | Multiple clocks on same CMB deskew pin | Redesign clock topology |
| TIMING-57 | Warning | Unsupported PHASESHIFT_MODE + digital deskew | Change MMCM configuration |

## Quick Verification Script

```tcl
# Collect evidence after an implementation iteration when those checks are relevant.
# Reports must be inspected; this procedure does not return a signoff verdict.
proc check_health {} {
    puts "=== ROUTE STATUS ==="
    report_route_status

    puts "=== TIMING ==="
    report_timing_summary -delay_type min_max

    puts "=== UNCONSTRAINED ==="
    check_timing

    puts "=== METHODOLOGY ==="
    report_methodology

    puts "=== QoR ==="
    report_qor_assessment
}
```
