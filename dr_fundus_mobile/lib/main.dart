import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'core/constants/app_colors.dart';
import 'features/diagnosis/controllers/diagnosis_controller.dart';
import 'features/diagnosis/views/home_dashboard_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();

  // Set system UI overlay style
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.dark,
    ),
  );

  runApp(
    const ProviderScope(
      child: RetinaGuardApp(),
    ),
  );
}

class RetinaGuardApp extends StatelessWidget {
  const RetinaGuardApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'RetinaGuard Mobile',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        scaffoldBackgroundColor: AppColors.background,
        colorScheme: ColorScheme.fromSeed(
          seedColor: AppColors.accent,
          primary: AppColors.accent,
          secondary: AppColors.primary,
          surface: Colors.white,
        ),
        appBarTheme: const AppBarTheme(
          elevation: 0.5,
          backgroundColor: Colors.white,
          foregroundColor: AppColors.textPrimary,
          centerTitle: false,
        ),
        cardTheme: CardThemeData(
          color: Colors.white,
          elevation: 1,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: const BorderSide(color: AppColors.cardBorder),
          ),
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: AppColors.accent,
            foregroundColor: Colors.white,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(10),
            ),
          ),
        ),
      ),
      home: const MainShell(),
    );
  }
}

/// Hai tab: "API" (ensemble trên server) và "Lite (offline)" (student TFLite trên máy).
/// Mỗi tab có Navigator riêng; tab Lite ghi đè diagnosisProvider trong ProviderScope con
/// nên dùng lại toàn bộ màn hình nhưng có state và mô hình riêng.
class MainShell extends StatefulWidget {
  const MainShell({super.key});

  @override
  State<MainShell> createState() => _MainShellState();
}

class _MainShellState extends State<MainShell> {
  int _index = 0;
  final _navKeys = [GlobalKey<NavigatorState>(), GlobalKey<NavigatorState>()];

  Widget _tabNavigator(int i) => Navigator(
        key: _navKeys[i],
        onGenerateRoute: (_) => MaterialPageRoute(builder: (_) => const HomeDashboardScreen()),
      );

  @override
  Widget build(BuildContext context) {
    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, _) {
        if (didPop) return;
        final nav = _navKeys[_index].currentState;
        if (nav != null && nav.canPop()) {
          nav.pop();
        } else if (_index != 0) {
          setState(() => _index = 0);
        } else {
          SystemNavigator.pop();
        }
      },
      child: Scaffold(
        body: IndexedStack(
          index: _index,
          children: [
            _tabNavigator(0),
            ProviderScope(
              overrides: [diagnosisProvider.overrideWith(createLiteDiagnosisNotifier)],
              child: _tabNavigator(1),
            ),
          ],
        ),
        bottomNavigationBar: NavigationBar(
          selectedIndex: _index,
          onDestinationSelected: (i) => setState(() => _index = i),
          height: 62,
          destinations: const [
            NavigationDestination(
              icon: Icon(Icons.cloud_outlined),
              selectedIcon: Icon(Icons.cloud),
              label: 'API (ensemble)',
            ),
            NavigationDestination(
              icon: Icon(Icons.offline_bolt_outlined),
              selectedIcon: Icon(Icons.offline_bolt),
              label: 'Lite (offline)',
            ),
          ],
        ),
      ),
    );
  }
}
