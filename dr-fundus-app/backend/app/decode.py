"""6-class decode used by the locked v2 training run.

Class 5 stays class 5 when it is the argmax. Otherwise the grade is the
expected severity of the renormalized probabilities on classes 0-4, cut by
the four SCORE thresholds. np.digitize(right=False) counts a cut when the
expected value is greater than or equal to the threshold.
"""


def advanced_predict_one(probs, thresholds):
    values = [float(p) for p in probs]
    if len(values) != 6:
        raise ValueError("expected 6 class probabilities")
    if len(thresholds) != 4:
        raise ValueError("expected 4 ordinal thresholds")
    chosen = 0
    for index in range(1, 6):
        if values[index] > values[chosen]:
            chosen = index
    if chosen == 5:
        return 5
    total = sum(values[:5])
    if total < 1e-8:
        total = 1e-8
    expected = sum((values[index] / total) * index for index in range(5))
    grade = 0
    for threshold in thresholds:
        if expected >= float(threshold):
            grade += 1
    if grade < 0:
        return 0
    if grade > 4:
        return 4
    return grade


def blend_probs(resnet_probs, vit_probs, resnet_weight, vit_weight):
    left = [float(p) for p in resnet_probs]
    right = [float(p) for p in vit_probs]
    if len(left) != 6 or len(right) != 6:
        raise ValueError("expected 6 class probabilities from each model")
    return [
        float(resnet_weight) * left[index] + float(vit_weight) * right[index]
        for index in range(6)
    ]
