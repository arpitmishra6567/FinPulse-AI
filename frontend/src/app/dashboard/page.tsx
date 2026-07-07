"use client";
import Link from "next/link";
import { useApi } from "@/lib/useApi";
import type { Analytics } from "@/lib/api";
import { Badge, Card, EmptyState, ErrorState, PageSkeleton, PageTitle, StatCard } from "@/components/ui";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";

const BAND_ORDER = ["Excellent", "Good", "Watch", "Vulnerable", "Critical"];
const BAND_FILL: Record<string, string> = {
  Excellent: "#059669", Good: "#0284c7", Watch: "#d97706", Vulnerable: "#ea580c", Critical: "#e11d48",
};
const READY_FILL = ["#0f4c81", "#0284c7", "#d97706", "#e11d48"];

function toRows(d: Record<string, number>, order?: string[]) {
  const keys = order ? order.filter(k => k in d) : Object.keys(d);
  return keys.map(name => ({ name, value: d[name] }));
}

export default function Dashboard() {
  const { data, error, loading } = useApi<Analytics>("/api/v1/analytics/portfolio");
  if (loading) return <PageSkeleton />;
  if (error) return <ErrorState message={error} />;
  if (!data || !data.demo_available)
    return <EmptyState message={data?.guidance ?? "Demo portfolio not generated. Run: python backend/scripts/generate_demo.py"} />;

  return (
    <div className="space-y-6">
      <PageTitle title="Portfolio Overview"
        subtitle="Continuously updated, explainable financial-health identity across the MSME portfolio." />
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-5">
        <StatCard label="Total MSMEs" value={data.total_msmes} />
        <StatCard label="Avg FinPulse Score" value={data.average_finpulse_score} sub="0–100 scale" />
        <StatCard label="Strong / Moderate Readiness" value={data.strong_or_moderate_readiness_count} sub="Indicative only" />
        <StatCard label="Unusual Patterns" value={data.unusual_pattern_count} sub="Review signals" />
        <StatCard label="Low Data Confidence" value={data.low_confidence_count} sub="Human review recommended" />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card title="Health Band Distribution">
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={toRows(data.band_distribution, BAND_ORDER)}>
              <XAxis dataKey="name" fontSize={12} /><YAxis allowDecimals={false} fontSize={12} /><Tooltip />
              <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                {toRows(data.band_distribution, BAND_ORDER).map(r =>
                  <Cell key={r.name} fill={BAND_FILL[r.name]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Card>
        <Card title="Credit Readiness (Indicative)">
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie data={toRows(data.credit_readiness_distribution)} dataKey="value" nameKey="name"
                   innerRadius={55} outerRadius={90} paddingAngle={2} label>
                {toRows(data.credit_readiness_distribution).map((_, i) =>
                  <Cell key={i} fill={READY_FILL[i % READY_FILL.length]} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </Card>
        <Card title="Portfolio Trend Status">
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={toRows(data.trend_distribution)} layout="vertical">
              <XAxis type="number" allowDecimals={false} fontSize={12} />
              <YAxis type="category" dataKey="name" width={160} fontSize={12} /><Tooltip />
              <Bar dataKey="value" fill="#0f4c81" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>
        <Card title="Sector Distribution">
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={toRows(data.sector_distribution)} layout="vertical">
              <XAxis type="number" allowDecimals={false} fontSize={12} />
              <YAxis type="category" dataKey="name" width={160} fontSize={12} /><Tooltip />
              <Bar dataKey="value" fill="#0284c7" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      <Card title="Portfolio Signals Requiring Attention">
        {data.attention_signals.length === 0
          ? <p className="text-sm text-slate-600">No priority signals detected.</p>
          : <ul className="divide-y divide-slate-100">
              {data.attention_signals.map(s => (
                <li key={s.msme_id} className="flex flex-wrap items-center gap-3 py-3">
                  <Link href={`/msmes/${s.msme_id}`} className="font-medium text-brand hover:underline">
                    {s.business_name ?? s.msme_id}
                  </Link>
                  <Badge label={s.band} />
                  <span className="text-sm text-slate-500">Score {s.finpulse_score}</span>
                  <span className="flex-1 text-xs text-slate-600">{s.reasons.join(" · ")}</span>
                </li>
              ))}
            </ul>}
      </Card>
    </div>
  );
}