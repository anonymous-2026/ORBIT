"""Controlled carrier perturbations for cue-consumption tests."""

from __future__ import annotations

from dataclasses import replace

from orbit_vla.types import CarrierPackage


class CarrierPerturbation:
    @staticmethod
    def wrong_target(package: CarrierPackage, replacement_id: str = "D1") -> CarrierPackage:
        ids = [replacement_id if idx == package.graph_ids[0] else idx for idx in package.graph_ids]
        text = package.text.replace(package.graph_ids[0], replacement_id) if package.text else None
        return replace(package, graph_ids=ids, text=text, control_tag="wrong_target_cue")

    @staticmethod
    def wrong_relation(package: CarrierPackage, wrong_relation: str = "near") -> CarrierPackage:
        relations = []
        for subject, relation, obj in package.graph_relations:
            relations.append((subject, wrong_relation, obj))
        text = package.text
        if text:
            for _, relation, _ in package.graph_relations:
                text = text.replace(f",{relation},", f",{wrong_relation},")
        return replace(package, graph_relations=relations, text=text, control_tag="wrong_relation_cue")

    @staticmethod
    def corrupted_visual_line(package: CarrierPackage) -> CarrierPackage:
        return replace(package, control_tag="corrupted_visual_line")

