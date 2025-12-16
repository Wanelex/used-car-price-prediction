import React from 'react';
import { CarListing } from '../api/listingsApi';
import '../styles/ListingCard.css';

interface ListingCardProps {
  listing: CarListing;
  onClick: () => void;
}

export default function ListingCard({ listing, onClick }: ListingCardProps) {
  // Format price
  const formattedPrice = new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(listing.price);

  // Format mileage
  const formattedMileage = new Intl.NumberFormat('tr-TR').format(listing.mileage || 0);

  // Build title from brand, series, model
  const title = `${listing.brand || ''} ${listing.series || ''} ${listing.model || ''}`.trim() || 'Bilinmeyen Araç';

  // Get first image URL if available
  const imageUrl = listing.images && listing.images.length > 0
    ? `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/data/images/${listing.images[0].path}`
    : null;

  return (
    <div className="listing-card" onClick={onClick}>
      <div className="listing-image">
        {imageUrl ? (
          <img src={imageUrl} alt={title} />
        ) : (
          <span>Görsel Yok</span>
        )}
      </div>
      <div className="listing-content">
        <div className="listing-title">{title}</div>
        <div className="listing-price">{formattedPrice}</div>
        <div className="listing-info">
          <div className="info-item">
            <span className="info-label">Yıl:</span> {listing.year || '-'}
          </div>
          <div className="info-item">
            <span className="info-label">KM:</span> {formattedMileage}
          </div>
          <div className="info-item">
            <span className="info-label">Yakıt:</span> {listing.fuel_type || '-'}
          </div>
          <div className="info-item">
            <span className="info-label">Vites:</span> {listing.transmission || '-'}
          </div>
        </div>
        {listing.location && (
          <div className="listing-location">{listing.location}</div>
        )}
      </div>
    </div>
  );
}
