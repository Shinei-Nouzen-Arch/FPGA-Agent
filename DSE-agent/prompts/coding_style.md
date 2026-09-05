# HLS Implementation Guidance

Apply these principles to the selected benchmark and installed HLS version. They are decision aids, not a demand to use every pragma or architecture in every kernel.

## Preserve the contract

Keep the top-level interface, memory layout, arithmetic behavior, reference tests, and tolerance intact. Use fixed-width integer/fixed-point types when the contract calls for them or a transformation preserves its semantics. Floating-point contracts remain valid: do not require every kernel to use `ap_int`/`ap_fixed`, or convert FP32 to FP16 as an unapproved tuning step.

Account for signedness, intermediate widths, truncation, overflow, saturation, rounding, reduction order, and boundary cases. Do not suppress a true dependency or weaken a test to obtain a better II.

## Make hardware intent inspectable

Organize modules and data movement so that the intended architecture can be compared with synthesis evidence. Separate load/compute/store when it serves the assigned architecture; simple kernels need not acquire an artificial three-stage pipeline.

Choose pipelining, unrolling, partitioning, reshaping, dataflow, and storage binding based on the actual recurrence, bandwidth, and area tradeoff. An absent pragma is not itself a correctness failure. State a target II with its transaction unit; recurrence-limited designs can legitimately have II greater than one.

Check concurrent accesses against the inferred memory ports/banks. Partitioning is one possible remedy, not a universal requirement for every array. Avoid full partitioning merely because an access is irregular; inspect area and scheduling consequences.

## Dataflow and storage

When dataflow is used, make channel ownership, production/consumption counts, access order, and backpressure explicit. Size FIFOs/buffers from the actual schedule and validate deadlock behavior in co-simulation. Do not assume that a universal depth formula or a FIFO alone guarantees progress.

Use tool-supported channel patterns for the selected release. Do not assert that all shared arrays, feedback, or interleaved reads/writes are universally forbidden; determine whether the concrete pattern is legal and safe.

Storage cost depends on depth, width, ports, replication, buffering, and mapping. Keep BRAM_18K/BRAM_36K/URAM units distinct. Use device-specific mapping evidence instead of a fixed DSP-per-MAC number or an unconditional "native FP16" claim.

## Synthesizability and observability

Keep dynamic allocation, unsupported recursion, host-only containers, and other unsupported constructs out of the synthesized path. Host-side test code may use suitable software facilities.

Variable-bound loops require a legal, bounded runtime contract where relevant; `LOOP_TRIPCOUNT` is an analysis aid, not a replacement for correct bounds or a synthesizability guarantee. Guard host-only diagnostics appropriately without removing required behavior.

Set interface depths from real transaction sizes and preserve configured clock uncertainty and tool options. Keep source, headers, configuration, and test data inside the assigned input manifest. Inspect warnings and generated reports instead of assuming pragmas took effect.

## Evidence-driven iteration

Use the architecture declaration and checklist to find mistakes early. Record measured synthesis estimates separately from routed resources. Explain substantial prediction errors; only change code when the evidence supports an actual defect or an authorized improvement. Preserve the best candidate, and validate every materially changed candidate through the policy-required stages.
