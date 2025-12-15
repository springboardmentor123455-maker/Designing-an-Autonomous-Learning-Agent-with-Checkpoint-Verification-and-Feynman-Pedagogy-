from graph import build_graph

if __name__ == "__main__":
    app = build_graph()
    state = {
        "checkpoint_index": 0,
        "answers": "Images are matrices of pixel values..."
    }
    result = app.invoke(state)
    print(result)
