import pytest
from datetime import datetime
from pydantic import ValidationError
from app.models.schema import (
    Paper, IngestRequest, QueryRequest, 
    Reference, QueryResponse
)


class TestPaperSchema:
    
    def test_creates_valid_paper(self):
        paper = Paper(
            arxiv_id="2301.12345",
            title="Autophagy in Neurodegenerative Diseases",
            authors=["John Doe", "Jane Smith", "Bob Johnson"],
            published=datetime(2023, 1, 15, 10, 30),
            categories=["q-bio.CB", "q-bio.NC"],
            abstract="This paper investigates the role of autophagy..."
        )
        
        assert paper.arxiv_id == "2301.12345"
        assert len(paper.authors) == 3
        assert len(paper.categories) == 2
        assert "autophagy" in paper.abstract.lower()
    
    def test_rejects_missing_required_fields(self):
        with pytest.raises(ValidationError) as exc_info:
            Paper(
                arxiv_id="2301.12345",
                title="Test Paper"
            )
        
        error = exc_info.value
        assert "authors" in str(error)
        assert "published" in str(error)
    
    def test_handles_single_author(self):
        paper = Paper(
            arxiv_id="2301.12345",
            title="Solo Research",
            authors=["Single Author"],
            published=datetime.now(),
            categories=["q-bio.CB"],
            abstract="Research abstract"
        )
        assert len(paper.authors) == 1


class TestIngestRequest:
    
    def test_uses_default_max_papers(self):
        request = IngestRequest()
        assert request.max_papers == 50
    
    def test_accepts_custom_max_papers(self):
        request = IngestRequest(max_papers=100)
        assert request.max_papers == 100
    
    def test_accepts_small_batch(self):
        request = IngestRequest(max_papers=10)
        assert request.max_papers == 10


class TestQueryRequest:
    
    def test_accepts_valid_query(self):
        request = QueryRequest(
            case_description="What are the mechanisms of autophagy in cancer cells?"
        )
        assert len(request.case_description) > 20
        assert "autophagy" in request.case_description
    
    def test_rejects_short_query(self):
        with pytest.raises(ValidationError):
            QueryRequest(case_description="Too short")
    
    def test_accepts_minimum_length_query(self):
        request = QueryRequest(case_description="a" * 20)
        assert len(request.case_description) == 20
    
    def test_rejects_empty_query(self):
        with pytest.raises(ValidationError):
            QueryRequest(case_description="")
    
    def test_accepts_long_query(self):
        long_query = (
            "I am researching the molecular mechanisms of autophagy "
            "in the context of neurodegenerative diseases, specifically "
            "how autophagy dysfunction contributes to protein aggregation "
            "in Alzheimer's and Parkinson's disease."
        )
        request = QueryRequest(case_description=long_query)
        assert len(request.case_description) > 100


class TestReferenceSchema:
    
    def test_creates_valid_reference(self):
        ref = Reference(
            arxiv_id="2301.12345",
            title="Autophagy Mechanisms",
            score=0.89
        )
        assert ref.arxiv_id == "2301.12345"
        assert 0 <= ref.score <= 1
    
    def test_handles_perfect_score(self):
        ref = Reference(
            arxiv_id="123",
            title="Test",
            score=1.0
        )
        assert ref.score == 1.0
    
    def test_handles_low_score(self):
        ref = Reference(
            arxiv_id="123",
            title="Test",
            score=0.01
        )
        assert ref.score == 0.01


class TestQueryResponse:
    
    def test_creates_valid_response(self):
        response = QueryResponse(
            answer="Based on available research literature, autophagy...",
            references=[
                Reference(arxiv_id="2301.12345", title="Paper 1", score=0.9),
                Reference(arxiv_id="2302.67890", title="Paper 2", score=0.8)
            ]
        )
        
        assert "research literature" in response.answer
        assert len(response.references) == 2
        assert response.references[0].score > response.references[1].score
    
    def test_allows_empty_references(self):
        response = QueryResponse(
            answer="Could not find sufficient relevant research.",
            references=[]
        )
        assert len(response.references) == 0
        assert "Could not find" in response.answer
    
    def test_rejects_missing_answer(self):
        with pytest.raises(ValidationError):
            QueryResponse(references=[])