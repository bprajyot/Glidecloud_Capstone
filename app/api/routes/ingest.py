from fastapi import APIRouter, HTTPException
from app.models.schema import IngestRequest, IngestResponse
from app.services.paper import  fetch_paper
from app.services.embedding import generate_embedding
from app.utils.text_cleaning import clean_text, chunk_text
from app.core.config import configs
from app.core.logging import logger
from app.db.database import db

router = APIRouter()


@router.post("/paper", response_model=IngestResponse)
async def ingest_paper(request: IngestRequest):
    try:
        logger.info(f"Starting ingestion of {request.max_papers} papers...")
        
        papers = await  fetch_paper(request.max_papers)
        
        if not papers:
            raise HTTPException(status_code=404, detail="No papers found")
        
        collection = db.get_collection()
        total_chunks = 0
        
        for i, paper in enumerate(papers, 1):
            logger.info(f"Processing paper {i}/{len(papers)}: {paper.arxiv_id}")
            
            clean_abstract = clean_text(paper.abstract)
            
            chunks = chunk_text(
                clean_abstract,
                chunk_size=configs.chunk_size,
                overlap=configs.chunk_overlap
            )
            logger.info(f"Created {len(chunks)} chunks")
            
            for chunk_idx, chunk in enumerate(chunks):
                embedding = generate_embedding(chunk)
                
                doc = {
                    "arxiv_id": paper.arxiv_id,
                    "title": paper.title,
                    "authors": paper.authors,
                    "published": paper.published,
                    "categories": paper.categories,
                    "chunk_text": chunk,
                    "chunk_index": chunk_idx,
                    "embedding": embedding
                }
                
                await collection.insert_one(doc)
                total_chunks += 1
            
            logger.info(f"Stored {len(chunks)} chunks for {paper.arxiv_id}")
        
        message = f"Successfully ingested {len(papers)} papers with {total_chunks} chunks"
        logger.info(message)
        
        return IngestResponse(
            papers_processed=len(papers),
            chunks_created=total_chunks,
            message=message
        )
    
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))