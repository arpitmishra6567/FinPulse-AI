from fastapi import APIRouter, HTTPException, Query
from backend.app.schemas.api import SimulationRequest
from backend.app.services.orchestrator import FinPulseOrchestrator, DEMO_GUIDANCE

router = APIRouter(prefix="/api/v1")


def _orc() -> FinPulseOrchestrator:
    return FinPulseOrchestrator.get()


def _get_or_404(fn, msme_id: str):
    try:
        return fn(msme_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"MSME '{msme_id}' not found")


@router.get("/status")
def status():
    o = _orc()
    return {"model_status": o.inference.status, "model_name": o.inference.model_name,
            "model_application_status_for_demo": o.model_application_status(),
            "demo_portfolio_loaded": o.demo_available,
            "demo_guidance": None if o.demo_available else DEMO_GUIDANCE,
            "msme_count": len(o.records)}


@router.get("/msmes")
def list_msmes(search: str | None = None, sector: str | None = None,
               health_band: str | None = None, trend_status: str | None = None,
               credit_readiness: str | None = None, confidence_status: str | None = None,
               anomaly_status: str | None = None,
               sort_by: str = "finpulse_score",
               sort_order: str = Query("desc", pattern="^(asc|desc)$"),
               page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)):
    o = _orc()
    if not o.demo_available:
        return {"items": [], "total": 0, "page": 1, "page_size": page_size,
                "total_pages": 1, "demo_available": False, "guidance": DEMO_GUIDANCE}
    return o.list_msmes(search=search, sector=sector, health_band=health_band,
                        trend_status=trend_status, credit_readiness_f=credit_readiness,
                        confidence_status=confidence_status, anomaly_status=anomaly_status,
                        sort_by=sort_by, sort_order=sort_order,
                        page=page, page_size=page_size)


@router.get("/msmes/{msme_id}")
def msme_summary(msme_id: str):
    return _get_or_404(_orc().summary, msme_id)


@router.get("/msmes/{msme_id}/health-card")
def health_card(msme_id: str):
    return _get_or_404(_orc().health_card, msme_id)


@router.get("/msmes/{msme_id}/twin")
def twin(msme_id: str):
    return _get_or_404(_orc().twin, msme_id)


@router.get("/msmes/{msme_id}/explanation")
def explanation(msme_id: str):
    return _get_or_404(_orc().explanation, msme_id)


@router.post("/msmes/{msme_id}/simulate")
def simulate_endpoint(msme_id: str, body: SimulationRequest):
    o = _orc()
    if msme_id not in o.records:
        raise HTTPException(status_code=404, detail=f"MSME '{msme_id}' not found")
    try:
        return o.run_simulation(msme_id, body.changes())
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/msmes/{msme_id}/simulate/current")
def simulate_current(msme_id: str):
    """Read-only: current values + allowed ranges for the four simulator fields.
    Exposes the values already returned by POST /simulate; scoring is untouched.
    """
    from backend.app.services.counterfactual import ALLOWED
    o = _orc()
    if msme_id not in o.records:
        raise HTTPException(status_code=404, detail=f"MSME '{msme_id}' not found")
    fin = o.assessments[msme_id]["financials"]
    return {
        "msme_id": msme_id,
        "current_values": {k: getattr(fin, k) for k in ALLOWED},
        "allowed_fields": {k: list(v) for k, v in ALLOWED.items()},
    }


@router.get("/analytics/portfolio")
def analytics():
    o = _orc()
    if not o.demo_available:
        return {"total_msmes": 0, "demo_available": False, "guidance": DEMO_GUIDANCE}
    return o.portfolio_analytics()


@router.get("/metadata/model")
def metadata_model():
    return _orc().model_metadata()


@router.get("/metadata/scoring")
def metadata_scoring():
    return _orc().scoring_metadata()


@router.get("/metadata/data-sources")
def metadata_data_sources():
    return _orc().data_sources_metadata()