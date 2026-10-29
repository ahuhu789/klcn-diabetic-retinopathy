// Generated from backend/app/classifier.py (CLASSES, SEVERITY_INFO) so Lite results read like the API.
export const CLASSES = [
  "0 - Không bệnh (No DR)",
  "1 - Nhẹ (Mild NPDR)",
  "2 - Trung bình (Moderate NPDR)",
  "3 - Nặng (Severe NPDR)",
  "4 - Tăng sinh (Proliferative DR)",
  "5 - Tổn thương không phải DR"
];

export const SEVERITY_INFO = {
  "0": {
    "title": "Giai đoạn 0: Không phát hiện tổn thương bệnh võng mạc đái tháo đường",
    "badge": "Bình thường",
    "description": "Võng mạc không có dấu hiệu vi phình mạch hoặc xuất huyết thuộc thang DR.",
    "advice": "Tái khám định kỳ sau 12 tháng. Duy trì đường huyết và huyết áp ổn định."
  },
  "1": {
    "title": "Giai đoạn 1: Bệnh võng mạc đái tháo đường nhẹ (Mild NPDR)",
    "badge": "Mức độ nhẹ",
    "description": "Dấu hiệu phù hợp với vi phình mạch nhỏ ở mao mạch võng mạc.",
    "advice": "Kiểm tra lại đáy mắt sau 6–9 tháng. Theo dõi HbA1c và lipid máu."
  },
  "2": {
    "title": "Giai đoạn 2: Bệnh võng mạc đái tháo đường trung bình (Moderate NPDR)",
    "badge": "Mức độ trung bình",
    "description": "Nhiều vi phình mạch, xuất huyết dạng chấm hoặc ngọn lửa, có thể kèm xuất tiết.",
    "advice": "Khám chuyên khoa mắt sau 3–6 tháng. Cân nhắc chụp mạch huỳnh quang nếu nghi phù hoàng điểm."
  },
  "3": {
    "title": "Giai đoạn 3: Bệnh võng mạc đái tháo đường nặng (Severe NPDR)",
    "badge": "Mức độ nặng",
    "description": "Tổn thương nặng theo quy tắc 4-2-1: xuất huyết ở 4 góc phần tư hoặc tĩnh mạch chuỗi hạt.",
    "advice": "Nguy cơ tiến triển sang thể tăng sinh. Cần khám đáy mắt sớm để xem xét laser hoặc anti-VEGF."
  },
  "4": {
    "title": "Giai đoạn 4: Bệnh võng mạc đái tháo đường tăng sinh (Proliferative DR)",
    "badge": "Tăng sinh",
    "description": "Tân mạch dễ vỡ, có thể gây xuất huyết dịch kính hoặc bong võng mạc co kéo.",
    "advice": "Cần khám chuyên khoa mắt sớm. Đây không phải chỉ định phẫu thuật tự động từ một ảnh."
  },
  "5": {
    "title": "Lớp 5: Tổn thương võng mạc không thuộc thang DR",
    "badge": "Không phải DR",
    "description": "Mô hình gán ảnh vào nhóm tổn thương không phải bệnh võng mạc đái tháo đường. Lớp này là một nhóm chung, không nêu tên từng bệnh.",
    "advice": "Không đọc kết quả này như một chẩn đoán đục thủy tinh thể, glôcôm, AMD hay tắc mạch. Cần bác sĩ mắt xem ảnh."
  }
};
