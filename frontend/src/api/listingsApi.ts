import axios from "axios";
import { getAuth } from "firebase/auth";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1";

const api = axios.create({
  baseURL: API_BASE_URL,
});

api.interceptors.request.use(async (config) => {
  const auth = getAuth();
  const user = auth.currentUser;

  if (user) {
    const token = await user.getIdToken(true);
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

export const getListings = async (limit: number = 50, skip: number = 0) => {
  const response = await api.get("/listings", {
    params: { limit, skip },
  });
  return response.data;
};

export const getListingById = async (listingId: string) => {
  const response = await api.get(`/listings/${listingId}`);
  return response.data;
};

export const deleteListing = async (listingId: string) => {
  const response = await api.delete(`/listings/${listingId}`);
  return response.data;
};

export const getStats = async () => {
  const response = await api.get("/listings/stats/summary");
  return response.data;
};

export const searchListings = async (filters: Record<string, any>) => {
  const response = await api.get("/listings/search", {
    params: filters,
  });
  return response.data;
};

export const analyzeListing = async (listingId: string) => {
  const response = await api.post(`/listings/${listingId}/analyze`);
  return response.data;
};

export const getJobs = async () => {
  const response = await api.get("/jobs");
  return response.data;
};
