from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.api.schemas import (
    ComponentInput,
    DataFlowInput,
    ThreatModelCreate,
    ThreatModelListItem,
    ThreatModelResponse,
    ThreatModelUpdate,
)
from app.db.models import ThreatModel, User
from app.db.session import get_db

router = APIRouter(prefix="/threat-models", tags=["threat-models"])


@router.post("/", response_model=ThreatModelResponse, status_code=status.HTTP_201_CREATED)
async def create_threat_model(
    body: ThreatModelCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    model = ThreatModel(
        name=body.name,
        description=body.description,
        created_by=user.id if user.id != 0 else None,
    )
    db.add(model)
    await db.commit()
    await db.refresh(model)
    return model


@router.get("/", response_model=list[ThreatModelListItem])
async def list_threat_models(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ThreatModel).order_by(ThreatModel.updated_at.desc())
    )
    return result.scalars().all()


@router.get("/{model_id}", response_model=ThreatModelResponse)
async def get_threat_model(
    model_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(ThreatModel).where(ThreatModel.id == model_id))
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Threat model not found")
    return model


@router.put("/{model_id}", response_model=ThreatModelResponse)
async def update_threat_model(
    model_id: int,
    body: ThreatModelUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(ThreatModel).where(ThreatModel.id == model_id))
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Threat model not found")
    if body.name is not None:
        model.name = body.name
    if body.description is not None:
        model.description = body.description
    if body.components is not None:
        model.components = [c.model_dump() for c in body.components]
    if body.data_flows is not None:
        model.data_flows = [f.model_dump() for f in body.data_flows]
    if body.trust_boundaries is not None:
        model.trust_boundaries = body.trust_boundaries
    if body.session_context is not None:
        model.session_context = body.session_context
    await db.commit()
    await db.refresh(model)
    return model


@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_threat_model(
    model_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(ThreatModel).where(ThreatModel.id == model_id))
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Threat model not found")
    await db.delete(model)
    await db.commit()
