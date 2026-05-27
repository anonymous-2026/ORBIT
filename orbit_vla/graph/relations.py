"""Geometric relation construction."""

from __future__ import annotations

import math

from orbit_vla.types import BoundingBox, GraphEdge, GraphNode, RelationType


def _center_distance(a: BoundingBox, b: BoundingBox) -> float:
    ax, ay = a.center
    bx, by = b.center
    return math.sqrt((ax - bx) ** 2 + (ay - by) ** 2)


def _normalized_distance(a: BoundingBox, b: BoundingBox) -> float:
    scale = max(a.width + a.height + b.width + b.height, 1e-6)
    return _center_distance(a, b) / scale


class RelationBuilder:
    def __init__(
        self,
        near_threshold: float = 0.25,
        overlap_threshold: float = 0.05,
        reachability_threshold: float = 0.35,
    ) -> None:
        self.near_threshold = near_threshold
        self.overlap_threshold = overlap_threshold
        self.reachability_threshold = reachability_threshold

    def build(self, nodes: list[GraphNode]) -> list[GraphEdge]:
        edges: list[GraphEdge] = []
        for subject in nodes:
            for obj in nodes:
                if subject.node_id == obj.node_id:
                    continue
                edges.extend(self._pairwise(subject, obj))
        edges.extend(self._target_reference_edges(nodes))
        return self._deduplicate(edges)

    def _pairwise(self, subject: GraphNode, obj: GraphNode) -> list[GraphEdge]:
        edges: list[GraphEdge] = []
        sx, sy = subject.bbox.center
        ox, oy = obj.bbox.center
        dx = ox - sx
        dy = oy - sy
        distance = _normalized_distance(subject.bbox, obj.bbox)
        overlap = subject.bbox.intersection_area(obj.bbox) / max(subject.bbox.area, obj.bbox.area, 1e-6)
        evidence = {
            "center_distance": distance,
            "relative_dx": dx,
            "relative_dy": dy,
            "mask_overlap_ratio": overlap,
        }
        if abs(dx) > abs(dy) and dx > 0:
            edges.append(self._edge(subject, RelationType.LEFT_OF, obj, evidence, 0.75))
        if abs(dx) > abs(dy) and dx < 0:
            edges.append(self._edge(subject, RelationType.RIGHT_OF, obj, evidence, 0.75))
        if distance <= self.near_threshold:
            edges.append(self._edge(subject, RelationType.NEAR, obj, evidence, 0.85))
        if overlap >= self.overlap_threshold:
            edges.append(self._edge(subject, RelationType.OVERLAP, obj, evidence, 0.8))
            if sy < oy:
                edges.append(self._edge(subject, RelationType.ON, obj, evidence, 0.7))
        if self._inside(subject.bbox, obj.bbox):
            edges.append(self._edge(subject, RelationType.INSIDE, obj, evidence, 0.75))
        if subject.role in {"actor", "gripper"} and distance <= self.reachability_threshold:
            edges.append(self._edge(subject, RelationType.REACHABLE, obj, evidence, 0.8))
        return edges

    def _target_reference_edges(self, nodes: list[GraphNode]) -> list[GraphEdge]:
        targets = [node for node in nodes if node.role == "target"]
        references = [node for node in nodes if node.role == "reference"]
        edges: list[GraphEdge] = []
        for target in targets:
            for reference in references:
                distance = _normalized_distance(target.bbox, reference.bbox)
                tx, ty = target.bbox.center
                rx, ry = reference.bbox.center
                evidence = {
                    "center_distance": distance,
                    "target_reference_vector": [rx - tx, ry - ty],
                    "relative_dx": rx - tx,
                    "relative_dy": ry - ty,
                }
                edges.append(self._edge(target, RelationType.TARGET_TO_REFERENCE, reference, evidence, 0.9))
        return edges

    @staticmethod
    def _inside(inner: BoundingBox, outer: BoundingBox) -> bool:
        return (
            inner.x1 >= outer.x1
            and inner.y1 >= outer.y1
            and inner.x2 <= outer.x2
            and inner.y2 <= outer.y2
        )

    @staticmethod
    def _edge(
        subject: GraphNode,
        relation: RelationType,
        obj: GraphNode,
        evidence: dict[str, float | list[float]],
        base_confidence: float,
    ) -> GraphEdge:
        confidence = min(1.0, base_confidence * subject.confidence * obj.confidence + 0.05)
        return GraphEdge(
            subject=subject.node_id,
            relation=relation,
            object=obj.node_id,
            confidence=confidence,
            evidence=dict(evidence),
            view=subject.view,
            rule_type="geometry",
        )

    @staticmethod
    def _deduplicate(edges: list[GraphEdge]) -> list[GraphEdge]:
        best: dict[tuple[str, str, str, str], GraphEdge] = {}
        for edge in edges:
            key = (edge.subject, edge.relation.value, edge.object, edge.view)
            if key not in best or edge.confidence > best[key].confidence:
                best[key] = edge
        return list(best.values())

