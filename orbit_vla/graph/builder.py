"""Scene graph construction from object proposals."""

from __future__ import annotations

from orbit_vla.graph.relations import RelationBuilder
from orbit_vla.types import GraphNode, SceneGraph, TaskRecord


class GraphBuilder:
    def __init__(self, relation_builder: RelationBuilder | None = None) -> None:
        self.relation_builder = relation_builder or RelationBuilder()

    def build(self, task: TaskRecord, proposals: list[dict]) -> SceneGraph:
        nodes = [GraphNode.from_dict(item) for item in proposals]
        nodes = self._assign_task_priors(task, nodes)
        edges = self.relation_builder.build(nodes)
        return SceneGraph(
            task_id=task.task_id,
            frame_name=task.frame.name if task.frame else None,
            nodes=nodes,
            edges=edges,
            source="proposal_json",
            metadata={"instruction": task.instruction, "task_type": task.task_type},
        )

    def _assign_task_priors(self, task: TaskRecord, nodes: list[GraphNode]) -> list[GraphNode]:
        if task.frame is None:
            return nodes
        frame_roles = task.frame.roles
        updated: list[GraphNode] = []
        for node in nodes:
            role_bonus = 0.0
            name = node.name.lower()
            for role, aliases in frame_roles.items():
                if any(alias.lower() in name for alias in aliases):
                    if node.role in {"object", "unknown"}:
                        node.role = role
                    role_bonus = max(role_bonus, 0.35)
            node.task_relevance_prior = max(node.task_relevance_prior, role_bonus)
            updated.append(node)
        return updated

