import axios from 'axios';

export type CarListing = {
  id: string;
  listing_id: string;
  // Basic Info
  brand: string;
  series?: string;
  model: string;
  year: number;
  price: number;
  mileage: number;
  listing_date?: string;
  title?: string;
  description?: string;
  // Technical Details
  fuel_type?: string;
  transmission?: string;
  body_type?: string;
  color?: string;
  engine_power?: string;
  engine_volume?: string;
  drive_type?: string;
  // Condition & Status
  vehicle_condition?: string;
  heavy_damage?: boolean;
  warranty?: string;
  plate_origin?: string;
  trade_option?: boolean;
  // Seller Info
  seller_type?: string;
  location?: string;
  phone?: string;
  // Quality & Validation
  data_quality_score: number;
  is_valid?: boolean;
  // Complex Data
  images?: Array<{
    type: string;
    path: string;
    downloaded_at?: string;
  }>;
  features?: Record<string, string[]>;
  technical_specs?: Record<string, string>;
  painted_parts?: {
    boyali?: string[];
    degisen?: string[];
    gorseller?: string[];
  };
  // Metadata
  crawled_at: string;
  updated_at: string;
  user_id: string;
};

export type SearchFilters = {
  brand?: string;
  min_year?: number;
  max_year?: number;
  min_price?: number;
  max_price?: number;
  limit?: number;
};

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
});

export const getListings = async (userId: string, limit: number = 50, skip: number = 0) => {
  const response = await api.get('/api/v1/listings', {
    headers: { 'user-id': userId },
    params: { limit, skip },
  });
  return response.data;
};

export const getListingById = async (userId: string, listingId: string) => {
  const response = await api.get(`/api/v1/listings/${listingId}`, {
    headers: { 'user-id': userId },
  });
  return response.data;
};

export const deleteListing = async (userId: string, listingId: string) => {
  const response = await api.delete(`/api/v1/listings/${listingId}`, {
    headers: { 'user-id': userId },
  });
  return response.data;
};

export const getStats = async (userId: string) => {
  const response = await api.get('/api/v1/listings/stats/summary', {
    headers: { 'user-id': userId },
  });
  return response.data;
};

export const searchListings = async (userId: string, filters: SearchFilters) => {
  const response = await api.get('/api/v1/listings/search', {
    headers: { 'user-id': userId },
    params: filters,
  });
  return response.data;
};
