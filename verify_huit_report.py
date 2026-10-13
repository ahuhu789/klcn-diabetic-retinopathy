# -*- coding: utf-8 -*-
"""
KỊCH BẢN THẨM ĐỊNH TỰ ĐỘNG CHẤT LƯỢNG VĂN BẢN DOCX BÁO CÁO TIẾN ĐỘ TUẦN
Kiểm tra tính toàn vẹn: Quy chuẩn HUIT (lề, font, bảng), yêu cầu R1, R2, R3, R4 và tính nhất quán dữ liệu.
"""

import os
import sys
import zipfile
import docx
from docx.shared import Cm

if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

DOCX_PATH = r"c:\Users\thanh\Desktop\klcn\Bao_Cao_Tien_Do_Tuan_KLCN_28-09_den_05-10.docx"

def run_verification():
    print("=" * 70)
    print("BẮT ĐẦU THẨM ĐỊNH TOÀN DIỆN TỆP BÁO CÁO DOCX")
    print("=" * 70)

    # 1. Kiểm tra tồn tại và kích thước tệp
    assert os.path.exists(DOCX_PATH), f"LỖI: Tệp không tồn tại tại {DOCX_PATH}"
    file_size_kb = os.path.getsize(DOCX_PATH) / 1024
    print(f"[TEST 1] Tồn tại tệp: HỢP LỆ ({DOCX_PATH})")
    print(f"[TEST 1] Kích thước tệp: {file_size_kb:.2f} KB (Yêu cầu > 40 KB)")
    assert file_size_kb > 40, "LỖI: Kích thước tệp quá nhỏ (< 40 KB)"

    # Kiểm tra tính hợp lệ của tệp ZIP OpenXML
    assert zipfile.is_zipfile(DOCX_PATH), "LỖI: Tệp không phải là tệp zip hợp lệ của Word OpenXML"
    print("[TEST 1] Cấu trúc OpenXML ZIP: HỢP LỆ")

    # Mở tài liệu bằng python-docx
    doc = docx.Document(DOCX_PATH)

    # 2. Kiểm tra căn lề và kích thước trang chuẩn A4 HUIT
    section = doc.sections[0]
    top_cm = round(section.top_margin.cm, 2)
    bottom_cm = round(section.bottom_margin.cm, 2)
    left_cm = round(section.left_margin.cm, 2)
    right_cm = round(section.right_margin.cm, 2)
    width_cm = round(section.page_width.cm, 2)
    height_cm = round(section.page_height.cm, 2)

    print(f"[TEST 2] Kích thước và căn lề trang:")
    print(f"         - Khổ giấy: {width_cm} x {height_cm} cm (Chuẩn A4: 21.0 x 29.7 cm)")
    print(f"         - Lề trên: {top_cm} cm (Chuẩn: 2.5 cm)")
    print(f"         - Lề dưới: {bottom_cm} cm (Chuẩn: 2.5 cm)")
    print(f"         - Lề trái (Gáy sách): {left_cm} cm (Chuẩn: 3.5 cm)")
    print(f"         - Lề phải: {right_cm} cm (Chuẩn: 2.5 cm)")

    assert abs(width_cm - 21.0) < 0.1, f"Khổ giấy không phải A4 (rộng): {width_cm}"
    assert abs(height_cm - 29.7) < 0.1, f"Khổ giấy không phải A4 (cao): {height_cm}"
    assert abs(top_cm - 2.5) < 0.05, f"Lề trên không chuẩn: {top_cm}"
    assert abs(bottom_cm - 2.5) < 0.05, f"Lề dưới không chuẩn: {bottom_cm}"
    assert abs(left_cm - 3.5) < 0.05, f"Lề trái không chuẩn: {left_cm}"
    assert abs(right_cm - 2.5) < 0.05, f"Lề phải không chuẩn: {right_cm}"
    print("         -> CĂN LỀ & KHỔ GIẤY A4 CHUẨN KHOA CNTT - HUIT: ĐẠT")

    # 3. Kiểm tra số lượng đoạn văn và font chữ
    num_paras = len(doc.paragraphs)
    num_tables = len(doc.tables)
    print(f"[TEST 3] Cấu trúc nội dung:")
    print(f"         - Tổng số đoạn văn (Paragraphs): {num_paras}")
    print(f"         - Tổng số bảng biểu (Tables): {num_tables}")
    assert num_paras >= 50, "Số lượng đoạn văn quá ít"
    assert num_tables >= 5, "Số lượng bảng biểu quá ít"

    # Kiểm tra font chữ Times New Roman trên các runs
    tnr_count = 0
    other_font_count = 0
    for p in doc.paragraphs:
        for r in p.runs:
            if r.font.name:
                if "Times New Roman" in r.font.name:
                    tnr_count += 1
                else:
                    other_font_count += 1

    for tbl in doc.tables:
        for row in tbl.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    for r in p.runs:
                        if r.font.name:
                            if "Times New Roman" in r.font.name:
                                tnr_count += 1
                            else:
                                other_font_count += 1

    print(f"         - Số lượng Run dùng Times New Roman: {tnr_count}")
    print(f"         - Số lượng Run dùng font khác: {other_font_count}")
    assert other_font_count == 0, f"Phát hiện font chữ khác Times New Roman: {other_font_count}"
    normal_font_name = doc.styles['Normal'].font.name
    print(f"         - Font mặc định Style 'Normal': {normal_font_name}")
    assert normal_font_name == "Times New Roman", f"Font Style Normal không phải Times New Roman: {normal_font_name}"
    print("         -> TYPOGRAPHY TIMES NEW ROMAN: ĐẠT")

    # 4. Kiểm tra cấu trúc OOXML của Bảng biểu (tblHeader, cantSplit, tcMar, shd, tcBorders, tblGrid, không duplicate tcW)
    print("[TEST 4] Kiểm định cấu trúc bảng biểu chuyên nghiệp OOXML:")
    import xml.etree.ElementTree as ET
    with zipfile.ZipFile(DOCX_PATH, "r") as z:
        dom = ET.fromstring(z.read("word/document.xml"))
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

    # Kiểm tra không có duplicate w:tcW
    all_tc = dom.findall(".//w:tc", ns)
    dup_tcw = sum(1 for c in all_tc if len(c.findall("w:tcPr/w:tcW", ns)) > 1)
    print(f"         - Kiểm tra duplicate w:tcW: {dup_tcw} ô trùng / {len(all_tc)} ô (Yêu cầu: 0)")
    assert dup_tcw == 0, f"Phát hiện {dup_tcw} ô bị duplicate thẻ w:tcW!"

    for idx, tbl in enumerate(doc.tables):
        xml_str = tbl._tbl.xml
        has_cant_split = "w:cantSplit" in xml_str
        has_shd = "w:shd" in xml_str
        has_tcmar = "w:tcMar" in xml_str
        has_borders = "w:tcBorders" in xml_str

        # Kiểm tra tblGrid đồng bộ với cell widths
        dom_tbl = dom.findall(".//w:tbl", ns)[idx]
        grid_cols = [int(gc.attrib[W + "w"]) for gc in dom_tbl.findall("w:tblGrid/w:gridCol", ns)]
        first_row_tcw = [int(c.find("w:tcPr/w:tcW", ns).attrib[W + "w"]) for c in dom_tbl.findall("w:tr", ns)[0].findall("w:tc", ns)]
        assert grid_cols == first_row_tcw, f"Bảng {idx+1} bị lệch tblGrid và cell tcW: {grid_cols} vs {first_row_tcw}"

        print(f"         - Bảng {idx+1} ({len(tbl.rows)} hàng x {len(tbl.columns)} cột): "
              f"cantSplit={has_cant_split}, shd={has_shd}, tcMar={has_tcmar}, tcBorders={has_borders}, "
              f"tblGrid_synced=True (sum={sum(grid_cols)} dxa)")
        assert has_cant_split, f"Bảng {idx+1} thiếu thuộc tính w:cantSplit"
        assert has_shd, f"Bảng {idx+1} thiếu thuộc tính w:shd"
        assert has_tcmar, f"Bảng {idx+1} thiếu thuộc tính w:tcMar"
        assert has_borders, f"Bảng {idx+1} thiếu thuộc tính w:tcBorders"
    print("         -> CẤU TRÚC OOXML BẢNG BIỂU & ĐỒNG BỘ tblGrid: ĐẠT")

    # 5. Kiểm tra nội dung bắt buộc: R1, R2, R3, R4
    full_text = []
    for p in doc.paragraphs:
        full_text.append(p.text)
    for tbl in doc.tables:
        for row in tbl.rows:
            for cell in row.cells:
                full_text.append(cell.text)
    full_text_str = "\n".join(full_text)

    print("[TEST 5] Kiểm định nội dung và tính toàn vẹn số liệu:")
    
    # R1: Đối sánh định lượng với các nghiên cứu mốc trên EyePACS
    r1_keywords = [
        "Ben Graham", "0.8490", "SparseConvNet",
        "Gulshan", "0.991", "Inception-v3", "Referable",
        "Pratt", "0.5120", "0.3850", "75.0%", "30.0%",
        "Vo & Verma", "0.6380", "0.4210", "76.5%",
        "He et al.", "CABNet", "0.6920",
        "ResNet-50", "0.7072", "0.5094", "78.4%",
        "ViT-B/16", "0.7215", "0.5284", "80.6%",
        "Hội chẩn Lai", "0.7350", "0.5420", "82.4%",
        "Fundus Gate", "99.94%", "100.0%"
    ]
    for kw in r1_keywords:
        assert kw in full_text_str, f"R1 thiếu từ khóa/chỉ số: {kw}"
    print("         -> R1 (Benchmark Matrix & 10 Models trên EyePACS): ĐẠT")

    # R2: Luận giải ưu điểm vượt trội
    r2_keywords = [
        "Smoothed Weighted Cross-Entropy Loss", "0.5094", "0.5420",
        "Explainable AI", "Grad-CAM", "Transformer Attribution",
        "Fundus Gate", "100.0%", "99.87%", "0.11%",
        "FastAPI", "React", "Cloudflare"
    ]
    for kw in r2_keywords:
        assert kw in full_text_str, f"R2 thiếu từ khóa/chỉ số: {kw}"
    print("         -> R2 (Smoothed Loss, XAI kép, Fundus Gate, Full-stack Web): ĐẠT")

    # R3: Phân tích khách quan các mặt hạn chế
    r3_keywords = [
        "Ben Graham", "0.8490", "Dual", "Tesla T4", "10 epochs",
        "Độ 0", "Độ 1", "vi phình mạch", "microaneurysms",
        "Vision Transformer", "343", "CPU", "520",
        "Messidor-2", "APTOS 2019"
    ]
    for kw in r3_keywords:
        assert kw in full_text_str, f"R3 thiếu từ khóa/chỉ số: {kw}"
    print("         -> R3 (Hạn chế QWK, Độ 0 vs 1, ViT latency, External validation): ĐẠT")

    # R4: Chuẩn quy cách Khoa CNTT - HUIT và chữ ký
    r4_keywords = [
        "BỘ CÔNG THƯƠNG",
        "TRƯỜNG ĐẠI HỌC CÔNG THƯƠNG TP. HỒ CHÍ MINH",
        "KHOA CÔNG NGHỆ THÔNG TIN",
        "ThS. Trần Đình Toàn",
        "Nguyễn Huy Thanh",
        "Nguyễn Cao Tấn Phúc",
        "Nguyễn Chí Thành",
        "XÁC NHẬN CỦA GIẢNG VIÊN HƯỚNG DẪN",
        "ĐẠI DIỆN NHÓM SINH VIÊN THỰC HIỆN"
    ]
    for kw in r4_keywords:
        assert kw in full_text_str, f"R4 thiếu từ khóa quy cách/chữ ký: {kw}"
    print("         -> R4 (Chuẩn quy cách HUIT, Tiêu ngữ, Bảng thông tin, Chữ ký GVHD/SV): ĐẠT")

    print("=" * 70)
    print("✅ TẤT CẢ 5 BÀI KIỂM THỬ THẨM ĐỊNH ĐỀU ĐẠT 100%! VĂN BẢN HOÀN TOÀN HỢP LỆ VÀ CHÍNH XÁC.")
    print("=" * 70)

if __name__ == "__main__":
    run_verification()
