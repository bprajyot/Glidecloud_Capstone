import re
from typing import List


import re
from typing import List


def clean_text(text: str) -> str:

    text = re.sub(
        r'\(According to\s+arXiv:[^)]+\)',
        '',
        text,
        flags=re.IGNORECASE
    )

    boilerplate_patterns = [
        r'^Based on available research literature,\s*',
        r'^In summary,\s*',
        r'^Furthermore,\s*',
        r'^For instance,\s*',
    ]
    for pattern in boilerplate_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)

    text = re.sub(r'\s+', ' ', text)

    text = re.sub(r'[^\w\s.,!?()-]', '', text)

    return text.strip()


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        if end < len(text):
            last_period = text.rfind('. ', start, end)
            if last_period > start:
                end = last_period + 1
        
        chunk = text[start:end].strip()
        if chunk: 
            chunks.append(chunk)
        
        start = end - overlap
    
    return chunks