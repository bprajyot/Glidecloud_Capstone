from typing import List


def chunk_text(text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        if end < len(text):
            last_period = text.rfind('. ', start, end)
            if last_period != -1 and last_period > start:
                end = last_period + 1
        
        chunks.append(text[start:end].strip())
        start = end - overlap
    
    return chunks