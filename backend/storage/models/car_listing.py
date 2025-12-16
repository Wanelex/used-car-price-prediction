"""CarListing model - main vehicle listing data"""

from sqlalchemy import Column, Integer, String, Numeric, DateTime, Boolean, JSON, Text, ForeignKey, Enum, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from decimal import Decimal
import enum

from .base import Base


class CarListingSource(str, enum.Enum):
    """Enum for listing source"""
    SAHIBINDEN = "sahibinden"
    ARABAM = "arabam"
    HEPSIEMLAK = "hepsiemlak"


class CarListing(Base):
    """
    Main car listing table
    Stores cleaned and validated car listing data from various sources
    """
    __tablename__ = "car_listings"

    # Primary key and identifiers
    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(String(50), unique=True, nullable=False, index=True)  # ilan_no
    url = Column(String(500), nullable=False)
    source = Column(String(50), default=CarListingSource.SAHIBINDEN, nullable=False)

    # Overview Section - Core Vehicle Information
    brand = Column(String(100), nullable=True)  # Marka (BMW, Toyota, etc.)
    series = Column(String(100), nullable=True)  # Seri (5 Serisi, etc.)
    model = Column(String(100), nullable=True)  # Model (530i, etc.)
    year = Column(Integer, nullable=True)  # Yıl (2004, 2025, etc.)
    price = Column(Numeric(15, 2), nullable=True)  # Fiyat in TL
    mileage = Column(Integer, nullable=True)  # KM (389000, etc.)
    listing_date = Column(DateTime, nullable=True)  # İlan Tarihi

    # Vehicle Details Section
    fuel_type = Column(String(100), nullable=True)  # Yakıt Tipi (Benzin, Dizel, etc.)
    transmission = Column(String(100), nullable=True)  # Vites (Otomatik, Düz, etc.)
    body_type = Column(String(100), nullable=True)  # Kasa Tipi (Sedan, SUV, etc.)
    engine_power = Column(String(100), nullable=True)  # Motor Gücü (231 hp, etc.)
    engine_volume = Column(String(100), nullable=True)  # Motor Hacmi (2979 cc, etc.)
    drive_type = Column(String(100), nullable=True)  # Çekiş (Arkadan İtiş, etc.)
    color = Column(String(100), nullable=True)  # Renk (Siyah, Beyaz, etc.)
    vehicle_condition = Column(String(100), nullable=True)  # Araç Durumu (İkinci El, etc.)

    # Seller & Listing Info Section
    seller_type = Column(String(100), nullable=True)  # Kimden (Galeriden, Sahibinden, etc.)
    location = Column(String(200), nullable=True)  # Konum (Ankara, İstanbul, etc.)
    warranty = Column(String(100), nullable=True)  # Garanti (Evet, Hayır, etc.)
    heavy_damage = Column(Boolean, nullable=True)  # Ağır Hasar Kayıtlı
    plate_origin = Column(String(100), nullable=True)  # Plaka / Uyruk (Türkiye, etc.)
    trade_option = Column(Boolean, nullable=True)  # Takas

    # Description fields
    title = Column(String(500), nullable=True)  # İlan başlığı
    description = Column(Text, nullable=True)  # Açıklama
    phone = Column(String(50), nullable=True)  # Telefon (if available)

    # Structured Data (JSONB for flexibility)
    features = Column(JSON, nullable=True, default={})  # Özellikler - nested dict
    # {
    #   "Güvenlik": ["ABS", "ESP", ...],
    #   "İç Donanım": ["Klima", "Elektrikli Camlar", ...],
    #   "Dış Donanım": ["Sunroof", "Park Sensörü", ...],
    #   "Multimedya": ["Apple CarPlay", "Android Auto", ...]
    # }

    technical_specs = Column(JSON, nullable=True, default={})  # Teknik Özellikler
    # {
    #   "Motor Tipi": "Benzinli / 6 silindir",
    #   "Hızlanma 0-100": "7,1 sn",
    #   "Azami Sürat": "245 km/saat",
    #   ...
    # }

    painted_parts = Column(JSON, nullable=True, default={})  # Boyalı ve Değişen Parçalar
    # {
    #   "boyali": ["Sağ Ön Kapı", "Sol Ön Kapı", ...],
    #   "degisen": ["Motor Kaputu", "Sağ Ön Çamurluk", ...],
    #   "gorseller": ["image_url_1", ...]
    # }

    # Metadata
    crawled_at = Column(DateTime, server_default=func.now(), nullable=False)  # When crawled
    cleaned_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)  # When cleaned
    data_quality_score = Column(Numeric(3, 2), default=0.0, nullable=False)  # 0.0 to 1.0
    has_images = Column(Boolean, default=False)
    has_painted_diagram = Column(Boolean, default=False)

    # Relationships
    images = relationship("ListingImage", back_populates="listing", cascade="all, delete-orphan")

    # Indexes for performance
    __table_args__ = (
        Index('idx_listing_id', 'listing_id'),
        Index('idx_brand_year', 'brand', 'year'),
        Index('idx_price_mileage', 'price', 'mileage'),
        Index('idx_source_date', 'source', 'crawled_at'),
        UniqueConstraint('listing_id', 'source', name='uq_listing_per_source'),
    )

    def __repr__(self):
        return f"<CarListing({self.listing_id}, {self.brand} {self.model}, ₺{self.price})>"

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'listing_id': self.listing_id,
            'brand': self.brand,
            'model': self.model,
            'year': self.year,
            'price': float(self.price) if self.price else None,
            'mileage': self.mileage,
            'seller_type': self.seller_type,
            'location': self.location,
            'data_quality_score': float(self.data_quality_score),
            'crawled_at': self.crawled_at.isoformat() if self.crawled_at else None,
        }
