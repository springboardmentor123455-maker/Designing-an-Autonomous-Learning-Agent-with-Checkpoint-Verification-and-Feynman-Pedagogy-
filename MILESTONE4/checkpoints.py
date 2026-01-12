from dataclasses import dataclass
from typing import List

@dataclass
class Checkpoint:
    id: int
    topic: str
    objectives: List[str]
    success_criteria: str

CHECKPOINTS = [
    Checkpoint(
        id=0,
        topic="Digital Image Fundamentals",
        objectives=[
            "Understand image as a matrix",
            "Pixel intensity and resolution",
            "RGB vs Grayscale"
        ],
        success_criteria="Can explain digital image representation"
    ),
    Checkpoint(
        id=1,
        topic="Image Preprocessing",
        objectives=[
            "Grayscale conversion",
            "Noise reduction",
            "Image resizing and normalization"
        ],
        success_criteria="Can preprocess images correctly"
    ),
    Checkpoint(
        id=2,
        topic="Edge Detection and Features",
        objectives=[
            "Understand edges and gradients",
            "Sobel vs Canny",
            "Why features matter"
        ],
        success_criteria="Can apply edge detection methods"
    ),
    Checkpoint(
        id=3,
        topic="Image Segmentation",
        objectives=[
            "Thresholding",
            "Region-based segmentation",
            "Clustering intuition"
        ],
        success_criteria="Can segment images into regions"
    ),
    Checkpoint(
        id=4,
        topic="Object Detection Basics",
        objectives=[
            "Bounding boxes",
            "Intersection over Union (IoU)",
            "Non-Maximum Suppression"
        ],
        success_criteria="Can explain object detection workflow"
    ),
]
