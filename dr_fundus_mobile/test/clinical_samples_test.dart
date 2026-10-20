import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:dr_fundus_mobile/core/constants/clinical_samples.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('the app bundles the 10 clinical sample photos', () async {
    expect(ClinicalSamples.all.length, 10);
    expect(ClinicalSamples.all.map((s) => s.filename).toSet().length, 10);
    for (final sample in ClinicalSamples.all) {
      expect(sample.isBundledAsset, isTrue);
      final data = await rootBundle.load(sample.url);
      expect(data.lengthInBytes, greaterThan(10000), reason: sample.filename);
    }
  });
}
