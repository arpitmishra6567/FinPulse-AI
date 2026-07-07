"use client";
import Link from "next/link";
import { useApi } from "@/lib/useApi";
import type { Analytics } from "@/lib/api";
import { Badge, Card, EmptyState, ErrorState, PageSkeleton, StatCard } from "@/components/ui";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";
import { Activity, ArrowRight, Github, Linkedin, Mail, ShieldCheck, Sparkles } from "lucide-react";

const BAND_ORDER = ["Excellent", "Good", "Watch", "Vulnerable", "Critical"];
const BAND_FILL: Record<string, string> = { Excellent: "#059669", Good: "#0284c7", Watch: "#d97706", Vulnerable: "#ea580c", Critical: "#e11d48" };
const READY_FILL = ["#0f4c81", "#0284c7", "#d97706", "#e11d48"];
function toRows(d: Record<string, number>, order?: string[]) { const keys = order ? order.filter(k => k in d) : Object.keys(d); return keys.map(name => ({ name, value: d[name] })); }

export default function Dashboard() {
  const { data, error, loading } = useApi<Analytics>("/api/v1/analytics/portfolio");
  if (loading) return <PageSkeleton />;
  if (error) return <ErrorState message={error} />;
  if (!data || !data.demo_available) return <EmptyState message={data?.guidance ?? "Demo portfolio not generated. Run: python backend/scripts/generate_demo.py"} />;

  return <div className="space-y-6">
    <section className="overflow-hidden rounded-2xl bg-gradient-to-br from-slate-950 via-brand-dark to-brand p-6 text-white shadow-lg md:p-8">
      <div className="grid gap-6 lg:grid-cols-[1fr_auto] lg:items-center"><div>
        <div className="mb-3 flex flex-wrap gap-2"><span className="rounded-full border border-white/20 bg-white/10 px-3 py-1 text-xs">Team FinPulse AI</span><span className="rounded-full border border-emerald-300/30 bg-emerald-400/10 px-3 py-1 text-xs text-emerald-100">Explainable · Responsible · Data-driven</span></div>
        <h1 className="text-3xl font-bold tracking-tight md:text-4xl">Financial Health Score</h1>
        <p className="mt-3 max-w-2xl text-sm leading-relaxed text-blue-100 md:text-base">An explainable financial-health intelligence prototype that turns multi-dimensional MSME signals into transparent scores, temporal trends, review signals, and actionable what-if scenarios.</p>
        <div className="mt-5 flex flex-wrap gap-3"><Link href="/msmes" className="inline-flex items-center gap-2 rounded-lg bg-white px-4 py-2 text-sm font-semibold text-brand shadow-sm hover:bg-blue-50">Explore MSMEs <ArrowRight className="h-4 w-4" /></Link><Link href="/transparency" className="inline-flex items-center gap-2 rounded-lg border border-white/25 bg-white/10 px-4 py-2 text-sm font-medium hover:bg-white/15"><ShieldCheck className="h-4 w-4" /> Model Transparency</Link></div>
      </div><div className="hidden rounded-2xl border border-white/15 bg-white/10 p-5 backdrop-blur lg:block"><Sparkles className="h-8 w-8 text-blue-200" /><p className="mt-4 text-xs uppercase tracking-widest text-blue-200">Problem Statement</p><p className="mt-1 text-xl font-semibold">Financial Health Score</p><p className="mt-3 max-w-52 text-xs text-blue-100">Decision support for understanding MSME financial health — not automated loan approval.</p></div></div>
    </section>

    <div className="grid grid-cols-2 gap-4 lg:grid-cols-5"><StatCard label="Total MSMEs" value={data.total_msmes} /><StatCard label="Avg FinPulse Score" value={data.average_finpulse_score} sub="0–100 scale" /><StatCard label="Strong / Moderate Readiness" value={data.strong_or_moderate_readiness_count} sub="Indicative only" /><StatCard label="Unusual Patterns" value={data.unusual_pattern_count} sub="Review signals" /><StatCard label="Low Data Confidence" value={data.low_confidence_count} sub="Human review recommended" /></div>

    <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
      <Card title="Health Band Distribution"><ResponsiveContainer width="100%" height={240}><BarChart data={toRows(data.band_distribution, BAND_ORDER)}><XAxis dataKey="name" fontSize={12} /><YAxis allowDecimals={false} fontSize={12} /><Tooltip /><Bar dataKey="value" radius={[6,6,0,0]}>{toRows(data.band_distribution, BAND_ORDER).map(r => <Cell key={r.name} fill={BAND_FILL[r.name]} />)}</Bar></BarChart></ResponsiveContainer></Card>
      <Card title="Credit Readiness (Indicative)"><ResponsiveContainer width="100%" height={240}><PieChart><Pie data={toRows(data.credit_readiness_distribution)} dataKey="value" nameKey="name" innerRadius={55} outerRadius={90} paddingAngle={2} label>{toRows(data.credit_readiness_distribution).map((_, i) => <Cell key={i} fill={READY_FILL[i % READY_FILL.length]} />)}</Pie><Tooltip /></PieChart></ResponsiveContainer></Card>
      <Card title="Portfolio Trend Status"><ResponsiveContainer width="100%" height={240}><BarChart data={toRows(data.trend_distribution)} layout="vertical"><XAxis type="number" allowDecimals={false} fontSize={12} /><YAxis type="category" dataKey="name" width={160} fontSize={12} /><Tooltip /><Bar dataKey="value" fill="#0f4c81" radius={[0,6,6,0]} /></BarChart></ResponsiveContainer></Card>
      <Card title="Sector Distribution"><ResponsiveContainer width="100%" height={240}><BarChart data={toRows(data.sector_distribution)} layout="vertical"><XAxis type="number" allowDecimals={false} fontSize={12} /><YAxis type="category" dataKey="name" width={160} fontSize={12} /><Tooltip /><Bar dataKey="value" fill="#0284c7" radius={[0,6,6,0]} /></BarChart></ResponsiveContainer></Card>
    </div>

    <Card title="Portfolio Signals Requiring Attention">{data.attention_signals.length === 0 ? <p className="text-sm text-slate-600">No priority signals detected.</p> : <ul className="divide-y divide-slate-100">{data.attention_signals.map(s => <li key={s.msme_id} className="flex flex-wrap items-center gap-3 py-3"><Link href={`/msmes/${s.msme_id}`} className="font-medium text-brand hover:underline">{s.business_name ?? s.msme_id}</Link><Badge label={s.band} /><span className="text-sm text-slate-500">Score {s.finpulse_score}</span><span className="flex-1 text-xs text-slate-600">{s.reasons.join(" · ")}</span></li>)}</ul>}</Card>

    <section className="grid gap-4 lg:grid-cols-[1.4fr_1fr]">
      <Card title="Team FinPulse AI"><div className="grid gap-3 sm:grid-cols-2"><div className="rounded-xl border border-blue-100 bg-blue-50 p-4"><p className="text-xs font-semibold uppercase tracking-wide text-brand">Team Leader</p><p className="mt-1 text-lg font-semibold">Arpit Mishra</p></div><div className="rounded-xl border border-slate-200 p-4"><p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Team Members</p><p className="mt-1 font-medium">Arpit Tiwari · Aman Pal · Ritesh Tiwari</p></div></div></Card>
      <Card title="Contact Us"><p className="mb-3 text-sm text-slate-600">Connect with the team or explore the project repository.</p><div className="flex flex-wrap gap-2"><a href="https://www.linkedin.com/in/arpit-mishra-7857y" target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-sm hover:bg-slate-50"><Linkedin className="h-4 w-4" /> LinkedIn</a><a href="https://github.com/arpitmishra6567/FinPulse-AI" target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-sm hover:bg-slate-50"><Github className="h-4 w-4" /> GitHub</a><a href="mailto:arpitmishra6567@gmail.com" target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-sm hover:bg-slate-50"><Mail className="h-4 w-4" /> Email</a></div></Card>
    </section>
    <div className="flex items-center justify-center gap-2 pb-2 text-xs text-slate-400"><Activity className="h-3.5 w-3.5" /> FinPulse AI · Financial Health Score · IDBI Innovate 2026 Prototype</div>
  </div>;
}
