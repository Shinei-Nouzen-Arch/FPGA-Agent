# Vivado Debug Troubleshooting and Reporting

Detailed troubleshooting, SVF programming, and debug reporting notes split from SKILL.md.

## Common Error Troubleshooting

### "debug hub not detected"

**Error message:**
```
INFO: [Labtools 27-1434] Device xxx (JTAG device index = 0) is programmed
with a design that has no supported debug core(s) in it.
WARNING: [Labtools 27-3123] The debug hub core was not detected at User
Scan Chain 1 or 3.
```

**Causes and solutions:**
1. Debug Hub clock is not free-running or is inactive
   - Ensure the clock connected to `dbg_hub` core is free-running and stable
   - If driven from MMCM/PLL, verify LOCKED is high
2. User Scan Chain mismatch
   - Launch hw_server with: `hw_server -e "set xsdb-user-bscan <C_USER_SCAN_CHAIN scan_chain_number>"` to detect debug hub at User Scan Chain 2 or 4
   - Check setting: `get_property C_USER_SCAN_CHAIN [get_debug_cores dbg_hub]`
3. BSCAN_SWITCH_USER_MASK not set correctly
   - Verify in Hardware Device Properties

### "unrecognizable debug core"

**Error message:**
```
CRITICAL WARNING: [Labtools 27-1433] Device xxx is programmed
with a design that has an unrecognizable debug core (slave type = 17) at
user chain = 1, index = 0.
Resolution:
1) Ensure that the clock signal connected to the debug core and/or debug
   hub is clean and free-running.
2) Ensure that the clock connected to the debug core and/or debug hub meets
   all timing constraints.
3) Ensure that the clock connected to debug core and/or debug hub is faster
   than the JTAG clock frequency.
```

**Causes and solutions:**
1. Debug core clock is inactive or unstable
   - Ensure the clock is free-running, stable, and meets timing
2. Debug core clock is slower than JTAG clock
   - Lower JTAG frequency or use a faster debug clock
   - Remember the 2.5x rule: debug hub clock must be > 2.5x JTAG clock
3. Timing violations in debug hub or debug core
   - Enable clock divider on dbg_hub (C_ENABLE_CLK_DIVIDER)
   - Add input pipe stages to ILA (C_INPUT_PIPE_STAGES)

### Debug Bridge IP Conflict

**Error message:**
```
[Chipscope 16-336] Failed to find or create hub core for debug slave
<debug core name>. Insertion of debug hub is not supported when there are
instantiated debug bridge cores in either master mode or switch enabled in
the design.
```

**Solution:** Ensure the design has at least one instance of a Debug Bridge IP in BSCAN-to-Debug Hub mode. Either remove the debug slave core or instantiate a debug bridge master in the region of the debug slave.

## SVF File Programming

Serial Vector Format (SVF) provides offline FPGA/configuration memory programming without a live JTAG connection.

**Note:** SVF programming is not supported on AMD Versal devices.

### SVF File Creation Flow

```
1. create_hw_target my_svf_target    ;# Create offline SVF target
2. open_hw_target                     ;# Open the SVF target
3. create_hw_device -part <part>      ;# Add devices to define JTAG chain
4. set_property PROGRAM.FILE {file.bit} $device
   program_hw_devices $device         ;# Record programming operations
5. write_hw_svf my_output.svf         ;# Write cached operations to SVF file
6. close_hw_target                    ;# Close SVF target
```

**Important:** Create ALL devices in the chain first, then perform programming operations. Interleaving `create_hw_device` and `program_hw_devices` produces incorrect SVF sequences.

### SVF Execution

```tcl
execute_hw_svf my_file.svf
```

- Use `-verbose` option to see JTAG_TCL operations
- **Size limit:** Vivado supports SVF files under 500 MB. For larger files, use a third-party SVF player.
- The XSVF file format is not supported in Vivado IDE.

## Configurable Report Strategies for Debug

### report_debug_core Usage

After inserting debug cores, use `report_debug_core` to verify the debug configuration:

```tcl
# Report all debug cores in the design
report_debug_core

# Key information reported:
#   - Debug core instances and types
#   - Connected probe nets and widths
#   - Clock domain assignments
#   - Core properties (C_DATA_DEPTH, C_ADV_TRIGGER, etc.)
```

### Useful Debug Verification Commands

| Command | Purpose |
|---|---|
| `report_debug_core` | List all debug cores, their probes, and properties |
| `get_debug_cores` | Return list of debug core objects in design |
| `get_debug_ports` | Return list of debug port objects |
| `report_property [get_debug_cores u_ila_0]` | Show all properties of a specific ILA core |
| `get_property C_USER_SCAN_CHAIN [get_debug_cores dbg_hub]` | Check BSCAN user scan chain setting |
| `get_property C_DATA_DEPTH [get_debug_cores u_ila_0]` | Check ILA capture depth |
| `report_hw_targets` | Report all active hardware targets, devices, and properties |

### Post-Implementation Debug Verification

```tcl
# After implementation, verify debug cores are intact
open_run impl_1
report_debug_core
report_utilization -cells [get_cells -hierarchical -filter {IS_DEBUG_CORE}]

# Check DONE status after programming
get_property REGISTER.IR.BIT5_DONE [lindex [get_hw_devices] 0]

# For Versal devices (different register)
get_property REGISTER.JTAG_STATUS.BIT[34]_DONE [lindex [get_hw_devices] 1]
```
