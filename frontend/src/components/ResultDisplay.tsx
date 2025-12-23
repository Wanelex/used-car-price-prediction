import React, { useState, useEffect } from 'react';
import type { CrawlResult } from '../api/crawlerApi';
import type { BuyabilityAnalysis } from '../api/listingsApi';
import './ResultDisplay.css';

interface ResultDisplayProps {
  result: CrawlResult;
  onNewCrawl: () => void;
}

// API base URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Helper to format price in Turkish Lira
const formatPrice = (price: string | number | null | undefined): string => {
  if (!price) return '-';
  const numPrice = typeof price === 'string' ? parseFloat(price.replace(/[^\d]/g, '')) : price;
  if (isNaN(numPrice)) return String(price);
  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(numPrice);
};

// Helper to format mileage
const formatMileage = (km: string | number | null | undefined): string => {
  if (!km) return '-';
  const numKm = typeof km === 'string' ? parseInt(km.replace(/[^\d]/g, '')) : km;
  if (isNaN(numKm)) return String(km);
  return new Intl.NumberFormat('tr-TR').format(numKm) + ' km';
};

export const ResultDisplay: React.FC<ResultDisplayProps> = ({ result, onNewCrawl }) => {
  const [activeTab, setActiveTab] = useState<'analysis' | 'listing' | 'details' | 'specs' | 'parts' | 'images' | 'html'>('analysis');
  const [analysis, setAnalysis] = useState<BuyabilityAnalysis | null>(null);
  const [analysisLoading, setAnalysisLoading] = useState(true);
  const [analysisError, setAnalysisError] = useState<string | null>(null);

  const crawlData = result.result;
  const listing = crawlData?.sahibinden_listing;

  // Fetch buyability analysis when component mounts
  useEffect(() => {
    const fetchAnalysis = async () => {
      if (!listing) {
        setAnalysisLoading(false);
        setAnalysisError('No listing data available');
        return;
      }

      // Extract year and mileage from listing
      const year = listing.yil || listing.year;
      const mileage = listing.km || listing.mileage;
      const engineVolume = listing.motor_hacmi || listing.engine_volume;
      const enginePower = listing.motor_gucu || listing.engine_power;

      // Parse mileage if it's a string
      let parsedMileage = mileage;
      if (typeof mileage === 'string') {
        parsedMileage = parseInt(mileage.replace(/[^\d]/g, ''));
      }

      // Parse year if it's a string
      let parsedYear = year;
      if (typeof year === 'string') {
        parsedYear = parseInt(year);
      }

      if (!parsedYear || !parsedMileage || isNaN(parsedYear) || isNaN(parsedMileage)) {
        setAnalysisLoading(false);
        setAnalysisError('Missing required data (year or mileage)');
        return;
      }

      try {
        setAnalysisLoading(true);
        setAnalysisError(null);

        const params = new URLSearchParams({
          year: String(parsedYear),
          mileage: String(parsedMileage),
        });
        if (engineVolume) params.append('engine_volume', String(engineVolume));
        if (enginePower) params.append('engine_power', String(enginePower));

        const response = await fetch(`${API_BASE_URL}/api/v1/analyze?${params}`, {
          method: 'POST',
        });

        if (!response.ok) {
          throw new Error('Analysis request failed');
        }

        const data = await response.json();
        setAnalysis(data.analysis);
      } catch (err: any) {
        console.error('Failed to fetch analysis:', err);
        setAnalysisError(err.message || 'Analysis unavailable');
      } finally {
        setAnalysisLoading(false);
      }
    };

    fetchAnalysis();
  }, [listing]);

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

  // Build title from brand, series, model
  const listingTitle = listing
    ? `${listing.marka || listing.brand || ''} ${listing.seri || listing.series || ''} ${listing.model || ''}`.trim() || 'Araç İlanı'
    : crawlData?.title || 'Crawl Result';

  // Get all images from crawl result (this is the reliable source)
  const allImages = crawlData?.images || [];
  // First 2 images for display
  const listingImages = allImages.slice(0, 2);

  return (
    <div className="result-display">
      <div className="result-header">
        <h2>{listingTitle}</h2>
        <button className="new-crawl-button" onClick={onNewCrawl}>
          Yeni Tarama Başlat
        </button>
      </div>

      {/* Show listing data if available */}
      {listing ? (
        <>
          <div className="tabs">
            <button
              className={`tab ${activeTab === 'analysis' ? 'active' : ''}`}
              onClick={() => setActiveTab('analysis')}
            >
              Alinabilirlik Analizi
            </button>
            <button
              className={`tab ${activeTab === 'listing' ? 'active' : ''}`}
              onClick={() => setActiveTab('listing')}
            >
              İlan Bilgileri
            </button>
            <button
              className={`tab ${activeTab === 'details' ? 'active' : ''}`}
              onClick={() => setActiveTab('details')}
            >
              İlan Detayları
            </button>
            <button
              className={`tab ${activeTab === 'specs' ? 'active' : ''}`}
              onClick={() => setActiveTab('specs')}
            >
              Teknik Özellikler
            </button>
            <button
              className={`tab ${activeTab === 'parts' ? 'active' : ''}`}
              onClick={() => setActiveTab('parts')}
            >
              Boyalı/Değişen
            </button>
            <button
              className={`tab ${activeTab === 'images' ? 'active' : ''}`}
              onClick={() => setActiveTab('images')}
            >
              Görseller
            </button>
            <button
              className={`tab ${activeTab === 'html' ? 'active' : ''}`}
              onClick={() => setActiveTab('html')}
            >
              HTML/Metadata
            </button>
          </div>

          <div className="tab-content">
            {/* Alinabilirlik Analizi Tab */}
            {activeTab === 'analysis' && (
              <div className="analysis-section">
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
            )}

            {/* İlan Bilgileri Tab */}
            {activeTab === 'listing' && (
              <div className="listing-section">
                {/* Images at top */}
                {listingImages.length > 0 && (
                  <div className="listing-images">
                    {listingImages.map((img: string, idx: number) => (
                      <div key={idx} className="listing-image">
                        <img src={img} alt={`Görsel ${idx + 1}`} onError={(e) => (e.currentTarget.style.display = 'none')} />
                      </div>
                    ))}
                  </div>
                )}

                <div className="info-table">
                  <div className="info-row">
                    <span className="info-label">İlan No</span>
                    <span className="info-value">{listing.ilan_no || listing.listing_id || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">İlan Tarihi</span>
                    <span className="info-value">{listing.ilan_tarihi || listing.listing_date || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Fiyat</span>
                    <span className="info-value price">{formatPrice(listing.fiyat || listing.price)}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Marka</span>
                    <span className="info-value">{listing.marka || listing.brand || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Seri</span>
                    <span className="info-value">{listing.seri || listing.series || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Model</span>
                    <span className="info-value">{listing.model || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Yıl</span>
                    <span className="info-value">{listing.yil || listing.year || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Yakıt Tipi</span>
                    <span className="info-value">{listing.yakit_tipi || listing.fuel_type || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Vites</span>
                    <span className="info-value">{listing.vites || listing.transmission || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Araç Durumu</span>
                    <span className="info-value">{listing.arac_durumu || listing.vehicle_condition || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">KM</span>
                    <span className="info-value">{formatMileage(listing.km || listing.mileage)}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Kasa Tipi</span>
                    <span className="info-value">{listing.kasa_tipi || listing.body_type || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Motor Gücü</span>
                    <span className="info-value">{listing.motor_gucu || listing.engine_power || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Motor Hacmi</span>
                    <span className="info-value">{listing.motor_hacmi || listing.engine_volume || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Çekiş</span>
                    <span className="info-value">{listing.cekis || listing.drive_type || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Renk</span>
                    <span className="info-value">{listing.renk || listing.color || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Garanti</span>
                    <span className="info-value">{listing.garanti || listing.warranty || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Ağır Hasar Kayıtlı</span>
                    <span className="info-value">{listing.agir_hasar_kayitli || listing.heavy_damage || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Plaka / Uyruk</span>
                    <span className="info-value">{listing.plaka_uyruk || listing.plate_origin || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Kimden</span>
                    <span className="info-value">{listing.kimden || listing.seller_type || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Takas</span>
                    <span className="info-value">{listing.takas || listing.trade_option || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Konum</span>
                    <span className="info-value">{listing.konum || listing.location || '-'}</span>
                  </div>
                </div>
              </div>
            )}

            {/* İlan Detayları Tab */}
            {activeTab === 'details' && (
              <div className="details-section">
                <h3>İlan Açıklaması</h3>
                <div className="description-box">
                  <pre>{listing.aciklama || listing.description || 'Açıklama bulunamadı.'}</pre>
                </div>
              </div>
            )}

            {/* Teknik Özellikler Tab */}
            {activeTab === 'specs' && (
              <div className="specs-section">
                <h3>Teknik Özellikler</h3>
                {(listing.teknik_ozellikler || listing.technical_specs) &&
                 Object.keys(listing.teknik_ozellikler || listing.technical_specs || {}).length > 0 ? (
                  <div className="info-table">
                    {Object.entries(listing.teknik_ozellikler || listing.technical_specs || {}).map(([key, value]) => (
                      <div key={key} className="info-row">
                        <span className="info-label">{key}</span>
                        <span className="info-value">{String(value) || '-'}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p>Teknik özellik bilgisi bulunamadı.</p>
                )}

                {/* Donanım Özellikleri */}
                <h3 style={{ marginTop: '24px' }}>Donanım Özellikleri</h3>
                {(listing.ozellikler || listing.features) &&
                 Object.keys(listing.ozellikler || listing.features || {}).length > 0 ? (
                  <div className="features-section">
                    {Object.entries(listing.ozellikler || listing.features || {}).map(([category, items]) => (
                      <div key={category} className="feature-category">
                        <h4>{category}</h4>
                        <div className="feature-list">
                          {Array.isArray(items) ? items.map((item: string, idx: number) => (
                            <span key={idx} className="feature-tag">{item}</span>
                          )) : <span className="feature-tag">{String(items)}</span>}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p>Donanım bilgisi bulunamadı.</p>
                )}
              </div>
            )}

            {/* Boyalı/Değişen Tab */}
            {activeTab === 'parts' && (
              <div className="parts-section">
                <h3>Boyalı ve Değişen Parçalar</h3>
                {(listing.boyali_degisen || listing.painted_parts) ? (
                  <div className="parts-container">
                    {/* Boyalı Parçalar */}
                    {(listing.boyali_degisen?.boyali || listing.painted_parts?.boyali) && (
                      <div className="parts-group">
                        <h4>Boyalı Parçalar</h4>
                        <div className="parts-list">
                          {(listing.boyali_degisen?.boyali || listing.painted_parts?.boyali || []).map((part: string, idx: number) => (
                            <span key={idx} className="part-tag painted">{part}</span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Değişen Parçalar */}
                    {(listing.boyali_degisen?.degisen || listing.painted_parts?.degisen) && (
                      <div className="parts-group">
                        <h4>Değişen Parçalar</h4>
                        <div className="parts-list">
                          {(listing.boyali_degisen?.degisen || listing.painted_parts?.degisen || []).map((part: string, idx: number) => (
                            <span key={idx} className="part-tag changed">{part}</span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Lokal Boyalı Parçalar */}
                    {(listing.boyali_degisen?.lokal_boyali || listing.painted_parts?.lokal_boyali) && (
                      <div className="parts-group">
                        <h4>Lokal Boyalı Parçalar</h4>
                        <div className="parts-list">
                          {(listing.boyali_degisen?.lokal_boyali || listing.painted_parts?.lokal_boyali || []).map((part: string, idx: number) => (
                            <span key={idx} className="part-tag local-painted">{part}</span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Raw text fallback - show if no structured arrays but aciklama exists */}
                    {!listing.boyali_degisen?.boyali && !listing.boyali_degisen?.degisen &&
                     !listing.painted_parts?.boyali && !listing.painted_parts?.degisen &&
                     (listing.boyali_degisen?.aciklama || listing.painted_parts?.aciklama) && (
                      <div className="parts-description">
                        <h4>Ham Veri</h4>
                        <pre style={{ whiteSpace: 'pre-wrap', fontSize: '14px' }}>
                          {listing.boyali_degisen?.aciklama || listing.painted_parts?.aciklama}
                        </pre>
                      </div>
                    )}

                    {!listing.boyali_degisen?.boyali && !listing.boyali_degisen?.degisen &&
                     !listing.painted_parts?.boyali && !listing.painted_parts?.degisen &&
                     !listing.boyali_degisen?.aciklama && !listing.painted_parts?.aciklama && (
                      <p>Boyalı veya değişen parça bilgisi bulunamadı.</p>
                    )}
                  </div>
                ) : (
                  <p>Boyalı veya değişen parça bilgisi bulunamadı.</p>
                )}
              </div>
            )}

            {/* Görseller Tab */}
            {activeTab === 'images' && (
              <div className="images-section">
                <h3>Araç Görselleri ({allImages.length} görsel)</h3>
                {allImages.length > 0 ? (
                  <div className="images-grid">
                    {allImages.slice(0, 12).map((img: string, idx: number) => (
                      <div key={idx} className="image-item">
                        <img src={img} alt={`Görsel ${idx + 1}`} onError={(e) => (e.currentTarget.style.display = 'none')} />
                      </div>
                    ))}
                  </div>
                ) : (
                  <p>Görsel bulunamadı.</p>
                )}
              </div>
            )}

            {/* HTML/Metadata Tab */}
            {activeTab === 'html' && (
              <div className="html-section">
                <h3>Metadata</h3>
                {crawlData?.metadata ? (
                  <div className="metadata-grid">
                    {Object.entries(crawlData.metadata).map(([key, value]) =>
                      value ? (
                        <div key={key} className="metadata-item">
                          <label>{key}</label>
                          <p>{typeof value === 'object' ? JSON.stringify(value) : String(value)}</p>
                        </div>
                      ) : null
                    )}
                  </div>
                ) : (
                  <p>Metadata bulunamadı</p>
                )}

                <h3 style={{ marginTop: '24px' }}>Crawl Bilgisi</h3>
                <div className="info-table">
                  <div className="info-row">
                    <span className="info-label">URL</span>
                    <span className="info-value">{crawlData?.final_url || result.url}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Süre</span>
                    <span className="info-value">{crawlData?.crawl_duration?.toFixed(2)}s</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">CAPTCHA Çözüldü</span>
                    <span className="info-value">{crawlData?.captcha_solved ? 'Evet' : 'Hayır'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Veri Kalitesi</span>
                    <span className="info-value">{listing.data_quality_score ? `${(listing.data_quality_score * 100).toFixed(0)}%` : '-'}</span>
                  </div>
                </div>

                {/* Debug: Raw Listing Data */}
                <h3 style={{ marginTop: '24px' }}>Debug: Ham İlan Verisi</h3>
                <div className="description-box">
                  <pre style={{ whiteSpace: 'pre-wrap', fontSize: '12px', maxHeight: '400px', overflow: 'auto' }}>
                    {JSON.stringify({
                      aciklama: listing.aciklama,
                      description: listing.description,
                      boyali_degisen: listing.boyali_degisen,
                      painted_parts: listing.painted_parts
                    }, null, 2)}
                  </pre>
                </div>
              </div>
            )}
          </div>
        </>
      ) : (
        /* Fallback for non-sahibinden pages */
        <div className="generic-result">
          <div className="info-grid">
            <div className="info-item">
              <label>URL</label>
              <p>{crawlData?.final_url || result.url}</p>
            </div>
            <div className="info-item">
              <label>Title</label>
              <p>{crawlData?.title || 'No title'}</p>
            </div>
          </div>
          <h3>Page Text</h3>
          <div className="description-box">
            <pre>{crawlData?.text?.substring(0, 2000) || 'No text content'}</pre>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResultDisplay;
