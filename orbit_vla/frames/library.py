"""Bounded semantic frame library."""

from __future__ import annotations

from orbit_vla.types import TaskFrame


def build_default_frame_library() -> dict[str, TaskFrame]:
    return {
        "food_serving": TaskFrame(
            name="food_serving",
            roles={
                "target": ["food", "fries", "snack", "bowl", "tray"],
                "reference": ["plate", "dish", "serving mat", "tray"],
                "condiment": ["ketchup", "sauce", "mustard", "mayo"],
                "distractor": ["red bottle", "toy", "unrelated bottle"],
            },
            default_relations=[
                {"subject_role": "target", "relation": "target_to_reference", "object_role": "reference"},
                {"subject_role": "condiment", "relation": "near", "object_role": "reference"},
            ],
            action_template="place the food-support target on or beside the reference plate",
            history_policy="off",
        ),
        "drink_preparation": TaskFrame(
            name="drink_preparation",
            roles={
                "target": ["cup", "mug"],
                "reference": ["user area", "serving area", "mat"],
                "accessory": ["spoon", "sugar", "creamer", "coffee bottle"],
                "distractor": ["second mug", "same color bottle"],
            },
            default_relations=[
                {"subject_role": "accessory", "relation": "near", "object_role": "target"},
                {"subject_role": "target", "relation": "target_to_reference", "object_role": "reference"},
            ],
            action_template="prepare the drink vessel and place useful accessories near it",
            history_policy="off",
        ),
        "workspace_preparation": TaskFrame(
            name="workspace_preparation",
            roles={
                "target": ["notebook", "laptop", "book"],
                "reference": ["desk center", "workspace"],
                "accessory": ["pen", "keyboard", "mouse"],
                "distractor": ["snack", "toy", "cup", "remote"],
            },
            default_relations=[
                {"subject_role": "target", "relation": "target_to_reference", "object_role": "reference"},
                {"subject_role": "accessory", "relation": "near", "object_role": "target"},
            ],
            action_template="clear distractors and keep work objects in the center workspace",
            history_policy="reward-filtered",
        ),
        "cleanup_arrangement": TaskFrame(
            name="cleanup_arrangement",
            roles={
                "target": ["clutter", "snack", "toy", "wrapper"],
                "reference": ["organizer", "side area", "container"],
                "keep": ["notebook", "book", "pen", "cup"],
                "distractor": ["salient wrong object"],
            },
            default_relations=[
                {"subject_role": "target", "relation": "target_to_reference", "object_role": "reference"},
            ],
            action_template="move clutter to the side or organizer while preserving useful objects",
            history_policy="reward-filtered",
        ),
        "breakfast_setup": TaskFrame(
            name="breakfast_setup",
            roles={
                "target": ["bread", "pastry", "cereal", "food"],
                "reference": ["plate", "dish"],
                "accessory": ["cup", "spoon", "fork", "jam", "condiment"],
                "distractor": ["duplicate cup", "wrong plate", "unrelated container"],
            },
            default_relations=[
                {"subject_role": "target", "relation": "target_to_reference", "object_role": "reference"},
                {"subject_role": "accessory", "relation": "near", "object_role": "reference"},
            ],
            action_template="arrange breakfast food, plate, drink, and useful utensils",
            history_policy="reward-filtered",
        ),
    }


DEFAULT_FRAME_LIBRARY = build_default_frame_library()

