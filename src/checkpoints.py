from typing import Dict, Any, List

CHECKPOINTS: List[Dict[str, Any]] = [
    {
        "id": 1,
        "topic": "Chain rule in calculus",
        "objectives": [
            "Understand the formula for chain rule",
            "Identify inner and outer functions",
            "Apply chain rule to simple composite functions",
        ],
        "success_threshold": 0.7,
    },
    {
        "id": 2,
        "topic": "Product rule in calculus",
        "objectives": [
            "Recall the product rule formula",
            "Differentiate products of two functions",
        ],
        "success_threshold": 0.7,
    },
    # add more later
]


def get_checkpoint(checkpoint_id: int) -> Dict[str, Any]:
    for cp in CHECKPOINTS:
        if cp["id"] == checkpoint_id:
            return cp
    raise ValueError(f"Checkpoint {checkpoint_id} not found")
