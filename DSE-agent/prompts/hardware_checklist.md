# Hardware Design Checklist

For T1, record **pass**, **fail**, or **not applicable**, with a short reason for each relevant item. A starred item is a gate when applicable; justified N/A is permitted. A failed correctness, safety, or explicit hard requirement needs repair. An optional optimization that was deliberately not selected does not force a redesign.

## A. Pipeline and recurrence

- **A1***: Does the schedule preserve real dependencies and the declared numerical behavior? Is any target II consistent with its transaction unit and recurrence bound?
- **A2**: Would loop pipelining, flattening, or task overlap address the actual bottleneck? Record the choice; no universal pipeline requirement.

## B. Parallel access and storage

- **B1***: Can the intended concurrent accesses be served without violating correctness or a hard throughput requirement?
- **B2**: Does the banking/partition/reshape strategy match the access pattern and area budget?
- **B3***: Are shared memories/channels used in a tool-supported, race-free way? Inspect the concrete pattern rather than assuming every shared array is illegal.

## C. Dataflow (N/A when absent)

- **C1***: Are producer/consumer ownership, token counts, and channel types consistent?
- **C2***: Are dependencies, feedback if any, and initialization compatible with forward progress and the selected tool flow?
- **C3***: Are access ordering and data availability correct across stages?
- **C4***: Is buffering justified by rates/scheduling, and will co-simulation exercise potential deadlocks?

## D. Resources

- **D1**: Estimate compute/DSP cost with mapping assumptions or a range; use null when unsupported by evidence.
- **D2**: Estimate storage including width/depth, banking, replication, and inferred buffering; identify BRAM units.
- **D3***: Check known hard resource limits. An uncertain prediction calls for measurement, not fabricated certainty. A proven violation needs an in-scope remedy.

## E. Timing

- **E1**: Identify likely critical logic/recurrence/routing paths and estimate only as precisely as evidence supports.
- **E2***: Is the selected period in the permitted clock set and compatible with any hard frequency requirement? Predictions are not post-route proof.

## F. Code and tests

- **F1***: No unsupported dynamic allocation in the synthesized path.
- **F2***: No unsupported recursion in the synthesized path.
- **F3***: Loop bounds and termination obey the benchmark contract; tripcount annotations alone do not establish this.
- **F4***: Host-only diagnostics are separated from synthesized behavior where required.
- **F5***: No unsupported host-only containers in the synthesized path; testbench/interface/numerical behavior is preserved.

Run C simulation after inspection. Do not proceed past a failed functional gate.

## After T2: compare prediction and evidence

Record forecast, synthesis result, units, and explanation for DSP, storage, and II. A resource discrepancy greater than 2x, or II above the declared forecast, requires diagnosis.

- If the prediction was wrong but requirements pass, correct the model, explain, and continue.
- If a real hard limit or correctness condition fails, make a targeted change and revalidate within the same assignment budget.
- If the tool or license failed, diagnose the environment; do not perform a ritual source edit.
- Keep synthesis resource estimates separate from final routed metrics. Do not automatically change precision to reduce a discrepancy.
