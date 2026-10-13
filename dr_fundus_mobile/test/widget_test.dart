import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dr_fundus_mobile/main.dart';

void main() {
  testWidgets('App root widget smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const ProviderScope(child: RetinaGuardApp()));
    await tester.pump(const Duration(milliseconds: 100));
    expect(find.byType(RetinaGuardApp), findsOneWidget);
  });
}
