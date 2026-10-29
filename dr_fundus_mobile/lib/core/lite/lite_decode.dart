/// "v2 + val-tuned decode" (hier_ext) for the Lite student, identical to
/// kg/v4_distill/eval/decode_ext.py decode():
///   q = p with q[1] *= w1, renormalised; g = argmax(q[0:5]) (first index on ties);
///   class 5 if q[5] > (g == 0 ? t5n : t5), else g.
class LiteDecode {
  static const double w1 = 1.5;
  static const double t5 = 0.45;
  static const double t5n = 0.75;

  static Map<String, dynamic> get record => {'family': 'hier_ext', 'w1': w1, 't5': t5, 't5n': t5n};

  static List<double> reweight(List<double> p, {double weight1 = w1}) {
    final q = List<double>.from(p);
    q[1] *= weight1;
    final s = q.fold<double>(0, (a, b) => a + b);
    return q.map((v) => v / s).toList();
  }

  /// Returns (stage, reweighted probabilities).
  static (int, List<double>) decode(List<double> p, {double weight1 = w1, double thr5 = t5, double thr5Normal = t5n}) {
    if (p.length != 6) throw ArgumentError('expected 6 class probabilities');
    final q = reweight(p, weight1: weight1);
    var g = 0;
    for (var i = 1; i < 5; i++) {
      if (q[i] > q[g]) g = i;
    }
    final thr = g == 0 ? thr5Normal : thr5;
    return (q[5] > thr ? 5 : g, q);
  }
}
