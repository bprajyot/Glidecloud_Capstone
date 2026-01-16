
import pytest
from app.utils.text_cleaning import clean_text, chunk_text


class TestCleanText:
    
    def test_removes_multiple_spaces(self):
        text = "This  has    multiple   spaces"
        result = clean_text(text)
        assert result == "This has multiple spaces"
        assert "  " not in result
    
    def test_removes_newlines_and_tabs(self):
        text = "Line 1\nLine 2\tLine 3"
        result = clean_text(text)
        assert "\n" not in result
        assert "\t" not in result
        assert "Line 1 Line 2 Line 3" in result
    
    def test_preserves_scientific_punctuation(self):
        text = "Autophagy (self-eating) occurs at pH 5.0-6.0."
        result = clean_text(text)
        assert "(" in result
        assert ")" in result
        assert "-" in result
        assert "." in result
    
    def test_handles_empty_string(self):
        result = clean_text("")
        assert result == ""
    
    def test_handles_real_abstract(self):
        text = """Autophagy   is a cellular process
        that   degrades    proteins.
        It   plays   a   role   in   cancer."""
        result = clean_text(text)
        assert "  " not in result
        assert "\n" not in result
        assert "autophagy" in result.lower()


class TestChunkText:
    
    def test_short_text_returns_single_chunk(self):
        text = "Short abstract about autophagy."
        chunks = chunk_text(text, chunk_size=100, overlap=20)
        assert len(chunks) == 1
        assert chunks[0] == text
    
    def test_long_text_creates_multiple_chunks(self):
        text = "A" * 500
        chunks = chunk_text(text, chunk_size=100, overlap=0)
        assert len(chunks) > 1
        assert len(chunks) == 5 
    def test_respects_chunk_size_limit(self):
        text = "word " * 200  
        chunks = chunk_text(text, chunk_size=150, overlap=0)
        for chunk in chunks:
            assert len(chunk) <= 150
    
    def test_overlap_creates_shared_content(self):
        text = "AAAAA BBBBB CCCCC DDDDD EEEEE FFFFF GGGGG"
        chunks = chunk_text(text, chunk_size=25, overlap=10)
        
        if len(chunks) > 1:
            for i in range(len(chunks) - 1):
                overlap_found = any(
                    word in chunks[i+1] 
                    for word in chunks[i].split()[-2:]
                )
                assert overlap_found, "Chunks should have overlapping content"
    
    def test_sentence_boundary_splitting(self):
        text = "First sentence. Second sentence. Third sentence. Fourth sentence."
        chunks = chunk_text(text, chunk_size=40, overlap=0)
        
        period_endings = [chunk.rstrip().endswith('.') for chunk in chunks]
        assert any(period_endings), "Should split at sentence boundaries"
    
    def test_no_empty_chunks_created(self):
        text = "Some text with   spaces"
        chunks = chunk_text(text, chunk_size=10, overlap=3)
        for chunk in chunks:
            assert len(chunk.strip()) > 0
    
    def test_handles_scientific_abstract(self):
        text = (
            "Autophagy is a cellular degradation process that plays a critical "
            "role in maintaining cellular homeostasis. It involves the formation "
            "of autophagosomes that engulf cytoplasmic components. These vesicles "
            "then fuse with lysosomes for degradation. Dysregulation of autophagy "
            "has been implicated in various diseases including cancer."
        )
        
        chunks = chunk_text(text, chunk_size=150, overlap=30)
        
        assert len(chunks) > 1
        
        combined = " ".join(chunks)
        assert "Autophagy" in combined
        assert "cancer" in combined
        
        assert all(len(chunk) <= 150 for chunk in chunks)