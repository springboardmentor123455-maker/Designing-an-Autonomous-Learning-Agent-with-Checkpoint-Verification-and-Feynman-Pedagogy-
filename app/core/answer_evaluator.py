def evaluate_user_responses(questions, answers):
    scores = []
    weak = []

    for q, a in zip(questions, answers):
        score = 0.0

        if len(a.split()) >= 10:
            score += 0.4
        if any(k in a.lower() for k in ["weight", "bias", "activation"]):
            score += 0.4

        if score < 0.7:
            weak.append(q)

        scores.append(min(score, 1.0))

    return sum(scores)/len(scores), weak
