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
  Info,
  Cpu,
  Sparkles,
  Clock,
  RefreshCw,
  FileText,
  AlertCircle,
  Check,
  HelpCircle,
  BarChart3,
  Stethoscope
} from 'lucide-react';

const API_BASE = '/api';

const STAGE_COLORS = [
  '#10b981', // 0: Normal (Green)
  '#f59e0b', // 1: Mild (Yellow/Amber)
  '#f97316', // 2: Moderate (Orange)
  '#ef4444', // 3: Severe (Red)
  '#a855f7'  // 4: Proliferative (Purple)
];

const STAGE_VIETNAMESE = {
  0: 'Không có bệnh võng mạc (No DR)',
  1: 'Bệnh võng mạc tiểu đường nhẹ (Mild NPDR)',
  2: 'Bệnh võng mạc tiểu đường trung bình (Moderate NPDR)',
  3: 'Bệnh võng mạc tiểu đường nặng (Severe NPDR)',
  4: 'Bệnh võng mạc tiểu đường tăng sinh (Proliferative DR)'
};

const DISEASE_LABELS = {
  'DR': { vi: 'Bệnh võng mạc đái tháo đường', en: 'Diabetic Retinopathy', tag: 'Mạch máu' },
  'ARMD': { vi: 'Thoái hóa hoàng điểm do tuổi tác', en: 'Age-related Macular Degeneration', tag: 'Hoàng điểm' },
  'MYA': { vi: 'Cận thị thoái hóa võng mạc', en: 'Pathological Myopia', tag: 'Khúc xạ' },
  'DN': { vi: 'Lắng đọng Drusen', en: 'Drusen', tag: 'Lắng đọng' },
  'ERM': { vi: 'Màng trước võng mạc', en: 'Epiretinal Membrane', tag: 'Co kéo' },
  'BRVO': { vi: 'Tắc nhánh tĩnh mạch võng mạc', en: 'Branch Retinal Vein Occlusion', tag: 'Tắc mạch' },
  'LS': { vi: 'Sẹo quang đông Laser', en: 'Laser Scars', tag: 'Điều trị' },
  'ODC_GLAUCOMA': { vi: 'Lõm gai thị / Biến đổi glôcôm', en: 'Optic Disc Cupping / Glaucoma', tag: 'Gai thị' },
  'CRVO': { vi: 'Tắc tĩnh mạch trung tâm võng mạc', en: 'Central Retinal Vein Occlusion', tag: 'Tắc mạch' },
  'RISK': { vi: 'Tín hiệu phát hiện tổn thương tổng quát', en: 'General Disease Risk', tag: 'Sàng lọc' }
};

