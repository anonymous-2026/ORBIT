# Data Formats

## Task JSON

```json
{
  "task_id": "fries_serving_example",
  "instruction": "I bought fries.",
  "task_type": "semantic_extension",
  "executable_goal": "prepare a food-serving setup",
  "required_carrier": "hybrid",
  "required_history": "off"
}
```

If no frame is provided, the bounded frame expander maps short intents into the default frame library.

## Scene Object JSON

Scene objects are normalized to image coordinates in `[0, 1]`.

```json
{
  "objects": [
    {
      "id": "T1",
      "name": "fries tray",
      "role": "target",
      "bbox": [0.34, 0.42, 0.48, 0.56],
      "confidence": 0.94,
      "view": "tpv"
    }
  ]
}
```

## Rollout JSONL

Each line represents one episode under one condition.

```json
{
  "task_id": "fries_serving_example",
  "condition": "hybrid_object_relation",
  "success": true,
  "wrong_object_contact": false,
  "reference_miss": false,
  "direction_error": 2.5,
  "trajectory_deviation": 0.06,
  "input_consistency_failure": false,
  "relation_following": true,
  "final_arrangement": true,
  "cue_response": 0.8
}
```

## Selector JSONL

Selector records store compact state, chosen action, and reward.

```json
{
  "task_id": "fries_serving_example",
  "state": {
    "graph_confidence": 0.9,
    "relation_failure": 1.0,
    "visual_ambiguity": 0.0,
    "history_useful": 0.0,
    "distractor_present": 1.0,
    "carrier_consistent": 1.0
  },
  "action": "text_relation",
  "reward": 0.92,
  "success": true,
  "harmful": false
}
```

