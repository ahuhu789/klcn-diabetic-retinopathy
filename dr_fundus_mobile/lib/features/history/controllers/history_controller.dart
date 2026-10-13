import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/storage/local_storage.dart';
import '../../../models/screening_history_item.dart';

class HistoryNotifier extends StateNotifier<List<ScreeningHistoryItem>> {
  final LocalStorageService _storage = LocalStorageService();

  HistoryNotifier() : super([]) {
    loadHistory();
  }

  Future<void> loadHistory() async {
    final list = await _storage.getHistory();
    state = list;
  }

  Future<void> addRecord(ScreeningHistoryItem item) async {
    await _storage.saveRecord(item);
    state = [item, ...state];
  }

  Future<void> deleteRecord(String id) async {
    await _storage.deleteRecord(id);
    state = state.where((item) => item.id != id).toList();
  }

  Future<void> clearAll() async {
    await _storage.clearAll();
    state = [];
  }
}

final historyProvider = StateNotifierProvider<HistoryNotifier, List<ScreeningHistoryItem>>((ref) {
  return HistoryNotifier();
});
