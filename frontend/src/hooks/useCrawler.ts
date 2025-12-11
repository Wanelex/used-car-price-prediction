import { useState, useCallback, useEffect, useRef } from 'react';
import { crawlerApi } from '../api/crawlerApi';
import type { CrawlRequest, CrawlResult } from '../api/crawlerApi';

type CrawlState = 'idle' | 'loading' | 'completed' | 'failed';

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
      setStatusMessage('Starting crawl...');
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
      setError(err.response?.data?.detail || err.message || 'Failed to start crawl');
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
          setError(status.message || 'Crawl failed');
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
      setStatusMessage('Crawl completed');
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
  };
};

export default useCrawler;
