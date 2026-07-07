export const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    cache: "no-store",
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    let detail = `API error ${res.status}`;
    try { const b = await res.json(); if (b?.detail) detail = String(b.detail); } catch {}
    throw new Error(detail);
  }
  return res.json();
}

/* ---------- shared types ---------- */
export interface MsmeSummary {
  msme_id: string; business_name: string | null; sector: string | null;
  finpulse_score: number; band: string; confidence_score: number;
  confidence_status: string; trend_status: string; credit_readiness: string;
  anomaly_status: string; latest_monthly_revenue: number | null; provenance: string;
}
export interface Paginated {
  items: MsmeSummary[]; total: number; page: number; page_size: number;
  total_pages: number; demo_available: boolean; guidance?: string;
}
export interface Dimension {
  score: number; status: string; positive_evidence: string[];
  risk_signals: string[]; neutral_fallback: boolean;
}
export interface HealthCard {
  identity: { msme_id: string; business_name: string | null; sector: string | null;
    business_age_years: number | null; provenance: string };
  finpulse_score: number; band: string;
  components: { dimension_composite: number; ml_component: number; anomaly_component: number };
  weights: Record<string, number>;
  dimensions: Record<string, Dimension>;
  dimension_weights: Record<string, number>;
  confidence: { confidence_score: number; confidence_status: string;
    missing_critical_evidence: string[]; recommendation: string };
  credit_readiness: { credit_readiness: string; rationale: string; disclaimer: string };
  anomaly: { anomaly_score: number; anomaly_status: string; detected_signals: string[]; note: string };
  trend: { trend_status: string; change_1m: number | null; change_3m: number | null; trend_6m_slope: number };
  model: { model_application_status: string; model_status: string; model_name: string;
    risk_probability: number | null; note: string };
  disclaimers: string[];
}
export interface Twin {
  msme_id: string; score_history: number[]; change_1m: number | null; change_3m: number | null;
  trend_6m_slope: number; deterioration_velocity: number; recovery_velocity: number;
  trend_status: string; trend_summary: string; change_points: number[];
  detected_start_period: number | null; note: string;
}
export interface Explanation {
  msme_id: string; explanation_mode: string; model_application_status: string;
  ml_factors: { feature: string; shap_value: number }[]; ml_factors_note: string;
  financial_health_signals: { dimension: string; score: number; status: string;
    positive: string[]; risks: string[] }[];
  responsible_ai_note: string;
}
export interface SimResult {
  msme_id: string; current_score: number; simulated_score: number; score_change: number;
  dimension_changes: Record<string, number>; improvement_insights: string[];
  disclaimer: string; current_values: Record<string, number | null>;
}
export interface Analytics {
  total_msmes: number; average_finpulse_score: number; average_confidence_score: number;
  band_distribution: Record<string, number>; credit_readiness_distribution: Record<string, number>;
  strong_or_moderate_readiness_count: number; trend_distribution: Record<string, number>;
  sector_distribution: Record<string, number>; unusual_pattern_count: number;
  low_confidence_count: number; improving_count: number; deteriorating_count: number;
  attention_signals: { msme_id: string; business_name: string | null; sector: string | null;
    finpulse_score: number; band: string; reasons: string[] }[];
  demo_available: boolean; guidance?: string;
}