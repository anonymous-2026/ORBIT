"""Shared data types for ORBIT."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class RelationType(str, Enum):
    LEFT_OF = "left_of"
    RIGHT_OF = "right_of"
    NEAR = "near"
    ON = "on"
    INSIDE = "inside"
    OVERLAP = "overlap"
    REACHABLE = "reachable"
    TARGET_TO_REFERENCE = "target_to_reference"


class CarrierStyle(str, Enum):
    IFRO = "IFRO"
    SSP = "SSP"
    DCSM = "DCSM"


class CarrierMode(str, Enum):
    TEXT_ONLY = "text-only"
    VISUAL_ONLY = "visual-only"
    HYBRID = "hybrid"


class RelationLevel(str, Enum):
    OBJECT_ONLY = "object-only"
    OBJECT_RELATION = "object+relation"


class HistoryMode(str, Enum):
    OFF = "off"
    REWARD_FILTERED = "reward-filtered"


@dataclass(frozen=True)
class BoundingBox:
    x1: float
    y1: float
    x2: float
    y2: float

    @classmethod
    def from_list(cls, values: list[float]) -> "BoundingBox":
        if len(values) != 4:
            raise ValueError("bbox must contain [x1, y1, x2, y2]")
        return cls(float(values[0]), float(values[1]), float(values[2]), float(values[3]))

    def to_list(self) -> list[float]:
        return [self.x1, self.y1, self.x2, self.y2]

    @property
    def width(self) -> float:
        return max(0.0, self.x2 - self.x1)

    @property
    def height(self) -> float:
        return max(0.0, self.y2 - self.y1)

    @property
    def center(self) -> tuple[float, float]:
        return ((self.x1 + self.x2) / 2.0, (self.y1 + self.y2) / 2.0)

    @property
    def area(self) -> float:
        return self.width * self.height

    def intersection_area(self, other: "BoundingBox") -> float:
        x1 = max(self.x1, other.x1)
        y1 = max(self.y1, other.y1)
        x2 = min(self.x2, other.x2)
        y2 = min(self.y2, other.y2)
        return max(0.0, x2 - x1) * max(0.0, y2 - y1)


@dataclass
class TaskFrame:
    name: str
    roles: dict[str, list[str]]
    default_relations: list[dict[str, str]]
    action_template: str
    history_policy: str = "off"
    max_objects: int = 3
    max_relations: int = 3

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TaskRecord:
    task_id: str
    instruction: str
    task_type: str
    frame: TaskFrame | None = None
    executable_goal: str | None = None
    required_carrier: str | None = None
    required_history: str = "off"
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TaskRecord":
        frame_data = data.get("frame")
        frame = TaskFrame(**frame_data) if isinstance(frame_data, dict) else None
        return cls(
            task_id=str(data["task_id"]),
            instruction=str(data["instruction"]),
            task_type=str(data.get("task_type", "semantic_extension")),
            frame=frame,
            executable_goal=data.get("executable_goal"),
            required_carrier=data.get("required_carrier"),
            required_history=str(data.get("required_history", "off")),
            metadata=dict(data.get("metadata", {})),
        )

    def to_dict(self) -> dict[str, Any]:
        out = asdict(self)
        if self.frame is not None:
            out["frame"] = self.frame.to_dict()
        return out


@dataclass
class GraphNode:
    node_id: str
    name: str
    role: str
    bbox: BoundingBox
    confidence: float = 1.0
    source: str = "proposal"
    view: str = "tpv"
    mask_id: str | None = None
    task_relevance_prior: float = 0.0
    attributes: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GraphNode":
        bbox = data.get("bbox")
        if isinstance(bbox, BoundingBox):
            parsed_bbox = bbox
        else:
            parsed_bbox = BoundingBox.from_list(list(bbox))
        return cls(
            node_id=str(data.get("id", data.get("node_id"))),
            name=str(data.get("name", data.get("category", "object"))),
            role=str(data.get("role", "object")),
            bbox=parsed_bbox,
            confidence=float(data.get("confidence", 1.0)),
            source=str(data.get("source", "proposal")),
            view=str(data.get("view", data.get("camera_view", "tpv"))),
            mask_id=data.get("mask_id"),
            task_relevance_prior=float(data.get("task_relevance_prior", 0.0)),
            attributes=dict(data.get("attributes", {})),
        )

    def to_dict(self) -> dict[str, Any]:
        out = asdict(self)
        out["id"] = self.node_id
        out["bbox"] = self.bbox.to_list()
        out.pop("node_id", None)
        return out


@dataclass
class GraphEdge:
    subject: str
    relation: RelationType
    object: str
    confidence: float
    evidence: dict[str, Any]
    view: str = "tpv"
    rule_type: str = "geometry"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GraphEdge":
        return cls(
            subject=str(data["subject"]),
            relation=RelationType(str(data["relation"])),
            object=str(data["object"]),
            confidence=float(data.get("confidence", 1.0)),
            evidence=dict(data.get("evidence", {})),
            view=str(data.get("view", data.get("camera_view", "tpv"))),
            rule_type=str(data.get("rule_type", "geometry")),
        )

    def to_dict(self) -> dict[str, Any]:
        out = asdict(self)
        out["relation"] = self.relation.value
        return out


@dataclass
class SceneGraph:
    task_id: str
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    frame_name: str | None = None
    source: str = "scene"
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SceneGraph":
        return cls(
            task_id=str(data["task_id"]),
            nodes=[GraphNode.from_dict(item) for item in data.get("nodes", [])],
            edges=[GraphEdge.from_dict(item) for item in data.get("edges", [])],
            frame_name=data.get("frame_name"),
            source=str(data.get("source", "scene")),
            metadata=dict(data.get("metadata", {})),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "frame_name": self.frame_name,
            "source": self.source,
            "metadata": self.metadata,
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
        }

    def node_by_id(self, node_id: str) -> GraphNode:
        for node in self.nodes:
            if node.node_id == node_id:
                return node
        raise KeyError(f"unknown node id: {node_id}")


@dataclass
class CarrierPackage:
    task_id: str
    mode: CarrierMode
    style: CarrierStyle | None
    relation_level: RelationLevel
    text: str | None
    image_path: str | None
    graph_ids: list[str]
    graph_relations: list[tuple[str, str, str]]
    control_tag: str | None = None
    validation: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        out = asdict(self)
        out["mode"] = self.mode.value
        out["style"] = self.style.value if self.style is not None else None
        out["relation_level"] = self.relation_level.value
        return out

