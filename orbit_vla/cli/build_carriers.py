"""Build ORBIT text, visual, or hybrid carrier packages."""

from __future__ import annotations

import argparse
from pathlib import Path

from orbit_vla.carriers.matrix import CarrierMatrixBuilder
from orbit_vla.io import read_json, write_json
from orbit_vla.pipeline import OrbitPipeline
from orbit_vla.types import CarrierMode, CarrierStyle, RelationLevel, SceneGraph, TaskRecord


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", required=True, help="Task JSON file")
    parser.add_argument("--graph", required=True, help="Selected graph JSON file")
    parser.add_argument("--output-dir", required=True, help="Carrier output directory")
    parser.add_argument("--image", default=None, help="Input image for visual or hybrid carriers")
    parser.add_argument("--matrix", action="store_true", help="Generate the default paper carrier matrix")
    parser.add_argument("--mode", default="hybrid", choices=[item.value for item in CarrierMode])
    parser.add_argument("--style", default="IFRO", choices=[item.value for item in CarrierStyle])
    parser.add_argument(
        "--relation-level",
        default="object+relation",
        choices=[item.value for item in RelationLevel],
    )
    args = parser.parse_args()

    task = TaskRecord.from_dict(read_json(args.task))
    graph = SceneGraph.from_dict(read_json(args.graph))
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    if args.matrix:
        if args.image is None:
            raise ValueError("--image is required when --matrix is used")
        packages = CarrierMatrixBuilder().build(task, graph, args.image, output_dir)
        write_json({"packages": [package.to_dict() for package in packages]}, output_dir / "manifest.json")
        return
    mode = CarrierMode(args.mode)
    style = CarrierStyle(args.style) if mode != CarrierMode.TEXT_ONLY else None
    package = OrbitPipeline().build_carrier_package(
        task=task,
        graph=graph,
        mode=mode,
        relation_level=RelationLevel(args.relation_level),
        output_dir=output_dir,
        image_path=args.image,
        style=style,
    )
    write_json(package.to_dict(), output_dir / "carrier_package.json")


if __name__ == "__main__":
    main()
