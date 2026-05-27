"""High-level ORBIT pipeline helpers."""

from __future__ import annotations

from pathlib import Path

from orbit_vla.carriers.text import TextCarrierEncoder
from orbit_vla.carriers.validation import CarrierValidator
from orbit_vla.carriers.visual import VisualCarrierRenderer
from orbit_vla.frames.expander import FrameExpander
from orbit_vla.graph.builder import GraphBuilder
from orbit_vla.selection.action_relevance import ActionRelevanceSelector
from orbit_vla.types import (
    CarrierMode,
    CarrierPackage,
    CarrierStyle,
    RelationLevel,
    SceneGraph,
    TaskRecord,
)


class OrbitPipeline:
    def __init__(
        self,
        frame_expander: FrameExpander | None = None,
        graph_builder: GraphBuilder | None = None,
        selector: ActionRelevanceSelector | None = None,
        text_encoder: TextCarrierEncoder | None = None,
        visual_renderer: VisualCarrierRenderer | None = None,
        validator: CarrierValidator | None = None,
    ) -> None:
        self.frame_expander = frame_expander or FrameExpander()
        self.graph_builder = graph_builder or GraphBuilder()
        self.selector = selector or ActionRelevanceSelector()
        self.text_encoder = text_encoder or TextCarrierEncoder()
        self.visual_renderer = visual_renderer or VisualCarrierRenderer()
        self.validator = validator or CarrierValidator()

    def build_graph(self, task: TaskRecord, proposals: list[dict]) -> SceneGraph:
        expanded = self.frame_expander.expand(task)
        graph = self.graph_builder.build(expanded, proposals)
        return self.selector.select(graph)

    def build_carrier_package(
        self,
        task: TaskRecord,
        graph: SceneGraph,
        mode: CarrierMode,
        relation_level: RelationLevel,
        output_dir: str | Path,
        image_path: str | Path | None = None,
        style: CarrierStyle | None = None,
    ) -> CarrierPackage:
        expanded = self.frame_expander.expand(task)
        text = None
        if mode in {CarrierMode.TEXT_ONLY, CarrierMode.HYBRID}:
            text = self.text_encoder.encode(expanded, graph, relation_level=relation_level)
        image_out = None
        if mode in {CarrierMode.VISUAL_ONLY, CarrierMode.HYBRID}:
            if image_path is None:
                raise ValueError("image_path is required for visual or hybrid carriers")
            if style is None:
                raise ValueError("style is required for visual or hybrid carriers")
            image_out = str(Path(output_dir) / f"{task.task_id}_{mode.value}_{style.value}.png")
            semantic_text = self.text_encoder.encode(expanded, graph, relation_level=relation_level)
            self.visual_renderer.render(image_path, graph, style, image_out, semantic_text=semantic_text)

        ids = [node.node_id for node in graph.nodes]
        relations = [(edge.subject, edge.relation.value, edge.object) for edge in graph.edges]
        package = CarrierPackage(
            task_id=task.task_id,
            mode=mode,
            style=style,
            relation_level=relation_level,
            text=text,
            image_path=image_out,
            graph_ids=ids,
            graph_relations=relations if relation_level == RelationLevel.OBJECT_RELATION else [],
        )
        package.validation = self.validator.validate(graph, package)
        return package

