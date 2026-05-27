"""Reward-filtered semantic memory."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class MemoryEntry:
    task_id: str
    frame: str
    carrier_mode: str
    relation_level: str
    history_mode: str
    reward: float
    success: bool
    failure_type: str | None = None
    graph_summary: dict[str, Any] | None = None
    note: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MemoryEntry":
        return cls(
            task_id=str(data["task_id"]),
            frame=str(data.get("frame", "unknown")),
            carrier_mode=str(data.get("carrier_mode", "hybrid")),
            relation_level=str(data.get("relation_level", "object+relation")),
            history_mode=str(data.get("history_mode", "off")),
            reward=float(data.get("reward", 0.0)),
            success=bool(data.get("success", False)),
            failure_type=data.get("failure_type"),
            graph_summary=data.get("graph_summary"),
            note=data.get("note"),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class RewardFilteredMemory:
    def __init__(self, min_reward: float = 0.5, keep_failures: bool = True) -> None:
        self.min_reward = min_reward
        self.keep_failures = keep_failures
        self.entries: list[MemoryEntry] = []

    def add(self, entry: MemoryEntry) -> None:
        if entry.reward >= self.min_reward or (self.keep_failures and not entry.success):
            self.entries.append(entry)

    def retrieve(self, frame: str | None = None, top_k: int = 3) -> list[MemoryEntry]:
        candidates = self.entries
        if frame is not None:
            candidates = [entry for entry in candidates if entry.frame == frame]
        return sorted(candidates, key=lambda item: item.reward, reverse=True)[:top_k]

    def action_prior(self, frame: str | None = None) -> dict[str, float]:
        counts: dict[str, float] = {}
        totals: dict[str, int] = {}
        for entry in self.retrieve(frame=frame, top_k=len(self.entries)):
            key = f"{entry.carrier_mode}|{entry.relation_level}|{entry.history_mode}"
            counts[key] = counts.get(key, 0.0) + entry.reward
            totals[key] = totals.get(key, 0) + 1
        return {key: counts[key] / totals[key] for key in counts}

