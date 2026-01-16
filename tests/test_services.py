import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.embedding import generate_embedding
from app.services.generation import (
    build_context, 
    create_prompt, 
    generate_answer
)


class TestEmbeddingService:    
    
    @patch('app.services.embedding.ollama.Client')
    def test_calls_correct_model(self, mock_client):
        mock_instance = Mock()
        mock_instance.embeddings.return_value = {"embedding": [0.1] * 1024}
        mock_client.return_value = mock_instance
        
        generate_embedding("test")
        
        call_kwargs = mock_instance.embeddings.call_args[1]
        assert call_kwargs['model'] == 'mxbai-embed-large'
    
    @patch('app.services.embedding.ollama.Client')
    def test_handles_scientific_text(self, mock_client):
        mock_instance = Mock()
        mock_instance.embeddings.return_value = {"embedding": [0.1] * 1024}
        mock_client.return_value = mock_instance
        
        scientific_text = (
            "Autophagy is a lysosomal degradation pathway "
            "that is essential for cell survival, development, "
            "and homeostasis."
        )
        
        result = generate_embedding(scientific_text)
        
        call_kwargs = mock_instance.embeddings.call_args[1]
        assert call_kwargs['prompt'] == scientific_text
        assert len(result) == 1024
    
    @patch('app.services.embedding.ollama.Client')
    def test_raises_on_ollama_failure(self, mock_client):
        mock_instance = Mock()
        mock_instance.embeddings.side_effect = Exception("Ollama connection failed")
        mock_client.return_value = mock_instance
        
        with pytest.raises(Exception) as exc_info:
            generate_embedding("test")
        
        assert "Ollama" in str(exc_info.value)


class TestGenerationService:
    
    def test_builds_context_from_chunks(self):
        chunks = [
            {
                "arxiv_id": "2301.12345",
                "title": "Autophagy in Cancer",
                "chunk_text": "Autophagy plays a dual role in cancer."
            },
            {
                "arxiv_id": "2302.67890",
                "title": "Cell Death Pathways",
                "chunk_text": "Apoptosis and autophagy are interconnected."
            }
        ]
        
        context = build_context(chunks)
        
        assert "2301.12345" in context
        assert "2302.67890" in context
        assert "Autophagy in Cancer" in context
        assert "dual role" in context
        
        assert "[Research Paper 1]" in context
        assert "[Research Paper 2]" in context
    
    def test_creates_prompt_with_instructions(self):
        query = "What is autophagy?"
        context = "arXiv:123: Autophagy is a cellular process."
        
        prompt = create_prompt(query, context)
        
        assert "ONLY" in prompt or "only" in prompt.lower()
        assert "research" in prompt.lower()
        assert query in prompt
        assert context in prompt
        
        assert "cite" in prompt.lower() or "arxiv" in prompt.lower()
        
        assert "hallucinate" in prompt.lower() or "make up" in prompt.lower()
    
    @patch('app.services.generation.ollama.Client')
    def test_generates_answer_with_chunks(self, mock_client):
        mock_instance = Mock()
        mock_instance.generate.return_value = {
            "response": (
                "Based on available research literature, autophagy "
                "is a cellular degradation process. According to "
                "arXiv:2301.12345, it plays a role in cancer."
            )
        }
        mock_client.return_value = mock_instance
        
        chunks = [
            {
                "arxiv_id": "2301.12345",
                "title": "Autophagy Research",
                "chunk_text": "Autophagy is important in cancer."
            }
        ]
        
        answer = generate_answer("What is autophagy?", chunks)
        
        assert isinstance(answer, str)
        assert len(answer) > 0
        assert "research literature" in answer.lower()
        mock_instance.generate.assert_called_once()
    
    def test_handles_empty_chunks(self):
        answer = generate_answer("query", [])
        
        assert isinstance(answer, str)
        assert "could not find" in answer.lower() or "insufficient" in answer.lower()
    
    @patch('app.services.generation.ollama.Client')
    def test_passes_complete_context_to_llm(self, mock_client):
        mock_instance = Mock()
        mock_instance.generate.return_value = {"response": "Answer"}
        mock_client.return_value = mock_instance
        
        chunks = [
            {
                "arxiv_id": "2301.12345",
                "title": "Paper 1",
                "chunk_text": "Important finding A"
            },
            {
                "arxiv_id": "2302.67890",
                "title": "Paper 2",
                "chunk_text": "Important finding B"
            }
        ]
        
        generate_answer("query", chunks)
        
        call_kwargs = mock_instance.generate.call_args[1]
        prompt = call_kwargs['prompt']
        
        assert "2301.12345" in prompt
        assert "2302.67890" in prompt
        assert "Important finding A" in prompt
        assert "Important finding B" in prompt
    
    @patch('app.services.generation.ollama.Client')
    def test_uses_correct_llm_model(self, mock_client):
        mock_instance = Mock()
        mock_instance.generate.return_value = {"response": "Answer"}
        mock_client.return_value = mock_instance
        
        chunks = [{"arxiv_id": "123", "title": "T", "chunk_text": "C"}]
        generate_answer("query", chunks)
        
        call_kwargs = mock_instance.generate.call_args[1]
        assert call_kwargs['model'] == 'llama3.2'