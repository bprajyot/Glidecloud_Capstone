import httpx
import xml.etree.ElementTree as ET
from typing import List
from datetime import datetime
import asyncio
from app.models.schema import Paper
from app.core.logging import logger


async def  fetch_paper(max_results: int = 50) -> List[Paper]:
    base_url = "https://export.arxiv.org/api/query"
    query = "cat:q-bio.TO"
    
    papers = []
    batch_size = 50
    
    logger.info(f"Fetching up to {max_results} papers from arXiv...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for start in range(0, max_results, batch_size):
            current_batch = min(batch_size, max_results - start)
            
            params = {
                "search_query": query,
                "start": start,
                "max_results": current_batch,
                "sortBy": "submittedDate",
                "sortOrder": "descending"
            }
            
            try:
                logger.info(f"Fetching batch: {start} to {start + current_batch}")
                response = await client.get(base_url, params=params)
                response.raise_for_status()
                
                batch_papers =  parse_response(response.text)
                papers.extend(batch_papers)
                
                logger.info(f"Got {len(batch_papers)} papers")
                
                if start + batch_size < max_results:
                    await asyncio.sleep(3)
                    
            except Exception as e:
                logger.error(f"Error fetching batch: {e}")
                break
    
    logger.info(f"Total papers fetched: {len(papers)}")
    return papers


def  parse_response(xml_text: str) -> List[Paper]:
    papers = []
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    
    root = ET.fromstring(xml_text)
    
    for entry in root.findall("atom:entry", ns):
        try:
            id_url = entry.find("atom:id", ns).text
            arxiv_id = id_url.split("/")[-1]
            
            title = entry.find("atom:title", ns).text.strip()
            title = " ".join(title.split())
            
            authors = [
                author.find("atom:name", ns).text
                for author in entry.findall("atom:author", ns)
            ]
            
            published_str = entry.find("atom:published", ns).text
            published = datetime.fromisoformat(published_str.replace("Z", "+00:00"))
            
            categories = [
                cat.attrib["term"]
                for cat in entry.findall("atom:category", ns)
            ]
            
            abstract = entry.find("atom:summary", ns).text.strip()
            abstract = " ".join(abstract.split())
            
            papers.append(Paper(
                arxiv_id=arxiv_id,
                title=title,
                authors=authors,
                published=published,
                categories=categories,
                abstract=abstract
            ))
            
        except Exception as e:
            logger.warning(f"Could not parse entry: {e}")
            continue
    
    return papers