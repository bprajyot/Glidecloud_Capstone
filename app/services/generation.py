import ollama
from typing import List, Dict, Any
from app.core.config import configs
from app.core.logging import logger


def generate_answer(case_description: str, retrieved_chunks: List[Dict[str, Any]]) -> str:
    if not retrieved_chunks:
        logger.warning("No relevant research found")
        return (
            "Based on available research literature, I could not find "
            "sufficient relevant studies to address this query. "
            "Please try rephrasing your question or consult additional sources."
        )
    
    logger.info("Generating answer from LLM...")
    
    context = build_context(retrieved_chunks)
    
    prompt = create_prompt(case_description, context)
    
    try:
        client = ollama.Client(host=configs.ollama_url)
        response = client.generate(
            model=configs.llm_model,
            prompt=prompt
        )
        
        answer = response["response"]
        logger.info(f"Generated answer ({len(answer)} chars)")
        return answer
    
    except Exception as e:
        logger.error(f"  ✗ Error generating answer: {e}")
        raise


def build_context(chunks: List[Dict[str, Any]]) -> str:
    context_parts = []
    
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(
            f"[Research Paper {i}]\n"
            f"arXiv ID: {chunk['arxiv_id']}\n"
            f"Title: {chunk['title']}\n"
            f"Content: {chunk['chunk_text']}\n"
        )
    
    return "\n".join(context_parts)


def create_prompt(case_description: str, context: str) -> str:
   return f"""You are a medical research assistant helping researchers understand scientific literature.

RULES:
1. Use ONLY the research papers provided below - do not add external knowledge
2. Always start with "Based on available research literature..."
3. Cite arXiv IDs when referencing findings (e.g., "According to arXiv:2301.12345...")
4. If the research doesn't contain enough information, clearly state this
5. Do NOT provide clinical advice or treatment recommendations
6. Do NOT hallucinate or make up information
7. Be honest about uncertainties and limitations

REMEMBER: This is a research support tool.

RESEARCHER'S QUESTION:
{case_description}

RELEVANT RESEARCH PAPERS:
{context}

Please provide a comprehensive response based on the research above, with proper citations."""