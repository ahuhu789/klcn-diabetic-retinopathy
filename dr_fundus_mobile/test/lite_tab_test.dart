import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dr_fundus_mobile/main.dart';

void main() {
  testWidgets('bottom navigation switches between API and Lite (offline) tabs', (tester) async {
    tester.view.physicalSize = const Size(2400, 4000);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.reset);
    await tester.pumpWidget(const ProviderScope(child: RetinaGuardApp()));
    await tester.pump(const Duration(milliseconds: 100));
    expect(find.text('API (ensemble)'), findsOneWidget);
    expect(find.text('Lite (offline)'), findsOneWidget);
    expect(find.text('RetinaGuard • API (ensemble)'), findsOneWidget);

    await tester.tap(find.text('Lite (offline)'));
    await tester.pump(const Duration(milliseconds: 300));
    expect(find.text('RetinaGuard • Lite (offline)'), findsOneWidget);
    expect(find.text('Phân tích Offline (Model A + Lite)'), findsOneWidget);
  });
}
