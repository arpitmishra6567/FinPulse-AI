"use client";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useApi } from "@/lib/useApi";
import type { Twin } from "@/lib/api";
import { Card, ErrorState, PageSkeleton, PageTitle, StatCard } from "@/components/ui";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceDot } from "recharts";

export default function TwinPage() {
  const { msmeId } = useParams<{ msmeId: string }>();
  const { data, error, loading } = useApi<Twin>(`/api/v1/msmes/${msmeId}/twin`);
  if (loading) return <PageSkeleton />;
  if (error) return <ErrorState message={error} />;
  if (!data) return null;

  const rows = data.score_history.map((s, i) => ({ month: `M${i + 1}`, score: s }));

  return (
    <div className="space-y-6">
      <PageTitle title="Temporal Financial Digital Twin"
        subtitle={`${data.msme_id} — monthly re-scoring via the real Phase 1 dimension + scoring engines.`} />
      <Link href={`/msmes/${msmeId}`} className="text-sm text-brand hover:underline">← Back to Health Card</Link>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-5">
        <StatCard label="1-Month Change" value={data.change_1m ?? "—"} />
        <StatCard label="3-Month Change" value={data.change_3m ?? "—"} />
        <StatCard label="6-Month Slope" value={`${data.trend_6m_slope}/mo`} />
        <StatCard label="Deterioration Velocity" value={data.deterioration_velocity} sub="worst monthly drop" />
        <StatCard label="Recovery Velocity" value={data.recovery_velocity} sub="best monthly gain" />
      </div>

      <Card title={`Score History — ${data.trend_status.replace(/_/g, " ")}`}>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={rows}>
            <XAxis dataKey="month" fontSize={12} />
            <YAxis domain={[0, 100]} fontSize={12} />
            <Tooltip />
            <Line type="monotone" dataKey="score" stroke="#0f4c81" strokeWidth={2} dot />
            {data.change_points.map(i => (
              <ReferenceDot key={i} x={`M${i + 2}`} y={data.score_history[i + 1]}
                r={6} fill="#e11d48" stroke="none" />
            ))}
          </LineChart>
        </ResponsiveContainer>
        <p className="mt-2 text-sm text-slate-600">{data.trend_summary}</p>
        {data.change_points.length > 0 &&
          <p className="mt-1 text-xs text-rose-700">
            Change points (≥10-pt monthly move) at month transitions: {data.change_points.map(i => `M${i + 1}→M${i + 2}`).join(", ")}
            {data.detected_start_period !== null && ` · detected start period: M${data.detected_start_period + 1}`}
          </p>}
        <p className="mt-2 text-[11px] text-slate-400">{data.note}</p>
      </Card>
    </div>
  );
}