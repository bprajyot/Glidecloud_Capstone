from fastapi import APIRouter, HTTPException
from app.models.schema import QueryRequest, QueryResponse, Reference
from app.services.retrieval import search_papers
from app.services.generation import generate_answer
from app.core.logging import logger
from app.db.database import db

router = APIRouter()


@router.post("/case", response_model=QueryResponse)
async def query_case(request: QueryRequest):
    try:
        logger.info(f"Received query: '{request.case_description[:100]}...'")
        
        collection = db.get_collection()
        
        retrieved_docs = await search_papers(request.case_description, collection)
        
        answer = generate_answer(request.case_description, retrieved_docs)
        
        references = []
        seen_ids = set()
        
        for doc in retrieved_docs:
            arxiv_id = doc["arxiv_id"]
            if arxiv_id not in seen_ids:
                references.append(Reference(
                    arxiv_id=arxiv_id,
                    title=doc["title"],
                    score=doc.get("score", 0.0)
                ))
                seen_ids.add(arxiv_id)
        
        logger.info(f"Query complete. Found {len(references)} unique papers")
        
        return QueryResponse(
            answer=answer,
            references=references
        )
    
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))