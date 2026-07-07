"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Activity, Building2, HeartPulse, LineChart, Search, Sparkles, ShieldCheck } from "lucide-react";
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
  return (
    <div className="flex min-h-screen bg-slate-50 text-slate-900">
      <aside className="hidden w-64 shrink-0 flex-col border-r border-slate-200 bg-white md:flex">
        <div className="border-b border-slate-200 px-5 py-4">
          <p className="text-lg font-semibold text-brand">FinPulse AI</p>
          <p className="text-xs text-slate-500">Explainable Financial Health Intelligence</p>
        </div>
        <nav className="flex-1 space-y-1 p-3">
          {NAV.map(({ href, label, icon: Icon, hint }) => {
            const active = path === href.split("?")[0] && !href.includes("?focus");
            return (
              <Link key={label} href={href}
                className={`flex items-center gap-3 rounded-lg px-3 py-2 text-sm ${
                  active ? "bg-brand text-white" : "text-slate-700 hover:bg-slate-100"}`}>
                <Icon className="h-4 w-4" />
                <span className="flex-1">{label}</span>
                {hint && <span className="text-[10px] text-slate-400">{hint}</span>}
              </Link>
            );
          })}
        </nav>
        <div className="border-t border-slate-200 p-4 text-[11px] leading-relaxed text-slate-500">
          <p className="font-medium text-slate-600">IDBI Innovate 2026 Prototype</p>
          <p>Decision support only. Not an IDBI product; no endorsement implied.</p>
        </div>
      </aside>
      <div className="flex min-w-0 flex-1 flex-col">
        <div className="border-b border-slate-200 bg-white px-4 py-2 text-xs text-slate-500 md:hidden">
          FinPulse AI — IDBI Innovate 2026 Prototype
        </div>
        <main className="mx-auto w-full max-w-7xl flex-1 p-4 md:p-8">{children}</main>
      </div>
    </div>
  );
}