# -*- coding: utf-8 -*-
"""
KỊCH BẢN TỰ ĐỘNG HÓA SINH BÁO CÁO TIẾN ĐỘ TUẦN KHÓA LUẬN TỐT NGHIỆP (HUIT)
Đề tài: Nghiên cứu Vision Transformer và ứng dụng phân loại mức độ bệnh võng mạc đái tháo đường từ ảnh đáy võng mạc mắt
Đơn vị: Khoa Công nghệ Thông tin - Trường Đại học Công Thương TP. Hồ Chí Minh (HUIT)
Giảng viên hướng dẫn: ThS. Trần Đình Toàn
Sinh viên thực hiện:
  1. Nguyễn Huy Thanh (MSSV: 2001230885 - Lớp: 14DHTH01)
  2. Nguyễn Cao Tấn Phúc (MSSV: 2001230680 - Lớp: 14DHTH03)
  3. Nguyễn Chí Thành (MSSV: 2001230898 - Lớp: 14DHTH01)
Thời gian báo cáo: Tuần 06 (06/10/2026 - 13/10/2026)
Chuyên đề: NGHIÊN CỨU & TRIỂN KHAI MÔ HÌNH C (SÀNG LỌC ĐA NHÃN BỆNH LÝ VÕNG MẠC RFMiD & ODIR-5K),
          HOÀN THIỆN HỆ THỐNG TRÍ TUỆ NHÂN TẠO ĐA NHIỆM (MODELS A + B + C) VÀ TÍCH HỢP ỨNG DỤNG DI ĐỘNG NATIVE NỀN TẢNG FLUTTER
"""

import os
import sys
import docx
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

OUTPUT_DOCX = r"c:\Users\thanh\Desktop\klcn\Bao_Cao_Tien_Do_Tuan_KLCN_06-10_den_13-10.docx"

# ==============================================================================
# 1. HỆ THỐNG MÃ MÀU VÀ ĐỊNH NGHĨA PHONG CÁCH HÀN LÂM HUIT
# ==============================================================================
COLOR_PRIMARY = RGBColor(16, 44, 87)       # Deep Navy (#102C57)
COLOR_SECONDARY = RGBColor(37, 99, 235)    # Royal Blue (#2563EB)
COLOR_TEXT = RGBColor(30, 41, 59)          # Dark Slate (#1E293B)
COLOR_MUTED = RGBColor(100, 116, 139)      # Muted Slate (#64748B)

HEX_PRIMARY = "102C57"
HEX_LIGHT_BG = "F1F5F9"
HEX_ALT_ROW = "F8FAFC"
HEX_BORDER = "CBD5E1"
HEX_HIGHLIGHT = "EFF6FF"
HEX_WHITE = "FFFFFF"

# ==============================================================================
# 2. CÁC HÀM TIỆN ÍCH CAN THIỆP CẤU TRÚC OOXML CHO BẢNG BIỂU
# ==============================================================================
def set_cell_shading(cell, color_hex):
    """Tô màu nền hex cho ô"""
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shd)

def set_cell_borders(cell, top=HEX_BORDER, bottom=HEX_BORDER, left=HEX_BORDER, right=HEX_BORDER, sz="4", val="single"):
    """Thiết lập đường viền mỏng thanh lịch cho ô"""
    tcPr = cell._tc.get_or_add_tcPr()
    top_val = "none" if top == "none" else val
    bottom_val = "none" if bottom == "none" else val
    left_val = "none" if left == "none" else val
    right_val = "none" if right == "none" else val
    
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="{top_val}" w:sz="{sz}" w:space="0" w:color="{top if top != "none" else "auto"}"/>'
        f'<w:bottom w:val="{bottom_val}" w:sz="{sz}" w:space="0" w:color="{bottom if bottom != "none" else "auto"}"/>'
        f'<w:left w:val="{left_val}" w:sz="{sz}" w:space="0" w:color="{left if left != "none" else "auto"}"/>'
        f'<w:right w:val="{right_val}" w:sz="{sz}" w:space="0" w:color="{right if right != "none" else "auto"}"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)

def set_cell_margins(cell, top=100, bottom=100, left=120, right=120):
    """Thiết lập đệm lề ô (Cell padding dxa: 1pt = 20 dxa)"""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def prevent_row_split(table):
    """Cấu hình chống gãy dòng qua trang và tự động lặp tiêu đề bảng"""
    header_tr = table.rows[0]._tr.get_or_add_trPr()
    header_tr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
    for row in table.rows:
        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

def set_table_col_widths(table, col_widths):
    """Gán độ rộng cột tuyệt đối cho bảng, đồng bộ tblGrid và tránh duplicate tcW (đơn vị cm)"""
    tblGrid = table._tbl.tblGrid
    if tblGrid is None:
        tblGrid = parse_xml(f'<w:tblGrid {nsdecls("w")}/>')
        table._tbl.append(tblGrid)
    tblGrid.clear()
    for w in col_widths:
        dxa_w = Cm(w).twips
        gridCol = parse_xml(f'<w:gridCol {nsdecls("w")} w:w="{dxa_w}"/>')
        tblGrid.append(gridCol)

    for row in table.rows:
        for c_idx, w in enumerate(col_widths):
            if c_idx < len(row.cells):
                cell = row.cells[c_idx]
                cell.width = Cm(w)

# ==============================================================================
# 3. CÁC HÀM XÂY DỰNG TYPOGRAPHY CHUẨN KHOA CNTT - HUIT
# ==============================================================================
def add_heading(doc, text, level=1):
    p = doc.add_paragraph()
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.bold = True
    if level == 1:
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(6)
        run.font.size = Pt(13.5)
        run.font.color.rgb = COLOR_PRIMARY
    elif level == 2:
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        run.font.size = Pt(12.5)
        run.font.color.rgb = COLOR_SECONDARY
    elif level == 3:
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        run.font.size = Pt(12)
        run.font.color.rgb = COLOR_TEXT
    return p

