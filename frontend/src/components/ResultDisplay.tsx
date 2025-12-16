import React, { useState } from 'react';
import type { CrawlResult } from '../api/crawlerApi';
import './ResultDisplay.css';

interface ResultDisplayProps {
  result: CrawlResult;
  onNewCrawl: () => void;
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

export const ResultDisplay: React.FC<ResultDisplayProps> = ({ result, onNewCrawl }) => {
  const [activeTab, setActiveTab] = useState<'listing' | 'details' | 'specs' | 'parts' | 'images' | 'html'>('listing');

  const crawlData = result.result;
  const listing = crawlData?.sahibinden_listing;

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

                    {/* Açıklama */}
                    {(listing.boyali_degisen?.aciklama || listing.painted_parts?.aciklama) && (
                      <div className="parts-description">
                        <p>{listing.boyali_degisen?.aciklama || listing.painted_parts?.aciklama}</p>
                      </div>
                    )}

                    {!listing.boyali_degisen?.boyali && !listing.boyali_degisen?.degisen &&
                     !listing.painted_parts?.boyali && !listing.painted_parts?.degisen && (
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
