"""Carrier consistency validation."""

from __future__ import annotations

from orbit_vla.types import CarrierPackage, SceneGraph


class CarrierValidator:
    def validate(self, graph: SceneGraph, package: CarrierPackage) -> dict[str, object]:
        graph_ids = {node.node_id for node in graph.nodes}
        graph_relations = {
            (edge.subject, edge.relation.value, edge.object)
            for edge in graph.edges
        }
        package_ids = set(package.graph_ids)
        package_relations = set(package.graph_relations)
        id_match = package_ids.issubset(graph_ids)
        relation_match = package_relations.issubset(graph_relations)
        expected_control = package.control_tag is not None
        valid = id_match and relation_match
        return {
            "valid": bool(valid or expected_control),
            "normal_valid": bool(valid and not expected_control),
            "expected_control": bool(expected_control),
            "id_match": bool(id_match),
            "relation_match": bool(relation_match),
            "missing_ids": sorted(package_ids - graph_ids),
            "missing_relations": sorted([list(item) for item in package_relations - graph_relations]),
            "control_tag": package.control_tag,
        }

