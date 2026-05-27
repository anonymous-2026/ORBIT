<p align="center">
  <img src="docs/static/images/logo.svg" alt="ORBIT logo" width="520">
</p>

<h1 align="center">ORBIT: Object-Relation Bridging with Interaction History for VLA Policies</h1>

ORBIT converts selected object-relation semantics and useful rollout history into validated VLA-facing inputs. The code mirrors the paper pipeline:

1. **Task-conditioned graph construction**: expand short requests into bounded task frames, build an object-relation graph, and select a compact action-relevant subgraph.
2. **Dual-carrier projection**: encode the selected subgraph as canonical text and visual carriers with shared semantic IDs.
3. **Rollout-conditioned adaptation**: choose carrier mode, relation level, and optional history with a lightweight selector and reward-filtered memory.

The repository treats the VLA policy as an external backend. It produces policy-facing input packages, validates carrier consistency, records metrics, and summarizes rollout outcomes.

## Supported Visual Mix Styles

Only three visual mix styles are part of the public implementation:

- `IFRO`: In-Frame Relational Overlay. Draw object boxes, IDs, and relation arrows directly in the image.
- `SSP`: Sidecar Semantic Panel. Keep the image minimally marked and place semantic details in a side panel.
- `DCSM`: Dual-Channel Semantic Mix. Combine in-frame relation marks with a side semantic panel.

Other marking styles are intentionally unsupported.

## Repository Layout

- `orbit_vla/`: core package
- `scripts/`: command-line entrypoints
- `configs/`: reusable configuration files
- `examples/`: small JSON examples
- `docs/`: pipeline and data-format notes

## Typical Pipeline

```bash
orbit-build-graph \
  --task examples/task_fries.json \
  --scene examples/scene_objects.json \
  --output outputs/graph.json

orbit-build-carriers \
  --task examples/task_fries.json \
  --graph outputs/graph.json \
  --image examples/tpv.png \
  --output-dir outputs/carriers \
  --matrix

orbit-summarize-rollouts \
  --rollouts examples/rollout_results.jsonl \
  --output outputs/metrics.json

orbit-selector-replay \
  --records examples/selector_records.jsonl \
  --output outputs/selector_summary.json
```

The example commands show the expected interfaces; policy execution is backend-specific and should write rollout JSONL in the documented format.

See `docs/data_formats.md`, `docs/pipeline.md`, `docs/visual_mix_styles.md`, `docs/backend_integration.md`, and `docs/reproducibility.md` for the public data contracts.
