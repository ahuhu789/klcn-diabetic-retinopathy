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
  HelpCircle,
  BarChart3
} from 'lucide-react';

const API_BASE = '/api';

const STAGE_COLORS = [
  '#10b981',
  '#f59e0b',
  '#f97316',
  '#ef4444',
  '#a855f7',
  '#64748b'
];

const BRANCH_LABELS = {
  vit3: 'ViT-B/16-384',
  effb4: 'EfficientNet-B4-448',
  e_twohead: 'EfficientNet-B4 hai đầu ra',
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
  const [dashboardTab, setDashboardTab] = useState('overview');
  const [activeHeatmapView, setActiveHeatmapView] = useState('compare');
  const [selectedDRModel, setSelectedDRModel] = useState('ensemble');
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
      
      setSelectedDRModel('ensemble');
      setActiveHeatmapView('ensemble');
      setDashboardTab('overview');
    } catch (err) {
      setError(err.message || "Đã xảy ra lỗi khi phân tích ảnh.");
    } finally {
      setLoading(false);
    }
  };

  // Model B v3: ensemble + 3 branches (ViT-B/16-384, EffB4-448, EffB4-448 two-head).
  const branches = (result?.dr_branches && result.dr_branches.length)
    ? result.dr_branches
    : [result?.dr_vit, result?.dr_effb4, result?.dr_twohead].filter(Boolean);
  const branchLabel = (b) => BRANCH_LABELS[b?.branch] || b?.model_used || 'Nhánh';
  const fmtWeight = (b) => (typeof b?.weight === 'number' ? b.weight.toFixed(2) : '?');
  const selectedBranch = branches.find((b) => b.branch === selectedDRModel);
  const currentDR = selectedDRModel !== 'ensemble' && selectedBranch
    ? selectedBranch
    : (result?.dr_result || branches[0]);
  const heatmapBranch = branches.find((b) => b.branch === activeHeatmapView);

  const isAgreement = branches.length > 0 && result?.dr_result && branches.every((b) => b.stage === result.dr_result.stage);

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
              <div className="brand-subtitle">Cổng ảnh đáy mắt và phân loại 6 lớp</div>
            </div>
          </div>
          
          <div className="header-badges">
            <div className="badge-pipeline">
              <ShieldCheck size={14} />
              <span>Model A: Fundus Gate (0.965)</span>
            </div>
            <div className="badge-pipeline badge-b">
              <Activity size={14} />
              <span>Model B: Ensemble 3 mô hình (0.45 / 0.40 / 0.15)</span>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Banner */}
      <section className="hero">
        <div className="container">
          <div className="hero-tag">Khóa Luận Tốt Nghiệp Đại Học • Hệ Thống AI Y Tế</div>
          <h1>Nghiên cứu Vision Transformer và phân loại <span>6 lớp ảnh đáy mắt</span></h1>
          <p>
            Ảnh đi qua <strong>Model A (Fundus Gate, τ = 0.965)</strong> trên ảnh gốc. Nếu hợp lệ, <strong>Model B</strong> áp Ben Graham 512 rồi ensemble ViT-B/16-384 (0.45), EfficientNet-B4-448 (0.40) và EfficientNet-B4-448 hai đầu ra (0.15). Lớp 0–4 là thang DR. Lớp 5 là nhóm tổn thương không phải DR, không phải tên một bệnh.
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
                  Vui lòng tải ảnh lên hoặc chọn ảnh mẫu bên trái, sau đó nhấn nút <strong>"Phân tích Toàn diện"</strong>.
                </p>
                <div className="empty-feature-list">
                  <div className="feature-item">✓ Model A kiểm tra ảnh đáy mắt hợp lệ</div>
                  <div className="feature-item">✓ Model B phân loại 6 lớp sau tiền xử lý Ben Graham</div>
                  <div className="feature-item">✓ Kết quả báo cáo là ensemble ViT 0.45 + EffB4 0.40 + EffB4 hai đầu ra 0.15</div>
                </div>
              </div>
            )}

            {/* State: Processing */}
            {loading && (
              <div className="loading-state">
                <div className="loading-spinner-box">
                  <div className="spinner-large"></div>
                </div>
                <h4>Đang phân tích ảnh...</h4>
                <p className="loading-step">
                  Giai đoạn 1: MobileNetV3 kiểm tra ảnh đáy mắt trên ảnh gốc...<br />
                  Giai đoạn 2: Ben Graham 512, rồi ViT-B/16-384, EfficientNet-B4-448 và EfficientNet-B4 hai đầu ra, rồi ensemble...
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
                      Khi ảnh không đạt chuẩn đáy võng mạc, <strong>Model B không được chạy</strong>.
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
                        <span>Model B: 6 lớp & XAI</span>
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
                              <span className="summary-tag tag-b">Kết quả báo cáo • Ensemble</span>
                              {result.dr_result && (
                                <span className={`stage-badge stage-${result.dr_result.stage}`}>
                                  {result.dr_result.badge}
                                </span>
                              )}
                            </div>
                            {result.dr_result ? (
                              <div className="summary-body">
                                <h3 className="summary-title">{result.dr_result.stage_name}</h3>
                                <p className="summary-desc">{result.dr_result.description}</p>
                                <div className="summary-confidence">
                                  <span>Xác suất lớp được chọn:</span>
                                  <strong>{(result.dr_result.confidence * 100).toFixed(1)}%</strong>
                                </div>
                              </div>
                            ) : (
                              <div className="summary-error">
                                {result.dr_error || "Mô hình DR không khả dụng"}
                              </div>
                            )}
                            <button className="btn-card-link" onClick={() => setDashboardTab('model_b')}>
                              <span>Xem 6 lớp và heatmap</span>
                              <ChevronRight size={14} />
                            </button>
                          </div>

                          <div className="summary-card model-b-summary">
                            <div className="summary-header">
                              <span className="summary-tag tag-b">Ba nhánh trước khi trộn</span>
                            </div>
                            <div className="summary-body">
                              <h3 className="summary-title">ViT 0.45 • EffB4 0.40 • EffB4 hai đầu ra 0.15</h3>
                              <p className="summary-desc">
                                {branches.length
                                  ? branches.map((b) => `${branchLabel(b)}: ${b.badge}`).join('. ')
                                  : 'Chưa có kết quả từng nhánh'}.
                                {" "}Lớp 5 chỉ có nghĩa là nhóm không phải DR.
                              </p>
                              {result.dr_result && (
                                <div className="summary-confidence">
                                  <span>{result.dr_result.benchmark_note}</span>
                                </div>
                              )}
                            </div>
                            <button className="btn-card-link" onClick={() => setDashboardTab('model_b')}>
                              <span>Đối chiếu từng nhánh</span>
                              <ChevronRight size={14} />
                            </button>
                          </div>
                        </div>

                        {/* Pipeline Status Breakdown Box */}
                        <div className="system-status-box">
                          <div className="status-box-title">
                            <ShieldCheck size={16} />
                            <span>Trạng thái hai mô hình</span>
                          </div>
                          <div className="status-grid">
                            <div className="status-col">
                              <span className="col-label">Model A (Fundus Gate):</span>
                              <span className="col-val val-green">✓ {result.model_status?.model_a || 'ready'}</span>
                            </div>
                            <div className="status-col">
                              <span className="col-label">Model B (ensemble 6 lớp):</span>
                              <span className="col-val val-green">✓ {result.model_status?.model_b || 'ready'}</span>
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
                            {branches.length > 0 && result.dr_result && (
                              <div className={`agreement-banner ${isAgreement ? 'agree-yes' : 'agree-diff'}`}>
                                {isAgreement ? <CheckCircle2 size={18} className="flex-shrink-0" /> : <AlertTriangle size={18} className="flex-shrink-0" />}
                                <div>
                                  <div>
                                    <strong>Kết quả báo cáo là ensemble:</strong> lớp {result.dr_result.stage} ({result.dr_result.badge}).
                                    {branches.map((b) => (
                                      <span key={b.branch || b.model_used}>{" "}{branchLabel(b)}: lớp {b.stage} ({b.badge}).</span>
                                    ))}
                                    {isAgreement
                                      ? " Các nhánh trùng lớp với ensemble."
                                      : " Các nhánh không hoàn toàn trùng lớp. Ensemble là quyết định đã khóa trên tập validation."}
                                  </div>
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
                                {result.dr_result?.heatmap_base64 && (
                                  <button
                                    className={`view-tab ${activeHeatmapView === 'ensemble' ? 'active' : ''}`}
                                    onClick={() => setActiveHeatmapView('ensemble')}
                                  >
                                    Ensemble (trộn theo trọng số)
                                  </button>
                                )}
                                {branches.filter((b) => b.heatmap_base64).length > 1 && (
                                  <button
                                    className={`view-tab ${activeHeatmapView === 'compare' ? 'active' : ''}`}
                                    onClick={() => setActiveHeatmapView('compare')}
                                  >
                                    👁️ So sánh {branches.filter((b) => b.heatmap_base64).length} heatmap song song
                                  </button>
                                )}
                                {branches.filter((b) => b.heatmap_base64).map((b) => (
                                  <button
                                    key={b.branch}
                                    className={`view-tab ${activeHeatmapView === b.branch ? 'active' : ''}`}
                                    onClick={() => setActiveHeatmapView(b.branch)}
                                  >
                                    {b.branch === 'vit3' ? '✨ ' : '⚡ '}{branchLabel(b)} ({fmtWeight(b)})
                                  </button>
                                ))}
                                <button
                                  className={`view-tab ${activeHeatmapView === 'original' ? 'active' : ''}`}
                                  onClick={() => setActiveHeatmapView('original')}
                                >
                                  📷 Ảnh gốc
                                </button>
                              </div>

                              {/* View Content */}
                              {activeHeatmapView === 'compare' && branches.some((b) => b.heatmap_base64) ? (
                                <div className="dual-heatmap-grid">
                                  {branches.filter((b) => b.heatmap_base64).map((b) => (
                                    <div className="heatmap-box" key={b.branch}>
                                      <div className="heatmap-title">{branchLabel(b)} • trọng số {fmtWeight(b)}</div>
                                      <img src={b.heatmap_base64} alt={`${branchLabel(b)} heatmap`} className="heatmap-img" />
                                      <div className="heatmap-caption">
                                        {b.branch === 'vit3' ? 'Grad-CAM trên token patch của khối Transformer cuối' : 'Grad-CAM trên lớp tích chập cuối (bn2)'}
                                      </div>
                                      <div className={`stage-badge stage-${b.stage}`}>
                                        Độ {b.stage}: {b.badge}
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              ) : (
                                <div className="single-heatmap-box">
                                  <img
                                    src={
                                      activeHeatmapView === 'ensemble' && result.dr_result?.heatmap_base64
                                        ? result.dr_result.heatmap_base64
                                        : heatmapBranch?.heatmap_base64
                                        ? heatmapBranch.heatmap_base64
                                        : previewUrl
                                    }
                                    alt="Heatmap View"
                                    className="heatmap-img"
                                  />
                                </div>
                              )}
                              <p className="heatmap-note">
                                * Vùng màu đỏ/cam biểu thị khu vực các mạng nơ-ron tập trung trọng số kích hoạt khi đưa ra quyết định phân loại tổn thương. Grad-CAM của mọi nhánh lấy lớp do ensemble chọn; heatmap ensemble là tổng có trọng số 0.45 / 0.40 / 0.15.
                              </p>
                            </div>

                            {/* Model Details Selector */}
                            <div className="model-details-card">
                              <div className="model-tab-buttons">
                                {result.dr_result && (
                                  <button
                                    className={`model-subtab ${selectedDRModel === 'ensemble' ? 'active' : ''}`}
                                    onClick={() => setSelectedDRModel('ensemble')}
                                  >
                                    <Layers size={14} />
                                    <span>Ensemble 0.45 / 0.40 / 0.15</span>
                                  </button>
                                )}
                                {branches.map((b) => (
                                  <button
                                    key={b.branch}
                                    className={`model-subtab ${selectedDRModel === b.branch ? 'active' : ''}`}
                                    onClick={() => setSelectedDRModel(b.branch)}
                                  >
                                    {b.branch === 'vit3' ? <Sparkles size={14} /> : <Cpu size={14} />}
                                    <span>{branchLabel(b)}</span>
                                  </button>
                                ))}
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
                                <span className="prob-section-title">Phân bố xác suất 6 lớp ({currentDR.model_used}). Lớp được chọn không phải lúc nào cũng là argmax:</span>
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

                    {/* TAB 4: CLINICAL EXPLANATION & DISCLAIMER */}
                    {dashboardTab === 'explanation' && (
                      <div className="tab-pane">
                        <div className="explanation-card">
                          <div className="exp-section">
                            <h3>
                              <ShieldCheck size={18} className="text-primary" />
                              <span>Cách đọc kết quả 6 lớp</span>
                            </h3>
                            <ul>
                              <li>
                                <strong>Model A</strong> nhìn ảnh gốc và chỉ quyết định ảnh có phải đáy mắt hay không. Ngưỡng giữ nguyên 0.965.
                              </li>
                              <li>
                                <strong>Model B</strong> chỉ chạy khi Model A chấp nhận. Ảnh được cắt nền tối, resize 512, rồi Ben Graham (hệ số 4, Gaussian σ = 20, mặt nạ tròn 0.95, JPEG q92) giống bộ cache huấn luyện; mỗi nhánh resize về 384 (ViT) hoặc 448 (EffB4), chuẩn hóa ImageNet và lấy trung bình với ảnh lật ngang (TTA).
                              </li>
                              <li>
                                Xác suất ensemble = 0.45 × ViT-B/16-384 + 0.40 × EfficientNet-B4-448 + 0.15 × EfficientNet-B4-448 hai đầu ra. Giải mã phân tầng: nếu p(lớp 5) &gt; 0.50 thì kết quả là lớp 5; nếu không, mức DR là argmax của 5 lớp 0–4. Trọng số và t5 được khóa trên tập validation.
                              </li>
                              <li>
                                Lớp 5 là một nhóm chung cho tổn thương không thuộc thang DR. Nó không nêu tên đục thủy tinh thể, glôcôm, AMD, cận thị bệnh lý hay tắc mạch.
                              </li>
                              <li>
                                Số liệu test (8818 ảnh, chấm một lần sau khi khóa trên validation): Acc 79.36%, macro-F1 0.6151, QWK_DR 0.7572, SCORE 0.6861 (CI95 0.6684–0.7035). Mild NPDR vẫn là lớp yếu (F1 0.2218).
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
              Model A (MobileNetV3 Gate) • Model B (ensemble ViT-B/16-384 0.45, EfficientNet-B4-448 0.40, EfficientNet-B4-448 hai đầu ra 0.15; 6 lớp).
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
