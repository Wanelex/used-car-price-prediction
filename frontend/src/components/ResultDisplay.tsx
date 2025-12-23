import React, { useState, useEffect } from 'react';
import type { CrawlResult } from '../api/crawlerApi';
import type { HybridAnalysis } from '../api/listingsApi';
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
  const [analysis, setAnalysis] = useState<HybridAnalysis | null>(null);
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

        // Add optional fields for statistical model
        if (engineVolume) params.append('engine_volume', String(engineVolume));
        if (enginePower) params.append('engine_power', String(enginePower));

        // Add optional fields for LLM analysis
        const make = listing.marka || listing.brand;
        const series = listing.seri || listing.series;
        const model = listing.model;
        const fuelType = listing.yakit_tipi || listing.fuel_type;
        const transmission = listing.vites || listing.transmission;
        const bodyType = listing.kasa_tipi || listing.body_type;
        const driveType = listing.cekis || listing.drive_type;
        const price = listing.fiyat || listing.price;

        if (make) params.append('make', String(make));
        if (series) params.append('series', String(series));
        if (model) params.append('model', String(model));
        if (fuelType) params.append('fuel_type', String(fuelType));
        if (transmission) params.append('transmission', String(transmission));
        if (bodyType) params.append('body_type', String(bodyType));
        if (driveType) params.append('drive_type', String(driveType));
        if (price) params.append('price', String(price));

        // Add parts data for crash score calculation
        const partsData = listing.boyali_degisen || listing.painted_parts;
        if (partsData) {
          if (partsData.boyali && partsData.boyali.length > 0) {
            params.append('painted_parts', partsData.boyali.join(','));
          }
          if (partsData.degisen && partsData.degisen.length > 0) {
            params.append('changed_parts', partsData.degisen.join(','));
          }
          if (partsData.lokal_boyali && partsData.lokal_boyali.length > 0) {
            params.append('local_painted_parts', partsData.lokal_boyali.join(','));
          }
        }

        const response = await fetch(`${API_BASE_URL}/api/v1/analyze?${params}`, {
          method: 'POST',
        });

        if (!response.ok) {
          throw new Error('Analysis request failed');
        }

        const data = await response.json();
        // Now response contains statistical_analysis and llm_analysis
        setAnalysis(data);
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

  // Get mechanical risk level class for LLM score
  const getMechanicalRiskClass = (score: number): string => {
    if (score >= 71) return 'risk-low';
    if (score >= 51) return 'risk-moderate';
    return 'risk-high';
  };

  // Get mechanical risk text in Turkish
  const getMechanicalRiskText = (score: number): string => {
    if (score >= 86) return 'Efsanevi Guvenilirlik';
    if (score >= 71) return 'Yuksek Guvenilirlik';
    if (score >= 51) return 'Orta Guvenilirlik';
    if (score >= 31) return 'Dusuk Guvenilirlik - Dikkat';
    return 'Mekanik Risk Yuksek';
  };

  // Get crash score risk level class
  const getCrashRiskClass = (score: number): string => {
    if (score >= 70) return 'risk-low';
    if (score >= 40) return 'risk-moderate';
    return 'risk-high';
  };

  // Get crash score verdict text based on score
  const getCrashVerdictText = (score: number): string => {
    if (score >= 90) return 'MUKEMMEL';
    if (score >= 70) return 'IYI';
    if (score >= 50) return 'DIKKAT';
    if (score >= 25) return 'TEHLIKE';
    return 'ALINMAMALI';
  };

  // Get buyability tier class for styling
  const getBuyabilityTierClass = (tier: string): string => {
    switch (tier) {
      case 'GUVENLI': return 'tier-guvenli';
      case 'NORMAL': return 'tier-normal';
      case 'DIKKAT': return 'tier-dikkat';
      case 'RISKLI': return 'tier-riskli';
      case 'KACIN': return 'tier-kacin';
      default: return 'tier-normal';
    }
  };

  // Get buyability score color class
  const getBuyabilityScoreClass = (score: number): string => {
    if (score >= 70) return 'score-high';
    if (score >= 50) return 'score-medium';
    return 'score-low';
  };

  // Get condition label in Turkish
  const getConditionLabel = (condition: string): string => {
    switch (condition) {
      case 'degisen': return 'Degisen';
      case 'boyali': return 'Boyali';
      case 'lokal_boyali': return 'Lokal Boyali';
      default: return condition;
    }
  };

  // Get condition tag class
  const getConditionClass = (condition: string): string => {
    switch (condition) {
      case 'degisen': return 'condition-changed';
      case 'boyali': return 'condition-painted';
      case 'lokal_boyali': return 'condition-local-painted';
      default: return '';
    }
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
            {/* Alinabilirlik Analizi Tab - Hybrid Two-Column Layout */}
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
                  <div className="hybrid-analysis-container">

                    {/* TOP SECTION: Buyability Score */}
                    {analysis.buyability_score && (
                      <div className={`buyability-score-section ${getBuyabilityTierClass(analysis.buyability_score.tier)}`}>
                        <div className="buyability-score-header">
                          <h3>Genel Alinabilirlik Skoru</h3>
                          {analysis.buyability_score.warning_message && (
                            <div className="buyability-warning">
                              <span className="warning-icon">!</span>
                              <span>{analysis.buyability_score.warning_message}</span>
                            </div>
                          )}
                        </div>

                        <div className="buyability-score-main">
                          <div className={`buyability-score-circle ${getBuyabilityScoreClass(analysis.buyability_score.final_score)}`}>
                            <span className="buyability-score-value">{analysis.buyability_score.final_score}</span>
                            <span className="buyability-score-max">/100</span>
                          </div>
                          <div className="buyability-tier-info">
                            <div className={`buyability-tier-badge ${getBuyabilityTierClass(analysis.buyability_score.tier)}`}>
                              {analysis.buyability_score.tier}
                            </div>
                            <p className="buyability-tier-label">{analysis.buyability_score.tier_label_tr}</p>
                          </div>
                        </div>

                        <div className="buyability-component-scores">
                          <div className="component-score-item">
                            <span className="component-label">Istatistiksel</span>
                            <div className="component-bar-container">
                              <div
                                className="component-bar"
                                style={{ width: `${analysis.buyability_score.component_scores.statistical || 0}%` }}
                              ></div>
                            </div>
                            <span className="component-value">
                              {analysis.buyability_score.component_scores.statistical ?? '-'}
                            </span>
                          </div>
                          <div className="component-score-item">
                            <span className="component-label">Mekanik</span>
                            <div className="component-bar-container">
                              <div
                                className="component-bar"
                                style={{ width: `${analysis.buyability_score.component_scores.mechanical || 0}%` }}
                              ></div>
                            </div>
                            <span className="component-value">
                              {analysis.buyability_score.component_scores.mechanical ?? '-'}
                            </span>
                          </div>
                          <div className="component-score-item">
                            <span className="component-label">Hasar</span>
                            <div className="component-bar-container">
                              <div
                                className="component-bar"
                                style={{ width: `${analysis.buyability_score.component_scores.crash || 0}%` }}
                              ></div>
                            </div>
                            <span className="component-value">
                              {analysis.buyability_score.component_scores.crash ?? '-'}
                            </span>
                          </div>
                        </div>

                        <div className="buyability-calculation-details">
                          <details>
                            <summary>Hesaplama Detaylari</summary>
                            <div className="calculation-breakdown">
                              <p><strong>Agirlikli Ortalama:</strong> {analysis.buyability_score.calculation_breakdown.weighted_average}</p>
                              <p><strong>Minimum Skor:</strong> {analysis.buyability_score.calculation_breakdown.min_score}</p>
                              <p><strong>Karisik Skor:</strong> {analysis.buyability_score.calculation_breakdown.blended_score}</p>
                              <p><strong>Uygulanan Ceza:</strong> -{analysis.buyability_score.calculation_breakdown.penalty_applied}</p>
                              <p><strong>Uygulanan Bonus:</strong> +{analysis.buyability_score.calculation_breakdown.bonus_applied}</p>
                              <p className="calculation-formula">{analysis.buyability_score.calculation_summary}</p>
                            </div>
                          </details>
                        </div>
                      </div>
                    )}

                    {/* LEFT COLUMN: Statistical Health Score */}
                    <div className="analysis-column statistical-column">
                      <h3 className="analysis-column-title">Istatistiksel Saglik Skoru</h3>

                      <div className={`risk-score-card ${getRiskLevelClass(analysis.statistical_analysis.risk_score)}`}>
                        <div className="risk-score-main">
                          <span className="risk-score-value">{analysis.statistical_analysis.risk_score}</span>
                          <span className="risk-score-max">/100</span>
                        </div>
                        <div className="risk-decision">
                          {analysis.statistical_analysis.decision === 'BUYABLE' ? 'ALINABILIR' : 'ALINMAMALI'}
                        </div>
                        <div className="risk-explanation">{getRiskLevelText(analysis.statistical_analysis.risk_score)}</div>
                      </div>

                      {/* Feature Scores */}
                      <div className="feature-scores">
                        <h4>Ozellik Puanlari</h4>
                        <div className="feature-scores-grid">
                          {Object.entries(analysis.statistical_analysis.feature_scores).map(([key, value]) => (
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
                      {analysis.statistical_analysis.risk_factors.length > 0 && (
                        <div className="risk-factors">
                          <h4>Risk Faktorleri</h4>
                          <ul className="risk-factors-list">
                            {analysis.statistical_analysis.risk_factors.map((factor, idx) => (
                              <li key={idx} className="risk-factor-item">{factor}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Top Contributing Features */}
                      <div className="top-features">
                        <h4>En Onemli Ozellikler</h4>
                        <div className="top-features-list">
                          {analysis.statistical_analysis.top_features.map((feat, idx) => (
                            <div key={idx} className="top-feature-item">
                              <span className="top-feature-name">{feat.feature}</span>
                              <span className="top-feature-value">{feat.value.toLocaleString('tr-TR')}</span>
                              <span className="top-feature-importance">({(feat.importance * 100).toFixed(1)}%)</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>

                    {/* RIGHT COLUMN: LLM Mechanical Score */}
                    <div className="analysis-column llm-column">
                      <h3 className="analysis-column-title">Mekanik Guvenilirlik Skoru</h3>

                      {analysis.llm_analysis ? (
                        <>
                          <div className={`risk-score-card ${getMechanicalRiskClass(analysis.llm_analysis.scores.mechanical_score)}`}>
                            <div className="risk-score-main">
                              <span className="risk-score-value">{analysis.llm_analysis.scores.mechanical_score}</span>
                              <span className="risk-score-max">/100</span>
                            </div>
                            <div className="risk-decision">
                              {analysis.llm_analysis.recommendation.buy_or_pass}
                            </div>
                            <div className="risk-explanation">{getMechanicalRiskText(analysis.llm_analysis.scores.mechanical_score)}</div>
                          </div>

                          {/* Car Identification */}
                          <div className="llm-section">
                            <h4>Arac Bilesenleri</h4>
                            <div className="llm-info-grid">
                              <div className="llm-info-item">
                                <span className="llm-label">Motor Kodu:</span>
                                <span className="llm-value">{analysis.llm_analysis.car_identification.engine_code}</span>
                              </div>
                              <div className="llm-info-item">
                                <span className="llm-label">Sanziman:</span>
                                <span className="llm-value">{analysis.llm_analysis.car_identification.transmission_name}</span>
                              </div>
                              {analysis.llm_analysis.car_identification.generation && (
                                <div className="llm-info-item">
                                  <span className="llm-label">Nesil:</span>
                                  <span className="llm-value">{analysis.llm_analysis.car_identification.generation}</span>
                                </div>
                              )}
                            </div>
                          </div>

                          {/* Expert Analysis */}
                          <div className="llm-section">
                            <h4>Uzman Analizi</h4>

                            <div className="llm-analysis-block">
                              <h5>Genel Degerlendirme</h5>
                              <p>{analysis.llm_analysis.expert_analysis.general_comment}</p>
                            </div>

                            <div className="llm-analysis-block">
                              <h5>Motor Guvenilirligi</h5>
                              <p>{analysis.llm_analysis.expert_analysis.engine_reliability}</p>
                            </div>

                            <div className="llm-analysis-block">
                              <h5>Sanziman Guvenilirligi</h5>
                              <p>{analysis.llm_analysis.expert_analysis.transmission_reliability}</p>
                            </div>

                            <div className="llm-analysis-block">
                              <h5>KM Dayaniklilik Kontrolu</h5>
                              <p>{analysis.llm_analysis.expert_analysis.km_endurance_check}</p>
                            </div>
                          </div>

                          {/* Recommendation */}
                          <div className="llm-section llm-recommendation">
                            <h4>Uzman Onerisi</h4>
                            <p className="llm-verdict">{analysis.llm_analysis.recommendation.verdict}</p>
                            <p className="llm-score-reasoning">
                              <strong>Puan Aciklamasi:</strong> {analysis.llm_analysis.scores.reasoning_for_score}
                            </p>
                          </div>
                        </>
                      ) : (
                        <div className="llm-unavailable">
                          <div className="llm-unavailable-icon">⚠️</div>
                          <h4>LLM Analizi Mevcut Degil</h4>
                          <p>Mekanik guvenilirlik analizi su anda kullanilamiyor. Lutfen istatistiksel skoru inceleyin.</p>
                          <p className="llm-unavailable-hint">OpenAI API anahtari yapilandirilmamis veya arac bilgileri eksik olabilir.</p>
                        </div>
                      )}
                    </div>

                    {/* THIRD COLUMN: Crash Score */}
                    <div className="analysis-column crash-column">
                      <h3 className="analysis-column-title">Hasar/Boya Skoru</h3>

                      {analysis.crash_score_analysis ? (
                        <>
                          <div className={`risk-score-card ${getCrashRiskClass(analysis.crash_score_analysis.score)}`}>
                            <div className="risk-score-main">
                              <span className="risk-score-value">{analysis.crash_score_analysis.score}</span>
                              <span className="risk-score-max">/100</span>
                            </div>
                            <div className="risk-decision">
                              {getCrashVerdictText(analysis.crash_score_analysis.score)}
                            </div>
                            <div className="risk-explanation">{analysis.crash_score_analysis.risk_level}</div>
                          </div>

                          {/* Summary */}
                          <div className="crash-section">
                            <h4>Ozet</h4>
                            <p className="crash-summary">{analysis.crash_score_analysis.summary}</p>
                          </div>

                          {/* Verdict */}
                          <div className="crash-section crash-verdict-section">
                            <h4>Degerlendirme</h4>
                            <p className="crash-verdict">{analysis.crash_score_analysis.verdict}</p>
                          </div>

                          {/* Deductions List */}
                          {analysis.crash_score_analysis.deductions.length > 0 && (
                            <div className="crash-section">
                              <h4>Parca Detaylari ({analysis.crash_score_analysis.total_deduction} puan dusuldu)</h4>
                              <div className="crash-deductions-list">
                                {analysis.crash_score_analysis.deductions.map((deduction, idx) => (
                                  <div key={idx} className="crash-deduction-item">
                                    <div className="crash-deduction-header">
                                      <span className="crash-part-name">{deduction.part_name}</span>
                                      <span className={`crash-condition-tag ${getConditionClass(deduction.condition)}`}>
                                        {getConditionLabel(deduction.condition)}
                                      </span>
                                      <span className="crash-deduction-points">-{deduction.deduction}</span>
                                    </div>
                                    <p className="crash-deduction-advice">{deduction.advice}</p>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* No deductions - pristine car */}
                          {analysis.crash_score_analysis.deductions.length === 0 && (
                            <div className="crash-section crash-pristine">
                              <div className="crash-pristine-icon">✓</div>
                              <h4>Kusursuz Durum</h4>
                              <p>Bu aracta boyali, lokal boyali veya degisen parca bulunmamaktadir.</p>
                            </div>
                          )}
                        </>
                      ) : (
                        <div className="crash-unavailable">
                          <div className="crash-unavailable-icon">⚠️</div>
                          <h4>Hasar Skoru Hesaplanamadi</h4>
                          <p>Boyali/degisen parca bilgisi mevcut degil.</p>
                        </div>
                      )}
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

                    {/* No parts message - show when no boyalı, lokal boyalı, or değişen parts exist */}
                    {!listing.boyali_degisen?.boyali && !listing.boyali_degisen?.degisen && !listing.boyali_degisen?.lokal_boyali &&
                     !listing.painted_parts?.boyali && !listing.painted_parts?.degisen && !listing.painted_parts?.lokal_boyali && (
                      <p className="no-parts-message">Boyalı veya değişen parça bulunmamaktadır.</p>
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
