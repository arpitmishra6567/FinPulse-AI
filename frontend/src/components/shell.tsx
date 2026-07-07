"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Activity, Building2, HeartPulse, LineChart, Search, Sparkles, ShieldCheck, Linkedin, Github, Mail } from "lucide-react";
import { ReactNode } from "react";

const NAV = [
  { href: "/dashboard", label: "Overview", icon: Activity },
  { href: "/msmes", label: "MSME Portfolio", icon: Building2 },
  { href: "/msmes?focus=health", label: "Financial Health", icon: HeartPulse, hint: "per MSME" },
  { href: "/msmes?focus=twin", label: "Temporal Twin", icon: LineChart, hint: "per MSME" },
  { href: "/msmes?focus=explain", label: "Explainability", icon: Search, hint: "per MSME" },
  { href: "/msmes?focus=simulate", label: "Improve My Score", icon: Sparkles, hint: "per MSME" },
  { href: "/transparency", label: "Model & Data Transparency", icon: ShieldCheck },
];

export default function Shell({ children }: { children: ReactNode }) {
  const path = usePathname();
  return <div className="flex min-h-screen bg-slate-50 text-slate-900">
    <aside className="hidden w-72 shrink-0 flex-col border-r border-slate-200 bg-white md:flex">
      <div className="border-b border-slate-200 bg-gradient-to-br from-slate-950 to-brand px-5 py-5 text-white"><p className="text-xl font-bold tracking-tight">FinPulse AI</p><p className="mt-1 text-xs text-blue-100">Explainable Financial Health Intelligence</p><span className="mt-3 inline-flex rounded-full border border-white/20 bg-white/10 px-2.5 py-1 text-[10px] font-medium">Financial Health Score</span></div>
      <nav className="flex-1 space-y-1 p-3">{NAV.map(({ href, label, icon: Icon, hint }) => { const base = href.split("?")[0]; const active = path === base && !href.includes("?"); return <Link key={label} href={href} className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition ${active ? "bg-brand text-white shadow-sm" : "text-slate-700 hover:bg-slate-100"}`}><Icon className="h-4 w-4" /><span className="flex-1">{label}</span>{hint && <span className={active ? "text-[10px] text-blue-100" : "text-[10px] text-slate-400"}>{hint}</span>}</Link>; })}</nav>
      <div className="border-t border-slate-200 p-4 text-[11px] leading-relaxed text-slate-500"><p className="font-semibold text-slate-700">Team FinPulse AI</p><p><b>Leader:</b> Arpit Mishra</p><p>Arpit Tiwari · Aman Pal · Ritesh Tiwari</p><div className="mt-3 flex gap-2"><a href="https://www.linkedin.com/in/arpit-mishra-7857y" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn" className="rounded-md border p-1.5 hover:bg-slate-100"><Linkedin className="h-3.5 w-3.5" /></a><a href="https://github.com/arpitmishra6567/FinPulse-AI" target="_blank" rel="noopener noreferrer" aria-label="GitHub" className="rounded-md border p-1.5 hover:bg-slate-100"><Github className="h-3.5 w-3.5" /></a><a href="mailto:arpitmishra6567@gmail.com" target="_blank" rel="noopener noreferrer" aria-label="Email" className="rounded-md border p-1.5 hover:bg-slate-100"><Mail className="h-3.5 w-3.5" /></a></div><p className="mt-3">IDBI Innovate 2026 Prototype · Decision support only. No endorsement implied.</p></div>
    </aside>
    <div className="flex min-w-0 flex-1 flex-col"><div className="border-b border-slate-200 bg-white px-4 py-2 text-xs text-slate-500 md:hidden">FinPulse AI — Financial Health Score</div><main className="mx-auto w-full max-w-7xl flex-1 p-4 md:p-8">{children}</main></div>
  </div>;
}
