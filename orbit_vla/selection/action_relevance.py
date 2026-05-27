"""Budgeted subgraph selection."""

from __future__ import annotations

from orbit_vla.types import GraphEdge, GraphNode, SceneGraph


class ActionRelevanceSelector:
    def __init__(
        self,
        max_objects: int = 3,
        max_relations: int = 3,
        distractor_penalty: float = 0.2,
    ) -> None:
        self.max_objects = max_objects
        self.max_relations = max_relations
        self.distractor_penalty = distractor_penalty

    def select(self, graph: SceneGraph) -> SceneGraph:
        selected_nodes = sorted(graph.nodes, key=self._node_score, reverse=True)[: self.max_objects]
        selected_ids = {node.node_id for node in selected_nodes}
        selected_edges = [
            edge for edge in graph.edges if edge.subject in selected_ids and edge.object in selected_ids
        ]
        selected_edges = sorted(selected_edges, key=self._edge_score, reverse=True)[: self.max_relations]
        return SceneGraph(
            task_id=graph.task_id,
            frame_name=graph.frame_name,
            source=graph.source,
            nodes=selected_nodes,
            edges=selected_edges,
            metadata={**graph.metadata, "selected": True},
        )

    def _node_score(self, node: GraphNode) -> float:
        role_weight = {
            "target": 1.0,
            "reference": 0.9,
            "actor": 0.7,
            "gripper": 0.7,
            "accessory": 0.55,
            "condiment": 0.55,
            "keep": 0.45,
            "distractor": -self.distractor_penalty,
        }.get(node.role, 0.2)
        return role_weight + node.task_relevance_prior + 0.25 * node.confidence

    @staticmethod
    def _edge_score(edge: GraphEdge) -> float:
        relation_weight = {
            "target_to_reference": 1.0,
            "inside": 0.85,
            "on": 0.85,
            "left_of": 0.75,
            "right_of": 0.75,
            "near": 0.65,
            "reachable": 0.55,
            "overlap": 0.45,
        }.get(edge.relation.value, 0.3)
        return relation_weight + 0.35 * edge.confidence

