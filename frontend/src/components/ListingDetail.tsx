import { useState, useEffect } from 'react';
import { type CarListing } from '../api/crawlerApi';
import { type BuyabilityAnalysis, analyzeListing } from '../api/listingsApi';
import '../styles/ListingDetail.css';

interface ListingDetailProps {
  listing: CarListing;
  onClose: () => void;
  onDelete: () => Promise<void>;
}

type TabType = 'analysis' | 'info' | 'details' | 'technical' | 'parts' | 'features';

export default function ListingDetail({ listing, onClose, onDelete }: ListingDetailProps) {
  const [isDeleting, setIsDeleting] = useState(false);
  const [analysis, setAnalysis] = useState<BuyabilityAnalysis | null>(null);
  const [analysisLoading, setAnalysisLoading] = useState(true);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<TabType>('analysis');

  // Fetch buyability analysis when component mounts
  useEffect(() => {
    const fetchAnalysis = async () => {
      try {
        setAnalysisLoading(true);
        setAnalysisError(null);
        const result = await analyzeListing(listing.listing_id);
        setAnalysis(result.analysis);
      } catch (err: any) {
        console.error('Failed to fetch analysis:', err);
        setAnalysisError(err.response?.data?.detail || 'Analysis unavailable');
      } finally {
        setAnalysisLoading(false);
      }
    };

    fetchAnalysis();
  }, [listing.listing_id]);

  const handleDelete = async () => {
    if (!window.confirm('Bu ilanı silmek istediğinizden emin misiniz?')) {
      return;
    }
    setIsDeleting(true);
    try {
      await onDelete();
    } finally {
      setIsDeleting(false);
    }
  };

  // Format price
  const formattedPrice = new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(listing.price || 0);

  // Format mileage
  const formattedMileage = new Intl.NumberFormat('tr-TR').format(listing.mileage || 0);

  // Build title
  const title = listing.title || `${listing.brand} ${listing.series || ''} ${listing.model || ''}`.trim();

  // Get first image
  const firstImage = listing.images?.[0];
  const imageUrl = firstImage
    ? typeof firstImage === 'string'
      ? firstImage
      : firstImage.path
        ? `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/data/images/${firstImage.path}`
        : firstImage.url
    : null;

  // Get risk level class based on score
  const getRiskLevelClass = (score: number): string => {
    if (score >= 71) return 'risk-low';
    if (score >= 51) return 'risk-moderate';
    return 'risk-high';
  };

  // Get risk level text in Turkish
  const getRiskLevelText = (score: number): string => {
    if (score >= 86) return 'Minimal Risk - Mukemmel Durum';
    if (score >= 71) return 'Cok Dusuk Risk - Iyi Durum';
    if (score >= 51) return 'Dusuk Risk - Kabul Edilebilir';
    if (score >= 31) return 'Orta Risk - Dikkatli Inceleme Onerilir';
    return 'Yuksek Risk - Ciddi Endiseler Var';
  };

  // Translate feature score names to Turkish
  const featureScoreLabels: Record<string, string> = {
    age_score: 'Arac Yasi',
    km_per_year_score: 'Yillik KM',
    km_score: 'Toplam KM',
    year_score: 'Model Yili',
    hp_score: 'Motor Gucu',
    ccm_score: 'Motor Hacmi'
  };

  const tabs: { id: TabType; label: string }[] = [
    { id: 'analysis', label: 'Alinabilirlik Analizi' },
    { id: 'info', label: 'Ilan Bilgileri' },
    { id: 'details', label: 'Ilan Detaylari' },
    { id: 'technical', label: 'Teknik Ozellikler' },
    { id: 'parts', label: 'Boyali/Degisen' },
    { id: 'features', label: 'Donanim' },
  ];

  return (
    <div className="modal" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        {/* Floating Header with Navbar */}
        <header className="modal-header-floating">
          <div className="header-title-row">
            <h2>{title}</h2>
            <button className="modal-close" onClick={onClose}>&times;</button>
          </div>
          <nav className="floating-nav">
            {tabs.map(tab => (
              <button
                key={tab.id}
                className={`nav-tab ${activeTab === tab.id ? 'active' : ''}`}
                onClick={() => setActiveTab(tab.id)}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </header>

        <div className="modal-body">
          {/* Hero Section: 3-Column Layout */}
          <div className="hero-section">
            {/* Left: Alinabilirlik Skoru */}
            <div className="hero-column hero-score">
              <h3>Alinabilirlik Skoru</h3>
              {analysisLoading && (
                <div className="hero-loading">
                  <div className="loading-spinner-small"></div>
                  <span>Analiz yapiliyor...</span>
                </div>
              )}
              {analysisError && (
                <div className="hero-error">
                  <span>Analiz yapilamadi</span>
                </div>
              )}
              {analysis && !analysisLoading && (
                <div className={`score-card ${getRiskLevelClass(analysis.risk_score)}`}>
                  <div className="score-main">
                    <span className="score-value">{analysis.risk_score}</span>
                    <span className="score-max">/100</span>
                  </div>
                  <div className="score-decision">
                    {analysis.decision === 'BUYABLE' ? 'ALINABILIR' : 'ALINMAMALI'}
                  </div>
                  <div className="score-explanation">{getRiskLevelText(analysis.risk_score)}</div>
                </div>
              )}
            </div>

            {/* Center: Main Image */}
            <div className="hero-column hero-image">
              {imageUrl ? (
                <img src={imageUrl} alt={title} />
              ) : (
                <div className="no-image">Gorsel Yok</div>
              )}
              <div className="image-price">{formattedPrice}</div>
            </div>

            {/* Right: Ozellik Puanlari */}
            <div className="hero-column hero-features">
              <h3>Ozellik Puanlari</h3>
              {analysisLoading && (
                <div className="hero-loading">
                  <div className="loading-spinner-small"></div>
                </div>
              )}
              {analysis && !analysisLoading && (
                <div className="feature-scores-compact">
                  {Object.entries(analysis.feature_scores).map(([key, value]) => (
                    <div key={key} className="feature-score-row">
                      <span className="feature-label">{featureScoreLabels[key] || key}</span>
                      <div className="feature-bar-container">
                        <div
                          className="feature-bar-fill"
                          style={{ width: `${value * 100}%` }}
                        ></div>
                      </div>
                      <span className="feature-value">{(value * 100).toFixed(0)}%</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Tab Content */}
          <div className="tab-content">
            {activeTab === 'analysis' && analysis && (
              <div className="content-section">
                {/* Risk Factors */}
                {analysis.risk_factors.length > 0 && (
                  <div className="subsection">
                    <h4>Risk Faktorleri</h4>
                    <ul className="risk-factors-list">
                      {analysis.risk_factors.map((factor, idx) => (
                        <li key={idx} className="risk-factor-item">{factor}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Top Contributing Features */}
                <div className="subsection">
                  <h4>En Onemli Ozellikler</h4>
                  <div className="top-features-grid">
                    {analysis.top_features.map((feat, idx) => (
                      <div key={idx} className="top-feature-card">
                        <span className="top-feature-name">{feat.feature}</span>
                        <span className="top-feature-value">{feat.value.toLocaleString('tr-TR')}</span>
                        <span className="top-feature-importance">({(feat.importance * 100).toFixed(1)}%)</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'info' && (
              <div className="content-section">
                <div className="info-grid">
                  <div className="info-row">
                    <span className="info-label">Ilan No</span>
                    <span className="info-value">{listing.listing_id || '-'}</span>
                  </div>
                  {listing.listing_date && (
                    <div className="info-row">
                      <span className="info-label">Ilan Tarihi</span>
                      <span className="info-value">{listing.listing_date}</span>
                    </div>
                  )}
                  <div className="info-row">
                    <span className="info-label">Fiyat</span>
                    <span className="info-value highlight">{formattedPrice}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Marka</span>
                    <span className="info-value">{listing.brand || '-'}</span>
                  </div>
                  {listing.series && (
                    <div className="info-row">
                      <span className="info-label">Seri</span>
                      <span className="info-value">{listing.series}</span>
                    </div>
                  )}
                  <div className="info-row">
                    <span className="info-label">Model</span>
                    <span className="info-value">{listing.model || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Yil</span>
                    <span className="info-value">{listing.year || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Yakit Tipi</span>
                    <span className="info-value">{listing.fuel_type || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Vites</span>
                    <span className="info-value">{listing.transmission || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Arac Durumu</span>
                    <span className="info-value">{listing.vehicle_condition || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">KM</span>
                    <span className="info-value">{formattedMileage}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Kasa Tipi</span>
                    <span className="info-value">{listing.body_type || '-'}</span>
                  </div>
                  {listing.engine_power && (
                    <div className="info-row">
                      <span className="info-label">Motor Gucu</span>
                      <span className="info-value">{listing.engine_power}</span>
                    </div>
                  )}
                  {listing.engine_volume && (
                    <div className="info-row">
                      <span className="info-label">Motor Hacmi</span>
                      <span className="info-value">{listing.engine_volume}</span>
                    </div>
                  )}
                  {listing.drive_type && (
                    <div className="info-row">
                      <span className="info-label">Cekis</span>
                      <span className="info-value">{listing.drive_type}</span>
                    </div>
                  )}
                  <div className="info-row">
                    <span className="info-label">Renk</span>
                    <span className="info-value">{listing.color || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Garanti</span>
                    <span className="info-value">{listing.warranty || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Agir Hasar Kayitli</span>
                    <span className="info-value">
                      {listing.heavy_damage === true ? 'Evet' : listing.heavy_damage === false ? 'Hayir' : '-'}
                    </span>
                  </div>
                  {listing.plate_origin && (
                    <div className="info-row">
                      <span className="info-label">Plaka / Uyruk</span>
                      <span className="info-value">{listing.plate_origin}</span>
                    </div>
                  )}
                  <div className="info-row">
                    <span className="info-label">Kimden</span>
                    <span className="info-value">{listing.seller_type || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Takas</span>
                    <span className="info-value">
                      {listing.trade_option === true ? 'Evet' : listing.trade_option === false ? 'Hayir' : '-'}
                    </span>
                  </div>
                  {listing.location && (
                    <div className="info-row">
                      <span className="info-label">Konum</span>
                      <span className="info-value">{listing.location}</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {activeTab === 'details' && (
              <div className="content-section">
                {listing.description ? (
                  <div className="description-box">
                    <pre className="description-text">{listing.description}</pre>
                  </div>
                ) : (
                  <p className="no-content">Ilan detayi bulunmuyor.</p>
                )}
              </div>
            )}

            {activeTab === 'technical' && (
              <div className="content-section">
                {listing.technical_specs && Object.keys(listing.technical_specs).length > 0 ? (
                  <div className="info-grid">
                    {Object.entries(listing.technical_specs).map(([key, value]) => (
                      <div key={key} className="info-row">
                        <span className="info-label">{key}</span>
                        <span className="info-value">{String(value) || '-'}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="no-content">Teknik ozellik bilgisi bulunmuyor.</p>
                )}
              </div>
            )}

            {activeTab === 'parts' && (
              <div className="content-section">
                {listing.painted_parts && (listing.painted_parts.boyali?.length || listing.painted_parts.degisen?.length) ? (
                  <div className="parts-container">
                    {listing.painted_parts.boyali && listing.painted_parts.boyali.length > 0 && (
                      <div className="parts-group">
                        <h4>Boyali Parcalar</h4>
                        <div className="parts-list">
                          {listing.painted_parts.boyali.map((part: string, idx: number) => (
                            <span key={idx} className="part-tag painted">{part}</span>
                          ))}
                        </div>
                      </div>
                    )}
                    {listing.painted_parts.degisen && listing.painted_parts.degisen.length > 0 && (
                      <div className="parts-group">
                        <h4>Degisen Parcalar</h4>
                        <div className="parts-list">
                          {listing.painted_parts.degisen.map((part: string, idx: number) => (
                            <span key={idx} className="part-tag changed">{part}</span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <p className="no-content">Boyali veya degisen parca bilgisi bulunmuyor.</p>
                )}
              </div>
            )}

            {activeTab === 'features' && (
              <div className="content-section">
                {listing.features && Object.keys(listing.features).length > 0 ? (
                  <div className="features-container">
                    {Object.entries(listing.features).map(([category, items]) => (
                      <div key={category} className="feature-category">
                        <h4>{category}</h4>
                        <div className="feature-list">
                          {Array.isArray(items) && items.map((item: string, idx: number) => (
                            <span key={idx} className="feature-tag">{item}</span>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="no-content">Donanim bilgisi bulunmuyor.</p>
                )}
              </div>
            )}
          </div>

          {/* Metadata */}
          <div className="metadata-section">
            <div className="metadata-row">
              <span>Veri Kalitesi: {((listing.data_quality_score || 0) * 100).toFixed(0)}%</span>
              <span>Cekilme: {listing.crawled_at ? new Date(listing.crawled_at).toLocaleDateString('tr-TR') : '-'}</span>
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>Kapat</button>
          <button
            className="btn btn-delete"
            onClick={handleDelete}
            disabled={isDeleting}
          >
            {isDeleting ? 'Siliniyor...' : 'Ilani Sil'}
          </button>
        </div>
      </div>
    </div>
  );
}
