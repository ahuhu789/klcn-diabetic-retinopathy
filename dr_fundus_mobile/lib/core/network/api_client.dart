import 'dart:io';
import 'dart:typed_data';
import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../constants/api_endpoints.dart';
import '../../models/prediction_response.dart';
import '../../models/sample_image_info.dart';

class ApiClient {
  late Dio _dio;
  String _baseUrl = ApiEndpoints.hfCloudUrl;

  ApiClient({String? baseUrl}) {
    if (baseUrl != null && baseUrl.isNotEmpty) {
      _baseUrl = baseUrl;
    }
    _initDio();
  }

  void _initDio() {
    _dio = Dio(
      BaseOptions(
        baseUrl: _baseUrl,
        connectTimeout: const Duration(seconds: 30),
        receiveTimeout: const Duration(seconds: 90),
        sendTimeout: const Duration(seconds: 60),
        headers: {
          'Accept': 'application/json',
        },
      ),
    );

    // Logging interceptor for debugging
    _dio.interceptors.add(
      LogInterceptor(
        request: true,
        requestHeader: false,
        requestBody: false,
        responseHeader: false,
        responseBody: false,
        error: true,
      ),
    );
  }

  String get baseUrl => _baseUrl;

  Future<void> updateBaseUrl(String newUrl) async {
    _baseUrl = newUrl.trim();
    if (_baseUrl.endsWith('/')) {
      _baseUrl = _baseUrl.substring(0, _baseUrl.length - 1);
    }
    _dio.options.baseUrl = _baseUrl;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(ApiEndpoints.prefBaseUrlKey, _baseUrl);
  }

  Future<void> loadSavedBaseUrl() async {
    final prefs = await SharedPreferences.getInstance();
    final saved = prefs.getString(ApiEndpoints.prefBaseUrlKey);
    if (saved != null && saved.isNotEmpty) {
      _baseUrl = saved;
      _dio.options.baseUrl = _baseUrl;
    }
  }

  /// Kiểm tra trạng thái máy chủ & độ trễ mạng (Ping)
  Future<Map<String, dynamic>> checkHealth() async {
    final stopwatch = Stopwatch()..start();
    try {
      final response = await _dio.get(ApiEndpoints.health);
      stopwatch.stop();
      if (response.statusCode == 200) {
        final data = Map<String, dynamic>.from(response.data);
        data['latency_ms'] = stopwatch.elapsedMilliseconds;
        return data;
      }
      throw Exception('Mã phản hồi HTTP: ${response.statusCode}');
    } catch (e) {
      stopwatch.stop();
      rethrow;
    }
  }

  /// Lấy danh sách 10 mẫu ảnh đáy mắt lâm sàng
  Future<List<SampleImageInfo>> getSamples() async {
    try {
      final response = await _dio.get(ApiEndpoints.samples);
      if (response.statusCode == 200 && response.data is List) {
        return (response.data as List)
            .map((item) => SampleImageInfo.fromJson(Map<String, dynamic>.from(item)))
            .toList();
      }
      return [];
    } catch (e) {
      throw Exception('Không thể tải danh sách ảnh mẫu: $e');
    }
  }

  /// Tải dữ liệu ảnh mẫu (binary bytes)
  Future<Uint8List> downloadSampleBytes(String relativeOrAbsoluteUrl) async {
    try {
      String fullUrl = relativeOrAbsoluteUrl;
      if (!fullUrl.startsWith('http')) {
        fullUrl = '$_baseUrl$relativeOrAbsoluteUrl';
      }
      final response = await _dio.get<List<int>>(
        fullUrl,
        options: Options(responseType: ResponseType.bytes),
      );
      return Uint8List.fromList(response.data!);
    } catch (e) {
      throw Exception('Lỗi tải tệp ảnh mẫu: $e');
    }
  }

  /// Gửi ảnh tệp tin để phân tích qua 3 mô hình AI
  Future<PredictionResponse> predictImageFile(
    File file, {
    void Function(int sent, int total)? onSendProgress,
  }) async {
    try {
      final fileName = file.path.split(Platform.pathSeparator).last;
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(
          file.path,
          filename: fileName,
        ),
      });

      final response = await _dio.post(
        ApiEndpoints.predict,
        data: formData,
        onSendProgress: onSendProgress,
      );

      if (response.statusCode == 200) {
        return PredictionResponse.fromJson(Map<String, dynamic>.from(response.data));
      } else {
        throw Exception(
            response.data?['detail'] ?? 'Máy chủ trả về lỗi HTTP ${response.statusCode}');
      }
    } on DioException catch (e) {
      if (e.response != null && e.response?.data != null) {
        final detail = e.response?.data['detail'] ?? e.message;
        throw Exception('Lỗi từ hệ thống AI: $detail');
      }
      throw Exception('Không thể kết nối đến máy chủ: ${e.message}');
    } catch (e) {
      throw Exception('Lỗi xử lý yêu cầu: $e');
    }
  }

  /// Gửi dữ liệu ảnh dạng Bytes (bộ nhớ RAM)
  Future<PredictionResponse> predictImageBytes(
    Uint8List bytes,
    String fileName, {
    void Function(int sent, int total)? onSendProgress,
  }) async {
    try {
      final formData = FormData.fromMap({
        'file': MultipartFile.fromBytes(
          bytes,
          filename: fileName,
        ),
      });

      final response = await _dio.post(
        ApiEndpoints.predict,
        data: formData,
        onSendProgress: onSendProgress,
      );

      if (response.statusCode == 200) {
        return PredictionResponse.fromJson(Map<String, dynamic>.from(response.data));
      } else {
        throw Exception(
            response.data?['detail'] ?? 'Máy chủ trả về lỗi HTTP ${response.statusCode}');
      }
    } on DioException catch (e) {
      if (e.response != null && e.response?.data != null) {
        final detail = e.response?.data['detail'] ?? e.message;
        throw Exception('Lỗi từ hệ thống AI: $detail');
      }
      throw Exception('Lỗi kết nối mạng: ${e.message}');
    } catch (e) {
      throw Exception('Lỗi phân tích: $e');
    }
  }
}
