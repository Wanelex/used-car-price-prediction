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

// ===== BUYABILITY ANALYSIS TYPES =====

export interface CarIdentification {
  engine_code: string;
  transmission_name: string;
  generation?: string;
}

export interface ExpertAnalysis {
  general_comment: string;
  engine_reliability: string;
  transmission_reliability: string;
  km_endurance_check: string;
}

export interface Recommendation {
  verdict: string;
  buy_or_pass: string;
}

export interface MechanicalScores {
  mechanical_score: number;
  reasoning_for_score: string;
}

export interface LLMMechanicalAnalysis {
  car_identification: CarIdentification;
  expert_analysis: ExpertAnalysis;
  recommendation: Recommendation;
  scores: MechanicalScores;
}

export interface FeatureScore {
  feature: string;
  value: number;
  importance: number;
}

export interface StatisticalAnalysis {
  risk_score: number;
  decision: string;
  probability: number;
  health_score: number;
  risk_factors: string[];
  feature_scores: Record<string, number>;
  top_features: FeatureScore[];
  explanation: string;
}

// ===== CRASH SCORE TYPES =====

export interface PartDeduction {
  part_name: string;
  condition: string; // 'degisen', 'boyali', or 'lokal_boyali'
  deduction: number;
  advice: string;
}

export interface CrashScoreAnalysis {
  score: number;
  total_deduction: number;
  deductions: PartDeduction[];
  summary: string;
  risk_level: string;
  verdict: string;
}

// ===== BUYABILITY SCORE TYPES =====

export interface ComponentScores {
  statistical: number | null;
  mechanical: number | null;
  crash: number | null;
}

export interface CalculationBreakdown {
  weighted_average: number;
  min_score: number;
  blended_score: number;
  penalty_applied: number;
  bonus_applied: number;
}

export interface BuyabilityScore {
  final_score: number;
  tier: 'KACIN' | 'RISKLI' | 'DIKKAT' | 'NORMAL' | 'GUVENLI';
  tier_label_tr: string;
  component_scores: ComponentScores;
  calculation_breakdown: CalculationBreakdown;
  calculation_summary: string;
  warning_message: string | null;
}

export interface HybridAnalysis {
  status: string;
  input: Record<string, any>;
  buyability_score?: BuyabilityScore | null;
  statistical_analysis: StatisticalAnalysis;
  llm_analysis?: LLMMechanicalAnalysis | null;
  crash_score_analysis?: CrashScoreAnalysis | null;
  timestamp: string;
}

// Legacy type alias for backward compatibility
export type BuyabilityAnalysis = StatisticalAnalysis;

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
