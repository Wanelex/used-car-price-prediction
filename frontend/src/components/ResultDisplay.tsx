import React, { useState, useEffect } from 'react';
import type { CrawlResult } from '../api/crawlerApi';
import { analyzeListing, saveListingAnalysis } from '../api/crawlerApi';
import type { HybridAnalysis } from '../api/listingsApi';
import { useLanguage } from '../i18n';
import './ResultDisplay.css';

export type TabType = 'analysis' | 'listing' | 'specs' | 'parts' | 'html';

interface ResultDisplayProps {
  result: CrawlResult;
  activeTab: TabType;
}

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

export const ResultDisplay: React.FC<ResultDisplayProps> = ({ result, activeTab }) => {
  const [analysis, setAnalysis] = useState<HybridAnalysis | null>(null);
  const [analysisLoading, setAnalysisLoading] = useState(true);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const { t, language } = useLanguage();

  const crawlData = result.result;
  const listing = crawlData?.sahibinden_listing;

  // Fetch buyability analysis when component mounts (with localStorage caching)
  useEffect(() => {
    const fetchAnalysis = async () => {
      if (!listing) {
        setAnalysisLoading(false);
        setAnalysisError('No listing data available');
        return;
      }

      // Get listing ID for cache key (include language for proper translation caching)
      const listingId = listing.ilan_no || listing.listing_id;
      const cacheKey = listingId ? `analysis_cache_${listingId}_${language}` : null;

      // Check if analysis results are already in the listing data (from server-side analysis)
      if (crawlData?.analysis) {
        console.log('Using server-side analysis for listing:', listingId);
        setAnalysis(crawlData.analysis);
        setAnalysisLoading(false);
        return;
      }

      // Check localStorage cache second
      if (cacheKey) {
        try {
          const cached = localStorage.getItem(cacheKey);
          if (cached) {
            const cachedData = JSON.parse(cached);
            // Check if cache is still valid (24 hours)
            if (cachedData.timestamp && Date.now() - cachedData.timestamp < 24 * 60 * 60 * 1000) {
              console.log('Using cached analysis for listing:', listingId);
              setAnalysis(cachedData.data);
              setAnalysisLoading(false);
              return;
            }
          }
        } catch (e) {
          console.warn('Failed to read analysis cache:', e);
        }
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

        const params: Record<string, string> = {
          year: String(parsedYear),
          mileage: String(parsedMileage),
        };

        // Add optional fields for statistical model
        if (engineVolume) params.engine_volume = String(engineVolume);
        if (enginePower) params.engine_power = String(enginePower);

        // Add optional fields for LLM analysis
        const make = listing.marka || listing.brand;
        const series = listing.seri || listing.series;
        const model = listing.model;
        const fuelType = listing.yakit_tipi || listing.fuel_type;
        const transmission = listing.vites || listing.transmission;
        const bodyType = listing.kasa_tipi || listing.body_type;
        const driveType = listing.cekis || listing.drive_type;
        const price = listing.fiyat || listing.price;

        if (make) params.make = String(make);
        if (series) params.series = String(series);
        if (model) params.model = String(model);
        if (fuelType) params.fuel_type = String(fuelType);
        if (transmission) params.transmission = String(transmission);
        if (bodyType) params.body_type = String(bodyType);
        if (driveType) params.drive_type = String(driveType);
        if (price) params.price = String(price);

        // Add parts data for crash score calculation
        const partsData = listing.boyali_degisen || listing.painted_parts;
        if (partsData) {
          if (partsData.boyali && partsData.boyali.length > 0) {
            params.painted_parts = partsData.boyali.join(',');
          }
          if (partsData.degisen && partsData.degisen.length > 0) {
            params.changed_parts = partsData.degisen.join(',');
          }
          if (partsData.lokal_boyali && partsData.lokal_boyali.length > 0) {
            params.local_painted_parts = partsData.lokal_boyali.join(',');
          }
        }

        // Add language for translations
        params.language = language;

        // Use authenticated API call
        const data = await analyzeListing(params);
        // Now response contains statistical_analysis and llm_analysis
        setAnalysis(data);

        // Cache the analysis result in localStorage
        if (cacheKey) {
          try {
            localStorage.setItem(cacheKey, JSON.stringify({
              data,
              timestamp: Date.now()
            }));
            console.log('Cached analysis for listing:', listingId);
          } catch (e) {
            console.warn('Failed to cache analysis:', e);
          }
        }

        // For old listings loaded from history that don't have analysis in DB yet,
        // save the analysis to the server so future loads won't re-analyze
        if (listing && !crawlData?.analysis && listingId && data) {
          try {
            console.log('Saving analysis results to server for listing:', listingId);
            await saveListingAnalysis(listingId, {
              buyability_score: data.buyability_score,
              statistical_analysis: data.statistical_analysis,
              llm_analysis: data.llm_analysis,
              crash_score_analysis: data.crash_score_analysis
            });
            console.log('Successfully saved analysis results to server');
          } catch (e) {
            console.warn('Could not save analysis to server:', e);
          }
        }
      } catch (err: any) {
        console.error('Failed to fetch analysis:', err);
        setAnalysisError(err.message || 'Analysis unavailable');
      } finally {
        setAnalysisLoading(false);
      }
    };

    fetchAnalysis();
  }, [listing, language]);

  // Get risk level class based on score
  const getRiskLevelClass = (score: number): string => {
    if (score >= 71) return 'risk-low';
    if (score >= 51) return 'risk-moderate';
    return 'risk-high';
  };

  // Get risk level text
  const getRiskLevelText = (score: number): string => {
    if (score >= 86) return t.analysis.riskLevels.minimal;
    if (score >= 71) return t.analysis.riskLevels.veryLow;
    if (score >= 51) return t.analysis.riskLevels.low;
    if (score >= 31) return t.analysis.riskLevels.medium;
    return t.analysis.riskLevels.high;
  };

  // Get mechanical risk level class for LLM score
  const getMechanicalRiskClass = (score: number): string => {
    if (score >= 71) return 'risk-low';
    if (score >= 51) return 'risk-moderate';
    return 'risk-high';
  };

  // Get mechanical risk text
  const getMechanicalRiskText = (score: number): string => {
    if (score >= 86) return t.analysis.mechanicalLevels.legendary;
    if (score >= 71) return t.analysis.mechanicalLevels.high;
    if (score >= 51) return t.analysis.mechanicalLevels.medium;
    if (score >= 31) return t.analysis.mechanicalLevels.low;
    return t.analysis.mechanicalLevels.risk;
  };

  // Get crash score risk level class
  const getCrashRiskClass = (score: number): string => {
    if (score >= 70) return 'risk-low';
    if (score >= 40) return 'risk-moderate';
    return 'risk-high';
  };

  // Get crash score verdict text based on score
  const getCrashVerdictText = (score: number): string => {
    if (score >= 90) return t.analysis.crashVerdicts.excellent;
    if (score >= 70) return t.analysis.crashVerdicts.good;
    if (score >= 50) return t.analysis.crashVerdicts.caution;
    if (score >= 25) return t.analysis.crashVerdicts.danger;
    return t.analysis.crashVerdicts.notBuyable;
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

  // Get condition label with translation support
  const getConditionLabel = (condition: string): string => {
    switch (condition) {
      case 'degisen': return t.analysis.conditionLabels.changed;
      case 'boyali': return t.analysis.conditionLabels.painted;
      case 'lokal_boyali': return t.analysis.conditionLabels.localPainted;
      default: return condition;
    }
  };

  // Translate crash score text (Turkish -> English when needed)
  const translateCrashText = (text: string): string => {
    if (!text) return text;
    // If English is selected and we have a translation, use it
    if (language === 'en' && t.analysis.crashScoreTranslations) {
      const translations = t.analysis.crashScoreTranslations as Record<string, string>;
      return translations[text] || text;
    }
    return text;
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

  // Translate feature score names
  const featureScoreLabels: Record<string, string> = {
    age_score: t.analysis.featureLabels.carAge,
    km_per_year_score: t.analysis.featureLabels.annualMileage,
    km_score: t.analysis.featureLabels.totalMileage,
    year_score: t.analysis.featureLabels.modelYear,
    hp_score: t.analysis.featureLabels.enginePower,
    ccm_score: t.analysis.featureLabels.engineVolume
  };

  // Build title from brand, series, model
  const listingTitle = listing
    ? `${listing.marka || listing.brand || ''} ${listing.seri || listing.series || ''} ${listing.model || ''}`.trim() || 'Araç İlanı'
    : crawlData?.title || 'Analysis Result';

  // Get all images from crawl result (this is the reliable source)
  const allImages = crawlData?.images || [];
  // First 2 images for display
  const listingImages = allImages.slice(0, 2);

  return (
      <div className="result-display">
        {/* Show listing data if available */}
        {listing ? (
          <>
            {/* Car Title - Centered below tabs */}
            <div className="car-title-section">
              <h1 className="car-title">{listingTitle}</h1>
            </div>

            <div className="tab-content">
            {/* Alinabilirlik Analizi Tab - Hybrid Two-Column Layout */}
            {activeTab === 'analysis' && (
              <div className="analysis-section">
                {analysisLoading && (
                  <div className="analysis-loading">
                    <div className="loading-spinner-small"></div>
                    <span>{t.analysis.analyzing}</span>
                  </div>
                )}
                {analysisError && (
                  <div className="analysis-error">
                    <span>{t.analysis.analysisFailed.replace('{error}', analysisError)}</span>
                  </div>
                )}
                {analysis && !analysisLoading && (
                  <div className="hybrid-analysis-container">

                    {/* HERO SECTION: Image + Score + Image */}
                    {analysis.buyability_score && (
                      <div className="hero-score-section">
                        {/* Left: First Car Image */}
                        <div className="hero-image-side">
                          {allImages.length > 0 && (
                            <img
                              src={allImages[0]}
                              alt={listingTitle}
                              className="hero-car-image"
                              onError={(e) => (e.currentTarget.style.display = 'none')}
                            />
                          )}
                        </div>
                        {/* Center: Score Info */}
                        <div className="hero-score-center">
                          <div className={`hero-score-circle ${getBuyabilityScoreClass(analysis.buyability_score.final_score)}`}>
                            <span className="hero-score-value">{analysis.buyability_score.final_score}</span>
                            <span className="hero-score-max">/100</span>
                          </div>
                          <div className={`hero-tier-badge ${getBuyabilityTierClass(analysis.buyability_score.tier)}`}>
                            {analysis.buyability_score.tier}
                          </div>
                          <div className="hero-component-scores">
                            <div className="hero-component-item">
                              <span className="hero-component-label">{t.analysis.componentScores.statistical}</span>
                              <span className="hero-component-value">{analysis.buyability_score.component_scores.statistical ?? '-'}</span>
                            </div>
                            <div className="hero-component-item">
                              <span className="hero-component-label">{t.analysis.componentScores.mechanical}</span>
                              <span className="hero-component-value">{analysis.buyability_score.component_scores.mechanical ?? '-'}</span>
                            </div>
                            <div className="hero-component-item">
                              <span className="hero-component-label">{t.analysis.componentScores.crash}</span>
                              <span className="hero-component-value">{analysis.buyability_score.component_scores.crash ?? '-'}</span>
                            </div>
                          </div>
                        </div>
                        {/* Right: Second Car Image */}
                        <div className="hero-image-side">
                          {allImages.length > 1 && (
                            <img
                              src={allImages[1]}
                              alt={listingTitle}
                              className="hero-car-image"
                              onError={(e) => (e.currentTarget.style.display = 'none')}
                            />
                          )}
                        </div>
                      </div>
                    )}

                    {/* LEFT COLUMN: Statistical Health Score */}
                    <div className="analysis-column statistical-column">
                      <h3 className="analysis-column-title">{t.analysis.statisticalHealthScore}</h3>

                      <div className={`risk-score-card ${getRiskLevelClass(analysis.statistical_analysis.risk_score)}`}>
                        <div className="risk-score-main">
                          <span className="risk-score-value">{analysis.statistical_analysis.risk_score}</span>
                          <span className="risk-score-max">/100</span>
                        </div>
                        <div className="risk-decision">
                          {analysis.statistical_analysis.decision === 'BUYABLE' ? t.analysis.buyable : t.analysis.notBuyable}
                        </div>
                        <div className="risk-explanation">{getRiskLevelText(analysis.statistical_analysis.risk_score)}</div>
                      </div>

                      {/* Feature Scores */}
                      <div className="feature-scores">
                        <h4>{t.analysis.featureScores}</h4>
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
                          <h4>{t.analysis.riskFactors}</h4>
                          <ul className="risk-factors-list">
                            {analysis.statistical_analysis.risk_factors.map((factor, idx) => (
                              <li key={idx} className="risk-factor-item">{factor}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Top Contributing Features */}
                      <div className="top-features">
                        <h4>{t.analysis.topFeatures}</h4>
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
                      <h3 className="analysis-column-title">{t.analysis.mechanicalReliabilityScore}</h3>

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
                            <h4>{t.analysis.carComponents}</h4>
                            <div className="llm-info-grid">
                              <div className="llm-info-item">
                                <span className="llm-label">{t.analysis.engineCode}</span>
                                <span className="llm-value">{analysis.llm_analysis.car_identification.engine_code}</span>
                              </div>
                              <div className="llm-info-item">
                                <span className="llm-label">{t.analysis.transmission}</span>
                                <span className="llm-value">{analysis.llm_analysis.car_identification.transmission_name}</span>
                              </div>
                              {analysis.llm_analysis.car_identification.generation && (
                                <div className="llm-info-item">
                                  <span className="llm-label">{t.analysis.generation}</span>
                                  <span className="llm-value">{analysis.llm_analysis.car_identification.generation}</span>
                                </div>
                              )}
                            </div>
                          </div>

                          {/* Expert Analysis */}
                          <div className="llm-section">
                            <h4>{t.analysis.expertAnalysis}</h4>

                            <div className="llm-analysis-block">
                              <h5>{t.analysis.generalEvaluation}</h5>
                              <p>{analysis.llm_analysis.expert_analysis.general_comment}</p>
                            </div>

                            <div className="llm-analysis-block">
                              <h5>{t.analysis.engineReliability}</h5>
                              <p>{analysis.llm_analysis.expert_analysis.engine_reliability}</p>
                            </div>

                            <div className="llm-analysis-block">
                              <h5>{t.analysis.transmissionReliability}</h5>
                              <p>{analysis.llm_analysis.expert_analysis.transmission_reliability}</p>
                            </div>

                            <div className="llm-analysis-block">
                              <h5>{t.analysis.mileageEndurance}</h5>
                              <p>{analysis.llm_analysis.expert_analysis.km_endurance_check}</p>
                            </div>
                          </div>

                          {/* Recommendation */}
                          <div className="llm-section llm-recommendation">
                            <h4>{t.analysis.expertRecommendation}</h4>
                            <p className="llm-verdict">{analysis.llm_analysis.recommendation.verdict}</p>
                            <p className="llm-score-reasoning">
                              <strong>{t.analysis.scoreReasoning}</strong> {analysis.llm_analysis.scores.reasoning_for_score}
                            </p>
                          </div>
                        </>
                      ) : (
                        <div className="llm-unavailable">
                          <div className="llm-unavailable-icon">⚠️</div>
                          <h4>{t.analysis.llmNotAvailable}</h4>
                          <p>{t.analysis.mechanicalAnalysisUnavailable}</p>
                          <p className="llm-unavailable-hint">{t.analysis.apiKeyMissing}</p>
                        </div>
                      )}
                    </div>

                    {/* THIRD COLUMN: Crash Score */}
                    <div className="analysis-column crash-column">
                      <h3 className="analysis-column-title">{t.analysis.damagePaintScore}</h3>

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
                            <div className="risk-explanation">{translateCrashText(analysis.crash_score_analysis.risk_level)}</div>
                          </div>

                          {/* Summary */}
                          <div className="crash-section">
                            <h4>{t.analysis.summary}</h4>
                            <p className="crash-summary">{translateCrashText(analysis.crash_score_analysis.summary)}</p>
                          </div>

                          {/* Verdict */}
                          <div className="crash-section crash-verdict-section">
                            <h4>{t.analysis.verdict}</h4>
                            <p className="crash-verdict">{translateCrashText(analysis.crash_score_analysis.verdict)}</p>
                          </div>

                          {/* Deductions List */}
                          {analysis.crash_score_analysis.deductions.length > 0 && (
                            <div className="crash-section">
                              <h4>{t.analysis.partDetails.replace('{points}', String(analysis.crash_score_analysis.total_deduction))}</h4>
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
                                    <p className="crash-deduction-advice">{translateCrashText(deduction.advice)}</p>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* No deductions - pristine car */}
                          {analysis.crash_score_analysis.deductions.length === 0 && (
                            <div className="crash-section crash-pristine">
                              <div className="crash-pristine-icon">✓</div>
                              <h4>{t.analysis.pristineCondition}</h4>
                              <p>{t.analysis.noPaintedParts}</p>
                            </div>
                          )}
                        </>
                      ) : (
                        <div className="crash-unavailable">
                          <div className="crash-unavailable-icon">⚠️</div>
                          <h4>{t.analysis.damageScoreUnavailable}</h4>
                          <p>{t.analysis.noPaintedPartsInfo}</p>
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
                    <span className="info-label">{t.listing.listingNo}</span>
                    <span className="info-value">{listing.ilan_no || listing.listing_id || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">{t.listing.listingDate}</span>
                    <span className="info-value">{listing.ilan_tarihi || listing.listing_date || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">{t.listing.price}</span>
                    <span className="info-value price">{formatPrice(listing.fiyat || listing.price)}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">{t.listing.brand}</span>
                    <span className="info-value">{listing.marka || listing.brand || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">{t.listing.series}</span>
                    <span className="info-value">{listing.seri || listing.series || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">{t.listing.model}</span>
                    <span className="info-value">{listing.model || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">{t.listing.year}</span>
                    <span className="info-value">{listing.yil || listing.year || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">{t.listing.fuelType}</span>
                    <span className="info-value">{listing.yakit_tipi || listing.fuel_type || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">{t.listing.transmission}</span>
                    <span className="info-value">{listing.vites || listing.transmission || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">{t.listing.vehicleCondition}</span>
                    <span className="info-value">{listing.arac_durumu || listing.vehicle_condition || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">{t.listing.mileage}</span>
                    <span className="info-value">{formatMileage(listing.km || listing.mileage)}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">{t.listing.bodyType}</span>
                    <span className="info-value">{listing.kasa_tipi || listing.body_type || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">{t.listing.enginePower}</span>
                    <span className="info-value">{listing.motor_gucu || listing.engine_power || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">{t.listing.engineVolume}</span>
                    <span className="info-value">{listing.motor_hacmi || listing.engine_volume || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">{t.listing.drivetrain}</span>
                    <span className="info-value">{listing.cekis || listing.drive_type || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">{t.listing.color}</span>
                    <span className="info-value">{listing.renk || listing.color || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">{t.listing.warranty}</span>
                    <span className="info-value">{listing.garanti || listing.warranty || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">{t.listing.severelyDamaged}</span>
                    <span className="info-value">{listing.agir_hasar_kayitli || listing.heavy_damage || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">{t.listing.plateNationality}</span>
                    <span className="info-value">{listing.plaka_uyruk || listing.plate_origin || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">{t.listing.sellerType}</span>
                    <span className="info-value">{listing.kimden || listing.seller_type || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">{t.listing.tradeIn}</span>
                    <span className="info-value">{listing.takas || listing.trade_option || '-'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">{t.listing.location}</span>
                    <span className="info-value">{listing.konum || listing.location || '-'}</span>
                  </div>
                </div>
              </div>
            )}

            {/* Teknik Özellikler Tab */}
            {activeTab === 'specs' && (
              <div className="specs-section">
                <h3>{t.specs.technicalSpecs}</h3>
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
                  <p>{t.specs.noTechnicalSpecs}</p>
                )}

                {/* Donanım Özellikleri */}
                <h3 style={{ marginTop: '24px' }}>{t.specs.equipmentFeatures}</h3>
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
                  <p>{t.specs.noEquipment}</p>
                )}
              </div>
            )}

            {/* Boyalı/Değişen Tab */}
            {activeTab === 'parts' && (
              <div className="parts-section">
                <h3>{t.parts.paintedAndChanged}</h3>
                {(listing.boyali_degisen || listing.painted_parts) ? (
                  <div className="parts-container">
                    {/* Boyalı Parçalar */}
                    {(listing.boyali_degisen?.boyali || listing.painted_parts?.boyali) && (
                      <div className="parts-group">
                        <h4>{t.parts.paintedParts}</h4>
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
                        <h4>{t.parts.changedParts}</h4>
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
                        <h4>{t.parts.locallyPainted}</h4>
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
                      <p className="no-parts-message">{t.parts.noPaintedOrChanged}</p>
                    )}
                  </div>
                ) : (
                  <p>{t.parts.noInfoAvailable}</p>
                )}
              </div>
            )}

            {/* HTML/Metadata Tab */}
            {activeTab === 'html' && (
              <div className="html-section">
                <h3>{t.metadata.metadata}</h3>
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
                  <p>{t.metadata.noMetadata}</p>
                )}

                <h3 style={{ marginTop: '24px' }}>{t.metadata.analysisInfo}</h3>
                <div className="info-table">
                  <div className="info-row">
                    <span className="info-label">{t.metadata.url}</span>
                    <span className="info-value">{crawlData?.final_url || result.url}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">{t.metadata.duration}</span>
                    <span className="info-value">{crawlData?.crawl_duration?.toFixed(2)}s</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">{t.metadata.captchaSolved}</span>
                    <span className="info-value">{crawlData?.captcha_solved ? t.common.yes : t.common.no}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">{t.metadata.dataQuality}</span>
                    <span className="info-value">{listing.data_quality_score ? `${(listing.data_quality_score * 100).toFixed(0)}%` : '-'}</span>
                  </div>
                </div>

                {/* Debug: Raw Listing Data */}
                <h3 style={{ marginTop: '24px' }}>{t.metadata.debugRawData}</h3>
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
