# Backend Integration

ORBIT does not bundle VLA model weights or benchmark assets. It expects an external VLA backend to consume generated carrier packages and return rollout records.

## Perception Boundary

The paper describes ORBIT with open-vocabulary proposals and optional mask refinement. In the public code, that boundary is represented by scene-object proposal JSON. Users may produce that JSON with any compatible detector, segmenter, simulator oracle, or benchmark annotation source, as long as the resulting objects follow `docs/data_formats.md`.

Required object fields:

- `id`
- `name`
- `role`
- `bbox`
- `confidence`
- `view`

Optional fields:

- `mask_id`
- `source`
- `attributes`

## Policy Backend Boundary

A policy backend should run each generated carrier package and log one JSONL row per episode. ORBIT summarizes those rows but does not update VLA weights.

Required rollout fields:

- `task_id`
- `condition`
- `success`
- `wrong_object_contact`
- `reference_miss`
- `direction_error`
- `trajectory_deviation`
- `input_consistency_failure`
- `relation_following`
- `final_arrangement`

Optional rollout fields:

- `cue_response`
- `reward`
- `failure_type`
- `history_used`
- `backend_name`

This boundary keeps ORBIT reusable across OpenPI, OpenVLA-style backends, simulator policies, and future VLA implementations.

