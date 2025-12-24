import { useState, useCallback, useEffect, useRef } from 'react';
import { crawlerApi } from '../api/crawlerApi';
import type { CrawlRequest, CrawlResult, CarListing } from '../api/crawlerApi';

type CrawlState = 'idle' | 'loading' | 'completed' | 'failed';

// Convert stored listing to CrawlResult format for display
function listingToCrawlResult(listing: CarListing): CrawlResult {
  // Normalize images to string URLs (handle both string and object formats)
  const normalizedImages = (listing.images || []).map((img) =>
    typeof img === 'string' ? img : img.url
  );

  // Convert English field names back to Turkish for ResultDisplay compatibility
  const sahibindenListing = {
    ilan_no: listing.listing_id,
    marka: listing.brand,
    seri: listing.series,
    model: listing.model,
    yil: listing.year,
    fiyat: listing.price,
    km: listing.mileage,
    yakit_tipi: listing.fuel_type,
    vites: listing.transmission,
    kasa_tipi: listing.body_type,
    motor_gucu: listing.engine_power,
    motor_hacmi: listing.engine_volume,
    cekis: listing.drive_type,
    renk: listing.color,
    kimden: listing.seller_type,
    il: listing.location,
    baslik: listing.title,
    aciklama: listing.description,
    teknik_ozellikler: listing.technical_specs,
    boyali_degisen: listing.painted_parts,
    gorseller: normalizedImages,
  };

  // Include analysis results if available (from server-side analysis)
  const result: any = {
    sahibinden_listing: sahibindenListing,
    images: normalizedImages,
  };

  // Add analysis results from the listing data
  if ((listing as any).buyability_score || (listing as any).statistical_analysis || (listing as any).llm_analysis || (listing as any).crash_score_analysis) {
    result.analysis = {
      buyability_score: (listing as any).buyability_score,
      statistical_analysis: (listing as any).statistical_analysis,
      llm_analysis: (listing as any).llm_analysis,
      crash_score_analysis: (listing as any).crash_score_analysis,
    };
  }

  return {
    job_id: `stored-${listing.listing_id}`,
    url: `https://www.sahibinden.com/ilan/${listing.listing_id}`,
    status: 'completed',
    result,
  } as CrawlResult;
}

export const useCrawler = () => {
  const [state, setState] = useState<CrawlState>('idle');
  const [jobId, setJobId] = useState<string | null>(null);
  const [result, setResult] = useState<CrawlResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState<number>(0);
  const [statusMessage, setStatusMessage] = useState<string>('');
  const [elapsedSeconds, setElapsedSeconds] = useState<number>(0);

  const pollingRef = useRef<NodeJS.Timeout | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const startTimeRef = useRef<Date | null>(null);

  // Start crawl
  const startCrawl = useCallback(async (request: CrawlRequest) => {
    try {
      setState('loading');
      setError(null);
      setProgress(0);
      setStatusMessage('Starting analysis...');
      setElapsedSeconds(0);
      setResult(null);
      startTimeRef.current = new Date();

      // Start crawl job
      const response = await crawlerApi.startCrawl(request);
      setJobId(response.job_id);
      setStatusMessage(response.message);

      // Start polling for status
      startPolling(response.job_id);

      // Start timer
      startTimer();
    } catch (err: any) {
      setState('failed');
      setError(err.response?.data?.detail || err.message || 'Failed to start analysis');
      stopPolling();
      stopTimer();
    }
  }, []);

  // Start polling
  const startPolling = (jId: string) => {
    pollingRef.current = setInterval(async () => {
      try {
        const status = await crawlerApi.getJobStatus(jId);
        setProgress(status.progress);
        setStatusMessage(status.message);

        if (status.status === 'completed') {
          stopPolling();
          stopTimer();
          fetchResult(jId);
        } else if (status.status === 'failed') {
          stopPolling();
          stopTimer();
          setState('failed');
          setError(status.message || 'Analysis failed');
        }
      } catch (err: any) {
        console.error('Polling error:', err);
        // Continue polling despite errors
      }
    }, 2000); // Poll every 2 seconds
  };

  // Start elapsed time timer
  const startTimer = () => {
    timerRef.current = setInterval(() => {
      setElapsedSeconds((prev) => prev + 1);
    }, 1000);
  };

  // Stop polling
  const stopPolling = () => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
  };

  // Stop timer
  const stopTimer = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  };

  // Fetch final result
  const fetchResult = async (jId: string) => {
    try {
      const data = await crawlerApi.getCrawlResult(jId);
      setResult(data);
      setState('completed');
      setProgress(100);
      setStatusMessage('Analysis completed');
    } catch (err: any) {
      setState('failed');
      setError(err.response?.data?.detail || 'Failed to fetch result');
    }
  };

  // Reset state
  const reset = useCallback(() => {
    stopPolling();
    stopTimer();
    setState('idle');
    setJobId(null);
    setResult(null);
    setError(null);
    setProgress(0);
    setStatusMessage('');
    setElapsedSeconds(0);
    startTimeRef.current = null;
  }, []);

  // Load a stored listing from history
  const loadStoredListing = useCallback((listing: CarListing) => {
    stopPolling();
    stopTimer();
    const crawlResult = listingToCrawlResult(listing);
    setResult(crawlResult);
    setJobId(crawlResult.job_id);
    setState('completed');
    setProgress(100);
    setStatusMessage('Loaded from history');
    setError(null);
    setElapsedSeconds(0);
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopPolling();
      stopTimer();
    };
  }, []);

  return {
    state,
    jobId,
    result,
    error,
    progress,
    statusMessage,
    elapsedSeconds,
    startCrawl,
    reset,
    loadStoredListing,
  };
};

export default useCrawler;
