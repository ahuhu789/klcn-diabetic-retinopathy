import React, { useState, useEffect, useRef } from 'react';
import { 
  Upload, 
  Eye, 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  ShieldCheck, 
  Activity, 
  Layers, 
  ChevronRight,
  Info
} from 'lucide-react';

const API_BASE = '/api';

const STAGE_COLORS = [
  '#10b981', // 0: Normal (Green)
  '#f59e0b', // 1: Mild (Yellow/Amber)
  '#f97316', // 2: Moderate (Orange)
  '#ef4444', // 3: Severe (Red)
  '#a855f7'  // 4: Proliferative (Purple)
];

export default function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [samples, setSamples] = useState([]);
  const [activeView, setActiveView] = useState('heatmap'); // 'heatmap' or 'original'
  const fileInputRef = useRef(null);

  // Load sample images on mount
  useEffect(() => {
    fetch(`${API_BASE}/samples`)
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) setSamples(data);
      })
      .catch(err => console.error("Could not fetch samples:", err));
  }, []);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      processFile(file);
    }
  };

  const processFile = (file) => {
    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
    setResult(null);
    setError(null);
  };

  const handleSelectSample = async (sample) => {
    try {
      setLoading(true);
      const res = await fetch(sample.url);
      const blob = await res.blob();
      const file = new File([blob], sample.filename, { type: 'image/jpeg' });
      processFile(file);
    } catch (err) {
      setError("Không thể tải ảnh mẫu: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setResult(null);
    setError(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleAnalyze = async () => {
    if (!selectedFile) return;

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch(`${API_BASE}/predict`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Lỗi máy chủ (${response.status})`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message || "Đã xảy ra lỗi khi phân tích ảnh.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {/* Header */}
      <header className="app-header">
        <div className="container header-content">
          <div className="brand">
            <div className="brand-icon">
              <Eye size={22} />
            </div>
            <div>
              <div className="brand-title">RetinaGuard AI</div>
              <div className="brand-subtitle">Hệ thống Phân tích Đáy mắt & Chẩn đoán Bệnh võng mạc</div>
            </div>
          </div>
          <div className="badge-pipeline">
            <ShieldCheck size={14} />
            <span>Fundus Gate (MobileNetV3) + DR Classifier (ResNet-50)</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container" style={{ flex: 1, paddingTop: '1.5rem' }}>
        <section className="hero">
          <h1>Sàng lọc & Phân độ <span>Võng mạc Đái tháo đường</span></h1>
          <p>
            Quy trình khép kín 2 giai đoạn: Tự động kiểm tra chất lượng & tính hợp lệ của ảnh đáy mắt (Input Gate), sau đó phát hiện và đánh giá mức độ tổn thương võng mạc kèm bản đồ nhiệt Grad-CAM.
          </p>
        </section>

        <div className="main-grid">
          {/* Left Column: Upload & Controls */}
          <div className="card">
            <div className="card-title">
              <Upload size={18} />
              <span>Nạp ảnh chụp đáy mắt</span>
            </div>

            {!previewUrl ? (
              <div 
                className="upload-dropzone"
                onClick={() => fileInputRef.current?.click()}
                onDragOver={(e) => e.preventDefault()}
                onDrop={(e) => {
                  e.preventDefault();
                  if (e.dataTransfer.files?.[0]) processFile(e.dataTransfer.files[0]);
                }}
              >
                <Upload className="upload-icon" />
                <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#334155', marginBottom: '0.25rem' }}>
                  Kéo thả ảnh hoặc bấm để chọn tệp
                </h3>
                <p style={{ fontSize: '0.85rem', color: '#64748b' }}>
                  Định dạng hỗ trợ: JPG, PNG (Ảnh đáy võng mạc hoặc ảnh bất kỳ để thử nghiệm Gate)
                </p>
              </div>
            ) : (
              <div className="preview-container">
                <img src={previewUrl} alt="Đáy mắt xem trước" className="preview-img" />
                <button className="btn-remove" onClick={handleClear}>✕ Đổi ảnh khác</button>
              </div>
            )}

            <input 
              type="file" 
              ref={fileInputRef} 
              style={{ display: 'none' }} 
              accept="image/*"
              onChange={handleFileChange}
            />

            {/* Samples */}
            {samples.length > 0 && (
              <div className="samples-bar">
                <div className="samples-label">Hoặc chọn nhanh ảnh mẫu kiểm nghiệm lâm sàng:</div>
                <div className="samples-grid">
                  {samples.map((s) => (
                    <img 
                      key={s.id} 
                      src={s.url} 
                      alt={s.filename} 
                      className="sample-thumb"
                      title={`Ảnh mẫu: ${s.filename}`}
                      onClick={() => handleSelectSample(s)}
                    />
                  ))}
                </div>
              </div>
            )}

            <button 
              className="btn-analyze"
              disabled={!selectedFile || loading}
              onClick={handleAnalyze}
            >
              {loading ? (
                <>
                  <div className="spinner"></div>
                  <span>Đang phân tích 2 giai đoạn...</span>
                </>
              ) : (
                <>
                  <Activity size={18} />
                  <span>Tiến hành Chẩn đoán</span>
                </>
              )}
            </button>

            {error && (
              <div style={{ marginTop: '1rem', padding: '0.75rem 1rem', background: '#fef2f2', color: '#991b1b', borderRadius: '8px', fontSize: '0.88rem', border: '1px solid #fecaca' }}>
                <strong>Lỗi:</strong> {error}
              </div>
            )}
          </div>

          {/* Right Column: Results */}
          <div className="card">
            <div className="card-title">
              <Layers size={18} />
              <span>Kết quả Phân tích Y khoa</span>
            </div>

            {!result && !loading && (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '300px', color: '#94a3b8', textAlign: 'center', padding: '2rem' }}>
                <Eye size={48} strokeWidth={1.5} style={{ marginBottom: '1rem', opacity: 0.5 }} />
                <h4 style={{ fontSize: '1.05rem', fontWeight: 600, color: '#64748b' }}>Chưa có dữ liệu phân tích</h4>
                <p style={{ fontSize: '0.88rem', maxWidth: '340px', marginTop: '0.5rem' }}>
                  Vui lòng tải ảnh lên hoặc chọn ảnh mẫu, sau đó nhấn nút <strong>"Tiến hành Chẩn đoán"</strong> để xem kết quả.
                </p>
              </div>
            )}

            {loading && (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '300px', gap: '1rem' }}>
                <div className="spinner" style={{ width: '36px', height: '36px', borderColor: '#bfdbfe', borderTopColor: '#2563eb' }}></div>
                <div style={{ fontSize: '0.95rem', color: '#475569', fontWeight: 600 }}>
                  Đang xử lý qua Fundus Gate và DR Classifier...
                </div>
              </div>
            )}

            {result && (
              <div>
                {/* Stage 1: Fundus Gate Result */}
                <div className={`gate-banner ${result.is_fundus ? 'gate-pass' : 'gate-reject'}`}>
                  {result.is_fundus ? <CheckCircle2 size={24} style={{ flexShrink: 0 }} /> : <XCircle size={24} style={{ flexShrink: 0 }} />}
                  <div>
                    <div className="gate-badge">
                      Giai đoạn 1: Fundus Gate • {result.is_fundus ? 'HỢP LỆ (PASS)' : 'TỪ CHỐI (REJECT)'}
                    </div>
                    <div className="gate-desc">
                      {result.message}
                    </div>
                    <div style={{ fontSize: '0.75rem', marginTop: '0.35rem', opacity: 0.85 }}>
                      Độ tự tin nhận diện đáy mắt: <strong>{(result.fundus_confidence * 100).toFixed(2)}%</strong> (Ngưỡng an toàn: ≥ {(result.threshold * 100).toFixed(2)}%)
                    </div>
                  </div>
                </div>

                {/* Stage 2: DR Classifier (Only if is_fundus is true) */}
                {result.is_fundus && result.dr_result && (
                  <div>
                    <div className="diag-header">
                      <div>
                        <div style={{ fontSize: '0.8rem', color: '#64748b', fontWeight: 600, textTransform: 'uppercase' }}>
                          Giai đoạn 2: Phân độ bệnh
                        </div>
                        <div style={{ fontSize: '1.15rem', fontWeight: 800, color: '#0f172a', marginTop: '0.2rem' }}>
                          {result.dr_result.stage_name}
                        </div>
                      </div>
                      <div className={`stage-badge stage-${result.dr_result.stage}`}>
                        {result.dr_result.badge}
                      </div>
                    </div>

                    {/* View Switcher for Grad-CAM */}
                    {result.dr_result.heatmap_base64 && (
                      <div style={{ marginBottom: '1rem' }}>
                        <div className="view-tabs">
                          <button 
                            className={`view-tab ${activeView === 'heatmap' ? 'active' : ''}`}
                            onClick={() => setActiveView('heatmap')}
                          >
                            Bản đồ nhiệt Grad-CAM (Explainable AI)
                          </button>
                          <button 
                            className={`view-tab ${activeView === 'original' ? 'active' : ''}`}
                            onClick={() => setActiveView('original')}
                          >
                            Ảnh gốc cắt tâm (224x224)
                          </button>
                        </div>
                        <div className="preview-container" style={{ maxHeight: '240px' }}>
                          <img 
                            src={activeView === 'heatmap' ? result.dr_result.heatmap_base64 : previewUrl} 
                            alt="Heatmap View" 
                            className="preview-img"
                          />
                        </div>
                        <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.4rem', textAlign: 'center' }}>
                          Vùng màu đỏ/cam biểu thị khu vực mô hình tập trung chú ý (vi phình mạch, xuất huyết, xuất tiết).
                        </div>
                      </div>
                    )}

                    {/* Clinical Info Box */}
                    <div className="section-title">Mô tả tổn thương võng mạc</div>
                    <div className="medical-box">
                      {result.dr_result.description}
                    </div>

                    <div className="section-title">Khuyến nghị can thiệp lâm sàng</div>
                    <div className="medical-box medical-advice">
                      {result.dr_result.advice}
                    </div>

                    {/* Probability Distribution */}
                    <div className="section-title">Xác suất phân bố 5 mức độ</div>
                    <div style={{ background: '#f8fafc', padding: '0.85rem 1rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                      {Object.entries(result.dr_result.probabilities).map(([className, prob], idx) => {
                        const isMax = idx === result.dr_result.stage;
                        return (
                          <div key={className} className="prob-item">
                            <div className="prob-meta">
                              <span style={{ fontWeight: isMax ? 700 : 500, color: isMax ? '#0f172a' : '#64748b' }}>
                                {className} {isMax && '★'}
                              </span>
                              <span style={{ fontWeight: isMax ? 700 : 500 }}>
                                {(prob * 100).toFixed(1)}%
                              </span>
                            </div>
                            <div className="prob-track">
                              <div 
                                className="prob-fill" 
                                style={{ 
                                  width: `${(prob * 100).toFixed(1)}%`,
                                  backgroundColor: STAGE_COLORS[idx]
                                }}
                              />
                            </div>
                          </div>
                        );
                      })}
                    </div>

                    <div style={{ marginTop: '0.75rem', fontSize: '0.75rem', color: '#94a3b8', textAlign: 'right' }}>
                      Mô hình: {result.dr_result.model_used} | {result.dr_result.benchmark_note}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <div className="container">
          Đề tài Khóa luận Tốt nghiệp: Hệ thống AI Phát hiện & Phân độ Võng mạc Đái tháo đường kết hợp Fundus Gate.
        </div>
      </footer>
    </div>
  );
}
