"""Graph validation audits."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from orbit_vla.types import SceneGraph


@dataclass
class GraphValidationReport:
    valid: bool
    target_present: bool
    reference_present: bool
    relation_present: bool
    evidence_present: bool
    id_consistency: bool
    node_count: int
    edge_count: int
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class GraphValidator:
    """Validate whether a selected graph is safe to pass into carrier generation."""

    def validate(self, graph: SceneGraph) -> GraphValidationReport:
        ids = [node.node_id for node in graph.nodes]
        id_consistency = len(ids) == len(set(ids))
        target_present = any(node.role == "target" for node in graph.nodes)
        reference_present = any(node.role == "reference" for node in graph.nodes)
        relation_present = len(graph.edges) > 0
        evidence_present = all(bool(edge.evidence) for edge in graph.edges)
        warnings: list[str] = []
        if not id_consistency:
            warnings.append("duplicate object IDs")
        if not target_present:
            warnings.append("missing target object")
        if not reference_present:
            warnings.append("missing reference object")
        if not relation_present:
            warnings.append("missing relation edges")
        if not evidence_present:
            warnings.append("one or more relation edges lack evidence")
        return GraphValidationReport(
            valid=all([id_consistency, target_present, reference_present, relation_present, evidence_present]),
            target_present=target_present,
            reference_present=reference_present,
            relation_present=relation_present,
            evidence_present=evidence_present,
            id_consistency=id_consistency,
            node_count=len(graph.nodes),
            edge_count=len(graph.edges),
            warnings=warnings,
        )
