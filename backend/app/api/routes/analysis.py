from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.api.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    ComponentAnalysis,
    MitigationItem,
    ScoredThreatItem,
    ThreatItem,
)
from app.core.threat_engine import analyze_component, analyze_full_model
from app.db.models import Mitigation, Threat, ThreatModel, User
from app.db.session import get_db
from app.ingestion.vectorstore import similarity_search

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/run", response_model=AnalysisResponse)
async def run_analysis(
    body: AnalysisRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    results = analyze_full_model(
        components=[c.model_dump() for c in body.components],
        data_flows=[f.model_dump() for f in body.data_flows],
        trust_boundaries=body.trust_boundaries,
        session_context=body.session_context or "",
    )

    aggregated = []
    total_risk = 0.0
    threat_count = 0

    for r in results:
        comp = ComponentAnalysis(
            component=r["component"],
            threats=[
                ThreatItem(**t) for t in r.get("threats", [])
            ],
            scored_threats=[
                ScoredThreatItem(**st) for st in r.get("scored_threats", [])
            ],
            mitigations=[
                MitigationItem(**m) for m in r.get("mitigations", [])
            ],
        )
        for st in comp.scored_threats:
            total_risk += st.risk_score
            threat_count += 1
        aggregated.append(comp)

    avg_risk = round(total_risk / threat_count, 2) if threat_count > 0 else 0.0

    return AnalysisResponse(
        components=aggregated,
        total_threats=threat_count,
        average_risk_score=avg_risk,
    )


@router.post("/run-for-model/{model_id}", response_model=AnalysisResponse)
async def run_analysis_for_model(
    model_id: int,
    body: AnalysisRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(ThreatModel).where(ThreatModel.id == model_id))
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Threat model not found")

    components_dicts = [c.model_dump() for c in body.components] if body.components else model.components
    data_flows_dicts = [f.model_dump() for f in body.data_flows] if body.data_flows else model.data_flows
    trust_boundaries = body.trust_boundaries or model.trust_boundaries
    session_context = body.session_context or model.session_context or ""

    results = analyze_full_model(
        components=components_dicts,
        data_flows=data_flows_dicts,
        trust_boundaries=trust_boundaries,
        session_context=session_context,
    )

    aggregated = []
    total_risk = 0.0
    threat_count = 0

    for r in results:
        comp = ComponentAnalysis(
            component=r["component"],
            threats=[ThreatItem(**t) for t in r.get("threats", [])],
            scored_threats=[ScoredThreatItem(**st) for st in r.get("scored_threats", [])],
            mitigations=[MitigationItem(**m) for m in r.get("mitigations", [])],
        )
        for st in comp.scored_threats:
            total_risk += st.risk_score
            threat_count += 1

        for t in comp.scored_threats:
            db_threat = Threat(
                model_id=model_id,
                component=r["component"],
                stride_category=t.stride_category,
                description=t.description,
                dread_scores=t.dread_scores.model_dump(),
                risk_score=t.risk_score,
            )
            db.add(db_threat)
            await db.flush()
            for m in comp.mitigations:
                db_mit = Mitigation(
                    threat_id=db_threat.id,
                    description="\n".join(m.actions),
                    source_standard=m.source_standard or "",
                )
                db.add(db_mit)

        aggregated.append(comp)

    model.components = components
    model.data_flows = data_flows
    model.trust_boundaries = trust_boundaries
    model.session_context = session_context
    model.status = "review"
    await db.commit()

    avg_risk = round(total_risk / threat_count, 2) if threat_count > 0 else 0.0
    return AnalysisResponse(
        components=aggregated,
        total_threats=threat_count,
        average_risk_score=avg_risk,
    )
