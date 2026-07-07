"use client";
import { useApi } from "@/lib/useApi";
import { Card, ErrorState, PageSkeleton, PageTitle } from "@/components/ui";

type ModelMeta = { model_status: string; model_name: string; metadata: any;
  model_application_status_for_demo: string; application_limits: string[] };
type ScoringMeta = { formula: string; fallbacks: Record<string, string>;
  dimension_weights: Record<string, number>; bands: { min_score: number; band: string }[];
  data_confidence_note: string };
type SourcesMeta = { provenance_definitions: Record<string, string>;
  limitations: string[]; architecture_principle: string };

export default function Transparency() {
  const model = useApi<ModelMeta>("/api/v1/metadata/model");
  const scoring = useApi<ScoringMeta>("/api/v1/metadata/scoring");
  const sources = useApi<SourcesMeta>("/api/v1/metadata/data-sources");
  if (model.loading || scoring.loading || sources.loading) return <PageSkeleton />;
  const err = model.error || scoring.error || sources.error;
  if (err) return <ErrorState message={err} />;

  return (
    <div className="space-y-6">
      <PageTitle title="Model & Data Transparency"
        subtitle="How FinPulse AI scores, what the model can and cannot do, and where every signal comes from." />

      <Card title="Trained Model">
        <p className="text-sm">
          Model: <b>{model.data!.model_name}</b> · status: <b>{model.data!.model_status}</b> ·
          demo applicability: <b>{model.data!.model_application_status_for_demo}</b>
        </p>
        {model.data!.metadata && (
          <dl className="mt-3 grid grid-cols-1 gap-1 text-xs text-slate-600 md:grid-cols-2">
            <div>Validation: {model.data!.metadata.validation_method}</div>
            <div>Positive risk class: {String(model.data!.metadata.positive_risk_class)} (financial distress)</div>
            <div>Training records: {model.data!.metadata.training_record_count}</div>
            <div>Dataset: {model.data!.metadata.dataset_name} ({model.data!.metadata.provenance})</div>
            <div>Excluded leakage features: {(model.data!.metadata.excluded_leakage_features ?? []).join(", ")}</div>
          </dl>
        )}
        <ul className="mt-3 list-disc pl-5 text-sm text-slate-600">
          {model.data!.application_limits.map(l => <li key={l}>{l}</li>)}
        </ul>
      </Card>

      <Card title="Scoring Methodology">
        <p className="rounded-lg bg-slate-50 p-3 font-mono text-xs">{scoring.data!.formula}</p>
        <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            <p className="text-xs font-semibold uppercase text-slate-500">Dimension weights</p>
            <ul className="mt-1 text-sm">
              {Object.entries(scoring.data!.dimension_weights).map(([k, v]) =>
                <li key={k} className="flex justify-between border-b border-slate-100 py-1">
                  <span>{k.replace(/_/g, " ")}</span><b>{(v * 100).toFixed(0)}%</b></li>)}
            </ul>
          </div>
          <div>
            <p className="text-xs font-semibold uppercase text-slate-500">Health bands</p>
            <ul className="mt-1 text-sm">
              {scoring.data!.bands.map(b =>
                <li key={b.band} className="flex justify-between border-b border-slate-100 py-1">
                  <span>{b.band}</span><span>≥ {b.min_score}</span></li>)}
            </ul>
          </div>
        </div>
        <p className="mt-3 text-xs text-slate-500">{scoring.data!.data_confidence_note}</p>
      </Card>

      <Card title="Data Provenance">
        <ul className="space-y-2 text-sm">
          {Object.entries(sources.data!.provenance_definitions).map(([k, v]) =>
            <li key={k}><b className="font-mono text-xs">{k}</b> — {v}</li>)}
        </ul>
        <p className="mt-3 text-xs font-medium text-brand">“{sources.data!.architecture_principle}”</p>
      </Card>

      <Card title="Honest Limitations">
        <ul className="list-disc pl-5 text-sm text-slate-600">
          {sources.data!.limitations.map(l => <li key={l}>{l}</li>)}
        </ul>
        <p className="mt-3 text-xs text-slate-500">
          IDBI Innovate 2026 Prototype. FinPulse AI is decision support — it never outputs
          “Loan Approved” and never claims fraud detection.
        </p>
      </Card>
    </div>
  );
}