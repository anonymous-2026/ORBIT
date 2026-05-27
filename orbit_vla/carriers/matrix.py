"""Carrier matrix generation for paper-facing conditions."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from orbit_vla.carriers.perturbations import CarrierPerturbation
from orbit_vla.types import CarrierMode, CarrierPackage, CarrierStyle, RelationLevel, SceneGraph, TaskRecord


@dataclass(frozen=True)
class CarrierCondition:
    name: str
    mode: CarrierMode
    relation_level: RelationLevel
    style: CarrierStyle | None = None
    perturbation: str | None = None


def default_carrier_conditions() -> list[CarrierCondition]:
    conditions = [
        CarrierCondition("text_object_only", CarrierMode.TEXT_ONLY, RelationLevel.OBJECT_ONLY),
        CarrierCondition("text_object_relation", CarrierMode.TEXT_ONLY, RelationLevel.OBJECT_RELATION),
    ]
    for style in CarrierStyle:
        suffix = style.value.lower()
        conditions.extend(
            [
                CarrierCondition(
                    f"visual_bbox_relation_{suffix}",
                    CarrierMode.VISUAL_ONLY,
                    RelationLevel.OBJECT_RELATION,
                    style,
                ),
                CarrierCondition(
                    f"hybrid_object_relation_{suffix}",
                    CarrierMode.HYBRID,
                    RelationLevel.OBJECT_RELATION,
                    style,
                ),
            ]
        )
    conditions.extend(
        [
            CarrierCondition(
                "wrong_target_cue",
                CarrierMode.HYBRID,
                RelationLevel.OBJECT_RELATION,
                CarrierStyle.DCSM,
                "wrong_target",
            ),
            CarrierCondition(
                "wrong_relation_cue",
                CarrierMode.HYBRID,
                RelationLevel.OBJECT_RELATION,
                CarrierStyle.DCSM,
                "wrong_relation",
            ),
            CarrierCondition(
                "corrupted_visual_line",
                CarrierMode.HYBRID,
                RelationLevel.OBJECT_RELATION,
                CarrierStyle.DCSM,
                "corrupted_visual_line",
            ),
        ]
    )
    return conditions


class CarrierMatrixBuilder:
    def __init__(self, pipeline: Any | None = None) -> None:
        if pipeline is None:
            from orbit_vla.pipeline import OrbitPipeline

            pipeline = OrbitPipeline()
        self.pipeline = pipeline

    def build(
        self,
        task: TaskRecord,
        graph: SceneGraph,
        image_path: str | Path,
        output_dir: str | Path,
        conditions: list[CarrierCondition] | None = None,
    ) -> list[CarrierPackage]:
        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)
        packages: list[CarrierPackage] = []
        for condition in conditions or default_carrier_conditions():
            condition_dir = output / condition.name
            condition_dir.mkdir(parents=True, exist_ok=True)
            package = self.pipeline.build_carrier_package(
                task=task,
                graph=graph,
                mode=condition.mode,
                relation_level=condition.relation_level,
                output_dir=condition_dir,
                image_path=image_path,
                style=condition.style,
            )
            if condition.perturbation == "wrong_target":
                package = CarrierPerturbation.wrong_target(package)
            elif condition.perturbation == "wrong_relation":
                package = CarrierPerturbation.wrong_relation(package)
            elif condition.perturbation == "corrupted_visual_line":
                package = CarrierPerturbation.corrupted_visual_line(package)
            package.metadata["condition"] = condition.name
            packages.append(package)
        return packages
