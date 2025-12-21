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
}

/**
 *  START CRAWL
 * POST /api/v1/jobs
 */
export async function startCrawl(url: string): Promise<Job> {
  const response = await api.post("/jobs", {
    url,
  });

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
 * Export as object (opsiyonel kullanım)
 */
export const crawlerApi = {
  startCrawl,
  getJob,
  getJobStatus,
  listJobs,
  deleteJob,
  deleteAllJobs,
};

export default crawlerApi;
