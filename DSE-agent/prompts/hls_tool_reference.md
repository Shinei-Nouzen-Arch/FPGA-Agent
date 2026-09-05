# HLS Tool and Evidence Reference

## Entry point

Use the bundled configuration-driven wrapper, not an assumed shell alias:

```bash
DSE_PROJECT_ROOT=/absolute/project /absolute/skill/DSE-agent/src/hls_run.sh /absolute/project/workspace/explorer csim
DSE_PROJECT_ROOT=/absolute/project /absolute/skill/DSE-agent/src/hls_run.sh /absolute/project/workspace/explorer csynth
DSE_PROJECT_ROOT=/absolute/project /absolute/skill/DSE-agent/src/hls_run.sh /absolute/project/workspace/explorer cosim
DSE_PROJECT_ROOT=/absolute/project /absolute/skill/DSE-agent/src/hls_run.sh /absolute/project/workspace/explorer impl
```

`all` runs Csim, Csynth, Cosim, and Impl and is forbidden under an implementation ban. The wrapper reads the active project directive and role assignment; Main prepares them during initialization. A relative workspace argument is resolved from `DSE_PROJECT_ROOT`, or the current directory when that variable is absent, not from the installed skill directory.

The command adapter uses `v++ -c --mode hls` for synthesis and `vitis-run --mode hls --csim/--cosim/--impl` for the other stages, preserving the complete configuration file. Check the installed tool's help/version for compatibility before a run; do not assume every Vitis release accepts this adapter.

## Configuration and inputs

Use the selected benchmark's part, top function, clock, uncertainty, interfaces, source flags, and simulation options. Do not hardcode a GEMM top or an example device.

Source/testbench paths in `syn.file` and `tb.file` are relative to the role workspace; repeated file entries are supported. All user-controlled headers, include files, and test data belong in the assignment's `input_paths` trees. Toolchain-provided standard headers are part of the selected tool environment, not benchmark files.

For each stage the helper hashes inputs and records the executable identity, command, completion, and fresh report hashes. Cosim/Impl require matching successful synthesis evidence. Merely finding an old `syn/` directory is insufficient. See [../references/contracts.md](../references/contracts.md).

## Reports and acceptance

| Stage | Evidence | Typical report names |
| --- | --- | --- |
| Csim | Functional result and test completion | HLS csim summary/log |
| Csynth | Schedule, latency/II, estimated resources | `*_csynth.rpt` |
| Cosim | RTL functional result, latency/interval | `*_cosim.rpt` |
| Impl | Routed timing and utilization | `export_impl.rpt`, routed timing/utilization reports |

Reports may appear under `hls_project/hls/` or older `hls_project/solution1/` layouts. Locate actual files rather than assuming a single fixed path.

A successful process/receipt is only execution evidence. Inspect reports for functional pass, required routed metrics, constraint compliance, and matching candidate identity. C synthesis does not establish final WNS. Cosim-only candidates remain provisional and have null post-implementation metrics.

## Diagnosis

- Top/source/testbench mismatch: reconcile with the benchmark declaration, preserving the reference contract.
- Interface-depth failure: use actual array/transaction sizes.
- High II: inspect dependencies, memory ports, scheduling, and the real hard requirement before changing code.
- Storage overuse: inspect banking, replication, inferred PIPO/FIFO mapping, and units.
- Negative routed WNS: use the actual critical path and assigned clock choices; do not infer validated Fmax from synthesis.
- Stale reports: restore the exact candidate or rerun the required stages; never relabel old output.
- Wrong benchmark/workspace: Main archives first, then seeds the correct role-local inputs.
