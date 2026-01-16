from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):
    mongodb_uri: str=os.getenv("MONGODB_URI")
    database_name: str = os.getenv("DATABASE_NAME")
    collection_name: str = os.getenv("COLLECTION_NAME")
    
    ollama_url: str = os.getenv("OLLAMA_URL")
    embedding_model: str = os.getenv("EMBEDDING_MODEL")
    llm_model: str = os.getenv("LLM_MODEL")
    
    chunk_size: int = 500
    chunk_overlap: int = 50
    
    top_k: int = 5
    min_score: float = 0.7


configs = Settings()