export default function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [samples, setSamples] = useState([]);
  const [sampleFilter, setSampleFilter] = useState('all');
  const [activeSampleInfo, setActiveSampleInfo] = useState(null);
  
  // Dashboard Navigation Tabs
  const [dashboardTab, setDashboardTab] = useState('overview'); // 'overview', 'model_b', 'model_c', 'explanation'
  const [activeHeatmapView, setActiveHeatmapView] = useState('compare'); // 'compare', 'vit', 'resnet', 'original'
  const [selectedDRModel, setSelectedDRModel] = useState('vit'); // 'vit' or 'resnet'
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
      setActiveSampleInfo(null);
      processFile(file);
    }
  };

  const processFile = (file) => {
    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
    setResult(null);
    setError(null);
    setDashboardTab('overview');
  };

  const handleSelectSample = async (sample) => {
    try {
      setLoading(true);
      setActiveSampleInfo(sample);
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
    setActiveSampleInfo(null);
    setDashboardTab('overview');
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
      
      // Auto-select best model for Model B
      if (data.dr_vit) {
        setSelectedDRModel('vit');
      } else {
        setSelectedDRModel('resnet');
      }
      setDashboardTab('overview');
    } catch (err) {
      setError(err.message || "Đã xảy ra lỗi khi phân tích ảnh.");
    } finally {
      setLoading(false);
    }
  };

  const currentDR = (selectedDRModel === 'vit' && result?.dr_vit) 
    ? result.dr_vit 
    : (result?.dr_resnet || result?.dr_result);

  const isAgreement = result?.dr_resnet && result?.dr_vit && (result.dr_resnet.stage === result.dr_vit.stage);

  return (
    <div className="app-shell">
      {/* Top Header */}
      <header className="app-header">
        <div className="container header-content">
          <div className="brand">
            <div className="brand-icon">
              <Eye size={22} />
            </div>
            <div>
              <div className="brand-title">RetinaGuard AI</div>
              <div className="brand-subtitle">Hệ thống Phân tích Đáy mắt & Sàng lọc Đa bệnh lý Võng mạc</div>
            </div>
          </div>
          
          <div className="header-badges">
            <div className="badge-pipeline">
              <ShieldCheck size={14} />
              <span>Model A: Fundus Gate (0.965)</span>
            </div>
            <div className="badge-pipeline badge-b">
              <Activity size={14} />
              <span>Model B: DR Severity (ViT & ResNet)</span>
            </div>
            <div className="badge-pipeline badge-c">
              <Stethoscope size={14} />
              <span>Model C: Multi-Label (E2 Harmonized)</span>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Banner */}
      <section className="hero">
        <div className="container">
          <div className="hero-tag">Khóa Luận Tốt Nghiệp Đại Học • Hệ Thống AI Y Tế</div>
          <h1>Nghiên cứu Vision Transformer và Sàng lọc <span>Đa Bệnh lý Võng mạc</span></h1>
          <p>
            Hệ thống tích hợp quy trình 3 giai đoạn độc lập: Xác thực ảnh đáy mắt hợp lệ qua <strong>Model A (Fundus Gate)</strong>, phân độ mức độ tổn thương võng mạc tiểu đường qua <strong>Model B (ViT-B/16 & ResNet-50)</strong> kết hợp XAI Heatmaps, và sàng lọc đồng mắc 10 nhóm bệnh lý võng mạc qua <strong>Model C (EfficientNet-B0 E2)</strong>.
          </p>
        </div>
      </section>

      {/* Main Workspace */}
      <main className="container workspace-container">
        <div className="main-grid">
          {/* Left Column: Image Upload & Preview Controls */}
          <div className="card upload-card">
            <div className="card-header">
              <div className="card-title">
                <Upload size={18} className="text-primary" />
                <span>Nạp ảnh chụp đáy võng mạc</span>
              </div>
              {result && (
                <button className="btn-text-reset" onClick={handleClear} title="Đặt lại ảnh">
                  <RefreshCw size={14} />
                  <span>Chọn ảnh mới</span>
                </button>
              )}
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
                <div className="dropzone-icon-box">
                  <Upload className="upload-icon" />
                </div>
                <h3 className="dropzone-heading">Kéo thả ảnh hoặc bấm để chọn tệp</h3>
                <p className="dropzone-desc">
                  Hỗ trợ: JPEG, PNG, WEBP (Ảnh đáy võng mạc hoặc ảnh bất kỳ để kiểm thử cổng Gate)
                </p>
                <span className="btn-browse">Chọn tệp từ thiết bị</span>
              </div>
            ) : (
              <div className="preview-wrapper">
                <div className="preview-container">
                  <img src={previewUrl} alt="Ảnh đáy mắt nạp vào" className="preview-img" />
                  <button className="btn-remove" onClick={handleClear}>✕ Đổi ảnh khác</button>
                </div>
                <div className="image-info-bar">
                  <span className="file-name">{selectedFile?.name || 'fundus_sample.jpg'}</span>
                  {selectedFile?.size && (
                    <span className="file-size">{(selectedFile.size / 1024).toFixed(1)} KB</span>
                  )}
                </div>
              </div>
            )}

            <input 
              type="file" 
              ref={fileInputRef} 
              style={{ display: 'none' }} 
              accept="image/*"
              onChange={handleFileChange}
            />

            {/* Clinical Preset Samples */}
            {samples.length > 0 && (
              <div className="samples-bar">
                <div className="samples-header-row">
                  <div className="samples-label">
                    <Layers size={14} />
                    <span>Bộ sưu tập ảnh mẫu kiểm định lâm sàng:</span>
                  </div>
                  <span className="samples-count-pill">{samples.length} mẫu</span>
                </div>

                {/* Filter Category Chips */}
                <div className="sample-filter-chips">
                  {[
                    { id: 'all', label: 'Tất cả' },
                    { id: 'Bệnh võng mạc khác', label: 'Bệnh lý khác (AMD, Glaucoma, MYA, BRVO)' },
                    { id: 'Đái tháo đường (DR)', label: 'Tiểu đường (DR)' },
                    { id: 'Khỏe mạnh', label: 'Khỏe mạnh' },
                  ].map(f => (
                    <button
                      key={f.id}
                      type="button"
                      className={`chip-btn ${sampleFilter === f.id ? 'chip-active' : ''}`}
                      onClick={() => setSampleFilter(f.id)}
                    >
                      {f.label}
                    </button>
                  ))}
                </div>

                {/* Grid of Samples */}
                <div className="samples-grid">
                  {samples
                    .filter(s => sampleFilter === 'all' || s.category === sampleFilter)
                    .map((s) => (
                      <div 
                        key={s.id} 
                        className={`sample-card ${previewUrl && selectedFile?.name === s.filename ? 'sample-active' : ''}`}
                        onClick={() => handleSelectSample(s)}
                        title={`${s.name} - ${s.description || ''}`}
                      >
                        <div className="sample-thumb-wrapper">
                          <img 
                            src={s.url} 
                            alt={s.filename} 
                            className="sample-thumb"
                          />
                          {s.tag && (
                            <span className={`sample-mini-tag tag-${s.badge_color || 'blue'}`}>
                              {s.tag}
                            </span>
                          )}
                        </div>
                        <span className="sample-name" title={s.name}>{s.name}</span>
                      </div>
                    ))}
                </div>

                {/* Active Sample Clinical Info Box */}
                {activeSampleInfo && (
                  <div className="sample-active-info-box">
                    <div className="sample-info-header">
                      <span className={`sample-mini-tag tag-${activeSampleInfo.badge_color || 'blue'}`}>
                        {activeSampleInfo.tag}
                      </span>
                      <strong className="sample-info-title">{activeSampleInfo.name}</strong>
                    </div>
                    <p className="sample-info-desc">{activeSampleInfo.description}</p>
                  </div>
                )}
              </div>
            )}

            {/* Action CTA Button */}
            <button 
              className="btn-analyze"
              disabled={!selectedFile || loading}
              onClick={handleAnalyze}
            >
              {loading ? (
                <>
                  <div className="spinner"></div>
                  <span>Đang thực thi Models A + B + C song song...</span>
                </>
              ) : (
                <>
                  <Activity size={18} />
                  <span>Phân tích Toàn diện (Models A + B + C)</span>
                </>
              )}
            </button>

            {error && (
              <div className="alert-error">
                <AlertCircle size={18} className="flex-shrink-0" />
                <div>
                  <strong>Thông báo lỗi:</strong> {error}
                </div>
              </div>
            )}

            {/* Model Pipeline Specs Note */}
            <div className="pipeline-specs-note">
              <div className="specs-title">
                <Info size={14} />
                <span>Quy chuẩn công nghệ độc lập:</span>
              </div>
              <p>Mỗi mô hình sử dụng tiền xử lý và mạng nơ-ron riêng biệt. Không có mô hình nào ghi đè hoặc giả lập kết quả của mô hình khác.</p>
            </div>
          </div>

          {/* Right Column: Multi-Model AI Diagnostic Dashboard */}
          <div className="card results-card">
            <div className="card-header">
              <div className="card-title">
                <Layers size={18} className="text-primary" />
                <span>Bảng điều khiển Kết quả Chẩn đoán Y khoa</span>
              </div>
              {result && (
                <div className="processing-badge">
                  <Clock size={12} />
                  <span>{result.processing_time_ms ? `${result.processing_time_ms} ms` : 'Hoàn tất'}</span>
                </div>
              )}
            </div>

            {/* State: Empty */}
            {!result && !loading && (
              <div className="empty-state">
                <div className="empty-icon-circle">
                  <Eye size={42} strokeWidth={1.5} />
                </div>
                <h4>Hệ thống sẵn sàng tiếp nhận ảnh</h4>
                <p>
                  Vui lòng tải ảnh lên hoặc chọn ảnh mẫu bên trái, sau đó nhấn nút <strong>"Phân tích Toàn diện"</strong> để khởi chạy đồng thời cả 3 mô hình AI.
                </p>
                <div className="empty-feature-list">
                  <div className="feature-item">✓ Model A kiểm tra ảnh đáy mắt hợp lệ</div>
                  <div className="feature-item">✓ Model B phân độ 5 cấp DR & sinh Heatmap</div>
                  <div className="feature-item">✓ Model C sàng lọc 10 bệnh lý võng mạc</div>
                </div>
              </div>
            )}

            {/* State: Processing */}
            {loading && (
              <div className="loading-state">
                <div className="loading-spinner-box">
                  <div className="spinner-large"></div>
                </div>
                <h4>Đang tiến hành chẩn đoán đa mô hình...</h4>
                <p className="loading-step">
                  Giai đoạn 1: MobileNetV3 Fundus Gate kiểm định chất lượng quang học...<br />
                  Giai đoạn 2: ResNet-50 & ViT-B/16 trích xuất tổn thương vi phình mạch...<br />
                  Giai đoạn 3: EfficientNet-B0 E2 quét 10 nhóm bệnh lý võng mạc đồng mắc...
                </p>
              </div>
            )}

            {/* State: Results Available */}
            {result && (
              <div className="results-container">
                {/* Stage 1: Fundus Gate Rejection or Pass Banner */}
                <div className={`gate-banner ${result.is_fundus ? 'gate-pass' : 'gate-reject'}`}>
                  <div className="gate-icon-col">
                    {result.is_fundus ? <CheckCircle2 size={24} /> : <XCircle size={24} />}
                  </div>
                  <div className="gate-content-col">
                    <div className="gate-badge">
                      Giai đoạn 1: Model A (Fundus Gate MobileNetV3) • {result.is_fundus ? 'HỢP LỆ (PASS)' : 'TỪ CHỐI (REJECT)'}
                    </div>
                    <div className="gate-desc">
                      {result.message}
                    </div>
                    <div className="gate-meta">
                      Độ tin cậy đáy mắt: <strong>{(result.fundus_confidence * 100).toFixed(2)}%</strong> 
                      <span className="meta-sep">•</span> 
                      Ngưỡng an toàn quy định: <strong>{(result.threshold * 100).toFixed(2)}%</strong>
                    </div>
                  </div>
                </div>

                {/* If Image was rejected, stop pipeline and show notice */}
                {!result.is_fundus && (
                  <div className="rejection-card">
                    <div className="rejection-title">
                      <AlertTriangle size={18} />
                      <span>Pipeline tự động dừng: Bảo vệ an toàn chẩn đoán y khoa</span>
                    </div>
                    <p className="rejection-p">
                      Hệ thống tuân thủ nghiêm ngặt nguyên tắc lâm sàng: Khi ảnh đầu vào không đạt tiêu chuẩn chụp đáy võng mạc, <strong>Model B và Model C sẽ không được kích hoạt</strong> nhằm ngăn chặn tuyệt đối hiện tượng chẩn đoán sai lệch (false positives).
                    </p>
                    <button className="btn-re-upload" onClick={() => fileInputRef.current?.click()}>
                      Tải lên ảnh chụp đáy võng mạc hợp lệ khác
                    </button>
                  </div>
                )}

                {/* If Image is Valid, show full Multi-Model Dashboard */}
                {result.is_fundus && (
                  <div className="dashboard-content">
                    {/* Navigation Tabs */}
                    <div className="dashboard-nav-tabs">
                      <button 
                        className={`dash-tab ${dashboardTab === 'overview' ? 'active' : ''}`}
                        onClick={() => setDashboardTab('overview')}
                      >
                        <BarChart3 size={15} />
                        <span>Tổng quan Chẩn đoán</span>
                      </button>
                      <button 
                        className={`dash-tab ${dashboardTab === 'model_b' ? 'active' : ''}`}
                        onClick={() => setDashboardTab('model_b')}
                      >
                        <Activity size={15} />
                        <span>Model B: Phân độ DR & XAI</span>
                      </button>
                      <button 
                        className={`dash-tab ${dashboardTab === 'model_c' ? 'active' : ''}`}
                        onClick={() => setDashboardTab('model_c')}
                      >
                        <Stethoscope size={15} />
                        <span>Model C: Sàng lọc Đa bệnh lý</span>
                      </button>
                      <button 
                        className={`dash-tab ${dashboardTab === 'explanation' ? 'active' : ''}`}
                        onClick={() => setDashboardTab('explanation')}
                      >
                        <HelpCircle size={15} />
                        <span>Giải thích & Disclaimer</span>
                      </button>
                    </div>

                    {/* TAB 1: EXECUTIVE OVERVIEW */}
                    {dashboardTab === 'overview' && (
                      <div className="tab-pane">
                        <div className="overview-summary-grid">
                          {/* Card 1: DR Staging (Model B) */}
                          <div className="summary-card model-b-summary">
                            <div className="summary-header">
                              <span className="summary-tag tag-b">Model B • DR Staging</span>
                              {currentDR && (
                                <span className={`stage-badge stage-${currentDR.stage}`}>
                                  {currentDR.badge}
                                </span>
                              )}
                            </div>
                            {currentDR ? (
                              <div className="summary-body">
                                <h3 className="summary-title">{currentDR.stage_name}</h3>
                                <p className="summary-desc">{currentDR.description}</p>
                                <div className="summary-confidence">
                                  <span>Độ tự tin phân loại ({currentDR.model_used}):</span>
                                  <strong>{(currentDR.confidence * 100).toFixed(1)}%</strong>
                                </div>
                              </div>
                            ) : (
                              <div className="summary-error">
                                {result.dr_error || "Mô hình DR không khả dụng"}
                              </div>
                            )}
                            <button className="btn-card-link" onClick={() => setDashboardTab('model_b')}>
                              <span>Xem biểu đồ & Heatmap XAI</span>
                              <ChevronRight size={14} />
                            </button>
                          </div>

                          {/* Card 2: Multi-Label Screening (Model C) */}
                          <div className="summary-card model-c-summary">
                            <div className="summary-header">
                              <span className="summary-tag tag-c">Model C • Multi-Label</span>
                              {result.model_c_result && (
                                <span className={`risk-pill ${result.model_c_result.overall_disease_risk ? 'risk-active' : 'risk-normal'}`}>
                                  {result.model_c_result.overall_disease_risk ? 'Cảnh báo Bệnh võng mạc' : 'Võng mạc Bình thường'}
                                </span>
                              )}
                            </div>
                            {result.model_c_result ? (
                              <div className="summary-body">
                                <h3 className="summary-title">
                                  {result.model_c_result.overall_disease_risk 
                                    ? `Phát hiện ${result.model_c_result.num_detected_conditions} nhóm dấu hiệu bệnh lý`
                                    : 'Không phát hiện bất thường ngoài vùng an toàn'
                                  }
                                </h3>
                                {result.model_c_result.detected_diseases.length > 0 ? (
                                  <div className="detected-chips-wrap">
                                    {result.model_c_result.detected_diseases.map(d => (
                                      <span key={d.code} className="detected-chip">
                                        <strong>{d.code}</strong>: {d.name} ({d.confidence_pct}%)
                                      </span>
                                    ))}
                                  </div>
                                ) : (
                                  <p className="summary-desc">Các bệnh lý như thoái hóa hoàng điểm (ARMD), cận thị thoái hóa (MYA), drusen (DN) đều nằm dưới ngưỡng cảnh báo.</p>
                                )}
                                <div className="summary-confidence">
                                  <span>Mô hình: {result.model_c_result.model_name}</span>
                                </div>
                              </div>
                            ) : (
                              <div className="summary-error">
                                {result.model_c_error || "Mô hình Model C không khả dụng"}
                              </div>
                            )}
                            <button className="btn-card-link" onClick={() => setDashboardTab('model_c')}>
                              <span>Xem 10 nhóm bệnh lý & Ngưỡng cắt</span>
                              <ChevronRight size={14} />
                            </button>
                          </div>
                        </div>

                        {/* Pipeline Status Breakdown Box */}
                        <div className="system-status-box">
                          <div className="status-box-title">
                            <ShieldCheck size={16} />
                            <span>Trạng thái Hoạt động của 3 Mô hình Độc lập</span>
                          </div>
                          <div className="status-grid">
                            <div className="status-col">
                              <span className="col-label">Model A (Fundus Gate):</span>
                              <span className="col-val val-green">✓ Hoạt động ({result.model_status?.model_a || 'ready'})</span>
                            </div>
                            <div className="status-col">
                              <span className="col-label">Model B (DR Classifier):</span>
                              <span className="col-val val-green">✓ Hoạt động ({result.model_status?.model_b || 'ready'})</span>
                            </div>
                            <div className="status-col">
                              <span className="col-label">Model C (Retinal Multi-Label):</span>
                              <span className="col-val val-green">✓ Hoạt động ({result.model_status?.model_c || 'ready'})</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* TAB 2: MODEL B (DR SEVERITY & GRAD-CAM) */}
                    {dashboardTab === 'model_b' && (
                      <div className="tab-pane">
                        {currentDR ? (
                          <div>
                            {/* Agreement Banner */}
                            {result.dr_resnet && result.dr_vit && (
                              <div className={`agreement-banner ${isAgreement ? 'agree-yes' : 'agree-diff'}`}>
                                {isAgreement ? <CheckCircle2 size={18} className="flex-shrink-0" /> : <AlertTriangle size={18} className="flex-shrink-0" />}
                                <div>
                                  {isAgreement ? (
                                    <div>
                                      <strong>Đồng thuận Song Kiến trúc:</strong> Cả ResNet-50 (CNN) và ViT-B/16 (Transformer) đều chẩn đoán đồng nhất ở <strong>Độ {result.dr_resnet.stage} ({result.dr_resnet.badge})</strong>.
                                    </div>
                                  ) : (
                                    <div>
                                      <strong>Chẩn đoán Phân biệt giữa 2 Kiến trúc:</strong> ResNet-50 phân độ <strong>Độ {result.dr_resnet.stage} ({result.dr_resnet.badge})</strong> | ViT-B/16 phân độ <strong>Độ {result.dr_vit.stage} ({result.dr_vit.badge})</strong>. Khuyến nghị bác sĩ đối chiếu bản đồ nhiệt của cả 2 mô hình.
                                    </div>
                                  )}
                                </div>
                              </div>
                            )}

                            {/* Heatmap Selector & Viewer */}
                            <div className="heatmap-section">
                              <div className="section-label">
                                <Sparkles size={14} />
                                <span>Trực quan hóa Bản đồ nhiệt Chú ý (XAI Grad-CAM Heatmaps)</span>
                              </div>

                              <div className="view-tabs">
                                {result.dr_resnet?.heatmap_base64 && result.dr_vit?.heatmap_base64 && (
                                  <button 
                                    className={`view-tab ${activeHeatmapView === 'compare' ? 'active' : ''}`}
                                    onClick={() => setActiveHeatmapView('compare')}
                                  >
                                    👁️ So sánh 2 Heatmap song song
                                  </button>
                                )}
                                {result.dr_vit?.heatmap_base64 && (
                                  <button 
                                    className={`view-tab ${activeHeatmapView === 'vit' ? 'active' : ''}`}
                                    onClick={() => setActiveHeatmapView('vit')}
                                  >
                                    ✨ ViT-B/16 (Transformer Attention)
                                  </button>
                                )}
                                {result.dr_resnet?.heatmap_base64 && (
                                  <button 
                                    className={`view-tab ${activeHeatmapView === 'resnet' ? 'active' : ''}`}
                                    onClick={() => setActiveHeatmapView('resnet')}
                                  >
                                    ⚡ ResNet-50 (CNN Grad-CAM)
                                  </button>
                                )}
                                <button 
                                  className={`view-tab ${activeHeatmapView === 'original' ? 'active' : ''}`}
                                  onClick={() => setActiveHeatmapView('original')}
                                >
                                  📷 Ảnh gốc (RGB 256x256)
                                </button>
                              </div>

                              {/* View Content */}
                              {activeHeatmapView === 'compare' && result.dr_resnet?.heatmap_base64 && result.dr_vit?.heatmap_base64 ? (
                                <div className="dual-heatmap-grid">
                                  <div className="heatmap-box">
                                    <div className="heatmap-title">ResNet-50 (CNN Grad-CAM)</div>
                                    <img src={result.dr_resnet.heatmap_base64} alt="ResNet Heatmap" className="heatmap-img" />
                                    <div className="heatmap-caption">Trọng tâm: Vùng vi phình mạch & xuất huyết cục bộ</div>
                                    <div className={`stage-badge stage-${result.dr_resnet.stage}`}>
                                      Độ {result.dr_resnet.stage}: {result.dr_resnet.badge}
                                    </div>
                                  </div>
                                  <div className="heatmap-box">
                                    <div className="heatmap-title">ViT-B/16 (Transformer Attention)</div>
                                    <img src={result.dr_vit.heatmap_base64} alt="ViT Heatmap" className="heatmap-img" />
                                    <div className="heatmap-caption">Trọng tâm: Tương quan toàn võng mạc (Self-Attention)</div>
                                    <div className={`stage-badge stage-${result.dr_vit.stage}`}>
                                      Độ {result.dr_vit.stage}: {result.dr_vit.badge}
                                    </div>
                                  </div>
                                </div>
                              ) : (
                                <div className="single-heatmap-box">
                                  <img 
                                    src={
                                      activeHeatmapView === 'vit' && result.dr_vit?.heatmap_base64 
                                        ? result.dr_vit.heatmap_base64 
                                        : activeHeatmapView === 'resnet' && result.dr_resnet?.heatmap_base64
                                        ? result.dr_resnet.heatmap_base64
                                        : previewUrl
                                    } 
                                    alt="Heatmap View" 
                                    className="heatmap-img"
                                  />
                                </div>
                              )}
                              <p className="heatmap-note">
                                * Vùng màu đỏ/cam biểu thị khu vực các mạng nơ-ron tập trung trọng số kích hoạt khi đưa ra quyết định phân loại tổn thương.
                              </p>
                            </div>

                            {/* Model Details Selector */}
                            <div className="model-details-card">
                              <div className="model-tab-buttons">
                                {result.dr_vit && (
                                  <button 
                                    className={`model-subtab ${selectedDRModel === 'vit' ? 'active' : ''}`}
                                    onClick={() => setSelectedDRModel('vit')}
                                  >
                                    <Sparkles size={14} />
                                    <span>Vision Transformer ViT-B/16</span>
                                  </button>
                                )}
                                {result.dr_resnet && (
                                  <button 
                                    className={`model-subtab ${selectedDRModel === 'resnet' ? 'active' : ''}`}
                                    onClick={() => setSelectedDRModel('resnet')}
                                  >
                                    <Cpu size={14} />
                                    <span>ResNet-50 Baseline</span>
                                  </button>
                                )}
                              </div>

                              <div className="dr-detail-header">
                                <div>
                                  <span className="dr-model-tag">Mô hình: {currentDR.model_used}</span>
                                  <h2 className="dr-stage-h2">{currentDR.stage_name}</h2>
                                </div>
                                <div className={`stage-badge stage-${currentDR.stage}`}>
                                  {currentDR.badge}
                                </div>
                              </div>

                              <div className="detail-box">
                                <span className="detail-box-title">Đặc điểm tổn thương võng mạc:</span>
                                <p>{currentDR.description}</p>
                              </div>

                              <div className="detail-box advice-box">
                                <span className="detail-box-title">Khuyến nghị can thiệp lâm sàng:</span>
                                <p>{currentDR.advice}</p>
                              </div>

                              {/* 5-Grade Probability Bar Chart */}
                              <div className="prob-section">
                                <span className="prob-section-title">Phân bố xác suất 5 mức độ theo ICDR ({currentDR.model_used}):</span>
                                <div className="prob-list">
                                  {Object.entries(currentDR.probabilities).map(([cName, pVal], idx) => {
                                    const isMax = idx === currentDR.stage;
                                    return (
                                      <div key={cName} className={`prob-row ${isMax ? 'prob-highlight' : ''}`}>
                                        <div className="prob-row-meta">
                                          <span className="prob-class-name">
                                            {cName} {isMax && '★ (Dự đoán)'}
                                          </span>
                                          <span className="prob-pct">{(pVal * 100).toFixed(1)}%</span>
                                        </div>
                                        <div className="prob-track">
                                          <div 
                                            className="prob-fill" 
                                            style={{ 
                                              width: `${(pVal * 100).toFixed(1)}%`,
                                              backgroundColor: STAGE_COLORS[idx]
                                            }}
                                          />
                                        </div>
                                      </div>
                                    );
                                  })}
                                </div>
                              </div>
                            </div>
                          </div>
                        ) : (
                          <div className="alert-error">
                            <AlertCircle size={18} />
                            <span>{result.dr_error || "Mô hình phân độ DR không khả dụng"}</span>
                          </div>
                        )}
                      </div>
                    )}

                    {/* TAB 3: MODEL C (MULTI-LABEL RETINAL SCREENING) */}
                    {dashboardTab === 'model_c' && (
                      <div className="tab-pane">
                        {result.model_c_result ? (
                          <div>
                            {/* Model C Header Info */}
                            <div className="model-c-header-card">
                              <div className="c-header-left">
                                <span className="c-badge">Model C • Multi-Source Retinal Classifier</span>
                                <h2>Sàng lọc 10 Nhóm Dấu hiệu Bệnh lý Võng mạc</h2>
                                <p className="c-subtitle">
                                  Kiến trúc: EfficientNet-B0 được huấn luyện từ dữ liệu hợp nhất RFMiD + ODIR-5K có điều hòa ngữ nghĩa. Ngưỡng phân loại được tối ưu hóa chuẩn mực từ tập Validation.
                                </p>
                              </div>
                              <div className="c-header-right">
                                <span className="c-version">{result.model_c_result.model_version}</span>
                                <span className="c-epoch">Epoch: {result.model_c_result.checkpoint_meta?.epoch || 'best'}</span>
                              </div>
                            </div>

                            {/* Overall Disease Risk Screening Banner */}
                            <div className={`risk-banner ${result.model_c_result.overall_disease_risk ? 'risk-banner-pos' : 'risk-banner-neg'}`}>
                              <div className="risk-banner-icon">
                                {result.model_c_result.overall_disease_risk ? <AlertTriangle size={24} /> : <CheckCircle2 size={24} />}
                              </div>
                              <div className="risk-banner-text">
                                <h3>
                                  Tín hiệu Sàng lọc Bất thường (General Risk): {result.model_c_result.overall_disease_risk ? 'CÓ DẤU HIỆU BỆNH LÝ (POSITIVE)' : 'KHÔNG PHÁT HIỆN BẤT THƯỜNG (NEGATIVE)'}
                                </h3>
                                <p>
                                  * Lưu ý học thuật: <code>RISK</code> đóng vai trò là cờ báo động sàng lọc sơ bộ (screening flag), không phải là một bệnh lý giải phẫu độc lập. Kết quả phản ánh tổng thể võng mạc có xuất hiện tổn thương nghi vấn cần hội chẩn y khoa hay không.
                                </p>
                              </div>
                            </div>

                            {/* Detected Conditions Summary List */}
                            <div className="detected-summary-section">
                              <div className="section-label">
                                <Check size={16} />
                                <span>Các nhóm bệnh lý vượt ngưỡng phát hiện ({result.model_c_result.num_detected_conditions} bệnh):</span>
                              </div>
                              
                              {result.model_c_result.detected_diseases.length > 0 ? (
                                <div className="detected-cards-grid">
                                  {result.model_c_result.detected_diseases.map(d => (
                                    <div key={d.code} className="detected-item-card">
                                      <div className="item-card-top">
                                        <span className="code-pill">{d.code}</span>
                                        <span className="conf-pill">{d.confidence_pct}%</span>
                                      </div>
                                      <h4 className="item-name">{d.name}</h4>
                                      <p className="item-desc">{d.vietnamese_desc}</p>
                                      <div className="item-thresh-info">
                                        Xác suất: <strong>{d.probability ?? (d.confidence_pct/100).toFixed(4)}</strong> | Ngưỡng cắt: <strong>{d.threshold ?? '0.1600'}</strong>
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              ) : (
                                <div className="no-diseases-box">
                                  ✓ Không có bệnh lý riêng lẻ nào vượt ngưỡng cảnh báo (Tất cả 10 lớp đều nằm dưới ngưỡng quyết định).
                                </div>
                              )}
                            </div>

                            {/* Full 10-Class Disease Screening Table */}
                            <div className="full-classes-section">
                              <div className="section-label">
                                <BarChart3 size={16} />
                                <span>Bảng đối soát chi tiết xác suất & ngưỡng quyết định (10 Nhóm bệnh lý):</span>
                              </div>

                              <div className="classes-table-wrap">
                                <table className="classes-table">
                                  <thead>
                                    <tr>
                                      <th>Mã</th>
                                      <th>Tên Bệnh lý (Anh / Việt)</th>
                                      <th>Xác suất dự đoán</th>
                                      <th>Ngưỡng quyết định (τ)</th>
                                      <th>Trực quan hóa</th>
                                      <th>Kết luận sàng lọc</th>
                                    </tr>
                                  </thead>
                                  <tbody>
                                    {Object.entries(result.model_c_result.full_probabilities).map(([code, pInfo]) => {
                                      const meta = DISEASE_LABELS[code] || { vi: pInfo.disease_name, en: pInfo.disease_name, tag: 'Chung' };
                                      const isPos = pInfo.detected;
                                      const probPct = (pInfo.probability * 100).toFixed(1);
                                      const threshPct = (pInfo.threshold * 100).toFixed(1);
                                      return (
                                        <tr key={code} className={isPos ? 'row-detected' : ''}>
                                          <td className="td-code">
                                            <strong>{code}</strong>
                                            <span className="tag-micro">{meta.tag}</span>
                                          </td>
                                          <td className="td-name">
                                            <div className="name-vi">{meta.vi}</div>
                                            <div className="name-en">{meta.en}</div>
                                          </td>
                                          <td className="td-prob">
                                            <strong>{(pInfo.probability).toFixed(4)}</strong>
                                            <span className="prob-pct-sub">({probPct}%)</span>
                                          </td>
                                          <td className="td-thresh">
                                            <span>{(pInfo.threshold).toFixed(4)}</span>
                                            <span className="thresh-pct-sub">({threshPct}%)</span>
                                          </td>
                                          <td className="td-bar">
                                            <div className="bar-track-wrap">
                                              {/* Threshold marker */}
                                              <div 
                                                className="thresh-marker" 
                                                style={{ left: `${Math.min(100, pInfo.threshold * 100)}%` }}
                                                title={`Ngưỡng τ = ${pInfo.threshold}`}
                                              />
                                              {/* Probability bar */}
                                              <div 
                                                className={`bar-fill-c ${isPos ? 'fill-positive' : 'fill-negative'}`}
                                                style={{ width: `${Math.min(100, pInfo.probability * 100)}%` }}
                                              />
                                            </div>
                                          </td>
                                          <td className="td-status">
                                            {isPos ? (
                                              <span className="badge-pos">● Phát hiện</span>
                                            ) : (
                                              <span className="badge-neg">○ Bình thường</span>
                                            )}
                                          </td>
                                        </tr>
                                      );
                                    })}
                                  </tbody>
                                </table>
                              </div>
                            </div>
                          </div>
                        ) : (
                          <div className="alert-error">
                            <AlertCircle size={18} />
                            <span>{result.model_c_error || "Mô hình Model C không khả dụng"}</span>
                          </div>
                        )}
                      </div>
                    )}

                    {/* TAB 4: CLINICAL EXPLANATION & DISCLAIMER */}
                    {dashboardTab === 'explanation' && (
                      <div className="tab-pane">
                        <div className="explanation-card">
                          <div className="exp-section">
                            <h3>
                              <ShieldCheck size={18} className="text-primary" />
                              <span>Nguyên tắc Phối hợp Độc lập giữa Model B và Model C</span>
                            </h3>
                            <p>
                              Hệ thống thiết kế theo kiến trúc <strong>phân ly nhiệm vụ độc lập (Decoupled Task Architecture)</strong>:
                            </p>
                            <ul>
                              <li>
                                <strong>Model B (DR Staging)</strong>: Chuyên trách đánh giá mức độ tổn thương võng mạc tiểu đường theo 5 giai đoạn chuẩn quốc tế (từ Độ 0 - Không bệnh đến Độ 4 - Tăng sinh). Mô hình được huấn luyện theo cơ chế thứ bậc (Ordinal Classification) và cung cấp bản đồ nhiệt Grad-CAM giúp giải thích vùng tổn thương.
                              </li>
                              <li>
                                <strong>Model C (Retinal Multi-Label)</strong>: Chuyên trách phát hiện đa bệnh lý đồng mắc (comorbidities) như thoái hóa hoàng điểm (ARMD), cận thị thoái hóa (MYA), màng trước võng mạc (ERM), biến đổi glôcôm (ODC) hoặc lắng đọng Drusen.
                              </li>
                              <li>
                                <strong>Không triệt tiêu hoặc ghi đè kết quả</strong>: Nếu Model B dự đoán Grade 0 (không có DR), điều này không đồng nghĩa bệnh nhân hoàn toàn không có bệnh mắt khác. Ngược lại, nếu Model C báo phát hiện DR, nhãn này chỉ đóng vai trò sàng lọc nhị phân và không làm thay đổi phân độ chi tiết của Model B.
                              </li>
                            </ul>
                          </div>

                          <div className="exp-section disclaimer-section">
                            <div className="disclaimer-header">
                              <AlertTriangle size={20} className="text-warning" />
                              <h4>Tuyên bố Miễn trừ Trách nhiệm Y khoa (Official Medical Disclaimer)</h4>
                            </div>
                            <blockquote className="disclaimer-quote">
                              {result.clinical_disclaimer || "Ứng dụng được phát triển phục vụ nghiên cứu khóa luận tốt nghiệp. Kết quả từ mô hình AI chỉ mang tính chất hỗ trợ sàng lọc và không thay thế kết luận của bác sĩ chuyên khoa mắt."}
                            </blockquote>
                            <p className="disclaimer-note">
                              Hệ thống được phát triển phục vụ mục đích nghiên cứu học thuật, nghiên cứu đối chuẩn mô hình thị giác máy tính và hỗ trợ kỹ thuật số cho sinh viên, học viên nhãn khoa. Mọi quyết định can thiệp lâm sàng hoặc phẫu thuật bắt buộc phải được chỉ định trực tiếp bởi bác sĩ nhãn khoa qua thăm khám đèn khe và chụp mạch huỳnh quang.
                            </p>
                          </div>
                        </div>
                      </div>
                    )}
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
          <div className="footer-content">
            <div>
              <strong>Khóa luận Tốt nghiệp Đại học</strong> • Đề tài: Nghiên cứu Vision Transformer và ứng dụng phân loại mức độ bệnh võng mạc đái tháo đường từ ảnh đáy võng mạc mắt.
            </div>
            <div className="footer-sub">
              Tích hợp 3 Mô hình Độc lập: Model A (MobileNetV3 Gate) • Model B (ResNet-50 & ViT-B/16 Hybrid) • Model C (EfficientNet-B0 E2 Multi-Label).
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
