import React, { useState } from 'react';
import { CarListing } from '../api/listingsApi';
import '../styles/ListingDetail.css';

interface ListingDetailProps {
  listing: CarListing;
  onClose: () => void;
  onDelete: () => Promise<void>;
}

export default function ListingDetail({ listing, onClose, onDelete }: ListingDetailProps) {
  const [isDeleting, setIsDeleting] = useState(false);

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
