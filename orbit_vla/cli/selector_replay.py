"""Replay a lightweight ORBIT selector on logged decisions."""

from __future__ import annotations

import argparse

from orbit_vla.adaptation.selector import (
    LinUCBSelector,
    SelectorRecord,
    default_selector_actions,
)
from orbit_vla.io import read_jsonl, write_json


DEFAULT_FEATURES = [
    "graph_confidence",
    "relation_failure",
    "visual_ambiguity",
    "history_useful",
    "distractor_present",
    "carrier_consistent",
]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records", required=True, help="Selector record JSONL file")
    parser.add_argument("--output", required=True, help="Output selector summary JSON")
    parser.add_argument("--alpha", type=float, default=0.6)
    args = parser.parse_args()

    rows = [SelectorRecord.from_dict(item) for item in read_jsonl(args.records)]
    selector = LinUCBSelector(default_selector_actions(), DEFAULT_FEATURES, alpha=args.alpha)
    summary = selector.replay(rows)
    write_json(summary.to_dict(), args.output)


if __name__ == "__main__":
    main()

