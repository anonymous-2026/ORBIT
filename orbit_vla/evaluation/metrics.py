"""Rollout metric aggregation."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from statistics import mean
from typing import Any


@dataclass
class MetricSummary:
    task_id: str
    condition: str
    episodes: int
    success_rate: float
    wrong_object_contact: float
    reference_miss: float
    direction_error: float
    trajectory_deviation: float
    input_consistency_failure: float
    relation_following: float
    final_arrangement: float
    cue_response: float | None = None
    condition_delta: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def summarize_rollouts(rows: list[dict[str, Any]]) -> list[MetricSummary]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        key = (str(row["task_id"]), str(row["condition"]))
        groups.setdefault(key, []).append(row)

    summaries = [
        _summarize_group(task_id, condition, group)
        for (task_id, condition), group in sorted(groups.items())
    ]
    baseline_by_task = {
        item.task_id: item.success_rate
        for item in summaries
        if item.condition in {"raw_short_intent_baseline", "stress_baseline_original"}
    }
    for item in summaries:
        if item.task_id in baseline_by_task:
            item.condition_delta = item.success_rate - baseline_by_task[item.task_id]
    return summaries


def _summarize_group(task_id: str, condition: str, group: list[dict[str, Any]]) -> MetricSummary:
    return MetricSummary(
        task_id=task_id,
        condition=condition,
        episodes=len(group),
        success_rate=_rate(group, "success"),
        wrong_object_contact=_rate(group, "wrong_object_contact"),
        reference_miss=_rate(group, "reference_miss"),
        direction_error=_mean(group, "direction_error"),
        trajectory_deviation=_mean(group, "trajectory_deviation"),
        input_consistency_failure=_rate(group, "input_consistency_failure"),
        relation_following=_rate(group, "relation_following"),
        final_arrangement=_rate(group, "final_arrangement"),
        cue_response=_mean_optional(group, "cue_response"),
    )


def _rate(group: list[dict[str, Any]], key: str) -> float:
    return sum(1.0 for row in group if bool(row.get(key, False))) / max(len(group), 1)


def _mean(group: list[dict[str, Any]], key: str) -> float:
    values = [float(row.get(key, 0.0)) for row in group]
    return mean(values) if values else 0.0


def _mean_optional(group: list[dict[str, Any]], key: str) -> float | None:
    values = [float(row[key]) for row in group if key in row and row[key] is not None]
    return mean(values) if values else None

