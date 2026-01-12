from typing import List
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def expand_objectives(topic: str, objectives: List[str]) -> str:
    if topic == "Digital Image Fundamentals":
        return (
            "Digital image fundamentals describe how images are represented as "
            "two-dimensional matrices of pixels. Each pixel stores an intensity "
            "value representing brightness in grayscale or color information in "
            "RGB images. Image resolution refers to the total number of pixels "
            "and determines image detail and quality."
        )

    if topic == "Image Preprocessing":
        return (
            "Image preprocessing prepares images for analysis through grayscale "
            "conversion, noise reduction, resizing, and normalization."
        )

    if topic == "Edge Detection and Features":
        return (
            "Edge detection identifies object boundaries using image gradients. "
            "Sobel and Canny operators detect intensity changes. Features help "
            "recognition and tracking."
        )

    if topic == "Image Segmentation":
        return (
            "Image segmentation divides images into meaningful regions using "
            "thresholding, region-based methods and clustering."
        )

    if topic == "Object Detection Basics":
        return (
            "Object detection identifies and locates objects using bounding boxes, "
            "IoU for overlap measurement and Non-Maximum Suppression."
        )

    return " ".join(objectives)

def compute_similarity(reference_text: str, answer: str) -> float:
    if not answer.strip():
        return 0.0

    ref_emb = embedding_model.encode([reference_text])
    ans_emb = embedding_model.encode([answer])

    return float(cosine_similarity(ans_emb, ref_emb)[0][0])
