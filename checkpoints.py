# src/checkpoints.py

CHECKPOINTS = [
    {
        "id": 1,
        "topic": "Arrays Basics",
        "objectives": [
            "Understand array structure",
            "Indexing and traversal",
            "Time complexity of access"
        ]
    },
    {
        "id": 2,
        "topic": "Binary Search",
        "objectives": [
            "Sorted arrays",
            "Divide and conquer",
            "Logarithmic complexity"
        ]
    },
    {
        "id": 3,
        "topic": "Two Pointer Technique",
        "objectives": [
            "Left/right pointers",
            "Optimizing linear scans"
        ]
    }
]


def get_checkpoint_by_id(checkpoint_id):
    for checkpoint in CHECKPOINTS:
        if checkpoint["id"] == checkpoint_id:
            return checkpoint
    return None
