import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime
from app.main import app
from app.models.schema import Paper


client = TestClient(app)


class TestHealthEndpoints:   
    def test_root_endpoint_returns_200(self):
        response = client.get("/")
        assert response.status_code == 200
    
    def test_root_returns_json(self):
        response = client.get("/")
        data = response.json()
        
        assert isinstance(data, dict)
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_health_endpoint_works(self):
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"


class TestQueryEndpoint:    
    @patch('app.api.routes.query.search_papers')
    @patch('app.api.routes.query.generate_answer')
    def test_successful_query(self, mock_generate, mock_search):
        mock_search.return_value = [
            {
                "arxiv_id": "2301.12345",
                "title": "Autophagy in Cancer",
                "chunk_text": "Autophagy plays a role...",
                "score": 0.92
            }
        ]
        
        mock_generate.return_value = (
            "Based on available research literature, autophagy is a cellular "
            "process. According to arXiv:2301.12345, it plays a role in cancer."
        )
        
        response = client.post(
            "/query/case",
            json={
                "case_description": "What is the role of autophagy in cancer?"
            }
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert "answer" in data
        assert "references" in data
        assert "research literature" in data["answer"]
        assert len(data["references"]) > 0
    
    def test_rejects_short_query(self):
        response = client.post(
            "/query/case",
            json={"case_description": "Too short"}
        )
        
        assert response.status_code == 422
    
    def test_rejects_empty_query(self):
        response = client.post(
            "/query/case",
            json={"case_description": ""}
        )
        
        assert response.status_code == 422
    
    def test_rejects_missing_description(self):
        response = client.post(
            "/query/case",
            json={}
        )
        
        assert response.status_code == 422
    
    @patch('app.api.routes.query.search_papers')
    @patch('app.api.routes.query.generate_answer')
    def test_handles_no_results(self, mock_generate, mock_search):
        mock_search.return_value = []
        mock_generate.return_value = "Could not find sufficient relevant research."
        
        response = client.post(
            "/query/case",
            json={"case_description": "What is the weather today in Mumbai?"}
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert "Could not find" in data["answer"]
        assert len(data["references"]) == 0
    
    @patch('app.api.routes.query.search_papers')
    @patch('app.api.routes.query.generate_answer')
    def test_deduplicates_references(self, mock_generate, mock_search):
        mock_search.return_value = [
            {
                "arxiv_id": "2301.12345",
                "title": "Same Paper",
                "chunk_text": "Chunk 1",
                "score": 0.95
            },
            {
                "arxiv_id": "2301.12345",
                "title": "Same Paper",
                "chunk_text": "Chunk 2",
                "score": 0.90
            },
            {
                "arxiv_id": "2302.67890",
                "title": "Different Paper",
                "chunk_text": "Chunk 3",
                "score": 0.85
            }
        ]
        mock_generate.return_value = "Answer with citations."
        
        response = client.post(
            "/query/case",
            json={"case_description": "Query about autophagy mechanisms"}
        )
        
        data = response.json()
        
        assert len(data["references"]) == 2
        
        ids = [ref["arxiv_id"] for ref in data["references"]]
        assert ids == ["2301.12345", "2302.67890"]
    
    @patch('app.api.routes.query.search_papers')
    def test_handles_service_error(self, mock_search):
        mock_search.side_effect = Exception("Database connection failed")
        
        response = client.post(
            "/query/case",
            json={"case_description": "Valid query but service fails"}
        )
        
        assert response.status_code == 500


class TestAPIDocumentation:
    
    def test_docs_endpoint_exists(self):
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_openapi_schema_exists(self):
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
    
    def test_openapi_documents_endpoints(self):
        response = client.get("/openapi.json")
        data = response.json()
        
        paths = data["paths"]
        
        assert "/" in paths
        assert "/health" in paths
        assert "/query/case" in paths