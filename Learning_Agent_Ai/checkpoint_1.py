from checkpoint_class_1 import Checkpoint

CHECKPOINTS = [
    Checkpoint(
        id="cp1",
        topic="Binary Search",
        objectives=[
            "Understand divide-and-conquer",
            "Know time complexity",
            "Apply binary search correctly",
        ],
        success_criteria="Explain and apply binary search",
    ),
    Checkpoint(
        id="cp2",
        topic="Merge Sort",
        objectives=[
            "Understand recursive sorting",
            "Explain merge operation",
            "Analyze time complexity",
        ],
        success_criteria="Explain merge sort",
    ),
    Checkpoint(
        id="cp3",
        topic="Hash Tables",
        objectives=[
            "Understand key-value mapping",
            "Explain collision handling",
            "Describe average lookup time",
        ],
        success_criteria="Explain hashing concepts",
    ),
    Checkpoint(
        id="cp4",
        topic="Graphs (BFS & DFS)",
        objectives=[
            "Understand graph traversal",
            "Differentiate BFS and DFS",
            "Explain use cases",
        ],
        success_criteria="Compare BFS and DFS",
    ),
    Checkpoint(
        id="cp5",
        topic="Dynamic Programming",
        objectives=[
            "Understand overlapping subproblems",
            "Explain memoization",
            "Explain tabulation",
        ],
        success_criteria="Explain dynamic programming",
    ),
]