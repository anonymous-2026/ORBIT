"""Build a selected ORBIT graph from a task record and scene proposals."""

from __future__ import annotations

import argparse

from orbit_vla.io import read_json, write_json
from orbit_vla.pipeline import OrbitPipeline
from orbit_vla.graph.validation import GraphValidator
from orbit_vla.types import TaskRecord


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", required=True, help="Task JSON file")
    parser.add_argument("--scene", required=True, help="Scene object proposal JSON file")
    parser.add_argument("--output", required=True, help="Output graph JSON")
    args = parser.parse_args()

    task = TaskRecord.from_dict(read_json(args.task))
    scene = read_json(args.scene)
    proposals = scene.get("objects", scene if isinstance(scene, list) else [])
    graph = OrbitPipeline().build_graph(task, proposals)
    graph_dict = graph.to_dict()
    graph_dict["validation"] = GraphValidator().validate(graph).to_dict()
    write_json(graph_dict, args.output)


if __name__ == "__main__":
    main()
