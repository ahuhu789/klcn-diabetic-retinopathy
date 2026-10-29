import 'dart:convert';
import 'dart:io';

import 'package:dr_fundus_mobile/core/lite/lite_decode.dart';
import 'package:dr_fundus_mobile/core/services/lite_inference_service.dart';
import 'package:flutter_test/flutter_test.dart';

/// Lite decode vs the Python reference (dr-fundus-app/lite_parity/python_reference.py ->
/// test/fixtures/lite_ref.json): 48 probability vectors + the student TTA probabilities of
/// 16 images, decoded with hier_ext {w1 1.5, t5 0.45, t5n 0.75}.
void main() {
  final ref = jsonDecode(File('test/fixtures/lite_ref.json').readAsStringSync()) as Map<String, dynamic>;
  List<double> vec(dynamic l) => (l as List).map((v) => (v as num).toDouble()).toList();

  test('decode params match the accepted v2 + val-tuned decode', () {
    expect(ref['decode'], {'w1': 1.5, 't5': 0.45, 't5n': 0.75});
    expect(LiteDecode.record, {'family': 'hier_ext', 'w1': 1.5, 't5': 0.45, 't5n': 0.75});
  });

  test('decode cases match Python', () {
    for (final c in ref['decode_cases'] as List) {
      final (stage, q) = LiteDecode.decode(vec(c['p']));
      expect(stage, c['cls'], reason: 'p=${c['p']}');
      final pq = vec(c['q']);
      for (var i = 0; i < 6; i++) {
        expect(q[i], closeTo(pq[i], 1e-9));
      }
    }
  });

  test('image probabilities decode like Python and pack like the API', () {
    for (final im in ref['images'] as List) {
      final pred = LiteInferenceService.buildPrediction(vec(im['probs']));
      expect(pred.stage, im['cls'], reason: im['file'] as String);
      expect(pred.probabilities.length, 6);
      expect(pred.probFor(pred.stage), closeTo(pred.confidence, 1e-9));
    }
  });

  test('normal guard: DR argmax 0 needs p5 > 0.75', () {
    expect(LiteDecode.decode([0.26, 0.01, 0.01, 0.01, 0.01, 0.70]).$1, 0);
    expect(LiteDecode.decode([0.15, 0.01, 0.01, 0.01, 0.01, 0.81]).$1, 5);
    expect(LiteDecode.decode([0.10, 0.20, 0.10, 0.00, 0.00, 0.60]).$1, 5);
  });
}
