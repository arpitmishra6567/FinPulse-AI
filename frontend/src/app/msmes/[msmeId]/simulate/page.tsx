"use client";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useApi } from "@/lib/useApi";
import type { HealthCard, SimResult } from "@/lib/api";
import { Card, ErrorState, PageSkeleton, PageTitle, fmtDim } from "@/components/ui";

type SimCurrent = {
  msme_id: string;
  current_values: Record<string, number>;
  allowed_fields: Record<string, [number, number]>;
};

const FIELD_META = [
  { key: "receivable_days", label: "Receivable Days", fallbackMin: 5, fallbackMax: 180, step: 1 },
  { key: "cash_reserve", label: "Cash Reserve (\u20b9)", fallbackMin: 0, fallbackMax: 5_000_000, step: 10_000 },
  { key: "customer_concentration", label: "Customer Concentration", fallbackMin: 0, fallbackMax: 1, step: 0.01 },
  { key: "debt_service_ratio", label: "Debt Service Ratio", fallbackMin: 0, fallbackMax: 1.5, step: 0.01 },
] as const;

export default function SimulatePage() {
  const { msmeId } = useParams<{ msmeId: string }>();
  const hc = useApi<HealthCard>(`/api/v1/msmes/${msmeId}/health-card`);
  const cur = useApi<SimCurrent>(`/api/v1/msmes/${msmeId}/simulate/current`);
  const [values, setValues] = useState<Record<string, number>>({});
  const [result, setResult] = useState<SimResult | null>(null);
  const [running, setRunning] = useState(false);
  const [simError, setSimError] = useState<string | null>(null);

  // Initialize sliders from the ACTUAL current backend values, per master prompt #4.
  useEffect(() => {
    if (!cur.data) return;
    const init: Record<string, number> = {};
    FIELD_META.forEach(f => {
      const v = cur.data!.current_values[f.key];
      if (typeof v === "number" && Number.isFinite(v)) init[f.key] = v;
    });
    setValues(init);
  }, [cur.data]);

  // Compute effective slider bounds: prefer backend `allowed_fields`, else fallback.
  const fields = FIELD_META.map(f => {
    const range = cur.data?.allowed_fields[f.key];
    return {
      ...f,
      min: range ? range[0] : f.fallbackMin,
      max: range ? range[1] : f.fallbackMax,
    };
  });

  async function run() {
    setRunning(true); setSimError(null);
    try {
      const body: Record<string, number> = {};
      // Only send fields the user actually moved (differ from current backend value).
      FIELD_META.forEach(f => {
        const v = values[f.key];
        const c = cur.data?.current_values[f.key];
        if (typeof v === "number" && v !== c) body[f.key] = v;
      });
      // API requires >=1 changed field; if user hasn't moved anything, nudge one.
      if (Object.keys(body).length === 0) {
        const c = cur.data?.current_values.receivable_days;
        if (typeof c === "number") body.receivable_days = c;
      }
      const r = await api<SimResult>(`/api/v1/msmes/${msmeId}/simulate`,
        { method: "POST", body: JSON.stringify(body) });
      setResult(r);
    } catch (e) { setSimError(e instanceof Error ? e.message : "Simulation failed"); }
    finally { setRunning(false); }
  }

  if (hc.loading || cur.loading) return <PageSkeleton />;
  if (hc.error) return <ErrorState message={hc.error} />;
  if (cur.error) return <ErrorState message={cur.error} />;
  if (!hc.data || !cur.data) return null;

  return (
    <div className="space-y-6">
      <PageTitle title="Improve My Score"
        subtitle={`${hc.data.identity.business_name ?? msmeId} · current FinPulse Score ${hc.data.finpulse_score} (${hc.data.band})`} />
      <Link href={`/msmes/${msmeId}`} className="text-sm text-brand hover:underline">← Back to Health Card</Link>

      <Card title="Scenario Controls">
        <p className="mb-3 text-xs text-slate-500">
          Sliders initialize from this MSME&apos;s current backend values.
        </p>
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          {fields.map(f => {
            const currentVal = cur.data!.current_values[f.key];
            return (
              <div key={f.key}>
                <div className="flex items-center justify-between text-sm">
                  <label className="font-medium">{f.label}</label>
                  <span className="text-slate-600">
                    {values[f.key] ?? "\u2014"}
                    {typeof currentVal === "number" && (
                      <span className="ml-2 text-xs text-slate-400">current: {currentVal}</span>
                    )}
                  </span>
                </div>
                <input type="range" min={f.min} max={f.max} step={f.step}
                  value={values[f.key] ?? f.min}
                  onChange={e => setValues(v => ({ ...v, [f.key]: Number(e.target.value) }))}
                  className="mt-2 w-full accent-brand" />
              </div>
            );
          })}
        </div>
        <button onClick={run} disabled={running}
          className="mt-5 rounded-lg bg-brand px-4 py-2 text-sm font-medium text-white hover:bg-brand-dark disabled:opacity-50">
          {running ? "Running scenario…" : "Run Scenario"}
        </button>
        {simError && <p className="mt-3 text-sm text-rose-700">{simError}</p>}
      </Card>

      {result && (
        <Card title="Scenario Result">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div><p className="text-xs text-slate-500">Current</p>
              <p className="text-3xl font-semibold">{result.current_score}</p></div>
            <div><p className="text-xs text-slate-500">Simulated</p>
              <p className="text-3xl font-semibold">{result.simulated_score}</p></div>
            <div><p className="text-xs text-slate-500">Change</p>
              <p className={`text-3xl font-semibold ${result.score_change >= 0 ? "text-emerald-600" : "text-rose-600"}`}>
                {result.score_change >= 0 ? "+" : ""}{result.score_change}</p></div>
          </div>
          <div className="mt-5 grid grid-cols-2 gap-2 md:grid-cols-3">
            {Object.entries(result.dimension_changes).map(([k, v]) => (
              <div key={k} className="rounded-lg border border-slate-200 p-3 text-sm">
                <p className="text-xs text-slate-500">{fmtDim(k)}</p>
                <p className={v >= 0 ? "text-emerald-700" : "text-rose-700"}>{v >= 0 ? "+" : ""}{v}</p>
              </div>
            ))}
          </div>
          <ul className="mt-4 list-disc pl-5 text-sm text-slate-600">
            {result.improvement_insights.map(i => <li key={i}>{i}</li>)}
          </ul>
          <p className="mt-3 text-xs font-medium text-amber-700">
            Simulation only — not a guarantee of credit approval.
          </p>
        </Card>
      )}
    </div>
  );
}