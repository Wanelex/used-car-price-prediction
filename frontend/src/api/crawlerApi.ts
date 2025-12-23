import axios from "axios";
import { getAuth } from "firebase/auth";

/**
 * Backend base url
 * FastAPI: http://127.0.0.1:8000
 * Prefix:  /api/v1
 */
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ??
  "http://127.0.0.1:8000/api/v1";

/**
 * Axios instance
 */
const api = axios.create({
  baseURL: API_BASE_URL,
});

/**
 *  Firebase Auth interceptor
 */
api.interceptors.request.use(async (config) => {
  const auth = getAuth();
  const user = auth.currentUser;

  if (user) {
    const token = await user.getIdToken(true);
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

/**
 * Job status types (backend ile birebir)
 */
export type JobStatus =
  | "pending"
  | "running"
  | "completed"
  | "failed"
  | "cancelled";

/**
 * Backend Job modeli (JobInfo)
 */
export interface Job {
  job_id: string;
  url: string;
  status: JobStatus;
  created_at: string;
  started_at?: string | null;
  completed_at?: string | null;
  error_message?: string | null;
  retry_count: number;
  progress: number;
  message?: string;
}

/**
 * Crawl Request (frontend form data)
 */
export interface CrawlRequest {
  url: string;
  use_stealth?: boolean;
  solve_captcha?: boolean;
  max_retries?: number;
  wait_time?: number;
  extract_images?: boolean;
  extract_links?: boolean;
}

/**
 * Crawl Result
 */
export interface CrawlResult {
  job_id: string;
  url: string;
  status: JobStatus;
  data?: any;
}

/**
 *  START CRAWL
 * POST /api/v1/crawl
 */
export async function startCrawl(request: CrawlRequest): Promise<Job> {
  const response = await api.post("/crawl", request);

  return response.data;
}

/**
 * GET JOB (detail)
 * GET /api/v1/jobs/{job_id}
 */
export async function getJob(jobId: string): Promise<Job> {
  const response = await api.get(`/jobs/${jobId}`);
  return response.data;
}

/**
 *  GET JOB STATUS
 * GET /api/v1/jobs/{job_id}/status
 */
export async function getJobStatus(jobId: string): Promise<{
  job_id: string;
  status: JobStatus;
  progress: number;
  message: string;
}> {
  const response = await api.get(`/jobs/${jobId}/status`);
  return response.data;
}

/**
 *  DELETE JOB
 * DELETE /api/v1/jobs/{job_id}
 */
export async function deleteJob(jobId: string) {
  const response = await api.delete(`/jobs/${jobId}`);
  return response.data;
}

/**
 *  DELETE ALL JOBS
 * DELETE /api/v1/jobs
 */
export async function deleteAllJobs() {
  const response = await api.delete("/jobs");
  return response.data;
}

/**
 *  LIST JOBS
 * GET /api/v1/jobs
 */
export async function listJobs(): Promise<Job[]> {
  const response = await api.get("/jobs");
  return response.data;
}

/**
 * GET CRAWL RESULT
 * GET /api/v1/crawl/{job_id}/result
 */
export async function getCrawlResult(jobId: string): Promise<CrawlResult> {
  const response = await api.get(`/crawl/${jobId}/result`);
  return response.data;
}

/**
 * Listing interface (from database)
 */
export interface CarListing {
  id?: string;
  listing_id: string;
  brand?: string;
  series?: string;
  model?: string;
  year?: number;
  price?: number;
  mileage?: number;
  fuel_type?: string;
  transmission?: string;
  body_type?: string;
  engine_power?: string;
  engine_volume?: string;
  drive_type?: string;
  color?: string;
  location?: string;
  seller_type?: string;
  title?: string;
  description?: string;
  technical_specs?: Record<string, any>;
  painted_parts?: Record<string, any>;
  crawled_at?: string;
  data_quality_score?: number;
  images?: Array<string | { url: string; is_primary?: boolean }>;
}

/**
 * GET LISTINGS (user's analysis history)
 * GET /api/v1/listings
 */
export async function getListings(limit = 50, skip = 0): Promise<{
  status: string;
  count: number;
  data: CarListing[];
}> {
  const auth = getAuth();
  const user = auth.currentUser;

  if (!user) {
    throw new Error("User not authenticated");
  }

  const response = await api.get("/listings", {
    params: { limit, skip },
    headers: {
      "user-id": user.uid
    }
  });
  return response.data;
}

/**
 * GET SINGLE LISTING
 * GET /api/v1/listings/{listing_id}
 */
export async function getListing(listingId: string): Promise<{
  status: string;
  data: CarListing;
}> {
  const auth = getAuth();
  const user = auth.currentUser;

  if (!user) {
    throw new Error("User not authenticated");
  }

  const response = await api.get(`/listings/${listingId}`, {
    headers: {
      "user-id": user.uid
    }
  });
  return response.data;
}

/**
 * DELETE LISTING
 * DELETE /api/v1/listings/{listing_id}
 */
export async function deleteListing(listingId: string): Promise<{
  status: string;
  message: string;
}> {
  const auth = getAuth();
  const user = auth.currentUser;

  if (!user) {
    throw new Error("User not authenticated");
  }

  const response = await api.delete(`/listings/${listingId}`, {
    headers: {
      "user-id": user.uid
    }
  });
  return response.data;
}

/**
 * ANALYZE LISTING
 * POST /api/v1/analyze
 */
export async function analyzeListing(params: Record<string, string>): Promise<any> {
  const queryString = new URLSearchParams(params).toString();
  const response = await api.post(`/analyze?${queryString}`);
  return response.data;
}

/**
 * Export as object (opsiyonel kullanım)
 */
export const crawlerApi = {
  startCrawl,
  getJob,
  getJobStatus,
  getCrawlResult,
  listJobs,
  deleteJob,
  deleteAllJobs,
  getListings,
  getListing,
  deleteListing,
  analyzeListing,
};

export default crawlerApi;
