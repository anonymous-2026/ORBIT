"""Lightweight selector over semantic carrier actions."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class SelectorAction:
    name: str
    carrier_mode: str
    relation_level: str
    history_mode: str = "off"

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass
class SelectorRecord:
    task_id: str
    state: dict[str, float]
    action: str
    reward: float
    success: bool
    harmful: bool = False
    reason: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SelectorRecord":
        return cls(
            task_id=str(data["task_id"]),
            state={str(k): float(v) for k, v in data.get("state", {}).items()},
            action=str(data["action"]),
            reward=float(data.get("reward", 0.0)),
            success=bool(data.get("success", False)),
            harmful=bool(data.get("harmful", False)),
            reason=data.get("reason"),
        )


@dataclass
class SelectorReplaySummary:
    decisions: int
    mean_reward: float
    success_rate: float
    harmful_select: float
    explanation_coverage: float
    action_counts: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class LinUCBSelector:
    def __init__(self, actions: list[SelectorAction], feature_names: list[str], alpha: float = 0.6) -> None:
        self.actions = actions
        self.feature_names = feature_names
        self.alpha = alpha
        dim = len(feature_names)
        self.a_mats = {action.name: np.eye(dim) for action in actions}
        self.b_vecs = {action.name: np.zeros(dim) for action in actions}

    def choose(self, state: dict[str, float]) -> tuple[SelectorAction, str]:
        x = self._vectorize(state)
        scores: list[tuple[float, SelectorAction]] = []
        for action in self.actions:
            inv = np.linalg.inv(self.a_mats[action.name])
            theta = inv @ self.b_vecs[action.name]
            score = float(x @ theta + self.alpha * np.sqrt(x @ inv @ x))
            scores.append((score, action))
        _, best = max(scores, key=lambda item: item[0])
        reason = self.explain(best, state)
        return best, reason

    def update(self, state: dict[str, float], action_name: str, reward: float) -> None:
        x = self._vectorize(state)
        self.a_mats[action_name] += np.outer(x, x)
        self.b_vecs[action_name] += reward * x

    def replay(self, records: list[SelectorRecord]) -> SelectorReplaySummary:
        rewards: list[float] = []
        successes = 0
        harmful = 0
        explanations = 0
        action_counts: dict[str, int] = {}
        for record in records:
            action, reason = self.choose(record.state)
            action_counts[action.name] = action_counts.get(action.name, 0) + 1
            selected_reward = record.reward if action.name == record.action else 0.0
            rewards.append(selected_reward)
            successes += int(record.success and action.name == record.action)
            harmful += int(record.harmful and action.name == record.action)
            explanations += int(bool(reason))
            self.update(record.state, record.action, record.reward)
        decisions = len(records)
        return SelectorReplaySummary(
            decisions=decisions,
            mean_reward=float(np.mean(rewards)) if rewards else 0.0,
            success_rate=successes / max(decisions, 1),
            harmful_select=harmful / max(decisions, 1),
            explanation_coverage=explanations / max(decisions, 1),
            action_counts=action_counts,
        )

    def explain(self, action: SelectorAction, state: dict[str, float]) -> str:
        cues = []
        if state.get("relation_failure", 0.0) > 0:
            cues.append("relation failure")
        if state.get("visual_ambiguity", 0.0) > 0:
            cues.append("visual ambiguity")
        if state.get("history_useful", 0.0) > 0:
            cues.append("reward-filtered history")
        if state.get("graph_confidence", 0.0) > 0.7:
            cues.append("high graph confidence")
        cue_text = ", ".join(cues) if cues else "default uncertainty"
        return f"selected {action.name} because state indicates {cue_text}"

    def _vectorize(self, state: dict[str, float]) -> np.ndarray:
        return np.asarray([float(state.get(name, 0.0)) for name in self.feature_names], dtype=float)


def default_selector_actions() -> list[SelectorAction]:
    return [
        SelectorAction("text_object", "text-only", "object-only", "off"),
        SelectorAction("text_relation", "text-only", "object+relation", "off"),
        SelectorAction("visual_relation", "visual-only", "object+relation", "off"),
        SelectorAction("hybrid_relation", "hybrid", "object+relation", "off"),
        SelectorAction("hybrid_history", "hybrid", "object+relation", "reward-filtered"),
    ]

