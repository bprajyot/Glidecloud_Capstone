from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class Paper(BaseModel):
    arxiv_id: str
    title: str
    authors: List[str]
    published: datetime
    categories: List[str]
    abstract: str


class IngestRequest(BaseModel):
    max_papers: int = Field(default=50, description="How many papers to fetch")


class IngestResponse(BaseModel):
    papers_processed: int
    chunks_created: int
    message: str


class QueryRequest(BaseModel):
    case_description: str = Field(..., min_length=20)


class Reference(BaseModel):
    arxiv_id: str
    title: str
    score: float


class QueryResponse(BaseModel):
    answer: str
    references: List[Reference]