"""Decoding for the locked v3 Model B (pure Python, no numpy/torch).

Ensemble probabilities are a weighted sum of the branch probabilities.
Decode families (same as phase_a_lib.py used to lock the config on VAL):

- argmax6: argmax over the 6 classes.
- hierarchical: class 5 iff p5 > t5, otherwise argmax(p[0:5]).
- hierarchical_ordinal: class 5 iff p5 > t5, otherwise the expected grade of
  the renormalized p[0:5] cut by 4 thresholds with np.digitize(right=False)
  semantics (a cut counts when expected >= threshold).

np.argmax keeps the first index on ties; so does this code.
"""


def _argmax(values):
    best = 0
    for index in range(1, len(values)):
        if values[index] > values[best]:
            best = index
    return best


def expected_grade(probs):
    values = [float(p) for p in probs[:5]]
    total = sum(values)
    if total < 1e-8:
        total = 1e-8
    return sum((values[index] / total) * index for index in range(5))


def decode_one(probs, family, t5=None, thresholds=None):
    values = [float(p) for p in probs]
    if len(values) != 6:
        raise ValueError("expected 6 class probabilities")
    if family == "argmax6":
        return _argmax(values)
    if t5 is None:
        raise ValueError("t5 is required for hierarchical decodes")
    if values[5] > float(t5):
        return 5
    if family == "hierarchical":
        return _argmax(values[:5])
    if family == "hierarchical_ordinal":
        if thresholds is None or len(thresholds) != 4:
            raise ValueError("expected 4 ordinal thresholds")
        expected = expected_grade(values)
        grade = sum(1 for cut in thresholds if expected >= float(cut))
        return max(0, min(4, grade))
    raise ValueError("unknown decode family %s" % family)


def decode_record(probs, record):
    """record = {"family": ..., "t5": ..., "thresholds": [..] or "a,b,c,d" or None}."""
    thresholds = record.get("thresholds")
    if isinstance(thresholds, str):
        thresholds = [float(v) for v in thresholds.split(",")] if thresholds.strip() else None
    return decode_one(probs, record["family"], record.get("t5"), thresholds)


def blend_probs(prob_list, weights):
    if len(prob_list) != len(weights):
        raise ValueError("one weight per branch")
    out = [0.0] * 6
    for probs, weight in zip(prob_list, weights):
        values = [float(p) for p in probs]
        if len(values) != 6:
            raise ValueError("expected 6 class probabilities from each branch")
        for index in range(6):
            out[index] += float(weight) * values[index]
    return out
