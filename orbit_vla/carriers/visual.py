"""Visual carrier rendering for IFRO, SSP, and DCSM."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from orbit_vla.types import CarrierStyle, GraphNode, SceneGraph


class VisualCarrierRenderer:
    def __init__(self, image_size: int = 1080) -> None:
        self.image_size = image_size
        self.colors = {
            "target": (255, 190, 46),
            "reference": (46, 145, 255),
            "actor": (80, 220, 120),
            "gripper": (80, 220, 120),
            "distractor": (245, 90, 90),
            "accessory": (190, 120, 255),
            "condiment": (190, 120, 255),
            "object": (230, 230, 230),
        }

    def render(
        self,
        image_path: str | Path,
        graph: SceneGraph,
        style: CarrierStyle,
        output_path: str | Path,
        semantic_text: str | None = None,
    ) -> str:
        image = self._load_square_image(image_path)
        if style == CarrierStyle.IFRO:
            rendered = self._render_ifro(image, graph)
        elif style == CarrierStyle.SSP:
            rendered = self._render_ssp(image, graph, semantic_text)
        elif style == CarrierStyle.DCSM:
            rendered = self._render_dcsm(image, graph, semantic_text)
        else:
            raise ValueError(f"unsupported carrier style: {style}")
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        rendered.save(output)
        return str(output)

    def _load_square_image(self, image_path: str | Path) -> Image.Image:
        image = Image.open(image_path).convert("RGB")
        width, height = image.size
        side = min(width, height)
        left = (width - side) // 2
        top = (height - side) // 2
        image = image.crop((left, top, left + side, top + side))
        return image.resize((self.image_size, self.image_size), Image.Resampling.BILINEAR)

    def _render_ifro(self, image: Image.Image, graph: SceneGraph) -> Image.Image:
        canvas = image.copy()
        draw = ImageDraw.Draw(canvas)
        self._draw_nodes(draw, graph.nodes)
        self._draw_edges(draw, graph)
        return canvas

    def _render_ssp(
        self,
        image: Image.Image,
        graph: SceneGraph,
        semantic_text: str | None,
    ) -> Image.Image:
        image_only = image.copy()
        draw = ImageDraw.Draw(image_only)
        self._draw_nodes(draw, graph.nodes, boxes=False)
        return self._compose_sidecar(image_only, graph, semantic_text)

    def _render_dcsm(
        self,
        image: Image.Image,
        graph: SceneGraph,
        semantic_text: str | None,
    ) -> Image.Image:
        image_only = self._render_ifro(image, graph)
        return self._compose_sidecar(image_only, graph, semantic_text)

    def _draw_nodes(self, draw: ImageDraw.ImageDraw, nodes: list[GraphNode], boxes: bool = True) -> None:
        font = self._font(size=28)
        for node in nodes:
            x1, y1, x2, y2 = self._scale_bbox(node)
            color = self.colors.get(node.role, self.colors["object"])
            if boxes:
                draw.rectangle((x1, y1, x2, y2), outline=color, width=5)
            label_w = max(54, len(node.node_id) * 18)
            draw.rectangle((x1, max(0, y1 - 36), x1 + label_w, y1), fill=color)
            draw.text((x1 + 6, max(0, y1 - 33)), node.node_id, fill=(0, 0, 0), font=font)

    def _draw_edges(self, draw: ImageDraw.ImageDraw, graph: SceneGraph) -> None:
        font = self._font(size=22)
        for edge in graph.edges:
            try:
                subject = graph.node_by_id(edge.subject)
                obj = graph.node_by_id(edge.object)
            except KeyError:
                continue
            sx, sy = self._scale_point(subject.bbox.center)
            ox, oy = self._scale_point(obj.bbox.center)
            color = (255, 230, 80)
            draw.line((sx, sy, ox, oy), fill=color, width=4)
            self._draw_arrowhead(draw, sx, sy, ox, oy, color)
            mx, my = (sx + ox) / 2, (sy + oy) / 2
            label = edge.relation.value
            draw.rectangle((mx - 6, my - 16, mx + len(label) * 11, my + 12), fill=(10, 18, 28))
            draw.text((mx, my - 14), label, fill=(255, 255, 255), font=font)

    @staticmethod
    def _draw_arrowhead(
        draw: ImageDraw.ImageDraw,
        sx: float,
        sy: float,
        ox: float,
        oy: float,
        color: tuple[int, int, int],
    ) -> None:
        dx, dy = ox - sx, oy - sy
        length = max((dx * dx + dy * dy) ** 0.5, 1.0)
        ux, uy = dx / length, dy / length
        px, py = -uy, ux
        size = 18
        points = [
            (ox, oy),
            (ox - ux * size + px * size * 0.55, oy - uy * size + py * size * 0.55),
            (ox - ux * size - px * size * 0.55, oy - uy * size - py * size * 0.55),
        ]
        draw.polygon(points, fill=color)

    def _compose_sidecar(
        self,
        image: Image.Image,
        graph: SceneGraph,
        semantic_text: str | None,
    ) -> Image.Image:
        panel_width = int(self.image_size * 0.42)
        canvas = Image.new("RGB", (self.image_size + panel_width, self.image_size), (245, 247, 250))
        canvas.paste(image, (0, 0))
        draw = ImageDraw.Draw(canvas)
        x = self.image_size + 24
        draw.text((x, 24), "Selected semantics", fill=(20, 27, 38), font=self._font(30))
        rows = []
        rows.extend(f"{node.node_id}: {node.name} ({node.role})" for node in graph.nodes)
        rows.extend(
            f"{edge.subject} -{edge.relation.value}-> {edge.object}"
            for edge in graph.edges
        )
        if semantic_text:
            rows.append("")
            rows.extend(semantic_text.splitlines())
        y = 76
        for row in rows[:24]:
            for chunk in self._wrap(row, 36):
                draw.text((x, y), chunk, fill=(35, 45, 62), font=self._font(20))
                y += 27
        return canvas

    @staticmethod
    def _wrap(text: str, width: int) -> list[str]:
        words = text.split()
        lines: list[str] = []
        current: list[str] = []
        for word in words:
            if sum(len(item) for item in current) + len(current) + len(word) > width:
                lines.append(" ".join(current))
                current = [word]
            else:
                current.append(word)
        if current:
            lines.append(" ".join(current))
        return lines or [""]

    def _scale_bbox(self, node: GraphNode) -> tuple[int, int, int, int]:
        return (
            int(node.bbox.x1 * self.image_size),
            int(node.bbox.y1 * self.image_size),
            int(node.bbox.x2 * self.image_size),
            int(node.bbox.y2 * self.image_size),
        )

    def _scale_point(self, point: tuple[float, float]) -> tuple[int, int]:
        return int(point[0] * self.image_size), int(point[1] * self.image_size)

    @staticmethod
    def _font(size: int) -> ImageFont.ImageFont:
        try:
            return ImageFont.truetype("DejaVuSans.ttf", size)
        except OSError:
            return ImageFont.load_default()

