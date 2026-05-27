# Reproducibility Notes

ORBIT separates semantic input construction from policy execution.

## Public Reproducibility Boundary

The repository provides:

- task-frame expansion
- graph construction and validation
- action-relevance selection
- text and visual carrier generation
- the full default carrier matrix
- rollout metric aggregation
- selector replay over logged records

The repository does not bundle VLA weights or benchmark assets. A policy backend should consume the generated carrier packages and write rollout JSONL following `docs/data_formats.md`.

See `docs/backend_integration.md` for the perception and policy backend contracts.

## Recommended Workflow

1. Prepare a task JSON and scene object proposal JSON.
2. Build and validate the selected graph.
3. Generate the full carrier matrix with `--matrix`.
4. Run the external VLA backend on each generated carrier package.
5. Write rollout JSONL.
6. Summarize metrics and replay selector decisions.

## Required Logs

For paper-style reporting, each rollout row should include:

- task ID and condition
- success
- wrong-object contact
- reference miss
- direction error
- trajectory deviation
- input consistency failure
- relation following
- final arrangement
- cue response when a control cue is used
