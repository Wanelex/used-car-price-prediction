import React, { useState, useEffect } from 'react';
import { CarListing, BuyabilityAnalysis, analyzeListing } from '../api/listingsApi';
import '../styles/ListingDetail.css';

interface ListingDetailProps {
  listing: CarListing;
  onClose: () => void;
  onDelete: () => Promise<void>;
}

export default function ListingDetail({ listing, onClose, onDelete }: ListingDetailProps) {
  const [isDeleting, setIsDeleting] = useState(false);
  const [analysis, setAnalysis] = useState<BuyabilityAnalysis | null>(null);
  const [analysisLoading, setAnalysisLoading] = useState(true);
  const [analysisError, setAnalysisError] = useState<string | null>(null);

  // Fetch buyability analysis when component mounts
  useEffect(() => {
    const fetchAnalysis = async () => {
      try {
        setAnalysisLoading(true);
        setAnalysisError(null);
        const result = await analyzeListing(listing.user_id, listing.listing_id);
        setAnalysis(result.analysis);
      } catch (err: any) {
        console.error('Failed to fetch analysis:', err);
        setAnalysisError(err.response?.data?.detail || 'Analysis unavailable');
      } finally {
        setAnalysisLoading(false);
      }
    };

    fetchAnalysis();
  }, [listing.listing_id, listing.user_id]);

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
  }).format(listing.price);

  // Format mileage
  const formattedMileage = new Intl.NumberFormat('tr-TR').format(listing.mileage || 0);

  // Build title
  const title = listing.title || `${listing.brand} ${listing.series || ''} ${listing.model || ''}`.trim();

  // Get first 2 images
  const displayImages = listing.images?.slice(0, 2) || [];

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

  return (
    <div className="modal" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{title}</h2>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>

        <div className="modal-body">
          {/* Images Section - First 2 images only */}
          {displayImages.length > 0 && (
            <div className="modal-section">
              <div className="image-gallery-small">
                {displayImages.map((image, idx) => {
                  const imageUrl = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/data/images/${image.path}`;
                  return (
                    <div key={idx} className="gallery-item-small">
                      <img src={imageUrl} alt={`Görsel ${idx + 1}`} />
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Buyability Analysis Section */}
          <div className="modal-section analysis-section">
            <h3>Alinabilirlik Analizi</h3>
            {analysisLoading && (
              <div className="analysis-loading">
                <div className="loading-spinner-small"></div>
                <span>Analiz yapiliyor...</span>
              </div>
            )}
            {analysisError && (
              <div className="analysis-error">
                <span>Analiz yapilamadi: {analysisError}</span>
              </div>
            )}
            {analysis && !analysisLoading && (
              <div className="analysis-content">
                {/* Main Risk Score */}
                <div className={`risk-score-card ${getRiskLevelClass(analysis.risk_score)}`}>
                  <div className="risk-score-main">
                    <span className="risk-score-value">{analysis.risk_score}</span>
                    <span className="risk-score-max">/100</span>
                  </div>
                  <div className="risk-decision">
                    {analysis.decision === 'BUYABLE' ? 'ALINABILIR' : 'ALINMAMALI'}
                  </div>
                  <div className="risk-explanation">{getRiskLevelText(analysis.risk_score)}</div>
                </div>

                {/* Feature Scores */}
                <div className="feature-scores">
                  <h4>Ozellik Puanlari</h4>
                  <div className="feature-scores-grid">
                    {Object.entries(analysis.feature_scores).map(([key, value]) => (
                      <div key={key} className="feature-score-item">
                        <span className="feature-score-label">{featureScoreLabels[key] || key}</span>
                        <div className="feature-score-bar">
                          <div
                            className="feature-score-fill"
                            style={{ width: `${value * 100}%` }}
                          ></div>
                        </div>
                        <span className="feature-score-value">{(value * 100).toFixed(0)}%</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Risk Factors */}
                {analysis.risk_factors.length > 0 && (
                  <div className="risk-factors">
                    <h4>Risk Faktorleri</h4>
                    <ul className="risk-factors-list">
                      {analysis.risk_factors.map((factor, idx) => (
                        <li key={idx} className="risk-factor-item">{factor}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Top Contributing Features */}
                <div className="top-features">
                  <h4>En Onemli Ozellikler</h4>
                  <div className="top-features-list">
                    {analysis.top_features.map((feat, idx) => (
                      <div key={idx} className="top-feature-item">
                        <span className="top-feature-name">{feat.feature}</span>
                        <span className="top-feature-value">{feat.value.toLocaleString('tr-TR')}</span>
                        <span className="top-feature-importance">({(feat.importance * 100).toFixed(1)}%)</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Section 1: İlan Bilgileri */}
          <div className="modal-section">
            <h3>İlan Bilgileri</h3>
            <div className="info-table">
              <div className="info-row">
                <span className="info-label">İlan No</span>
                <span className="info-value">{listing.listing_id || '-'}</span>
              </div>
              {listing.listing_date && (
                <div className="info-row">
                  <span className="info-label">İlan Tarihi</span>
                  <span className="info-value">{listing.listing_date}</span>
                </div>
              )}
              <div className="info-row">
                <span className="info-label">Fiyat</span>
                <span className="info-value price-value">{formattedPrice}</span>
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
                <span className="info-label">Yıl</span>
                <span className="info-value">{listing.year || '-'}</span>
              </div>
              <div className="info-row">
                <span className="info-label">Yakıt Tipi</span>
                <span className="info-value">{listing.fuel_type || '-'}</span>
              </div>
              <div className="info-row">
                <span className="info-label">Vites</span>
                <span className="info-value">{listing.transmission || '-'}</span>
              </div>
              <div className="info-row">
                <span className="info-label">Araç Durumu</span>
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
                  <span className="info-label">Motor Gücü</span>
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
                  <span className="info-label">Çekiş</span>
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
                <span className="info-label">Ağır Hasar Kayıtlı</span>
                <span className="info-value">
                  {listing.heavy_damage === true ? 'Evet' : listing.heavy_damage === false ? 'Hayır' : '-'}
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
                  {listing.trade_option === true ? 'Evet' : listing.trade_option === false ? 'Hayır' : '-'}
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

          {/* Section 2: İlan Detayları (Description) */}
          {listing.description && (
            <div className="modal-section">
              <h3>İlan Detayları</h3>
              <div className="description-box">
                <pre className="description-text">{listing.description}</pre>
              </div>
            </div>
          )}

          {/* Section 3: Teknik Özellikler */}
          {listing.technical_specs && Object.keys(listing.technical_specs).length > 0 && (
            <div className="modal-section">
              <h3>Teknik Özellikler</h3>
              <div className="info-table">
                {Object.entries(listing.technical_specs).map(([key, value]) => (
                  <div key={key} className="info-row">
                    <span className="info-label">{key}</span>
                    <span className="info-value">{value || '-'}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Section 4: Boyalı ve Değişen Parçalar */}
          {listing.painted_parts && (listing.painted_parts.boyali?.length || listing.painted_parts.degisen?.length) ? (
            <div className="modal-section">
              <h3>Boyalı ve Değişen Parçalar</h3>
              <div className="parts-section">
                {listing.painted_parts.boyali && listing.painted_parts.boyali.length > 0 && (
                  <div className="parts-group">
                    <h4>Boyalı Parçalar</h4>
                    <div className="parts-list">
                      {listing.painted_parts.boyali.map((part, idx) => (
                        <span key={idx} className="part-tag painted">{part}</span>
                      ))}
                    </div>
                  </div>
                )}
                {listing.painted_parts.degisen && listing.painted_parts.degisen.length > 0 && (
                  <div className="parts-group">
                    <h4>Değişen Parçalar</h4>
                    <div className="parts-list">
                      {listing.painted_parts.degisen.map((part, idx) => (
                        <span key={idx} className="part-tag changed">{part}</span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : null}

          {/* Section 4b: Donanım/Özellikler */}
          {listing.features && Object.keys(listing.features).length > 0 && (
            <div className="modal-section">
              <h3>Donanım Özellikleri</h3>
              <div className="features-section">
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
            </div>
          )}

          {/* Metadata */}
          <div className="modal-section metadata-section">
            <h3>Veri Bilgisi</h3>
            <div className="info-table">
              <div className="info-row">
                <span className="info-label">Veri Kalitesi</span>
                <span className="info-value">{((listing.data_quality_score || 0) * 100).toFixed(0)}%</span>
              </div>
              <div className="info-row">
                <span className="info-label">Çekilme Tarihi</span>
                <span className="info-value">
                  {listing.crawled_at ? new Date(listing.crawled_at).toLocaleDateString('tr-TR') : '-'}
                </span>
              </div>
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
            {isDeleting ? 'Siliniyor...' : 'İlanı Sil'}
          </button>
        </div>
      </div>
    </div>
  );
}
