# ORBIT Pipeline

## Inputs

ORBIT consumes three public data types:

- task records with an instruction, optional bounded frame, and expected roles
- scene object proposals with boxes, optional masks, and confidence scores
- rollout records emitted by an external VLA evaluation backend

## Stage 1: Task-Conditioned Graph Construction

Short instructions are mapped to bounded frames such as food serving, drink preparation, workspace preparation, cleanup arrangement, and breakfast setup. A scene graph stores object nodes and relation edges. Relation evidence is geometric and view-aware.

## Stage 2: Dual-Carrier Projection

The selected subgraph is projected into:

- canonical text with `[TASK]`, `[OBJECTS]`, `[RELATIONS]`, and `[ACTION_HINT]`
- visual carriers using one of `IFRO`, `SSP`, or `DCSM`

Normal carriers must have matching object IDs and relation sets across graph, text, and image metadata. Control carriers may intentionally corrupt a target, relation, or visual line, but must be tagged as expected controls.

## Stage 3: Rollout-Conditioned Adaptation

The selector chooses a semantic conditioning action:

```text
z = (carrier_mode, relation_level, history_mode)
```

The default implementation uses a small LinUCB-style selector with reward-filtered memory. It selects among text-only, visual-only, and hybrid carrier packages rather than updating policy weights.

## Output Policy

The code produces JSON artifacts and visual packages that can be passed to a VLA evaluation backend. It does not assume a specific VLA implementation.

