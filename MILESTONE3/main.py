from graph import build_graph
from checkpoints import CHECKPOINTS

if __name__ == "__main__":
    app = build_graph()
    result = app.invoke({
        "checkpoint": CHECKPOINTS[2],
        "answers": "Edges are detected using gradients like Sobel and Canny.",
        "confidence": 3
    })
    print(result)
