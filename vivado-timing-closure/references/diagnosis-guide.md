# Timing Violation Diagnosis Guide

For report-only requests, use the available reports to explain the result and identify verification gaps. The optimization actions below apply when execution or changes are authorized. Use the main skill's [Timing Acceptance Criteria](../SKILL.md#timing-acceptance-criteria) and [Iteration Pattern](../SKILL.md#iteration-pattern) for closure and stopping decisions.

## How to Read a Timing Report

### Timing Summary Structure

```
WNS(ns)  TNS(ns)  Failing Endpoints  WHS(ns)  THS(ns)  WPWS(ns)  TPWS(ns)
-0.419   -361.827 1461               0.086     0.000     0.475      0.000
```

- **WNS** (Worst Negative Slack): The single worst failing path. If this can be fixed, TNS usually follows.
- **TNS** (Total Negative Slack): Sum of all failing path slacks. Large TNS with small WNS means many paths share similar issues.
- **Failing Endpoints**: Number of register endpoints failing setup. A decrease in this number even without WNS improvement is progress.
- **WHS** must be > 0 for hold (positive is good).
- **WPWS** must be > 0 for pulse width (positive is good).

### Clock Summary

```
Clock             Period(ns)  Frequency(MHz)
clk_fpl26contest  1.500       666.667
```

Target Fmax = 666.667 MHz. Actual Fmax = 1000 / (1.500 - (-0.419)) = 1000 / 1.919 = 521.10 MHz.

Fmax deficit = 666.67 - 521.10 = 145.57 MHz.

### Worst Path Analysis

```
Startpoint: layer0_reg/data_out_reg[20]/C    (source FF)
Endpoint:   layer1_reg/data_out_reg[60]/D    (sink FF)
Slack:      -0.419 ns
Logic Levels: 4-5 (typical for logicnets)
Route%:     60-75% (from QoR suggestions)
```

## Diagnosis Patterns

### Pattern 1: Route-Dominated Violation (Route > 60%)

**Symptoms**:
- Path delay breakdown shows net delay > 60% of total
- Critical cells spread across large Manhattan distance (> 70 tiles)
- Native path/placement analysis, or `analyze_critical_path_spread` if that optional helper is available, shows substantial spread that supports a pblock experiment
- WNS is moderate (-0.1 to -0.5 ns)

**Root Cause**: Cells on critical paths placed too far apart. Routing takes long detours.

**Solution**:
1. `place_design -directive Explore` (first line — often fixes it alone)
2. Pblock re-placement if Explore is insufficient
3. Cell re-placement via RapidWright for 1-2 isolated paths

**Expected improvement**: 10-45% Fmax

### Pattern 2: Logic-Dominated Violation (Logic > 60%)

**Symptoms**:
- Cell delay dominates path delay
- High logic level count (6+ levels between registers)
- Often seen in designs with deep combinational chains
- `report_qor_suggestions` flags LUT budgeting issues

**Root Cause**: Too many logic levels between registers. Clock period too short for the combinational work.

**Solution**:
1. LUT input cone optimization (if LUT2-LUT5 chains exist)
2. Pipeline insertion — requires RTL change or RapidWright ECO within the authorized scope
3. Logic restructuring (MUXF remapping, carry chain optimization)

**Expected improvement**: Variable, may require architectural changes

### Pattern 3: High Fanout Net Violation

**Symptoms**:
- Nets with fanout > 200 appearing on multiple critical paths
- Source driver placement is poor relative to loads
- Routing delay on these nets dominates path delay

**Root Cause**: Single driver must reach hundreds of loads spread across the chip.

**Solution**:
1. `optimize_fanout` with split_factor = fanout/100 (min 3, max 8)
2. Place replicated drivers near their load clusters
3. Re-route split nets

**Warning**: Fanout splitting adds replicated cells. If the design is already dense (high utilization), this can cause congestion and degrade timing. Always test on a copy first.

**Discriminator**: If `optimize_fanout` makes timing WORSE (common in 30-40% of cases), the design's fanout is architectural (e.g., neural network layer outputs) and should not be split.

### Pattern 4: Congestion-Induced Violation

**Symptoms**:
- WNS degrades significantly after routing (compared to post-placement estimate)
- `report_design_analysis` shows high congestion scores
- Many nodes with routing overlaps during route_design
- Intermediate routing WNS much worse than final (or vice versa)

**Root Cause**: Too many nets competing for limited routing resources in a region.

**Solution**:
1. `report_design_analysis -congestion` to identify congested areas
2. Adjust placement density in congested regions (CELL_BLOAT_FACTOR)
3. Reduce MUXF/CARRY chain usage in congested areas via opt_design
4. Use routing directives: `route_design -directive NoTimingRelaxation`
5. In extreme cases: re-floorplan with more space allocation

**Expected improvement**: 5-15% reduction in TNS

### Pattern 5: Control Set Overload

**Symptoms**:
- `report_qor_assessment` flags CONTROL_SET issues
- Many different reset/set/clock_enable combinations
- Placement seems suboptimal despite low utilization

**Root Cause**: Too many unique control sets (combinations of clock, reset, set, CE) limit placer flexibility. Each unique control set can only use specific SLICE sites.

**Solution**:
1. Reduce reset usage (only reset control logic, not datapath)
2. Use synchronous resets where possible
3. Consolidate clock enable signals
4. In RTL: avoid unique resets per register; share reset signals

### Pattern 6: SSI Cross-SLR Violation

**Symptoms** (xcvu3p and other SSI devices):
- Paths crossing SLR boundaries have very high routing delay
- SLL (Super Long Line) resource overuse
- One SLR has much higher utilization than others

**Root Cause**: SSI devices partition logic across multiple dies. Cross-die connections use expensive SLL resources.

