import ollama
from typing import List
from app.core.config import configs
from app.core.logging import logger


def generate_embedding(text: str) -> List[float]:
    try:
        client = ollama.Client(host=configs.ollama_url)
        response = client.embeddings(
            model=configs.embedding_model,
            prompt=text
        )
        return response["embedding"]
    
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        raise


async def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    embeddings = []
    
    for i, text in enumerate(texts):
        if (i + 1) % 10 == 0:
            logger.info(f"Generated {i + 1}/{len(texts)} embeddings")
        
        embedding = generate_embedding(text)
        embeddings.append(embedding)
    
    return embeddings