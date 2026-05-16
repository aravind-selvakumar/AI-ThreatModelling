from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.api.schemas import RAGQueryRequest, RAGQueryResponse
from app.core.rag import query_rag
from app.db.models import User

router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/query", response_model=RAGQueryResponse)
async def rag_query(
    body: RAGQueryRequest,
    user: User = Depends(get_current_user),
):
    result = query_rag(query=body.query, session_context=body.session_context or "")
    return RAGQueryResponse(
        query=result["query"],
        answer=result["answer"],
        source_documents=result["source_documents"],
    )
