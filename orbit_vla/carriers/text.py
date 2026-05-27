"""Canonical textual carrier encoding."""

from __future__ import annotations

from orbit_vla.types import RelationLevel, SceneGraph, TaskRecord


class TextCarrierEncoder:
    def __init__(self, max_objects: int = 3, max_relations: int = 3) -> None:
        self.max_objects = max_objects
        self.max_relations = max_relations

    def encode(
        self,
        task: TaskRecord,
        graph: SceneGraph,
        relation_level: RelationLevel = RelationLevel.OBJECT_RELATION,
    ) -> str:
        nodes = graph.nodes[: self.max_objects]
        relations = graph.edges[: self.max_relations]
        task_line = task.executable_goal or task.instruction
        object_tokens = [
            f"{node.node_id}: {node.name} | {node.role}"
            for node in nodes
        ]
        lines = [
            f"[TASK] {task_line}",
            "[OBJECTS] " + "; ".join(object_tokens),
        ]
        if relation_level == RelationLevel.OBJECT_RELATION and relations:
            rel_tokens = [
                f"rel({edge.subject},{edge.relation.value},{edge.object})"
                for edge in relations
            ]
            lines.append("[RELATIONS] " + "; ".join(rel_tokens))
        if task.frame is not None:
            lines.append(f"[ACTION_HINT] {task.frame.action_template}")
            lines.append(f"[FRAME] {task.frame.name}")
        return "\n".join(lines)

