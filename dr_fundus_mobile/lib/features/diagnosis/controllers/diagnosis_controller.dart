import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';
import '../../../core/constants/clinical_samples.dart';
import '../../../core/network/api_client.dart';
import '../../../models/prediction_response.dart';
import '../../../models/sample_image_info.dart';
import '../../../models/screening_history_item.dart';
import '../../history/controllers/history_controller.dart';
import '../../settings/controllers/settings_controller.dart';
import '../../../core/services/local_inference_service.dart';

class DiagnosisState {
  final File? selectedFile;
  final SampleImageInfo? selectedSample;
  final Uint8List? imageBytes;
  final String? imageName;
  final List<SampleImageInfo> samples;
  final String sampleFilter;
  final bool isLoading;
  final double uploadProgress;
  final PredictionResponse? result;
  final String? errorMessage;
  final int dashboardTab;
  final double blendOpacity;
  final String activeGradCamModel; // 'ensemble', 'vit3', 'effb4' hoặc 'e_twohead'

  DiagnosisState({
    this.selectedFile,
    this.selectedSample,
    this.imageBytes,
    this.imageName,
    this.samples = const [],
    this.sampleFilter = 'all',
    this.isLoading = false,
    this.uploadProgress = 0.0,
    this.result,
    this.errorMessage,
    this.dashboardTab = 0,
    this.blendOpacity = 0.65,
    this.activeGradCamModel = 'ensemble',
  });

  DiagnosisState copyWith({
    File? selectedFile,
    SampleImageInfo? selectedSample,
    Uint8List? imageBytes,
    String? imageName,
    List<SampleImageInfo>? samples,
    String? sampleFilter,
    bool? isLoading,
    double? uploadProgress,
    PredictionResponse? result,
    String? errorMessage,
    int? dashboardTab,
    double? blendOpacity,
    String? activeGradCamModel,
    bool clearFile = false,
    bool clearSample = false,
    bool clearResult = false,
  }) {
    return DiagnosisState(
      selectedFile: selectedFile ?? (clearFile ? null : this.selectedFile),
      selectedSample: selectedSample ?? (clearSample ? null : this.selectedSample),
      imageBytes: imageBytes ?? (clearFile ? null : this.imageBytes),
      imageName: imageName ?? (clearFile ? null : this.imageName),
      samples: samples ?? this.samples,
      sampleFilter: sampleFilter ?? this.sampleFilter,
      isLoading: isLoading ?? this.isLoading,
      uploadProgress: uploadProgress ?? this.uploadProgress,
      result: clearResult ? null : (result ?? this.result),
      errorMessage: errorMessage,
      dashboardTab: dashboardTab ?? this.dashboardTab,
      blendOpacity: blendOpacity ?? this.blendOpacity,
      activeGradCamModel: activeGradCamModel ?? this.activeGradCamModel,
    );
  }
}

class DiagnosisNotifier extends StateNotifier<DiagnosisState> {
  final ApiClient _apiClient;
  final Ref _ref;
  final ImagePicker _picker = ImagePicker();

  DiagnosisNotifier(this._apiClient, this._ref)
      : super(DiagnosisState(samples: ClinicalSamples.all));

  void setSampleFilter(String filter) {
    state = state.copyWith(sampleFilter: filter);
  }

  void setDashboardTab(int index) {
    state = state.copyWith(dashboardTab: index);
  }

  void setBlendOpacity(double opacity) {
    state = state.copyWith(blendOpacity: opacity);
  }

  void setActiveGradCamModel(String model) {
    state = state.copyWith(activeGradCamModel: model);
  }

  Future<void> pickImage(ImageSource source) async {
    try {
      final picked = await _picker.pickImage(
        source: source,
        maxWidth: 2048,
        maxHeight: 2048,
        imageQuality: 95,
      );

      if (picked != null) {
        final file = File(picked.path);
        final bytes = await file.readAsBytes();
        state = state.copyWith(
          selectedFile: file,
          imageBytes: bytes,
          imageName: picked.name,
          clearSample: true,
          clearResult: true,
          errorMessage: null,
          dashboardTab: 0,
        );
      }
    } catch (e) {
      state = state.copyWith(errorMessage: 'Không thể truy cập camera/thư viện: $e');
    }
  }

