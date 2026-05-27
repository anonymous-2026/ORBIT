# ORBIT Code Implementation Plan

This repository is being rebuilt as a clean open-source implementation of the method described in the paper: task-conditioned graph construction, dual-carrier projection, and rollout-conditioned adaptation for VLA policies.

## Scope

The repository will implement the public ORBIT interface only:

- bounded task-frame expansion from short intents
- task-conditioned object-relation graph construction
- action-relevance subgraph selection
- coordinated textual and visual carriers
- exactly three visual mix styles: `IFRO`, `SSP`, and `DCSM`
- carrier validation and control-condition tagging
- rollout metric aggregation
- a lightweight LinUCB-style selector with reward-filtered memory
- CLI scripts that compose these pieces into reproducible inputs and summaries

The repository will not include internal coordination logs, historical failed branches, or unsupported marking styles.

## Build Order

- [x] Clear the old repository contents while preserving repository metadata.
- [x] Create this implementation plan and checklist.
- [x] Define package metadata, README, and public repository layout.
- [x] Implement shared schemas for tasks, frames, graphs, carriers, metrics, and selector records.
- [x] Implement bounded task-frame expansion.
- [x] Implement graph construction and geometric relation evidence.
- [x] Implement action-relevance selection.
- [x] Implement textual carrier encoding.
- [x] Implement visual carrier rendering for `IFRO`, `SSP`, and `DCSM` only.
- [x] Implement carrier validation and controlled perturbations.
- [x] Implement metric aggregation for task success, relation following, cue response, and consistency.
- [x] Implement rollout-conditioned selector and reward-filtered memory.
- [x] Add CLI scripts for graph building, carrier generation, metric summarization, and selector replay.
- [x] Add minimal example task and scene inputs.
- [x] Add documentation for reproducing the paper-facing pipeline.
- [x] Final pass: remove unsupported styles, internal terminology, and stale references.

## Detail Pass

- [x] Add graph validation audits for target/reference/relation/evidence coverage.
- [x] Add full carrier-matrix generation for paper conditions.
- [x] Add explicit reward-filtered memory utilities.
- [x] Add license and reproducibility documentation.
- [x] Run lightweight syntax and CLI smoke checks after the scripts are complete.
- [x] Add paper-alignment and backend-integration notes.

## Verification Notes

- `python3 -m compileall -q orbit_vla scripts` passed.
- CLI help checks passed for graph building, carrier generation, rollout summarization, and selector replay.
- Minimal example interface check passed using `/tmp/orbit_code_repo_check`, covering graph export, full carrier matrix export, metric aggregation, and selector replay.
- Generated Python cache files were removed from the repository tree after verification.

## File Layout

- `orbit_vla/`: importable Python package
- `scripts/`: command-line entrypoints
- `configs/`: reusable config files
- `examples/`: small JSON examples for tasks, scenes, metrics, and selector replay
- `docs/`: public-facing usage notes

## Implementation Notes

- The VLA policy itself is treated as an external backend. ORBIT produces validated policy-facing inputs and analyzes rollout outputs.
- Perception backends are adapter interfaces. The default repository path accepts object proposals from JSON and constructs relation evidence deterministically.
- Visual carrier code must keep `IFRO`, `SSP`, and `DCSM` as the only supported styles.
- Script names and documentation should describe public method functionality, not internal experiment history.
