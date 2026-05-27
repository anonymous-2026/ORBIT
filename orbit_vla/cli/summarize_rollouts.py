"""Aggregate rollout JSONL metrics."""

from __future__ import annotations

import argparse

from orbit_vla.evaluation import summarize_rollouts
from orbit_vla.io import read_jsonl, write_json


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rollouts", required=True, help="Rollout JSONL file")
    parser.add_argument("--output", required=True, help="Output summary JSON")
    args = parser.parse_args()
    rows = read_jsonl(args.rollouts)
    summaries = [item.to_dict() for item in summarize_rollouts(rows)]
    write_json({"summaries": summaries}, args.output)


if __name__ == "__main__":
    main()

