import { useState, useCallback, useEffect } from 'react';
import {
  type CarListing,
  type SearchFilters,
  getListings,
  getListingById,
  deleteListing as deleteListingApi,
  getStats,
  searchListings as searchListingsApi,
} from '../api/listingsApi';

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

export function useListings(userId: string | null): UseListingsReturn {
  const [listings, setListings] = useState<CarListing[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadListings = useCallback(
    async (limit: number = 50) => {
      if (!userId) {
        setError('No user ID provided');
        return;
      }

      setLoading(true);
      setError(null);
      try {
        const response = await getListings(userId, limit);
        setListings(response.data);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to load listings';
        setError(errorMessage);
        console.error('Error loading listings:', err);
      } finally {
        setLoading(false);
      }
    },
    [userId]
  );

  const loadStats = useCallback(async () => {
    if (!userId) {
      setError('No user ID provided');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const response = await getStats(userId);
      setStats(response.data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load stats';
      setError(errorMessage);
      console.error('Error loading stats:', err);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  const deleteListing = useCallback(
    async (listingId: string): Promise<boolean> => {
      if (!userId) {
        setError('No user ID provided');
        return false;
      }

      setLoading(true);
      setError(null);
      try {
        await deleteListingApi(userId, listingId);
        setListings(listings.filter(l => l.id !== listingId));
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
    [userId, listings]
  );

  const searchListings = useCallback(
    async (filters: SearchFilters) => {
      if (!userId) {
        setError('No user ID provided');
        return;
      }

      setLoading(true);
      setError(null);
      try {
        const response = await searchListingsApi(userId, filters);
        setListings(response.data);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to search listings';
        setError(errorMessage);
        console.error('Error searching listings:', err);
      } finally {
        setLoading(false);
      }
    },
    [userId]
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
