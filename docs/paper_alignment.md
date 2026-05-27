# Paper Alignment

This file maps the paper method to the public code.

## Stage 1: Task-Conditioned Graph Construction

- bounded task frames: `orbit_vla/frames/`
- object-relation graph construction: `orbit_vla/graph/`
- graph validation: `orbit_vla/graph/validation.py`
- action-relevance selection: `orbit_vla/selection/`

## Stage 2: Dual-Carrier Projection

- textual carrier: `orbit_vla/carriers/text.py`
- visual carriers: `orbit_vla/carriers/visual.py`
- supported styles: `IFRO`, `SSP`, `DCSM`
- carrier matrix: `orbit_vla/carriers/matrix.py`
- carrier validation and controls: `orbit_vla/carriers/validation.py`, `orbit_vla/carriers/perturbations.py`

## Stage 3: Rollout-Conditioned Adaptation

- selector: `orbit_vla/adaptation/selector.py`
- reward-filtered memory: `orbit_vla/adaptation/memory.py`
- rollout metrics: `orbit_vla/evaluation/metrics.py`

## Public Boundary

The code implements ORBIT's semantic conditioning layer. It does not ship VLA weights, benchmark assets, or a policy runner. Those are external backends that should consume carrier packages and emit rollout JSONL.

