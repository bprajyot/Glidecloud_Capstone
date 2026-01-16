from typing import List, Dict, Any
from app.core.config import configs
from app.core.logging import logger
from app.services.embedding import generate_embedding


async def search_papers(query: str, collection, top_k: int = None) -> List[Dict[str, Any]]:
    if top_k is None:
        top_k = configs.top_k
    
    logger.info(f"Searching for: '{query[:50]}...'")
    
    query_embedding = generate_embedding(query)
    logger.info(f"Generated query embedding (dim={len(query_embedding)})")
    
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",  
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": top_k * 10,  
                "limit": top_k
            }
        },
        {
            "$project": {
                "arxiv_id": 1,
                "title": 1,
                "authors": 1,
                "chunk_text": 1,
                "chunk_index": 1,
                "score": {"$meta": "vectorSearchScore"}
            }
        }
    ]
    
    try:
        results = []
        async for doc in collection.aggregate(pipeline):
            if doc.get("score", 0) >= configs.min_score:
                results.append(doc)
        
        logger.info(f"Found {len(results)} relevant chunks")
        return results
    
    except Exception as e:
        logger.error(f"Vector search failed: {e}")
        raise