import 'dart:convert';
import 'dart:io';
import 'package:path_provider/path_provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../models/screening_history_item.dart';

class LocalStorageService {
  static const String _historyKey = 'screening_history_records';

  /// Lấy toàn bộ lịch sử các ca sàng lọc
  Future<List<ScreeningHistoryItem>> getHistory() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final listJson = prefs.getStringList(_historyKey) ?? [];
      final list = listJson
          .map((itemStr) => ScreeningHistoryItem.deserialize(itemStr))
          .toList();
      // Sắp xếp ca mới nhất lên đầu
      list.sort((a, b) => b.timestamp.compareTo(a.timestamp));
      return list;
    } catch (e) {
      return [];
    }
  }

  /// Lưu một ca sàng lọc mới
  Future<void> saveRecord(ScreeningHistoryItem item) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final listJson = prefs.getStringList(_historyKey) ?? [];
      listJson.insert(0, item.serialize());
      // Giới hạn lưu tối đa 50 ca gần nhất
      if (listJson.length > 50) {
        listJson.removeRange(50, listJson.length);
      }
      await prefs.setStringList(_historyKey, listJson);
    } catch (e) {
      // Ignored
    }
  }

  /// Xóa một ca khỏi lịch sử
  Future<void> deleteRecord(String id) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final listJson = prefs.getStringList(_historyKey) ?? [];
      listJson.removeWhere((itemStr) {
        final decoded = jsonDecode(itemStr);
        return decoded['id'] == id;
      });
      await prefs.setStringList(_historyKey, listJson);
    } catch (e) {
      // Ignored
    }
  }

  /// Xóa toàn bộ lịch sử
  Future<void> clearAll() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_historyKey);
  }

  /// Lưu tệp ảnh vào thư mục tài liệu của ứng dụng
  Future<String> saveImagePermanently(File sourceFile, String fileName) async {
    try {
      final appDir = await getApplicationDocumentsDirectory();
      final savedPath = '${appDir.path}/$fileName';
      final savedFile = await sourceFile.copy(savedPath);
      return savedFile.path;
    } catch (e) {
      return sourceFile.path;
    }
  }
}
