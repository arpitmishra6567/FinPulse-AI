"use client";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useApi } from "@/lib/useApi";
import type { Explanation } from "@/lib/api";
import { Badge, Card, ErrorState, PageSkeleton, PageTitle, fmtDim } from "@/components/ui";

export default function ExplainPage() {
  const { msmeId } = useParams<{ msmeId: string }>();
  const { data, error, loading } = useApi<Explanation>(`/api/v1/msmes/${msmeId}/explanation`);
  if (loading) return <PageSkeleton />;
  if (error) return <ErrorState message={error} />;
  if (!data) return null;

  return (
    <div className="space-y-6">
      <PageTitle title="Explainability" subtitle={`${data.msme_id} · mode: ${data.explanation_mode}`} />
      <Link href={`/msmes/${msmeId}`} className="text-sm text-brand hover:underline">← Back to Health Card</Link>

      <Card title="ML Factors (SHAP)">
        {data.ml_factors.length > 0 ? (
          <ul className="space-y-2 text-sm">
            {data.ml_factors.map(f => (
              <li key={f.feature} className="flex items-center gap-3">
                <span className="w-64 truncate">{f.feature}</span>
                <div className="h-2 flex-1 rounded bg-slate-100">
                  <div className={`h-2 rounded ${f.shap_value >= 0 ? "bg-rose-400" : "bg-emerald-400"}`}
                       style={{ width: `${Math.min(Math.abs(f.shap_value) * 200, 100)}%` }} />
                </div>
                <span className="w-20 text-right text-xs">{f.shap_value}</span>
              </li>
            ))}
          </ul>
        ) : (
          <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
            {data.ml_factors_note}
            <p className="mt-1 text-xs">model_application_status: {data.model_application_status}</p>
          </div>
        )}
      </Card>

      <Card title="Financial Health Signals (Transparent Rules)">
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {data.financial_health_signals.map(s => (
            <div key={s.dimension} className="rounded-lg border border-slate-200 p-4">
              <div className="flex items-center justify-between">
                <p className="font-medium">{fmtDim(s.dimension)}</p>
                <Badge label={`${s.score}`} tone="bg-slate-100 text-slate-700 border-slate-200" />
              </div>
              <p className="text-xs text-slate-500">{s.status}</p>
              {s.positive.map(p => <p key={p} className="mt-1 text-xs text-emerald-700">＋ {p}</p>)}
              {s.risks.map(r => <p key={r} className="mt-1 text-xs text-rose-700">－ {r}</p>)}
              {s.positive.length + s.risks.length === 0 &&
                <p className="mt-1 text-xs text-slate-400">No dominant signals.</p>}
            </div>
          ))}
        </div>
      </Card>

      <Card title="Responsible AI">
        <p className="text-sm text-slate-600">{data.responsible_ai_note}</p>
      </Card>
    </div>
  );
}