import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/constants/api_endpoints.dart';
import '../../../core/network/api_client.dart';

class SettingsState {
  final String baseUrl;
  final bool isPinging;
  final int? latencyMs;
  final bool isHealthy;
  final Map<String, dynamic>? healthData;
  final String? errorMessage;

  SettingsState({
    required this.baseUrl,
    this.isPinging = false,
    this.latencyMs,
    this.isHealthy = false,
    this.healthData,
    this.errorMessage,
  });

  SettingsState copyWith({
    String? baseUrl,
    bool? isPinging,
    int? latencyMs,
    bool? isHealthy,
    Map<String, dynamic>? healthData,
    String? errorMessage,
  }) {
    return SettingsState(
      baseUrl: baseUrl ?? this.baseUrl,
      isPinging: isPinging ?? this.isPinging,
      latencyMs: latencyMs ?? this.latencyMs,
      isHealthy: isHealthy ?? this.isHealthy,
      healthData: healthData ?? this.healthData,
      errorMessage: errorMessage,
    );
  }
}

class SettingsNotifier extends StateNotifier<SettingsState> {
  final ApiClient _apiClient;

  SettingsNotifier(this._apiClient)
      : super(SettingsState(baseUrl: _apiClient.baseUrl)) {
    init();
  }

  Future<void> init() async {
    await _apiClient.loadSavedBaseUrl();
    state = state.copyWith(baseUrl: _apiClient.baseUrl);
    await pingServer();
  }

  Future<void> updateBaseUrl(String newUrl) async {
    await _apiClient.updateBaseUrl(newUrl);
    state = state.copyWith(baseUrl: _apiClient.baseUrl, errorMessage: null);
    await pingServer();
  }

  Future<void> pingServer() async {
    state = state.copyWith(isPinging: true, errorMessage: null);
    try {
      final health = await _apiClient.checkHealth();
      state = state.copyWith(
        isPinging: false,
        isHealthy: health['status'] == 'healthy',
        latencyMs: health['latency_ms'],
        healthData: health,
        errorMessage: null,
      );
    } catch (e) {
      state = state.copyWith(
        isPinging: false,
        isHealthy: false,
        latencyMs: null,
        healthData: null,
        errorMessage: e.toString().replaceAll('Exception: ', ''),
      );
    }
  }
}

final apiClientProvider = Provider<ApiClient>((ref) {
  return ApiClient();
});

final settingsProvider = StateNotifierProvider<SettingsNotifier, SettingsState>((ref) {
  final client = ref.watch(apiClientProvider);
  return SettingsNotifier(client);
});
