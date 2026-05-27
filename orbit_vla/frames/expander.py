"""Bounded intent expansion."""

from __future__ import annotations

from orbit_vla.frames.library import DEFAULT_FRAME_LIBRARY
from orbit_vla.types import TaskFrame, TaskRecord


class FrameExpander:
    """Map short natural requests to a small bounded task-frame library."""

    def __init__(self, frame_library: dict[str, TaskFrame] | None = None) -> None:
        self.frame_library = frame_library or DEFAULT_FRAME_LIBRARY
        self.keyword_map = {
            "fries": "food_serving",
            "薯条": "food_serving",
            "coffee": "drink_preparation",
            "咖啡": "drink_preparation",
            "drink": "drink_preparation",
            "喝": "drink_preparation",
            "work": "workspace_preparation",
            "工作": "workspace_preparation",
            "study": "workspace_preparation",
            "学习": "workspace_preparation",
            "messy": "cleanup_arrangement",
            "乱": "cleanup_arrangement",
            "cleanup": "cleanup_arrangement",
            "breakfast": "breakfast_setup",
            "早餐": "breakfast_setup",
        }

    def expand(self, task: TaskRecord) -> TaskRecord:
        if task.frame is not None:
            return task
        frame_name = self.match_frame(task.instruction)
        frame = self.frame_library.get(frame_name) if frame_name else None
        if frame is None:
            return task
        return TaskRecord(
            task_id=task.task_id,
            instruction=task.instruction,
            task_type=task.task_type,
            frame=frame,
            executable_goal=task.executable_goal or frame.action_template,
            required_carrier=task.required_carrier,
            required_history=task.required_history or frame.history_policy,
            metadata=dict(task.metadata),
        )

    def match_frame(self, instruction: str) -> str | None:
        lowered = instruction.lower()
        for keyword, frame_name in self.keyword_map.items():
            if keyword.lower() in lowered:
                return frame_name
        return None

