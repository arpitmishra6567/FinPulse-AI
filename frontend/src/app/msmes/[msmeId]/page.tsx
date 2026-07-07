"use client";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useApi } from "@/lib/useApi";
import type { HealthCard } from "@/lib/api";
import { Badge, Card, ErrorState, PageSkeleton, PageTitle, fmtDim } from "@/components/ui";

const STATUS_TONE: Record<string, string> = {
  Healthy: "bg-emerald-100 text-emerald-800 border-emerald-200",
  Adequate: "bg-sky-100 text-sky-800 border-sky-200",
  Stressed: "bg-amber-100 text-amber-800 border-amber-200",
  Weak: "bg-rose-100 text-rose-800 border-rose-200",
};

export default function HealthCardPage() {
  const { msmeId } = useParams<{ msmeId: string }>();
  const { data, error, loading } = useApi<HealthCard>(`/api/v1/msmes/${msmeId}/health-card`);
  if (loading) return <PageSkeleton />;
  if (error) return <ErrorState message={error} />;
  if (!data) return null;

  const dims = Object.entries(data.dimensions);
  const why = [
    ...dims.flatMap(([k, d]) => d.risk_signals.map(r => ({ kind: "risk", dim: k, text: r }))),
    ...dims.flatMap(([k, d]) => d.positive_evidence.map(p => ({ kind: "pos", dim: k, text: p }))),
  ].slice(0, 6);

  return (
    <div className="space-y-6">
      <PageTitle title={data.identity.business_name ?? data.identity.msme_id}
        subtitle={`${data.identity.msme_id} · ${data.identity.sector ?? "—"} · ${data.identity.business_age_years ?? "—"} yrs · provenance: ${data.identity.provenance}`} />
      <nav className="flex flex-wrap gap-2 text-sm">
        {[["twin", "Temporal Twin"], ["explain", "Explainability"], ["simulate", "Improve My Score"]].map(([p, l]) =>
          <Link key={p} href={`/msmes/${msmeId}/${p}`}
            className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 hover:bg-slate-100">{l}</Link>)}
      </nav>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-4">
        <Card className="lg:col-span-1">
          <p className="text-xs font-medium uppercase tracking-wide text-slate-500">FinPulse Score</p>
          <p className="mt-2 text-5xl font-semibold text-slate-900">{data.finpulse_score}</p>
          <div className="mt-2"><Badge label={data.band} /></div>
          <div className="mt-4 space-y-1 text-xs text-slate-600">
            <p>Dimension composite (65%): <b>{data.components.dimension_composite}</b></p>
            <p>ML component (25%): <b>{data.components.ml_component}</b></p>
            <p>Anomaly component (10%): <b>{data.components.anomaly_component}</b></p>
          </div>
        </Card>
        <Card title="Data Confidence" className="lg:col-span-1">
          <p className="text-3xl font-semibold">{data.confidence.confidence_score}</p>
          <p className="mt-1 text-sm">{data.confidence.confidence_status}</p>
          <p className="mt-2 text-xs text-slate-500">{data.confidence.recommendation}</p>
          {data.confidence.missing_critical_evidence.length > 0 &&
            <p className="mt-2 text-xs text-amber-700">
              Missing critical evidence: {data.confidence.missing_critical_evidence.join(", ")}
            </p>}
        </Card>
        <Card title="Credit Readiness (Indicative)" className="lg:col-span-1">
          <p className="text-xl font-semibold">{data.credit_readiness.credit_readiness}</p>
          <p className="mt-1 text-sm text-slate-600">{data.credit_readiness.rationale}</p>
          <p className="mt-2 text-xs text-slate-500">{data.credit_readiness.disclaimer}</p>
        </Card>
        <Card title="Trend & Pattern" className="lg:col-span-1">
          <p className="text-sm">Trend: <b>{data.trend.trend_status.replace(/_/g, " ")}</b></p>
          <p className="text-xs text-slate-500">1m {data.trend.change_1m ?? "—"} · 3m {data.trend.change_3m ?? "—"} · 6m slope {data.trend.trend_6m_slope}/mo</p>
          <p className="mt-3 text-sm">{data.anomaly.anomaly_status}</p>
          {data.anomaly.detected_signals.length > 0 &&
            <ul className="mt-1 list-disc pl-4 text-xs text-amber-700">
              {data.anomaly.detected_signals.map(s => <li key={s}>{s}</li>)}
            </ul>}
          <p className="mt-2 text-[11px] text-slate-400">{data.anomaly.note}</p>
        </Card>
      </div>

      <Card title="Six Financial Health Dimensions">
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {dims.map(([key, d]) => (
            <div key={key} className="rounded-lg border border-slate-200 p-4">
              <div className="flex items-center justify-between">
                <p className="font-medium">{fmtDim(key)}</p>
                <Badge label={d.status} tone={STATUS_TONE[d.status]} />
              </div>
              <div className="mt-2 h-2 rounded-full bg-slate-100">
                <div className="h-2 rounded-full bg-brand" style={{ width: `${d.score}%` }} />
              </div>
              <p className="mt-1 text-xs text-slate-500">
                Score {d.score} · weight {(data.dimension_weights[key] * 100).toFixed(0)}%
              </p>
              {d.positive_evidence.map(p =>
                <p key={p} className="mt-1 text-xs text-emerald-700">＋ {p}</p>)}
              {d.risk_signals.map(r =>
                <p key={r} className="mt-1 text-xs text-rose-700">－ {r}</p>)}
            </div>
          ))}
        </div>
      </Card>

      <Card title="Why this score?">
        {why.length === 0 ? <p className="text-sm text-slate-600">No dominant signals — broadly neutral evidence.</p> :
          <ul className="space-y-1 text-sm">
            {why.map((w, i) =>
              <li key={i} className={w.kind === "risk" ? "text-rose-700" : "text-emerald-700"}>
                {w.kind === "risk" ? "▼" : "▲"} <span className="text-slate-500">[{fmtDim(w.dim)}]</span> {w.text}
              </li>)}
          </ul>}
      </Card>

      <Card title="Model Applicability">
        <p className="text-sm">
          Status: <b>{data.model.model_application_status}</b> · trained model: {data.model.model_name} ({data.model.model_status})
        </p>
        {data.model.risk_probability === null &&
          <p className="mt-1 text-xs text-amber-700">{data.model.note}</p>}
        <ul className="mt-3 list-disc pl-5 text-xs text-slate-500">
          {data.disclaimers.map(d => <li key={d}>{d}</li>)}
        </ul>
      </Card>
    </div>
  );
}