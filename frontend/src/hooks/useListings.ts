import { useState, useCallback } from 'react';
import { type CarListing } from '../api/crawlerApi';
import {
  getListings,
  deleteListing as deleteListingApi,
  getStats,
  searchListings as searchListingsApi,
} from '../api/listingsApi';

type SearchFilters = Record<string, any>;

interface Stats {
  total_listings: number;
  avg_price: number;
  avg_quality_score: number;
  price_range: {
    min: number;
    max: number;
  };
  year_range: {
    min: number;
    max: number;
  };
}

interface UseListingsReturn {
  listings: CarListing[];
  stats: Stats | null;
  loading: boolean;
  error: string | null;
  loadListings: (limit?: number) => Promise<void>;
  loadStats: () => Promise<void>;
  deleteListing: (listingId: string) => Promise<boolean>;
  searchListings: (filters: SearchFilters) => Promise<void>;
  reset: () => void;
}

export function useListings(_userId: string | null): UseListingsReturn {
  const [listings, setListings] = useState<CarListing[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadListings = useCallback(
    async (limit: number = 50) => {
      setLoading(true);
      setError(null);
      try {
        const response = await getListings(limit);
        setListings(response.data);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to load listings';
        setError(errorMessage);
        console.error('Error loading listings:', err);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const loadStats = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getStats();
      setStats(response.data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load stats';
      setError(errorMessage);
      console.error('Error loading stats:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const deleteListing = useCallback(
    async (listingId: string): Promise<boolean> => {
      setLoading(true);
      setError(null);
      try {
        await deleteListingApi(listingId);
        setListings(prev => prev.filter(l => l.id !== listingId));
        return true;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to delete listing';
        setError(errorMessage);
        console.error('Error deleting listing:', err);
        return false;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const searchListings = useCallback(
    async (filters: SearchFilters) => {
      setLoading(true);
      setError(null);
      try {
        const response = await searchListingsApi(filters);
        setListings(response.data);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to search listings';
        setError(errorMessage);
        console.error('Error searching listings:', err);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const reset = useCallback(() => {
    setListings([]);
    setStats(null);
    setError(null);
  }, []);

  return {
    listings,
    stats,
    loading,
    error,
    loadListings,
    loadStats,
    deleteListing,
    searchListings,
    reset,
  };
}