  Future<void> selectSample(SampleImageInfo sample) async {
    try {
      state = state.copyWith(
        isLoading: true,
        selectedSample: sample,
        imageName: sample.filename,
        clearFile: true,
        clearResult: true,
        errorMessage: null,
      );

      final Uint8List bytes;
      if (sample.isBundledAsset) {
        final data = await rootBundle.load(sample.url);
        bytes = data.buffer.asUint8List(data.offsetInBytes, data.lengthInBytes);
      } else {
        bytes = await _apiClient.downloadSampleBytes(sample.url);
      }
      state = state.copyWith(
        isLoading: false,
        imageBytes: bytes,
        dashboardTab: 0,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'Lỗi tải ảnh mẫu: $e',
      );
    }
  }

  void clearImage() {
    state = state.copyWith(
      clearFile: true,
      clearSample: true,
      clearResult: true,
      errorMessage: null,
      dashboardTab: 0,
    );
  }

  Future<void> runAnalysis() async {
    if (state.imageBytes == null) {
      state = state.copyWith(errorMessage: 'Vui lòng chọn ảnh đáy mắt trước khi phân tích!');
      return;
    }

    state = state.copyWith(
      isLoading: true,
      uploadProgress: 0.1,
      errorMessage: null,
      clearResult: true,
    );

    try {
      // 1. CHẠY CỔNG KIỂM DUYỆT MODEL A TRỰC TIẾP TRÊN ĐIỆN THOẠI (ON-DEVICE EDGE)
      final localService = LocalInferenceService();
      final gateRes = await localService.evaluateFundusGate(state.imageBytes!);

      if (!gateRes.isFundus) {
        final rejectRes = PredictionResponse(
          isFundus: false,
          fundusConfidence: gateRes.confidence,
          threshold: gateRes.threshold,
          message: gateRes.message,
          clinicalDisclaimer: 'Hệ thống đã tự động từ chối ảnh không hợp lệ ngay tại thiết bị biên (Mobile Edge).',
        );

        state = state.copyWith(
          isLoading: false,
          result: rejectRes,
          uploadProgress: 1.0,
          dashboardTab: 0,
        );
        return;
      }

      // 2. GỬI LÊN SERVER ĐỂ CHẠY ENSEMBLE 6 LỚP (MODEL B)
      PredictionResponse res;
      try {
        if (state.selectedFile != null) {
          res = await _apiClient.predictImageFile(
            state.selectedFile!,
            onSendProgress: (sent, total) {
              if (total > 0) {
                state = state.copyWith(uploadProgress: 0.3 + (sent / total) * 0.7);
              }
            },
          );
        } else {
          res = await _apiClient.predictImageBytes(
            state.imageBytes!,
            state.imageName ?? 'sample.jpg',
            onSendProgress: (sent, total) {
              if (total > 0) {
                state = state.copyWith(uploadProgress: 0.3 + (sent / total) * 0.7);
              }
            },
          );
        }

      } catch (_) {
        res = PredictionResponse(
          isFundus: true,
          fundusConfidence: gateRes.confidence,
          threshold: gateRes.threshold,
          message: 'Ảnh đáy mắt hợp lệ trên máy, nhưng không gọi được server Model B.',
          drError: 'Cần kết nối tới backend để chạy ensemble 6 lớp và bản đồ nhiệt. Model B không chạy trên điện thoại.',
          clinicalDisclaimer: 'Cổng kiểm tra ảnh chạy trên máy. Phân loại 6 lớp cần server.',
        );
      }

      state = state.copyWith(
        isLoading: false,
        result: res,
        uploadProgress: 1.0,
        dashboardTab: 0,
      );

      // Lưu tự động vào lịch sử khám cục bộ
      final record = ScreeningHistoryItem(
        id: 'REC-${DateTime.now().millisecondsSinceEpoch}',
        patientName: state.selectedSample != null
            ? '[Ảnh mẫu] ${state.selectedSample!.name}'
            : 'Bệnh nhân ${DateTime.now().hour}:${DateTime.now().minute}',
        patientId: 'BN-${DateTime.now().millisecondsSinceEpoch.toString().substring(7)}',
        timestamp: DateTime.now(),
        imagePath: state.selectedFile?.path ?? '',
        isSample: state.selectedSample != null,
        sampleFilename: state.selectedSample?.filename,
        response: res,
      );
      _ref.read(historyProvider.notifier).addRecord(record);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: e.toString().replaceAll('Exception: ', ''),
      );
    }
  }
}

final diagnosisProvider = StateNotifierProvider<DiagnosisNotifier, DiagnosisState>((ref) {
  final client = ref.watch(apiClientProvider);
  return DiagnosisNotifier(client, ref);
});