def add_body_p(doc, text, bold_prefix="", italic=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    p.paragraph_format.line_spacing = 1.2
    
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = "Times New Roman"
        r_pre.font.size = Pt(12)
        r_pre.bold = True
        r_pre.font.color.rgb = COLOR_TEXT
        
    r_body = p.add_run(text)
    r_body.font.name = "Times New Roman"
    r_body.font.size = Pt(12)
    r_body.italic = italic
    r_body.font.color.rgb = COLOR_TEXT
    return p

def add_bullet(doc, text, bold_prefix=""):
    p = doc.add_paragraph(style='List Bullet')
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    p.paragraph_format.line_spacing = 1.15
    
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = "Times New Roman"
        r_pre.font.size = Pt(12)
        r_pre.bold = True
        r_pre.font.color.rgb = COLOR_TEXT
        
    r_body = p.add_run(text)
    r_body.font.name = "Times New Roman"
    r_body.font.size = Pt(12)
    r_body.font.color.rgb = COLOR_TEXT
    return p

def add_caption(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(10)
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(10)
    run.italic = True
    run.bold = True
    run.font.color.rgb = COLOR_TEXT
    return p

def add_callout_box(doc, text, bold_title=""):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.rows[0].cells[0]
    cell.width = Cm(15.0)
    
    set_cell_shading(cell, HEX_HIGHLIGHT)
    set_cell_borders(cell, top="none", bottom="none", left=HEX_PRIMARY, right="none", sz="24")
    set_cell_margins(cell, top=120, bottom=120, left=180, right=140)
    
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    
    if bold_title:
        r_title = p.add_run(bold_title + "\n")
        r_title.font.name = "Times New Roman"
        r_title.font.size = Pt(11)
        r_title.bold = True
        r_title.font.color.rgb = COLOR_PRIMARY
        
    r_txt = p.add_run(text)
    r_txt.font.name = "Times New Roman"
    r_txt.font.size = Pt(10.5)
    r_txt.italic = True
    r_txt.font.color.rgb = COLOR_TEXT
    
    prevent_row_split(tbl)
    set_table_col_widths(tbl, [15.0])
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

# ==============================================================================
# 4. CHƯƠNG TRÌNH CHÍNH XÂY DỰNG TOÀN VẸN TÀI LIỆU
# ==============================================================================
def generate_report():
    print(">>> Khởi tạo tài liệu Word mới...")
    doc = docx.Document()
    doc.styles['Normal'].font.name = "Times New Roman"

    # Cấu hình A4 chuẩn HUIT: lề trái 3.5cm (đóng gáy), phải 2.5cm, trên 2.5cm, dưới 2.5cm
    for s in doc.sections:
        s.page_width = Cm(21.0)
        s.page_height = Cm(29.7)
        s.top_margin = Cm(2.5)
        s.bottom_margin = Cm(2.5)
        s.left_margin = Cm(3.5)
        s.right_margin = Cm(2.5)

    print(">>> 1. Xây dựng Khung Bìa tiêu đề & Tiêu ngữ chính quy...")
    p_hdr1 = doc.add_paragraph()
    p_hdr1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_hdr1.paragraph_format.space_before = Pt(0)
    p_hdr1.paragraph_format.space_after = Pt(1)
    r1 = p_hdr1.add_run("BỘ CÔNG THƯƠNG\nTRƯỜNG ĐẠI HỌC CÔNG THƯƠNG TP. HỒ CHÍ MINH\nKHOA CÔNG NGHỆ THÔNG TIN")
    r1.font.name = "Times New Roman"
    r1.font.size = Pt(11)
    r1.bold = True
    r1.font.color.rgb = COLOR_PRIMARY

    p_star = doc.add_paragraph()
    p_star.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_star.paragraph_format.space_before = Pt(2)
    p_star.paragraph_format.space_after = Pt(10)
    r_star = p_star.add_run("-----  -----")
    r_star.font.name = "Times New Roman"
    r_star.font.size = Pt(11)
    r_star.bold = True

    p_main_title = doc.add_paragraph()
    p_main_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_main_title.paragraph_format.space_before = Pt(8)
    p_main_title.paragraph_format.space_after = Pt(4)
    r_mt = p_main_title.add_run("BÁO CÁO TIẾN ĐỘ THỰC HIỆN ĐỀ TÀI KHÓA LUẬN TỐT NGHIỆP")
    r_mt.font.name = "Times New Roman"
    r_mt.font.size = Pt(15)
    r_mt.bold = True
    r_mt.font.color.rgb = COLOR_PRIMARY

    p_sub_title = doc.add_paragraph()
    p_sub_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub_title.paragraph_format.space_before = Pt(2)
    p_sub_title.paragraph_format.space_after = Pt(12)
    r_st = p_sub_title.add_run(
        "TUẦN THỰC HIỆN: 06/10/2026 – 13/10/2026\n"
        "CHUYÊN ĐỀ: NGHIÊN CỨU & TRIỂN KHAI MÔ HÌNH C (SÀNG LỌC ĐA NHÃN BỆNH LÝ VÕNG MẠC RFMiD & ODIR-5K), "
        "HOÀN THIỆN HỆ THỐNG TRÍ TUỆ NHÂN TẠO ĐA NHIỆM (MODELS A + B + C) VÀ TÍCH HỢP ỨNG DỤNG DI ĐỘNG NATIVE NỀN TẢNG FLUTTER"
    )
    r_st.font.name = "Times New Roman"
    r_st.font.size = Pt(12)
    r_st.bold = True
    r_st.font.color.rgb = COLOR_SECONDARY

    print(">>> 2. Xây dựng Bảng thông tin đề tài & sinh viên (Metadata)...")
    tbl_meta = doc.add_table(rows=5, cols=2)
    tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Tên đề tài:", "Nghiên cứu Vision Transformer và ứng dụng phân loại mức độ bệnh võng mạc đái tháo đường từ ảnh đáy võng mạc mắt"),
        ("Ngành đào tạo:", "Công nghệ Thông tin (Khoa Công nghệ Thông tin - Trường Đại học Công Thương TP.HCM)"),
        ("Giảng viên hướng dẫn:", "ThS. Trần Đình Toàn"),
        ("Sinh viên thực hiện:", "1. Nguyễn Huy Thanh (MSSV: 2001230885 - Lớp: 14DHTH01)\n2. Nguyễn Cao Tấn Phúc (MSSV: 2001230680 - Lớp: 14DHTH03)\n3. Nguyễn Chí Thành (MSSV: 2001230898 - Lớp: 14DHTH01)"),
        ("Giai đoạn thực hiện:", "Giai đoạn Đóng gói sản phẩm (Product Finalization) & Kiểm thử thực địa (Mobile & Web Integration)")
    ]
    for row_idx, (label, val) in enumerate(meta_data):
        row = tbl_meta.rows[row_idx]
        c0, c1 = row.cells[0], row.cells[1]
        
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_before = Pt(2)
        p0.paragraph_format.space_after = Pt(2)
        r0 = p0.add_run(label)
        r0.font.name = "Times New Roman"
        r0.font.size = Pt(11)
        r0.bold = True
        r0.font.color.rgb = COLOR_PRIMARY
        
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_before = Pt(2)
        p1.paragraph_format.space_after = Pt(2)
        r1 = p1.add_run(val)
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(11)
        r1.font.color.rgb = COLOR_TEXT
        
        bg_col = HEX_LIGHT_BG if row_idx % 2 == 0 else HEX_WHITE
        set_cell_shading(c0, bg_col)
        set_cell_shading(c1, bg_col)
        set_cell_borders(c0)
        set_cell_borders(c1)
        set_cell_margins(c0, top=80, bottom=80, left=120, right=100)
        set_cell_margins(c1, top=80, bottom=80, left=120, right=100)
        
    prevent_row_split(tbl_meta)
    set_table_col_widths(tbl_meta, [4.2, 10.8])
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # --------------------------------------------------------------------------
    # MỤC 1. MỤC TIÊU VÀ NHIỆM VỤ ĐẶT RA TRONG TUẦN
    # --------------------------------------------------------------------------
    print(">>> 3. Soạn thảo Mục 1: Mục tiêu và nhiệm vụ đặt ra trong tuần...")
    add_heading(doc, "1. MỤC TIÊU VÀ NHIỆM VỤ ĐẶT RA TRONG TUẦN (06/10/2026 – 13/10/2026)", level=1)
    
    add_body_p(doc, 
        "Tiếp nối các thắng lợi học thuật của các tuần trước (huấn luyện thành công Cổng an toàn Fundus Gate đạt Recall 100% "
        "và thiết lập kỷ lục Quadratic Weighted Kappa QWK 0.7428 trên tập EyePACS với mô hình thứ bậc lai ResNet-50 kết hợp ViT-B/16), "
        "trong tuần từ 06/10/2026 đến 13/10/2026, nhóm nghiên cứu chuyển trọng tâm chiến lược sang giai đoạn HOÀN THIỆN SẢN PHẨM (PRODUCT FINALIZATION) "
        "và MỞ RỘNG NĂNG LỰC SÀNG LỌC ĐA BỆNH LÝ TOÀN DIỆN. Dưới sự định hướng chuyên môn sâu sắc của Giảng viên hướng dẫn ThS. Trần Đình Toàn, "
        "nhóm đã đặt ra và hoàn thành xuất sắc 5 nhiệm vụ trọng tâm sau:")

    add_bullet(doc, 
        "Nghiên cứu, kiểm định dữ liệu và giải quyết bài toán khoa học cốt lõi của Mô hình C (Model C) – Phân loại đa nhãn bệnh lý đáy mắt "
        "(Multi-label Retinal Disease Classification) từ một ảnh chụp đáy mắt màu (Single-image RGB) duy nhất kết hợp hai nguồn dữ liệu quốc tế "
        "RFMiD (Nature Scientific Data) và ODIR-5K (Peking University).",
        bold_prefix="Mục tiêu 1 (Nghiên cứu & Thực nghiệm Model C): ")

    add_bullet(doc, 
        "Triển khai thuật toán 'Điều hòa nhãn ngữ nghĩa' (Semantic Label Harmonization), giải quyết triệt để rào cản bất đối xứng bệnh lý 2 mắt "
        "(phát hiện 44.7% bệnh nhân có bệnh lý 2 mắt khác nhau và 23.4% có 1 mắt bình thường đi kèm 1 mắt bệnh lý trong ODIR-5K), "
        "ngăn chặn triệt để nguy cơ đưa 452 nhãn dương tính giả DR vào huấn luyện; thiết lập biểu diễn nhãn 3 trạng thái {+1, 0, -1} "
        "và hàm mất mát có mặt nạ che Masked BCEWithLogitsLoss.",
        bold_prefix="Mục tiêu 2 (Điều hòa nhãn & Hàm mất mát Masked Loss): ")

    add_bullet(doc, 
        "Thực hiện đối chuẩn thực nghiệm định lượng qua 3 cấu hình: E1 (RFMiD Baseline), E2 (Harmonized Masked Loss - mô hình chính), "
        "và E3 (Ablation Study sao chép ngây thơ mức bệnh nhân) trên kiến trúc mạng EfficientNet-B0; đánh giá độc lập trên tập kiểm thử "
        "chuẩn RFMiD Test (N=640 ảnh, 6,400 lượt quyết định) để lựa chọn checkpoint tối ưu nhất đưa vào sản phẩm.",
        bold_prefix="Mục tiêu 3 (Thực nghiệm định lượng & Đánh giá Model C): ")

    add_bullet(doc, 
        "Hoàn thiện kiến trúc đường ống tích hợp 3 mô hình AI độc lập (Pipeline Models A + B + C): Model A (MobileNetV3 Fundus Gate, threshold 0.965) "
        "kiểm định hợp lệ ảnh; nếu hợp lệ, chạy song song Model B (Phân loại thứ bậc 5 cấp độ DR kèm bản đồ nhiệt Grad-CAM) và Model C "
        "(Sàng lọc đa nhãn bệnh lý đáy mắt); chuẩn hóa Backend FastAPI RESTful Services và duy trì đường hầm Cloudflare Tunnel công khai.",
        bold_prefix="Mục tiêu 4 (Đóng gói Backend & Pipeline Tích hợp 3 Mô hình): ")

    add_bullet(doc, 
        "Nghiên cứu, thiết kế và phát triển toàn diện ứng dụng di động native RetinaGuard AI Mobile trên nền tảng Flutter SDK (Dart), "
        "hỗ trợ chụp ảnh từ camera kính soi đáy mắt cầm tay, carousel ảnh bệnh mẫu lâm sàng, chuyển đổi linh hoạt LAN/Cloudflare URL, "
        "giao diện Dashboard y tế đa mô hình, bản đồ nhiệt XAI, xuất báo cáo PDF và lưu lịch sử ngoại tuyến; tự động thiết lập bộ công cụ build trên PC, "
        "khắc phục xung đột AGP 8 Manifest, biên dịch thành công APK native và gỡ lỗi không dây 100% qua Wireless ADB trên thiết bị thật Redmi 13 (Android 15).",
        bold_prefix="Mục tiêu 5 (Phát triển & Triển khai Ứng dụng Di động Flutter Native): ")

    # --------------------------------------------------------------------------
    # MỤC 2. NGHIÊN CỨU & THỰC HIỆN CHI TIẾT MÔ HÌNH C (MODEL C)
    # --------------------------------------------------------------------------
    print(">>> 4. Soạn thảo Mục 2: Nghiên cứu & Thực hiện chi tiết Mô hình C...")
    add_heading(doc, "2. NGHIÊN CỨU & THỰC HIỆN CHI TIẾT MÔ HÌNH C (SÀNG LỌC ĐA NHÃN BỆNH LÝ VÕNG MẠC)", level=1)

    add_heading(doc, "2.1. Đặt vấn đề và tính cần thiết lâm sàng của Mô hình C", level=2)
    add_body_p(doc, 
        "Trong quy trình tầm soát nhãn khoa thực tế tại các bệnh viện mắt và trung tâm y tế dự phòng, bệnh nhân tiểu đường hoặc người cao tuổi "
        "khi được chỉ định chụp đáy mắt thường không chỉ có nguy cơ mắc bệnh võng mạc đái tháo đường (Diabetic Retinopathy - DR) "
        "mà còn có tỷ lệ rất cao đồng mắc các bệnh lý thoái hóa và mạch máu võng mạc nguy hiểm khác. Cụ thể:")

    add_bullet(doc, "Thoái hóa hoàng điểm tuổi già (Age-related Macular Degeneration - ARMD/AMD): Nguyên nhân hàng đầu gây mù lòa không hồi phục ở người trên 50 tuổi tại các quốc gia phát triển và đang phát triển.", bold_prefix="1. Nhóm thoái hóa hoàng điểm: ")
    add_bullet(doc, "Tắc tĩnh mạch võng mạc (Branch/Central Retinal Vein Occlusion - BRVO/CRVO): Tai biến mạch máu võng mạc cấp tính dẫn đến thiếu máu cục bộ, xuất huyết diện rộng và phù hoàng điểm nặng.", bold_prefix="2. Nhóm bệnh mạch máu võng mạc: ")
    add_bullet(doc, "Lõm gai thị nghi ngờ Glôcôm (Optic Disc Cupping / Glaucoma - ODC/GL): 'Kẻ trộm thị lực thầm lặng' do tăng nhãn áp làm teo lõm đầu dây thần kinh thị giác.", bold_prefix="3. Nhóm bệnh thần kinh thị giác: ")
    add_bullet(doc, "Màng trước võng mạc (Epiretinal Membrane - ERM), Cận thị thoái hóa (Pathological Myopia - PM), Lắng đọng Drusen (DN), và Sẹo bỏng laser võng mạc sau quang đông (Laser Scars - LS).", bold_prefix="4. Nhóm tổn thương phối hợp: ")

    add_body_p(doc, 
        "Nếu hệ thống AI chỉ trang bị duy nhất Model B (phân loại cấp độ DR), khi một bệnh nhân có đáy mắt hoàn toàn không có dấu hiệu DR "
        "(Model B trả về Grade 0: Normal) nhưng lại đang có khối thoái hóa hoàng điểm thể ướt hoặc lõm gai Glôcôm tiến triển, "
        "hệ thống sẽ tạo ra kết luận 'Bình thường' sai lầm nghiêm trọng (False Reassurance), tước đi cơ hội can thiệp kịp thời của người bệnh. "
        "Do đó, sự ra đời của Mô hình C (Model C) với chức năng SÀNG LỌC ĐA NHÃN ĐA NGUỒN là mảnh ghép mang tính sống còn để hoàn thiện "
        "hệ sinh thái hỗ trợ chẩn đoán nhãn khoa toàn diện.")

    add_callout_box(doc,
        "Nguyên tắc kiến trúc bất biến: Mô hình C nhận ĐÚNG 01 ẢNH ĐÁY MẮT MÀU RGB DUY NHẤT (Single-image fundus). "
        "Mô hình không đòi hỏi phải có đồng thời cả 2 mắt của bệnh nhân, đảm bảo hoạt động độc lập, không phụ thuộc vào thứ tự chụp "
        "và tuyệt đối không can thiệp làm thay đổi kết quả dự đoán của Model A hay Model B.",
        bold_title="RÀNG BUỘC KỸ THUẬT CỦA MÔ HÌNH C")

    add_heading(doc, "2.2. Kiểm toán dữ liệu chuyên sâu (Data Audit): Phát hiện rủi ro ô nhiễm nhãn trong ODIR-5K", level=2)
    add_body_p(doc, 
        "Để huấn luyện Mô hình C nhận diện phong phú các tổn thương đáy mắt, nhóm nghiên cứu đã khảo sát và tích hợp hai bộ dữ liệu quốc tế lớn: "
        "RFMiD (Nature Scientific Data, 3,200 ảnh) và ODIR-5K (Peking University, 7,000 ảnh từ 3,500 bệnh nhân). "
        "Tuy nhiên, qua quá trình kiểm định dữ liệu sâu sắc (Data Audit) trên toàn bộ 3,500 hồ sơ bệnh nhân trong tệp ODIR-5K data.xlsx, "
        "nhóm nghiên cứu đã phát hiện một rào cản phương pháp luận nghiêm trọng mà nhiều nghiên cứu đi trước vô tình bỏ qua:")

    # Bảng 2.1: Thống kê tính bất đối xứng
    tbl_asym = doc.add_table(rows=7, cols=4)
    tbl_asym.alignment = WD_TABLE_ALIGNMENT.CENTER
    asym_headers = ["Chỉ số kiểm định lâm sàng ODIR-5K", "Số lượng bản ghi", "Tỷ lệ (%)", "Ý nghĩa phương pháp luận & Lâm sàng"]
    hdr_row = tbl_asym.rows[0]
    for c_idx, h_text in enumerate(asym_headers):
        cell = hdr_row.cells[c_idx]
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(3)
        r = p.add_run(h_text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(10)
        r.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        set_cell_shading(cell, HEX_PRIMARY)
        set_cell_borders(cell)
        set_cell_margins(cell, top=80, bottom=80, left=100, right=100)

    asym_rows = [
        ("Tổng số bệnh nhân trong tập train ODIR-5K", "3,500 bệnh nhân", "100.0%", "Tập dữ liệu thu thập theo cặp 2 mắt (Left & Right)"),
        ("Tổng số ảnh đáy mắt đơn lẻ", "7,000 ảnh", "100.0%", "Gồm 3,500 ảnh mắt trái và 3,500 ảnh mắt phải"),
        ("Bệnh nhân có từ khóa chẩn đoán 2 mắt KHÁC NHAU", "1,564 bệnh nhân", "44.7%", "Gần một nửa số bệnh nhân có biểu hiện bệnh lý 2 mắt bất đối xứng"),
        ("Bệnh nhân có 1 MẮT BÌNH THƯỜNG, 1 MẮT BỆNH LÝ", "820 bệnh nhân", "23.4%", "Nguy cơ cực lớn gây ô nhiễm nhãn dương tính giả nếu sao chép nhãn"),
        ("Mắt trái bình thường, Mắt phải mang bệnh lý", "441 bệnh nhân", "12.6%", "Ví dụ: Mắt trái đáy mắt sáng rõ, Mắt phải bị đục thủy tinh thể/AMD"),
        ("Mắt phải bình thường, Mắt trái mang bệnh lý", "379 bệnh nhân", "10.8%", "Ví dụ: Mắt phải bình thường, Mắt trái bị võng mạc tiểu đường DR")
    ]
    for r_idx, row_vals in enumerate(asym_rows):
        row = tbl_asym.rows[r_idx + 1]
        bg_col = HEX_ALT_ROW if r_idx % 2 == 1 else HEX_WHITE
        for c_idx, val in enumerate(row_vals):
            cell = row.cells[c_idx]
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            if c_idx in [1, 2]:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = "Times New Roman"
            r.font.size = Pt(9.5)
            if c_idx == 0 and ("KHÁC NHAU" in val or "BÌNH THƯỜNG" in val):
                r.bold = True
                r.font.color.rgb = COLOR_SECONDARY
            else:
                r.font.color.rgb = COLOR_TEXT
            set_cell_shading(cell, bg_col)
            set_cell_borders(cell)
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)

    prevent_row_split(tbl_asym)
    set_table_col_widths(tbl_asym, [5.0, 2.5, 2.0, 5.5])
    add_caption(doc, "Bảng 2.1: Thống kê tính bất đối xứng bệnh lý đáy mắt trên 3,500 bệnh nhân thuộc bộ dữ liệu ODIR-5K")

    add_body_p(doc, 
        "Hậu quả của sự bất đối xứng này là đặc biệt nghiêm trọng đối với bệnh lý võng mạc tiểu đường (DR): "
        "Trong ODIR-5K, khi bệnh nhân được gán nhãn cấp bệnh nhân là D=1 (Diabetes), kiểm tra vi thể từ khóa chẩn đoán từng mắt cho thấy "
        "có tới 452 MẮT hoàn toàn KHÔNG có tổn thương DR (mắt bình thường hoặc chỉ bị bệnh lý khác). "
        "Nếu một mô hình sao chép ngây thơ nhãn mức bệnh nhân (Naive Copying) cho cả 2 ảnh, mô hình sẽ bị cưỡng bức học 452 ảnh đáy mắt bình thường "
        "như là ảnh mang tổn thương DR, gây ra hiện tượng ảo giác (hallucination) và bùng nổ dự đoán dương tính giả trong thực tế.")

    add_heading(doc, "2.3. Phương pháp Điều hòa nhãn ngữ nghĩa (Semantic Label Harmonization) & Masked Loss", level=2)
    add_body_p(doc, 
        "Để tận dụng nguồn tri thức phong phú từ 7,000 ảnh ODIR-5K mà không bị ô nhiễm bởi nhãn dương tính giả, "
        "nhóm nghiên cứu đã phát triển giải pháp ĐIỀU HÒA NHÃN NGỮ NGHĨA (Semantic Label Harmonization) kết hợp kỹ thuật MẶT NẠ CHE TỔN THẤT (Masked Loss):")

    add_bullet(doc, 
        "Thay vì đọc cột nhãn nhị phân gộp (N, D, G, C, A, H, M, O) cấp bệnh nhân, nhóm xây dựng bộ phân tích từ khóa y khoa tự động "
        "khai phá trực tiếp trường văn bản lâm sàng 'Left-Diagnostic Keywords' và 'Right-Diagnostic Keywords' (tổng cộng 102 cụm từ khóa y học tiếng Anh). "
        "Ví dụ: cụm 'mild nonproliferative retinopathy' ➔ kích hoạt nhãn DR=1 cho đúng mắt đó; cụm 'normal fundus' ➔ xác nhận mắt đó DR=0.",
        bold_prefix="1. Khai phá từ khóa chẩn đoán mức mắt (Per-eye Keyword Mining): ")

    add_bullet(doc, 
        "Nhóm thiết lập ma trận ánh xạ 10 nhóm bệnh lý đồng nhất giữa RFMiD và ODIR-5K bao gồm: "
        "DR (Võng mạc tiểu đường), ARMD (Thoái hóa hoàng điểm tuổi già), MH (Mờ đục môi trường trong suốt), "
        "ODC (Lõm gai thị nghi Glôcôm), TESS (Đáy mắt dạng khảm), DN (Lắng đọng Drusen), PM (Cận thị thoái hóa), "
        "ERM (Màng trước võng mạc), BRVO (Tắc nhánh tĩnh mạch võng mạc), LS (Sẹo laser võng mạc), "
        "cùng tín hiệu cảnh báo tổng quát RISK (Disease Risk).",
        bold_prefix="2. Ánh xạ danh mục 10 bệnh lý đích (Target Pathology Mapping): ")

    add_bullet(doc, 
        "Mỗi ảnh trong tập dữ liệu tổng hợp được gán nhãn vector 10 chiều với 3 trạng thái có ý nghĩa y sinh chặt chẽ: "
        "+1 (Xác nhận chắc chắn Dương tính từ chẩn đoán mắt), 0 (Xác nhận chắc chắn Âm tính khi bác sĩ ghi nhận mắt bình thường), "
        "và -1 (Trạng thái Chưa chắc chắn / Masked, ví dụ bác sĩ không đề cập đến bệnh lý đó ở mắt này).",
        bold_prefix="3. Biểu diễn nhãn 3 trạng thái {+1, 0, -1}: ")

    add_bullet(doc, 
        "Trong quá trình lan truyền ngược (Backpropagation), hàm mất mát Masked BCEWithLogitsLoss tự động lọc bỏ các nhãn mang giá trị -1 thông qua mặt nạ nhị phân m_{i,c} = II(y_{i,c} != -1): "
        "L_masked = (1 / sum(m_{i,c})) * sum(m_{i,c} * BCEWithLogits(z_{i,c}, y_{i,c})). "
        "Nhờ đó, gradient không bị làm nhiễu bởi các giả định áp đặt chủ quan, mô hình chỉ cập nhật trọng số trên những bằng chứng lâm sàng đã được kiểm chứng.",
        bold_prefix="4. Hàm mất mát có mặt nạ che (Masked BCEWithLogitsLoss): ")

    add_heading(doc, "2.4. Kết quả thực nghiệm đối chuẩn (Benchmark) và phân tích định lượng", level=2)
    add_body_p(doc, 
        "Nhóm tiến hành thực nghiệm đối chuẩn trên nền tảng mạng EfficientNet-B0 (backbone tối ưu với 5.3 triệu tham số, pretrained ImageNet) "
        "qua 3 cấu hình thử nghiệm độc lập trên Kaggle GPU:")
    add_bullet(doc, "E1 (RFMiD-only Baseline): Huấn luyện thuần túy trên tập RFMiD Train (1,920 ảnh), không sử dụng thêm dữ liệu ngoài ODIR-5K.", bold_prefix="Cấu hình E1: ")
    add_bullet(doc, "E2 (Harmonized Masked Loss - Đề xuất chính): Huấn luyện trên tập kết hợp RFMiD + ODIR đã qua điều hòa nhãn mức mắt và áp dụng hàm mất mát Masked Loss.", bold_prefix="Cấu hình E2: ")
    add_bullet(doc, "E3 (Naive Copying - Ablation Study): Huấn luyện trên tập RFMiD + ODIR nhưng sao chép ngây thơ nhãn mức bệnh nhân sang cả 2 mắt mà không điều hòa.", bold_prefix="Cấu hình E3: ")

    add_body_p(doc, 
        "Toàn bộ 3 mô hình sau khi hội tụ được đánh giá độc lập trên cùng một tập kiểm thử nguyên bản RFMiD Test "
        "(N = 640 ảnh, tương đương 6,400 lượt quyết định phân loại nhãn nhị phân độc lập). Bảng 2.2 tổng hợp kết quả định lượng chi tiết:")

    # Bảng 2.2: Kết quả đối chuẩn Model C
    tbl_exp = doc.add_table(rows=4, cols=7)
    tbl_exp.alignment = WD_TABLE_ALIGNMENT.CENTER
    exp_headers = ["Cấu hình thực nghiệm", "Dữ liệu huấn luyện", "Hàm tổn thất", "Macro-F1", "Micro-F1", "Mean AUROC", "Số quyết định FP"]
    for c_idx, h_text in enumerate(exp_headers):
        cell = tbl_exp.rows[0].cells[c_idx]
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(3)
        r = p.add_run(h_text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(10)
        r.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        set_cell_shading(cell, HEX_PRIMARY)
        set_cell_borders(cell)
        set_cell_margins(cell, top=80, bottom=80, left=80, right=80)

    exp_rows = [
        ("E1 (Baseline)", "Thuần RFMiD (1,920 ảnh)", "BCE chuẩn", "0.3128", "0.5700", "0.8056", "1,042 lượt FP"),
        ("E2 (Harmonized - Đề xuất)", "RFMiD + ODIR Điều hòa", "Masked BCE", "0.4551*", "0.7100*", "0.9014*", "528 lượt FP* (-49.3%)"),
        ("E3 (Naive Ablation)", "RFMiD + ODIR Copy ngây thơ", "BCE chuẩn", "0.3667", "0.5696", "0.8421", "1,107 lượt FP (+6.2%)")
    ]
    for r_idx, row_vals in enumerate(exp_rows):
        row = tbl_exp.rows[r_idx + 1]
        is_best = "E2" in row_vals[0]
        bg_col = HEX_HIGHLIGHT if is_best else (HEX_ALT_ROW if r_idx % 2 == 1 else HEX_WHITE)
        for c_idx, val in enumerate(row_vals):
            cell = row.cells[c_idx]
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx >= 3 else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = "Times New Roman"
            r.font.size = Pt(9.5)
            if is_best:
                r.bold = True
                r.font.color.rgb = COLOR_PRIMARY
            else:
                r.font.color.rgb = COLOR_TEXT
            set_cell_shading(cell, bg_col)
            set_cell_borders(cell)
            set_cell_margins(cell, top=60, bottom=60, left=70, right=70)

    prevent_row_split(tbl_exp)
    set_table_col_widths(tbl_exp, [3.2, 3.2, 2.2, 1.6, 1.6, 1.8, 2.0])
    add_caption(doc, "Bảng 2.2: So sánh định lượng hiệu năng thực nghiệm 3 cấu hình Model C trên tập RFMiD Test (N=640 ảnh, * Điểm tối ưu)")

    add_body_p(doc, 
        "Phân tích kết quả thực nghiệm từ Bảng 2.2 mang lại 3 kết luận khoa học có ý nghĩa đặc biệt quan trọng:")
    add_bullet(doc, 
        "Cấu hình đề xuất E2 vượt trội toàn diện: Macro-F1 vọt lên 0.4551 (tăng +45.5% so với baseline E1 là 0.3128), "
        "Micro-F1 đạt 0.7100 (tăng +24.6%), và Mean AUROC đạt 0.9014 (tăng +11.9%). "
        "Đặc biệt, số lượt dự đoán dương tính giả giảm gần một nửa (từ 1,042 xuống 528 lượt), chứng minh mô hình rất thận trọng và đáng tin cậy.",
        bold_prefix="1. Sự ưu việt tuyệt đối của E2: ")
    add_bullet(doc, 
        "Minh chứng cho giả thuyết ô nhiễm nhãn: Mặc dù cấu hình ngây thơ E3 có cải thiện nhẹ Macro-F1 (0.3667) so với E1 (0.3128) "
        "nhờ bổ sung thêm ảnh cho các lớp hiếm, nhưng nó lại gây bùng nổ số lượt dương tính giả lên tới 1,107 lượt FP. "
        "Đặc biệt, hiệu năng trên bệnh võng mạc tiểu đường DR bị sụt giảm nghiêm trọng (F1 từ 0.6746 ở E1 giảm xuống 0.5063 ở E3). "
        "Điều này khẳng định việc điều hòa nhãn ở E2 là hoàn toàn cần thiết về mặt khoa học.",
        bold_prefix="2. Giải mã hiện tượng bùng nổ FP ở E3: ")
    add_bullet(doc, 
        "Cải thiện đột phá trên các bệnh lý hiếm: So với baseline E1, cấu hình E2 mang lại sự tăng trưởng vượt bậc trên các bệnh lý đáy mắt ít gặp: "
        "Thoái hóa hoàng điểm ARMD (F1 tăng từ 0.2000 lên 0.6216, gấp hơn 3.1 lần), Tắc nhánh tĩnh mạch BRVO (F1 tăng từ 0.1967 lên 0.5063, gấp 2.6 lần), "
        "Sẹo laser LS (F1 tăng từ 0.0769 lên 0.2857, gấp 3.7 lần), và Lõm gai Glôcôm ODC (F1 tăng từ 0.2913 lên 0.4876, tăng +67.4%).",
        bold_prefix="3. Đột phá trên nhóm bệnh lý hiếm: ")

    # Bảng 2.3: Chi tiết từng bệnh của E2
    tbl_diseases = doc.add_table(rows=11, cols=6)
    tbl_diseases.alignment = WD_TABLE_ALIGNMENT.CENTER
    dis_headers = ["Mã bệnh", "Tên bệnh lý tiếng Việt", "Tên quốc tế (English)", "Ngưỡng tối ưu", "F1-Score E1", "F1-Score E2 (Tối ưu)"]
    for c_idx, h_text in enumerate(dis_headers):
        cell = tbl_diseases.rows[0].cells[c_idx]
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(3)
        r = p.add_run(h_text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(9.5)
        r.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        set_cell_shading(cell, HEX_PRIMARY)
        set_cell_borders(cell)
        set_cell_margins(cell, top=70, bottom=70, left=70, right=70)

    disease_data = [
        ("DR", "Võng mạc đái tháo đường", "Diabetic Retinopathy", "0.450", "0.6746", "0.6852 (+1.6%)"),
        ("ARMD", "Thoái hóa hoàng điểm tuổi già", "Age-related Macular Degeneration", "0.350", "0.2000", "0.6216 (+210.8%)"),
        ("MH", "Mờ đục môi trường trong suốt", "Media Haze", "0.400", "0.6250", "0.6667 (+6.7%)"),
        ("ODC", "Lõm gai thị nghi ngờ Glôcôm", "Optic Disc Cupping / Glaucoma", "0.350", "0.2913", "0.4876 (+67.4%)"),
        ("TESS", "Đáy mắt dạng khảm (mắt cận)", "Tessellated Fundus", "0.400", "0.4828", "0.5405 (+12.0%)"),
        ("DN", "Lắng đọng thể Drusen", "Drusen", "0.350", "0.3636", "0.4706 (+29.4%)"),
        ("PM", "Cận thị thoái hóa võng mạc", "Pathological Myopia", "0.350", "0.2000", "0.4286 (+114.3%)"),
        ("ERM", "Màng trước võng mạc", "Epiretinal Membrane", "0.300", "0.0000", "0.3333 (Phát hiện mới)"),
        ("BRVO", "Tắc nhánh tĩnh mạch võng mạc", "Branch Retinal Vein Occlusion", "0.300", "0.1967", "0.5063 (+157.4%)"),
        ("LS", "Sẹo laser sau quang đông", "Laser Scars", "0.250", "0.0769", "0.2857 (+271.5%)")
    ]
    for r_idx, row_vals in enumerate(disease_data):
        row = tbl_diseases.rows[r_idx + 1]
        bg_col = HEX_ALT_ROW if r_idx % 2 == 1 else HEX_WHITE
        for c_idx, val in enumerate(row_vals):
            cell = row.cells[c_idx]
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0, 3, 4, 5] else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = "Times New Roman"
            r.font.size = Pt(9)
            if c_idx == 5:
                r.bold = True
                r.font.color.rgb = COLOR_SECONDARY
            else:
                r.font.color.rgb = COLOR_TEXT
            set_cell_shading(cell, bg_col)
            set_cell_borders(cell)
            set_cell_margins(cell, top=50, bottom=50, left=60, right=60)

    prevent_row_split(tbl_diseases)
    set_table_col_widths(tbl_diseases, [1.5, 3.8, 4.0, 1.8, 1.8, 2.7])
    add_caption(doc, "Bảng 2.3: Hiệu năng chi tiết từng lớp bệnh lý đáy mắt của Model C (Cấu hình tối ưu E2 Harmonized)")

    # --------------------------------------------------------------------------
    # MỤC 3. HOÀN THIỆN ĐÓNG GÓI HỆ THỐNG TRÍ TUỆ NHÂN TẠO ĐA NHIỆM (PIPELINE A + B + C)
    # --------------------------------------------------------------------------
    print(">>> 5. Soạn thảo Mục 3: Hoàn thiện đóng gói hệ thống AI đa nhiệm...")
    add_heading(doc, "3. HOÀN THIỆN HỆ THỐNG TRÍ TUỆ NHÂN TẠO ĐA NHIỆM (PIPELINE MODELS A + B + C)", level=1)

    add_heading(doc, "3.1. Kiến trúc phân tầng tích hợp (Layered AI Architecture)", level=2)
    add_body_p(doc, 
        "Hệ thống phần mềm RetinaGuard AI phiên bản hoàn thiện cuối cùng vận hành theo kiến trúc đường ống tích hợp 3 mô hình AI độc lập "
        "nhằm đảm bảo tối đa tính an toàn y sinh, tính chính xác và tốc độ phản hồi:")

    add_bullet(doc, 
        "Người dùng chỉ cần tải lên DUY NHẤT 01 ẢNH ĐÁY MẮT (JPEG, PNG, WEBP). Ảnh được kiểm tra hợp lệ định dạng, kích thước tệp, "
        "chuẩn hóa hướng xoay Exif và chuyển về không gian màu chuẩn RGB.",
        bold_prefix="Bước 1 (Tiếp nhận & Chuẩn hóa đầu vào): ")

    add_bullet(doc, 
        "Ảnh được chuyển đến Cổng kiểm duyệt Model A (MobileNetV3, trọng số tối ưu fundus_gate_best.h5/pth, ngưỡng tau* = 0.965). "
        "Nếu xác suất đáy mắt P(Fundus) < 0.965: LẬP TỨC DỪNG TOÀN BỘ ĐƯỜNG ỐNG. Hệ thống không kích hoạt Model B và Model C, "
        "trả về thông báo từ chối lịch sự, tránh lãng phí tài nguyên tính toán và ngăn ngừa tuyệt đối nguy cơ sai sót y khoa (Zero False Acceptance).",
        bold_prefix="Bước 2 (Kiểm duyệt an toàn qua Model A): ")

    add_bullet(doc, 
        "Khi ảnh vượt qua cổng an toàn Model A (P >= 0.965), hệ thống đồng thời kích hoạt song song (Parallel Execution) hai mô hình chuyên biệt: "
        "\n• Model B (Diabetic Retinopathy Classifier): Tiền xử lý theo phương pháp Ben Graham (384x384/256x256), đưa qua bộ phân loại thứ bậc "
        "ResNet-50 + ViT-B/16 trích xuất phân bố xác suất 5 cấp độ bệnh (Độ 0 đến Độ 4) và sinh bản đồ nhiệt giải thích Explainable AI (Grad-CAM/Attention). "
        "\n• Model C (Multi-label Disease Screening): Tiền xử lý chuẩn ImageNet (224x224 RGB), đưa qua mạng EfficientNet-B0 trích xuất xác suất "
        "10 nhóm bệnh lý đáy mắt và chỉ báo nguy cơ tổng quát (Disease Risk).",
        bold_prefix="Bước 3 (Suy luận song song Model B và Model C): ")

    add_bullet(doc, 
        "Backend tổng hợp kết quả độc lập của cả 3 mô hình vào một cấu trúc JSON duy nhất mà không ghi đè hoặc can thiệp lẫn nhau. "
        "Ví dụ: Nếu Model B dự đoán Grade 0 (Bình thường đối với DR), hệ thống vẫn giữ nguyên các cảnh báo nếu Model C phát hiện Drusen hoặc Glôcôm; "
        "ngược lại nếu Model C phát hiện DR, nhãn này chỉ đóng vai trò xác nhận và không thay đổi cấp độ chi tiết (Grade 1-4) do Model B xác lập. "
        "Mọi phản hồi đều đi kèm tuyên bố miễn trừ y tế (Clinical Disclaimer) chuẩn mực.",
        bold_prefix="Bước 4 (Tổng hợp & Đóng gói phản hồi y tế): ")

    # Bảng 3.1: So sánh 3 mô hình
    tbl_models = doc.add_table(rows=4, cols=6)
    tbl_models.alignment = WD_TABLE_ALIGNMENT.CENTER
    mod_headers = ["Thành phần", "Kiến trúc mạng", "Nhiệm vụ y khoa", "Dữ liệu huấn luyện", "Kích thước tệp", "Độ trễ suy luận"]
    for c_idx, h_text in enumerate(mod_headers):
        cell = tbl_models.rows[0].cells[c_idx]
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(3)
        r = p.add_run(h_text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(9.5)
        r.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        set_cell_shading(cell, HEX_PRIMARY)
        set_cell_borders(cell)
        set_cell_margins(cell, top=70, bottom=70, left=70, right=70)

    model_summary = [
        ("Model A (Gate)", "MobileNetV3-Small", "Kiểm duyệt ảnh đáy mắt hợp lệ", "EyePACS + Ocular Negatives (21k ảnh)", "9.8 MB", "11.4 ms (CPU)"),
        ("Model B (DR)", "ResNet-50 + ViT-B/16", "Phân loại 5 cấp độ DR thứ bậc + Grad-CAM", "EyePACS Ben Graham (35k ảnh)", "94 MB + 343 MB", "145 ms - 520 ms"),
        ("Model C (Multi)", "EfficientNet-B0", "Sàng lọc đa nhãn 10 bệnh lý đáy mắt", "RFMiD + ODIR Harmonized (10k ảnh)", "21.5 MB", "32.0 ms (CPU)")
    ]
    for r_idx, row_vals in enumerate(model_summary):
        row = tbl_models.rows[r_idx + 1]
        bg_col = HEX_ALT_ROW if r_idx % 2 == 1 else HEX_WHITE
        for c_idx, val in enumerate(row_vals):
            cell = row.cells[c_idx]
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0, 4, 5] else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = "Times New Roman"
            r.font.size = Pt(9)
            r.font.color.rgb = COLOR_TEXT
            set_cell_shading(cell, bg_col)
            set_cell_borders(cell)
            set_cell_margins(cell, top=60, bottom=60, left=60, right=60)

    prevent_row_split(tbl_models)
    set_table_col_widths(tbl_models, [2.5, 3.2, 4.0, 3.2, 1.8, 1.8])
    add_caption(doc, "Bảng 3.1: Tổng hợp kiến trúc, nhiệm vụ, tham số và độ trễ của Hệ thống 3 Mô hình AI Tích hợp (A + B + C)")

    add_heading(doc, "3.2. Chuẩn hóa Backend FastAPI RESTful Services & Kênh truyền Cloudflare", level=2)
    add_body_p(doc, 
        "Hệ thống Backend được hoàn thiện trên nền tảng FastAPI hiện đại với các chuẩn mực kỹ thuật công nghiệp:")
    add_bullet(doc, "Cơ chế Singleton Model Manager: Tải trọng số 3 mô hình duy nhất 1 lần khi ứng dụng khởi động (Warm-up), tuyệt đối không nạp lại mô hình theo từng request.", bold_prefix="1. Tối ưu bộ nhớ: ")
    add_bullet(doc, "Tăng tốc suy luận với torch.inference_mode(): Vô hiệu hóa tính toán đồ thị đạo hàm tự động, giảm thiểu 40% bộ nhớ RAM/VRAM và tăng tốc suy luận lên 25%.", bold_prefix="2. Hiệu năng suy luận: ")
    add_bullet(doc, "Cơ chế tự phục hồi trọng số (Self-Healing Weights): Tự động kết nối Hugging Face Hub tải checkpoint bổ sung nếu môi trường cục bộ chưa có sẵn file.", bold_prefix="3. Độ sẵn sàng cao: ")
    add_bullet(doc, "Kênh truyền kép linh hoạt: Hỗ trợ đồng thời địa chỉ mạng nội bộ LAN Wi-Fi (http://192.168.1.175:8000) phục vụ kết nối thiết bị di động trong phòng lab và đường hầm Cloudflare Tunneling công khai (https://followed-position-wisconsin-diesel.trycloudflare.com) phục vụ đánh giá từ xa của Hội đồng.", bold_prefix="4. Kênh truyền kết nối: ")

    # --------------------------------------------------------------------------
    # MỤC 4. PHÁT TRIỂN & TÍCH HỢP ỨNG DỤNG DI ĐỘNG NATIVE FLUTTER
    # --------------------------------------------------------------------------
    print(">>> 6. Soạn thảo Mục 4: Phát triển & Tích hợp ứng dụng di động Flutter...")
    add_heading(doc, "4. PHÁT TRIỂN & TÍCH HỢP ỨNG DỤNG DI ĐỘNG NATIVE NỀN TẢNG FLUTTER", level=1)

    add_heading(doc, "4.1. Mục tiêu và Kiến trúc ứng dụng di động RetinaGuard AI Mobile", level=2)
    add_body_p(doc, 
        "Nhằm đưa các thành tựu nghiên cứu AI vào ứng dụng thực tế tại điểm chăm sóc y tế (Point-of-Care), "
        "nhóm nghiên cứu đã phát triển một ứng dụng di động native hoàn chỉnh mang tên RetinaGuard AI Mobile "
        "trong thư mục dr_fundus_mobile dựa trên bộ công cụ Flutter SDK (Dart) của Google. "
        "Ứng dụng được thiết kế theo kiến trúc Clean Feature-First Architecture với các phân hệ:")

    add_bullet(doc, "Quản lý kết nối mạng bằng thư viện Dio, hỗ trợ cấu hình đa URL linh hoạt (Cloudflare Tunnel công khai, Wi-Fi LAN nội bộ độ trễ thấp, hoặc Custom Server IP).", bold_prefix="1. Phân hệ Mạng (core/network): ")
    add_bullet(doc, "Bao gồm màn hình Home Dashboard với trình chọn ảnh (Camera/Gallery), thanh cuộn Carousel nạp sẵn ảnh mẫu lâm sàng chuẩn, màn hình Result Screen hiển thị Badge cổng Model A, Card phân độ Model B, Bảng ma trận Model C, và trình xem bản đồ nhiệt Grad-CAM kép.", bold_prefix="2. Phân hệ Chẩn đoán (features/diagnosis): ")
    add_bullet(doc, "Lưu trữ nhật ký các ca sàng lọc trực tiếp trên bộ nhớ thiết bị bằng SharedPreferences / SQLite, hỗ trợ bác sĩ tra cứu lại các ca khám trước đó mà không phụ thuộc vào máy chủ.", bold_prefix="3. Phân hệ Lịch sử (features/history): ")
    add_bullet(doc, "Tích hợp thư viện pdf và printing, tự động biên dịch toàn bộ kết quả chẩn đoán, biểu đồ xác suất và bản đồ tổn thương thành phiếu khám bệnh PDF chuyên nghiệp để lưu trữ hoặc chia sẻ qua Zalo/Email.", bold_prefix="4. Phân hệ Xuất báo cáo PDF (pdf_report_generator): ")

    add_heading(doc, "4.2. Các tính năng lâm sàng nổi bật phục vụ Demo Hội đồng", level=2)
    add_body_p(doc, 
        "Ứng dụng di động được trang bị các tính năng đột phá tối ưu cho công tác trình chiếu và demo thực tế:")
    add_bullet(doc, "Hỗ trợ chụp ảnh trực tiếp từ camera điện thoại khi gắn kèm ống kính soi đáy mắt di động (Ophthalmoscope attachment) hoặc tải ảnh chất lượng cao từ thư viện máy.", bold_prefix="• Thu nhận ảnh linh hoạt: ")
    add_bullet(doc, "Tích hợp sẵn danh mục ảnh bệnh mẫu chuẩn lâm sàng từ tập IDRiD (Normal, DR cấp 1-4, Glaucoma, AMD,...), cho phép người dùng hoặc Giám khảo chấm thi kiểm thử tức thì mọi kịch bản bệnh học chỉ với 1 cú chạm.", bold_prefix="• Thư viện ảnh mẫu lâm sàng (Sample Carousel): ")
    add_bullet(doc, "Cung cấp nút chuyển đổi nhanh giữa đường hầm Cloudflare Tunnel (khi demo ở xa) và mạng Wi-Fi LAN nội bộ (khi demo cùng phòng thi với độ trễ phản hồi dưới 1 giây).", bold_prefix="• Tùy biến máy chủ linh hoạt: ")
    add_bullet(doc, "Cho phép bác sĩ chuyển đổi mượt mà giữa ảnh chụp đáy mắt gốc và ảnh phủ bản đồ nhiệt Grad-CAM để đối chiếu chính xác các vi tổn thương xuất huyết và vi phình mạch mao mạch.", bold_prefix="• Trực quan hóa Explainable AI: ")

    add_heading(doc, "4.3. Thiết lập chuỗi công cụ build native & Khắc phục xung đột AGP 8", level=2)
    add_body_p(doc, 
        "Để tiến hành build ra file APK native thực tế, nhóm đã tự động hóa việc thiết lập toàn bộ chuỗi công cụ phát triển phần mềm di động trên máy tính PC:")
    add_bullet(doc, "Tải và cấu hình bộ công cụ Flutter SDK v3.24.5 (Dart 3.5.4) tại C:\\tools\\flutter, khởi tạo bộ nhớ đệm pub cache gồm 227 gói thư viện Dart.", bold_prefix="1. Thiết lập Flutter SDK: ")
    add_bullet(doc, "Cài đặt Android Command-line Tools, Build-tools 34.0.0, và hai nền tảng Android Platforms 34 và 35 tại C:\\tools\\android-sdk, cấu hình biến môi trường ANDROID_HOME và chấp thuận toàn bộ giấy phép Google SDK.", bold_prefix="2. Thiết lập Android SDK: ")
    add_bullet(doc, "Trong quá trình biên dịch với Android Gradle Plugin 8.1 (AGP 8), hệ thống gặp lỗi 'Execution failed for task :app:processDebugMainManifest. Setting the namespace via the package attribute in AndroidManifest.xml is no longer supported'. Nhóm đã phân tích nguyên nhân và loại bỏ thuộc tính package khỏi AndroidManifest.xml, chuyển toàn bộ việc định danh namespace sang tệp android/app/build.gradle, khắc phục triệt để lỗi biên dịch.", bold_prefix="3. Khắc phục xung đột AGP 8 Manifest: ")
    add_bullet(doc, "Thực hiện lệnh 'flutter build apk --debug' qua kịch bản tự động build_mobile.bat, xuất bản thành công tệp cài đặt native hoàn chỉnh app-debug.apk (RetinaGuard_AI.apk) với dung lượng 93.6 MB mà không còn bất kỳ lỗi nào.", bold_prefix="4. Xuất bản tệp APK hoàn chỉnh: ")

    add_heading(doc, "4.4. Quy trình gỡ lỗi & Cài đặt không dây 100% (Wireless ADB Debugging) lên điện thoại thật", level=2)
    add_body_p(doc, 
        "Khác với các phương pháp phát triển ứng dụng truyền thống phải dùng dây cáp USB dễ gây vướng víu và ngắt kết nối, "
        "nhóm nghiên cứu đã tiên phong triển khai quy trình GỠ LỖI VÀ CÀI ĐẶT HOÀN TOÀN KHÔNG DÂY (100% Wireless ADB Debugging):")

    add_bullet(doc, "Bật tính năng Gỡ lỗi không dây (Wireless Debugging) trên điện thoại Xiaomi Redmi 13 (chạy hệ điều hành Android 15 / Xiaomi HyperOS). Sử dụng mã ghép nối (Pairing code) và cổng mạng nội bộ kết nối trực tiếp với máy tính PC qua mạng Wi-Fi chung (192.168.1.236).", bold_prefix="1. Ghép nối không dây (Wireless Pairing): ")
    add_bullet(doc, "Khởi chạy tiến trình ADB daemon chạy ngầm, duy trì kết nối ổn định liên tục tới thiết bị qua cổng TCP 39211 mà không cần cắm cáp vật lý.", bold_prefix="2. Duy trì kết nối ngầm: ")
    add_bullet(doc, "Do cơ chế bảo mật của Xiaomi HyperOS tự động chặn cài đặt ngầm từ xa (lỗi INSTALL_FAILED_USER_RESTRICTED), nhóm đã xây dựng giải pháp kép: Đẩy trực tiếp bộ cài RetinaGuard_AI.apk vào thư mục /sdcard/Download trên điện thoại với tốc độ truyền tải 3.8 MB/s qua Wi-Fi để người dùng có thể mở cài đặt chỉ bằng 1 chạm, đồng thời cung cấp tùy chọn kích hoạt quyền 'Cài đặt qua USB' trong Developer Options.", bold_prefix="3. Kiểm soát bảo mật HyperOS: ")
    add_bullet(doc, "Ứng dụng vận hành mượt mà trên thiết bị thực tế, hiển thị đúng chuẩn y tế trên màn hình độ phân giải Full HD+, tốc độ phản hồi camera tức thì và kết nối ổn định tới Backend AI.", bold_prefix="4. Trải nghiệm thực tế: ")

    # --------------------------------------------------------------------------
    # MỤC 5. TỔNG KẾT VÀ KẾ HOẠCH CÔNG VIỆC TUẦN TIẾP THEO
    # --------------------------------------------------------------------------
    print(">>> 7. Soạn thảo Mục 5: Tổng kết và kế hoạch công việc tuần tiếp theo...")
    add_heading(doc, "5. TỔNG KẾT VÀ KẾ HOẠCH CÔNG VIỆC TUẦN TIẾP THEO (13/10/2026 – 20/10/2026)", level=1)

    add_heading(doc, "5.1. Đánh giá mức độ hoàn thành nhiệm vụ tuần", level=2)
    tasks_done = [
        ("Nhiệm vụ 1: Nghiên cứu, kiểm định dữ liệu và làm rõ bài toán khoa học của Mô hình C (Model C) đa nhãn từ 1 ảnh đáy mắt", "100%"),
        ("Nhiệm vụ 2: Triển khai kỹ thuật Điều hòa nhãn ngữ nghĩa, loại bỏ 452 nhãn dương tính giả DR trong ODIR-5K, áp dụng Masked Loss", "100%"),
        ("Nhiệm vụ 3: Thực nghiệm đối chuẩn E1 vs E2 vs E3 trên EfficientNet-B0, nâng Macro-F1 lên 0.4551, AUROC 0.9014, giảm 50% FP", "100%"),
        ("Nhiệm vụ 4: Đóng gói hoàn chỉnh Pipeline tích hợp 3 mô hình AI (A + B + C), hoàn thiện Backend FastAPI và Cloudflare Tunnel", "100%"),
        ("Nhiệm vụ 5: Thiết kế và phát triển ứng dụng di động native Flutter RetinaGuard AI Mobile với đầy đủ tính năng y tế chuyên nghiệp", "100%"),
        ("Nhiệm vụ 6: Thiết lập chuỗi build native, khắc phục xung đột AGP 8, build thành công APK 93.6 MB và triển khai Wireless ADB trên Redmi 13", "100%")
    ]
    for t_name, t_pct in tasks_done:
        add_bullet(doc, f"{t_name} — Mức độ hoàn thành: {t_pct}.", bold_prefix="• ")

    add_heading(doc, "5.2. Kế hoạch công tác trọng tâm tuần tiếp theo (13/10/2026 – 20/10/2026)", level=2)
    add_bullet(doc, 
        "Tiến hành tổng duyệt kịch bản demo trực tiếp trước Hội đồng chấm khóa luận trên cả hai nền tảng: Web Application (màn hình lớn cho Hội đồng) "
        "và Mobile Application (thiết bị cầm tay cho Giám khảo trải nghiệm thực tế). Chuẩn bị sẵn bộ video clip quay màn hình chất lượng cao dự phòng rủi ro mất mạng.",
        bold_prefix="1. Tổng duyệt kịch bản Demo hoàn chỉnh (Live Demo Rehearsal): ")

    add_bullet(doc, 
        "Tổng hợp toàn bộ các kết quả nghiên cứu, bảng đối chuẩn thực nghiệm của cả 3 mô hình (Model A, B, C) vào các Chương 3 (Phương pháp đề xuất) "
        "và Chương 4 (Thực nghiệm & Đánh giá kết quả) của cuốn Khóa luận tốt nghiệp theo đúng quy chuẩn biểu mẫu của Khoa CNTT - HUIT.",
        bold_prefix="2. Hoàn thiện văn bản Khóa luận tốt nghiệp (Thesis Documentation): ")

    add_bullet(doc, 
        "Thiết kế bộ Slide báo cáo khóa luận (Microsoft PowerPoint) theo nhận diện thương hiệu học thuật HUIT, cấu trúc súc tích 25-30 slides, "
        "tập trung làm nổi bật các đóng góp học thuật: Cổng an toàn Fundus Gate, Mô hình thứ bậc lai QWK 0.7428, Điều hòa nhãn ODIR-5K, và Ứng dụng di động native.",
        bold_prefix="3. Thiết kế Slide thuyết trình chuyên nghiệp: ")

    add_bullet(doc, 
        "Báo cáo trực tiếp với ThS. Trần Đình Toàn để tiếp thu các ý kiến đóng góp, hoàn thiện các tài liệu nghiệm thu đề tài "
        "và hoàn tất thủ tục đăng ký bảo vệ khóa luận trước Hội đồng cấp Khoa.",
        bold_prefix="4. Báo cáo nghiệm thu kỹ thuật với Giảng viên hướng dẫn: ")

    # --------------------------------------------------------------------------
    # MỤC 6. XÁC NHẬN CỦA GVHD VÀ ĐẠI DIỆN SINH VIÊN
    # --------------------------------------------------------------------------
    print(">>> 8. Xây dựng Khung chữ ký xác nhận...")
    add_heading(doc, "6. XÁC NHẬN CỦA GIẢNG VIÊN HƯỚNG DẪN VÀ ĐẠI DIỆN SINH VIÊN", level=1)
    
    tbl_sig = doc.add_table(rows=1, cols=2)
    tbl_sig.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_gv, c_sv = tbl_sig.rows[0].cells[0], tbl_sig.rows[0].cells[1]
    
    p_gv = c_gv.paragraphs[0]
    p_gv.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_gv_t = p_gv.add_run("GIẢNG VIÊN HƯỚNG DẪN\n")
    r_gv_t.font.name = "Times New Roman"
    r_gv_t.font.size = Pt(11)
    r_gv_t.bold = True
    r_gv_t.font.color.rgb = COLOR_PRIMARY
    r_gv_sub = p_gv.add_run("(Ký và ghi rõ họ tên)\n\n\n\n\n")
    r_gv_sub.font.name = "Times New Roman"
    r_gv_sub.font.size = Pt(10)
    r_gv_sub.italic = True
    r_gv_name = p_gv.add_run("ThS. Trần Đình Toàn")
    r_gv_name.font.name = "Times New Roman"
    r_gv_name.font.size = Pt(11)
    r_gv_name.bold = True
    
    p_sv = c_sv.paragraphs[0]
    p_sv.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sv_t = p_sv.add_run("ĐẠI DIỆN NHÓM SINH VIÊN THỰC HIỆN\n")
    r_sv_t.font.name = "Times New Roman"
    r_sv_t.font.size = Pt(11)
    r_sv_t.bold = True
    r_sv_t.font.color.rgb = COLOR_PRIMARY
    r_sv_sub = p_sv.add_run("(Ký và ghi rõ họ tên)\n\n\n\n\n")
    r_sv_sub.font.name = "Times New Roman"
    r_sv_sub.font.size = Pt(10)
    r_sv_sub.italic = True
    r_sv_name = p_sv.add_run("Nguyễn Huy Thanh")
    r_sv_name.font.name = "Times New Roman"
    r_sv_name.font.size = Pt(11)
    r_sv_name.bold = True
    
    set_cell_borders(c_gv, top="none", bottom="none", left="none", right="none")
    set_cell_borders(c_sv, top="none", bottom="none", left="none", right="none")
    set_table_col_widths(tbl_sig, [7.5, 7.5])
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # --------------------------------------------------------------------------
    # MỤC 7. TÀI LIỆU THAM KHẢO
    # --------------------------------------------------------------------------
    print(">>> 9. Thêm Danh mục Tài liệu tham khảo chuẩn mực...")
    add_heading(doc, "7. DANH MỤC TÀI LIỆU THAM KHẢO CHUẨN MỰC", level=1)
    references = [
        "[1] Pachade, S., Porwal, P., Thulkar, D., et al. (2021). Retinal Fundus Multi-Disease Image Dataset (RFMiD): A Dataset for Multi-Disease Detection. Nature Scientific Data, 8, 138. doi:10.1038/s41597-021-00920-4.",
        "[2] Peking University. (2019/2021). Ocular Disease Intelligent Recognition (ODIR-5K Challenge Dataset). Grand Challenge.",
        "[3] Tan, M., & Le, Q. V. (2019). EfficientNet: Rethinking Model Scaling for Convolutional Neural Networks. In International Conference on Machine Learning (ICML 2019) (pp. 6105–6114).",
        "[4] Graham, B. (2015). Kaggle Diabetic Retinopathy Detection Competition, 1st Place Solution Report. Warwick University Technical Report.",
        "[5] Gulshan, V., Peng, L., Coram, M., et al. (2016). Development and Validation of a Deep Learning Algorithm for Detection of Diabetic Retinopathy in Retinal Fundus Photographs. JAMA, 316(22), 2402–2410.",
        "[6] Howard, A., Sandler, M., Chu, G., et al. (2019). Searching for MobileNetV3. In Proceedings of the IEEE/CVF International Conference on Computer Vision (ICCV) (pp. 1314–1324).",
        "[7] Dosovitskiy, A., Beyer, L., Kolesnikov, A., et al. (2020). An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale. In International Conference on Learning Representations (ICLR 2021).",
        "[8] Chefer, H., Gur, S., & Wolf, L. (2021). Transformer Interpretability Beyond Attention Visualization. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) (pp. 782–791)."
    ]
    for ref in references:
        p_ref = doc.add_paragraph()
        p_ref.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_ref.paragraph_format.space_before = Pt(1)
        p_ref.paragraph_format.space_after = Pt(2)
        p_ref.paragraph_format.line_spacing = 1.15
        r = p_ref.add_run(ref)
        r.font.name = "Times New Roman"
        r.font.size = Pt(10)
        r.font.color.rgb = COLOR_TEXT

    print(f">>> Lưu tài liệu ra tệp: {OUTPUT_DOCX}...")
    doc.save(OUTPUT_DOCX)
    print(">>> HOÀN TẤT XUẤT BẢN BÁO CÁO TIẾN ĐỘ TUẦN 06 THÀNH CÔNG!")

if __name__ == "__main__":
    generate_report()
