import 'dart:convert';
import 'dart:typed_data';
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;
import 'package:printing/printing.dart';
import '../../models/prediction_response.dart';
import '../constants/clinical_constants.dart';

class PdfReportGenerator {
  /// Tạo và chia sẻ hoặc in phiếu kết quả chẩn đoán lâm sàng PDF
  static Future<void> generateAndShare({
    required String patientName,
    required String patientId,
    required DateTime timestamp,
    required PredictionResponse result,
    Uint8List? originalImageBytes,
  }) async {
    final pdf = pw.Document();

    // Chuẩn bị ảnh heatmap base64 nếu có
    // Heatmap ensemble (tổng có trọng số Grad-CAM của 3 nhánh); nếu thiếu thì lấy nhánh ViT.
    pw.MemoryImage? vitHeatmapImage;
    final heatmapSource = result.drResult?.heatmapBase64 ?? result.drVit?.heatmapBase64;
    if (heatmapSource != null) {
      try {
        final cleanBase64 = heatmapSource
            .replaceAll(RegExp(r'^data:image\/[a-zA-Z]+;base64,'), '');
        vitHeatmapImage = pw.MemoryImage(base64Decode(cleanBase64));
      } catch (_) {}
    }

    pw.MemoryImage? origImage;
    if (originalImageBytes != null) {
      try {
        origImage = pw.MemoryImage(originalImageBytes);
      } catch (_) {}
    }

    pdf.addPage(
      pw.MultiPage(
        pageFormat: PdfPageFormat.a4,
        margin: const pw.EdgeInsets.all(32),
        build: (pw.Context context) {
          return [
            // Header
            pw.Row(
              mainAxisAlignment: pw.MainAxisAlignment.spaceBetween,
              crossAxisAlignment: pw.CrossAxisAlignment.start,
              children: [
                pw.Column(
                  crossAxisAlignment: pw.CrossAxisAlignment.start,
                  children: [
                    pw.Text(
                      'TRƯỜNG ĐẠI HỌC CÔNG THƯƠNG TP. HỒ CHÍ MINH',
                      style: pw.TextStyle(
                        fontSize: 10,
                        fontWeight: pw.FontWeight.bold,
                        color: PdfColors.blue900,
                      ),
                    ),
                    pw.Text(
                      'KHOA CÔNG NGHỆ THÔNG TIN - BỘ MÔN AI & THỊ GIÁC MÁY TÍNH',
                      style: const pw.TextStyle(fontSize: 8, color: PdfColors.grey700),
                    ),
                    pw.SizedBox(height: 4),
                    pw.Text(
                      'PHIẾU KẾT QUẢ SÀNG LỌC ĐÁY MẮT (AI ASSISTED)',
                      style: pw.TextStyle(
                        fontSize: 14,
                        fontWeight: pw.FontWeight.bold,
                        color: PdfColors.black,
                      ),
                    ),
                  ],
                ),
                pw.Container(
                  padding: const pw.EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: pw.BoxDecoration(
                    color: PdfColors.grey200,
                    borderRadius: pw.BorderRadius.circular(4),
                  ),
                  child: pw.Text(
                    'RetinaGuard v2.0',
                    style: pw.TextStyle(fontSize: 9, fontWeight: pw.FontWeight.bold),
                  ),
                ),
              ],
            ),
            pw.Divider(thickness: 1.5, color: PdfColors.blue800),
            pw.SizedBox(height: 8),

            // Patient Info Card
            pw.Container(
              padding: const pw.EdgeInsets.all(10),
              decoration: pw.BoxDecoration(
                color: PdfColors.grey100,
                borderRadius: pw.BorderRadius.circular(6),
                border: pw.Border.all(color: PdfColors.grey300),
              ),
              child: pw.Row(
                mainAxisAlignment: pw.MainAxisAlignment.spaceBetween,
                children: [
                  pw.Column(
                    crossAxisAlignment: pw.CrossAxisAlignment.start,
                    children: [
                      pw.Text('Họ và tên: $patientName',
                          style: pw.TextStyle(fontWeight: pw.FontWeight.bold, fontSize: 11)),
                      pw.Text('Mã bệnh nhân: $patientId', style: const pw.TextStyle(fontSize: 10)),
                    ],
                  ),
                  pw.Column(
                    crossAxisAlignment: pw.CrossAxisAlignment.end,
                    children: [
                      pw.Text('Thời gian khám: ${timestamp.toString().substring(0, 16)}',
                          style: const pw.TextStyle(fontSize: 10)),
                      pw.Text(
                        'Độ trễ AI: ${result.processingTimeMs?.toStringAsFixed(0) ?? "N/A"} ms',
                        style: const pw.TextStyle(fontSize: 9, color: PdfColors.grey700),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            pw.SizedBox(height: 12),

            // Section 1: Gate & Safety Check
            pw.Row(
              children: [
                pw.Text('1. KIỂM DUYỆT ẢNH ĐẦU VÀO (MODEL A): ',
                    style: pw.TextStyle(fontWeight: pw.FontWeight.bold, fontSize: 10)),
                pw.Text(
                  result.isFundus
                      ? 'HỢP LỆ (Độ tin cậy: ${(result.fundusConfidence * 100).toStringAsFixed(2)}% >= 96.5%)'
                      : 'BỊ TỪ CHỐI (Ảnh không đạt chuẩn đáy mắt)',
                  style: pw.TextStyle(
                    fontWeight: pw.FontWeight.bold,
                    fontSize: 10,
                    color: result.isFundus ? PdfColors.green800 : PdfColors.red800,
                  ),
                ),
              ],
            ),
            pw.SizedBox(height: 10),

            // Section 2: DR Staging (Model B)
            if (result.drResult != null) ...[
              pw.Text('2. PHÂN ĐỘ BỆNH VÕNG MẠC ĐÁI THÁO ĐƯỜNG (MODEL B - ICDR):',
                  style: pw.TextStyle(fontWeight: pw.FontWeight.bold, fontSize: 10)),
              pw.SizedBox(height: 4),
              pw.Container(
                padding: const pw.EdgeInsets.all(8),
                decoration: pw.BoxDecoration(
                  color: PdfColors.blue50,
                  borderRadius: pw.BorderRadius.circular(6),
                  border: pw.Border.all(color: PdfColors.blue200),
                ),
                child: pw.Column(
                  crossAxisAlignment: pw.CrossAxisAlignment.start,
                  children: [
                    pw.Row(
                      mainAxisAlignment: pw.MainAxisAlignment.spaceBetween,
                      children: [
                        pw.Text(
                          'Cấp độ: ${result.drResult!.stage} - ${result.drResult!.badge}',
                          style: pw.TextStyle(
                            fontSize: 12,
                            fontWeight: pw.FontWeight.bold,
                            color: result.drResult!.stage >= 3
                                ? PdfColors.red800
                                : PdfColors.blue900,
                          ),
                        ),
                        pw.Text(
                          'Độ tin cậy: ${(result.drResult!.confidence * 100).toStringAsFixed(1)}%',
                          style: pw.TextStyle(fontWeight: pw.FontWeight.bold, fontSize: 10),
                        ),
                      ],
                    ),
                    pw.SizedBox(height: 4),
                    pw.Text('Mô tả tổn thương: ${result.drResult!.description}',
                        style: const pw.TextStyle(fontSize: 9)),
                    pw.SizedBox(height: 3),
                    pw.Text('Khuyến nghị theo dõi: ${result.drResult!.advice}',
                        style: pw.TextStyle(
                            fontSize: 9, fontStyle: pw.FontStyle.italic, color: PdfColors.grey800)),
                  ],
                ),
              ),
              pw.SizedBox(height: 10),
            ],

            // Section 3: Dual Image & Heatmap
            if (origImage != null || vitHeatmapImage != null) ...[
              pw.Text('3. ĐỐI SOÁT HÌNH ẢNH LÂM SÀNG & BẢN ĐỒ NHIỆT XAI:',
                  style: pw.TextStyle(fontWeight: pw.FontWeight.bold, fontSize: 10)),
              pw.SizedBox(height: 6),
              pw.Row(
                mainAxisAlignment: pw.MainAxisAlignment.spaceEvenly,
                children: [
                  if (origImage != null)
                    pw.Column(
                      children: [
                        pw.Container(
                          width: 140,
                          height: 140,
                          decoration: pw.BoxDecoration(
                            border: pw.Border.all(color: PdfColors.grey400),
                            borderRadius: pw.BorderRadius.circular(4),
                          ),
                          child: pw.ClipRRect(
                            horizontalRadius: 4,
                            verticalRadius: 4,
                            child: pw.Image(origImage, fit: pw.BoxFit.cover),
                          ),
                        ),
                        pw.SizedBox(height: 4),
                        pw.Text('Ảnh đáy mắt gốc', style: const pw.TextStyle(fontSize: 8)),
                      ],
                    ),
                  if (vitHeatmapImage != null)
                    pw.Column(
                      children: [
                        pw.Container(
                          width: 140,
                          height: 140,
                          decoration: pw.BoxDecoration(
                            border: pw.Border.all(color: PdfColors.grey400),
                            borderRadius: pw.BorderRadius.circular(4),
                          ),
                          child: pw.ClipRRect(
                            horizontalRadius: 4,
                            verticalRadius: 4,
                            child: pw.Image(vitHeatmapImage, fit: pw.BoxFit.cover),
                          ),
                        ),
                        pw.SizedBox(height: 4),
                        pw.Text('Bản đồ nhiệt Grad-CAM (ensemble)',
                            style: const pw.TextStyle(fontSize: 8)),
                      ],
                    ),
                ],
              ),
              pw.SizedBox(height: 10),
            ],

            if (result.drResult != null) ...[
              pw.Text('4. XÁC SUẤT 6 LỚP CỦA ENSEMBLE:',
                  style: pw.TextStyle(fontWeight: pw.FontWeight.bold, fontSize: 10)),
              pw.SizedBox(height: 4),
              pw.TableHelper.fromTextArray(
                headers: ['Lớp', 'Xác suất'],
                headerStyle: pw.TextStyle(fontWeight: pw.FontWeight.bold, fontSize: 8),
                headerDecoration: const pw.BoxDecoration(color: PdfColors.grey300),
                cellStyle: const pw.TextStyle(fontSize: 8),
                cellHeight: 16,
                data: result.drResult!.probabilities.entries.map((entry) {
                  return [entry.key, '${(entry.value * 100).toStringAsFixed(1)}%'];
                }).toList(),
              ),
              pw.SizedBox(height: 6),
              pw.Text(result.drResult!.benchmarkNote, style: const pw.TextStyle(fontSize: 8)),
              pw.SizedBox(height: 10),
            ],

            // Clinical Disclaimer Footer
            pw.Container(
              padding: const pw.EdgeInsets.all(6),
              decoration: pw.BoxDecoration(
                color: PdfColors.yellow50,
                border: pw.Border.all(color: PdfColors.amber300),
                borderRadius: pw.BorderRadius.circular(4),
              ),
              child: pw.Text(
                ClinicalConstants.clinicalDisclaimer,
                style: const pw.TextStyle(fontSize: 7, color: PdfColors.grey800),
              ),
            ),
          ];
        },
      ),
    );

    // Mở bảng chia sẻ hoặc in ấn trực tiếp
    await Printing.layoutPdf(
      onLayout: (PdfPageFormat format) async => pdf.save(),
      name: 'Phieu_Sang_Loc_RetinaGuard_${patientId}.pdf',
    );
  }
}
