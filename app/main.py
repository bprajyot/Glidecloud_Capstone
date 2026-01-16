from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.database import db
from app.api.routes import ingest, query
from app.core.logging import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Medical RAG System...")
    await db.connect()
    logger.info("System ready!")
    
    yield
    
    logger.info("Shutting down...")
    await db.close()
    logger.info("Goodbye!")


app = FastAPI(
    title="Medical RAG System",
    description="Research support tool for medical literature (arXiv q-bio papers)",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(ingest.router, prefix="/ingest", tags=["Ingestion"])
app.include_router(query.router, prefix="/query", tags=["Query"])


@app.get("/")
async def root():
    return {
        "status": "healthy",
        "message": "Medical RAG System is running!",
        "disclaimer": "This is a research tool, not for clinical decisions"
    }


@app.get("/health")
async def health():
    return {"status": "ok"}