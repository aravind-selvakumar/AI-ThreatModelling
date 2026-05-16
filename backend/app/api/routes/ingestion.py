import os
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_admin
from app.api.schemas import DocumentResponse, IngestionStatus
from app.db.models import Standard, User
from app.db.session import get_db
from app.ingestion.chunker import split_documents
from app.ingestion.loader import load_bytes
from app.ingestion.vectorstore import (
    add_documents,
    clear_collection,
    get_collection_stats,
)

router = APIRouter(prefix="/ingestion", tags=["ingestion"])

ALLOWED_EXTENSIONS = {".pdf", ".md", ".txt"}


@router.post("/upload", response_model=IngestionStatus)
async def upload_document(
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    ext = Path(file.filename or "file.txt").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file")

    docs = load_bytes(content, file.filename)
    chunks = split_documents(docs)

    record = Standard(title=file.filename, content=content.decode("utf-8", errors="replace"), doc_type=ext.lstrip("."))
    db.add(record)
    await db.commit()
    await db.refresh(record)

    ids = add_documents(chunks)

    return IngestionStatus(
        document_id=record.id,
        filename=file.filename,
        chunk_count=len(chunks),
        status="ingested",
    )


@router.get("/documents", response_model=list[DocumentResponse])
async def list_documents(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    result = await db.execute(select(Standard).order_by(Standard.created_at.desc()))
    return result.scalars().all()


@router.delete("/documents/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    result = await db.execute(select(Standard).where(Standard.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    await db.delete(doc)
    await db.commit()


@router.post("/reindex", response_model=IngestionStatus)
async def reindex_all(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    result = await db.execute(select(Standard))
    standards = result.scalars().all()

    clear_collection()

    total_chunks = 0
    for std in standards:
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{std.doc_type}") as tmp:
            tmp.write(std.content.encode("utf-8"))
            tmp_path = tmp.name
        try:
            docs = load_bytes(std.content.encode("utf-8"), std.title or f"doc_{std.id}.{std.doc_type}")
            chunks = split_documents(docs)
            add_documents(chunks)
            total_chunks += len(chunks)
        finally:
            os.unlink(tmp_path)

    return IngestionStatus(
        document_id=0,
        filename="__all__",
        chunk_count=total_chunks,
        status="reindexed",
    )


@router.get("/stats")
async def stats(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    from sqlalchemy import func
    count_result = await db.execute(select(func.count(Standard.id)))
    doc_count = count_result.scalar()

    try:
        vs_stats = get_collection_stats()
        chunk_count = vs_stats.get("chunk_count", 0)
    except Exception:
        chunk_count = 0

    return {"documents": doc_count, "chunks": chunk_count}