**Solution**:
1. `USER_SLR_ASSIGNMENT` to guide SLR placement
2. `USER_SLL_REG` to increase Laguna register usage
3. Pblock per-SLR to keep critical logic within one die
4. Register SLR crossings (pipeline across boundaries)

## Using report_qor_suggestions Output

The `.rqs` output contains:

1. **XDC Suggestions**: Path-level recommendations with net/LUT budget analysis
2. **ML Strategies**: Auto-generated implementation directives ranked by predicted effectiveness
3. **Strategy IDs**: RQS_STRAT-N with specific directives for each step

### Interpreting ML Strategy Rankings:

```
#1 RQS_STRAT-37: ExtraTimingOpt + AggressiveExplore + NoTimingRelaxation
#2 RQS_STRAT-2:  Explore + Explore + Explore
#3 RQS_STRAT-35: ExtraNetDelay_low + AggressiveExplore + NoTimingRelaxation
```

Always try strategy #1 first. If it doesn't work, #2 (the "safe" Explore strategy) is a reliable fallback.

## Congestion Deep-Dive (from UG949)

### Router Log Congestion Table

When congestion level is 4+, the router prints a congestion table:

```
Global Congestion: overall interconnect usage across all types
Long Congestion:   long-distance interconnect usage (given direction)
Short Congestion:  all other interconnect usage (given direction)
```

- **Long congestion** → longer routing delays (router switches to short wires, travel further)
- **Short congestion** → longer runtime; if tile% > 5%, QoR degradation

### CLB-Level Congestion

Even when global congestion is acceptable (<5), local CLB congestion can cause routing failure:

```
INFO: [Route 35-443] CLB routing congestion detected. Several CLBs have
high routing utilization, which can impact timing closure. Congested CLBs
and Nets are dumped in: iter_NNN_CongestedCLBsAndNets.txt
```

Read the generated txt file to find the specific CLBs and nets causing local hotspots. Apply `CELL_BLOAT_FACTOR` to affected modules.

### Router Priority During Congestion

1. Global Iterations: router seeks compliant solution (no overlaps, satisfies setup + hold)
2. If not converging: **stops timing optimization**, prioritizes finding valid routing
3. Warning appears: `Route 35-447` — "router will prioritize successful completion of routing"
4. Once valid routing found: **re-enables timing optimization**

**Implication**: Intermediate routing WNS during congestion can spike dramatically. This is normal — wait for the final result.

### Place 46-14 Warning

```
WARNING: [Place 46-14] The placer has determined that this design is highly
congested and may have difficulty routing. Run report_design_analysis -congestion
for a detailed report.
```

This appears after placement. Do NOT ignore it — analyze congestion before routing.

## Complexity Analysis (from UG949)

Run BEFORE implementation to predict routing difficulty:

```tcl
report_design_analysis -complexity [-hierarchical_depth <N>]
```

### Rent Exponent Ranges:

| Range | Classification | Implication |
|-------|---------------|-------------|
| 0.0 – 0.65 | Normal | Should implement without major routing issues |
| 0.65 – 0.85 | High | Especially significant if total instances > 15,000 |
| > 0.85 | Very high | Combined with high instance count → may fail implementation |

### Average Fanout Ranges:

| Range | Classification | Implication |
|-------|---------------|-------------|
| < 4 | Normal | Standard routing demand |
| 4 – 5 | High | Congestion likely; SSI designs >100K instances may not fit in one SLR |
| > 5 | Very high | Design may fail implementation |

### How to Use Complexity Analysis:

1. Run on top-level design first
2. If metrics are high, use `-hierarchical_depth` to drill into submodules
3. Small modules (<15K instances) can have high metrics but still work
4. Focus optimization on high-Rent/high-fanout modules with high instance counts
5. Consider floorplan restructuring for modules with very high Rent exponents

## Practical Diagnostic Workflow (Updated)

Use available evidence for diagnosis; the implementation steps apply only when optimization is requested. A missing optional helper does not prevent native report analysis or other feasible work.

```
1. Inspect current reports or open the relevant checkpoint when execution is in scope
2. report_timing_summary → record setup, hold, pulse width, and failure counts
3. WNS >= 0 or high QoR score → perform full Timing Acceptance Criteria
   All applicable checks and requested deliverables complete → closure is complete
   Otherwise → investigate the remaining failures or missing evidence
4. check_timing → any unconstrained internal endpoints?
   YES → diagnose and correct supported issues within scope, preserving IP constraints
5. report_methodology → any TIMING/XDC violations?
   YES → investigate and address within scope, then refresh affected evidence
6. report_qor_assessment → what's the score?
   1-2 → major constraint or configuration issue, investigate further
   3-5 → assess remaining issues; the score alone is not signoff
7. report_clock_interaction → any RED cells (unsafe timed async clocks)?
   YES → verify clock relationships and CDC before applying justified exceptions
8. report_qor_suggestions → review suggested ML strategies
9. report_design_analysis -congestion → any congestion warnings?
   Place 46-14 or congestion level 5 → apply congestion mitigation BEFORE routing
10. report_design_analysis -complexity → Rent >0.65 or avg fanout >4?
    YES → design has inherent complexity; consider floorplan restructuring
11. Look at PATTERN of worst paths (use diagnosis patterns above)
12. Select strategy based on dominant pattern
13. Apply authorized optimization, record all relevant metrics, preserve the best candidate
14. Assess progress using the main skill's Iteration Pattern
    Strategy plateau → end that loop, reassess, and try a supported alternative within limits
    No feasible in-scope next step or overall limit reached → report incomplete closure,
    remaining violations, best artifacts, and the concrete limitation or missing decision
```
