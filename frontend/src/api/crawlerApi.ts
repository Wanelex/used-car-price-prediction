import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export type JobStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';

export interface CrawlRequest {
  url: string;
  use_stealth?: boolean;
  use_proxy?: boolean;
  solve_captcha?: boolean;
  timeout?: number;
  max_retries?: number;
  wait_time?: number;
  wait_for_selector?: string;
  extract_images?: boolean;
  extract_links?: boolean;
  custom_headers?: Record<string, string>;
}

export interface CrawlResponse {
  job_id: string;
  status: JobStatus;
  message: string;
  estimated_time?: number;
}

export interface JobStatusResponse {
  job_id: string;
  status: JobStatus;
  progress: number;
  message: string;
}

export interface PageMetadata {
  title?: string;
  description?: string;
  keywords?: string[];
  author?: string;
  og_title?: string;
  og_description?: string;
  og_image?: string;
  canonical_url?: string;
  language?: string;
  charset?: string;
}

export interface CrawlResult {
  job_id: string;
  url: string;
  status: JobStatus;
  timestamp: string;
  result?: {
    html?: string;
    text?: string;
    title?: string;
    metadata?: PageMetadata;
    images?: string[];
    links?: string[];
    final_url?: string;
    response_time?: number;
    captcha_solved?: boolean;
    method?: string;
    crawl_duration?: number;
  };
  crawl_duration?: number;
  error_message?: string;
}

async function startCrawl(request: CrawlRequest): Promise<CrawlResponse> {
  const response = await api.post('/api/v1/crawl', request);
  return response.data;
}

async function getJobStatus(jobId: string): Promise<JobStatusResponse> {
  const response = await api.get(`/api/v1/jobs/${jobId}/status`);
  return response.data;
}

async function getCrawlResult(jobId: string): Promise<CrawlResult> {
  const response = await api.get(`/api/v1/crawl/${jobId}/result`);
  return response.data;
}

async function healthCheck() {
  const response = await api.get('/health');
  return response.data;
}

export const crawlerApi = {
  startCrawl,
  getJobStatus,
  getCrawlResult,
  healthCheck,
};

export default crawlerApi;
