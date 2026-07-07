"use client";
import Link from "next/link";
import { useMemo, useState } from "react";
import { useApi } from "@/lib/useApi";
import type { Paginated } from "@/lib/api";
import { Badge, Card, EmptyState, ErrorState, PageSkeleton, PageTitle, fmtINR } from "@/components/ui";

const BANDS = ["Excellent", "Good", "Watch", "Vulnerable", "Critical"];

export default function Portfolio() {
  const [search, setSearch] = useState("");
  const [band, setBand] = useState("");
  const [sector, setSector] = useState("");
  const [page, setPage] = useState(1);

  const qs = useMemo(() => {
    const p = new URLSearchParams({ page: String(page), page_size: "15" });
    if (search) p.set("search", search);
    if (band) p.set("health_band", band);
    if (sector) p.set("sector", sector);
    return `/api/v1/msmes?${p.toString()}`;
  }, [search, band, sector, page]);

  const { data, error, loading } = useApi<Paginated>(qs);
  const sectors = useApi<Paginated>("/api/v1/msmes?page_size=100");
  const sectorOptions = useMemo(() =>
    Array.from(new Set((sectors.data?.items ?? []).map(i => i.sector).filter(Boolean))) as string[],
    [sectors.data]);

  if (error) return <ErrorState message={error} />;

  return (
    <div className="space-y-4">
      <PageTitle title="MSME Portfolio" subtitle="Search and filter the deterministic synthetic_demo portfolio." />
      <Card>
        <div className="flex flex-wrap gap-3">
          <input value={search} onChange={e => { setPage(1); setSearch(e.target.value); }}
            placeholder="Search business or MSME ID…"
            className="w-64 rounded-lg border border-slate-300 px-3 py-2 text-sm" />
          <select value={band} onChange={e => { setPage(1); setBand(e.target.value); }}
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm">
            <option value="">All bands</option>{BANDS.map(b => <option key={b}>{b}</option>)}
          </select>
          <select value={sector} onChange={e => { setPage(1); setSector(e.target.value); }}
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm">
            <option value="">All sectors</option>{sectorOptions.map(s => <option key={s}>{s}</option>)}
          </select>
        </div>
      </Card>

      {loading ? <PageSkeleton /> :
        !data || data.total === 0 ? (
          <EmptyState message={data?.guidance ?? "No MSMEs match the current filters."} />
        ) : (
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-200 text-left text-xs uppercase tracking-wide text-slate-500">
                  <th className="py-2 pr-4">Business</th><th className="py-2 pr-4">MSME ID</th>
                  <th className="py-2 pr-4">Sector</th><th className="py-2 pr-4">Score</th>
                  <th className="py-2 pr-4">Band</th><th className="py-2 pr-4">Trend</th>
                  <th className="py-2 pr-4">Confidence</th><th className="py-2 pr-4">Readiness</th>
                  <th className="py-2 pr-4">Pattern</th><th className="py-2">Revenue</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map(m => (
                  <tr key={m.msme_id} className="border-b border-slate-100 hover:bg-slate-50">
                    <td className="py-2 pr-4">
                      <Link href={`/msmes/${m.msme_id}`} className="font-medium text-brand hover:underline">
                        {m.business_name ?? m.msme_id}
                      </Link>
                    </td>
                    <td className="py-2 pr-4 text-slate-500">{m.msme_id}</td>
                    <td className="py-2 pr-4">{m.sector}</td>
                    <td className="py-2 pr-4 font-semibold">{m.finpulse_score}</td>
                    <td className="py-2 pr-4"><Badge label={m.band} /></td>
                    <td className="py-2 pr-4 text-xs">{m.trend_status.replace(/_/g, " ")}</td>
                    <td className="py-2 pr-4 text-xs">{m.confidence_score} · {m.confidence_status.split(" —")[0]}</td>
                    <td className="py-2 pr-4 text-xs">{m.credit_readiness}</td>
                    <td className="py-2 pr-4 text-xs">
                      {m.anomaly_status === "Unusual Financial Pattern"
                        ? <Badge label="Unusual Pattern" tone="bg-amber-100 text-amber-800 border-amber-200" />
                        : <span className="text-slate-400">Normal</span>}
                    </td>
                    <td className="py-2 text-xs">{fmtINR(m.latest_monthly_revenue)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-4 flex items-center justify-between text-sm">
            <p className="text-slate-500">{data.total} MSMEs · page {data.page} of {data.total_pages}</p>
            <div className="flex gap-2">
              <button disabled={page <= 1} onClick={() => setPage(p => p - 1)}
                className="rounded-lg border px-3 py-1.5 disabled:opacity-40">Previous</button>
              <button disabled={page >= data.total_pages} onClick={() => setPage(p => p + 1)}
                className="rounded-lg border px-3 py-1.5 disabled:opacity-40">Next</button>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}