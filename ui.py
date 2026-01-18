import streamlit as st
import requests
import time
from typing import Dict, Any, List
import json
st.set_page_config(
    page_title="Medical Case Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)
API_BASE_URL = "http://localhost:8000"

def check_api_health() -> bool:
    """Check if the FastAPI server is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def get_api_url() -> str:
    """Get the current API URL (custom or default)."""
    return st.session_state.get('api_base_url', API_BASE_URL)


def call_ingest_api(max_papers: int) -> Dict[str, Any]:
    url = f"{get_api_url()}/ingest/arxiv"
    payload = {"max_papers": max_papers}
    
    try:
        response = requests.post(url, json=payload, timeout=3600)  # 1 hour timeout
        response.raise_for_status()
        return {
            "success": True,
            "data": response.json()
        }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Request timed out. The server might still be processing."
        }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "Cannot connect to API server. Is it running?"
        }
    except requests.exceptions.HTTPError as e:
        return {
            "success": False,
            "error": f"HTTP Error: {e.response.status_code} - {e.response.text}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def call_query_api(case_description: str) -> Dict[str, Any]:
    url = f"{get_api_url()}/query/case"
    payload = {"case_description": case_description}
    
    try:
        response = requests.post(url, json=payload, timeout=120)  # 2 minute timeout
        response.raise_for_status()
        return {
            "success": True,
            "data": response.json()
        }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Query timed out. Try a simpler question or check the server."
        }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "Cannot connect to API server. Is it running?"
        }
    except requests.exceptions.HTTPError as e:
        return {
            "success": False,
            "error": f"HTTP Error: {e.response.status_code} - {e.response.text}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def display_api_request(method: str, endpoint: str, payload: Dict = None):
    """Display the API request being made."""
    with st.expander("📡 API Request Details", expanded=False):
        st.code(f"""
Method: {method}
Endpoint: {get_api_url()}{endpoint}
Payload: {json.dumps(payload, indent=2) if payload else 'None'}
        """, language="python")

def display_api_response(response: Dict[str, Any]):
    with st.expander("📨 API Response", expanded=False):
        st.json(response)

def main():
    
    col1, col2 = st.columns([18, 2])
    api_status = check_api_health()

    with col1:
        st.title("Medical Case Assistant")
    with col2:
        if api_status:
            st.success("Server Online")
        else:
            st.error("API Server: Offline")
    
    # Main content tabs
    tab1, tab2= st.tabs(["Query", "Ingest Data"])
    
    # ========================================================================
    # TAB 1: QUERY INTERFACE
    # ========================================================================
    
    with tab1:
        st.header("Query Research Literature")
        
        if not api_status:
            st.error("API server is not running. Please start it first.")
            st.code("uvicorn app.main:app --reload")
            st.stop()
        
        # Example queries
        with st.expander("Example Queries"):
            st.markdown("""
            - How are Genetic Algorithms (GA) and Particle Swarm Optimization (PSO) applied to controller design?
            - Which papers focus on optimization, and which focus on representation learning?
            - What trends can be observed in the application of bio-inspired techniques over time?
            - What common principles of biological inspiration appear across these papers?
            - What are the mechanisms of circadian rhythm regulation?
            """)
        
        # Query input
        query_text = st.text_area(
            "Enter your medical/biological research question:",
            height=100,
            placeholder="e.g., What are the mechanisms of autophagy in cancer cells?",
            key="query_input"
        )
        
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            search_button = st.button("Search", type="primary", use_container_width=True)
        
        # Process query
        if search_button:
            if not query_text or len(query_text) < 20:
                st.warning("Please enter a detailed query (at least 20 characters).")
            else:                
                # Make API call
                with st.spinner("🔎 Querying research literature via API..."):
                    start_time = time.time()
                    result = call_query_api(query_text)
                    elapsed_time = time.time() - start_time
                
                # Display results
                if result["success"]:
                    data = result["data"]
                    
                    # Show timing
                    st.caption(f"Query completed in {elapsed_time:.2f} seconds")
                    
                    # Display answer
                    st.subheader("Answer")
                    st.markdown(data["answer"])
                    
                    # Display references
                    if data.get("references"):
                        st.subheader(f"References ({len(data['references'])} papers)")
                        
                        for i, ref in enumerate(data["references"], 1):
                            with st.container():
                                col1, col2, col3 = st.columns([0.5, 3, 1])
                                
                                with col1:
                                    st.metric("", f"#{i}")
                                
                                with col2:
                                    st.markdown(f"**{ref['title']}**")
                                    st.caption(f"arXiv:{ref['arxiv_id']} | Similarity: {ref['score']:.3f}")
                                
                                with col3:
                                    arxiv_url = f"https://arxiv.org/abs/{ref['arxiv_id']}"
                                    st.link_button("View Paper", arxiv_url)
                                
                                st.divider()
                    else:
                        st.info("No references found for this query.")
                
                else:
                    st.error(f"Query failed: {result['error']}")
                    st.info("Make sure the API server is running and the database has papers.")
    
    
    with tab2:
        st.header("Ingest Papers from arXiv")
        
        if not api_status:
            st.error("⚠️ API server is not running. Please start it first.")
            st.code("uvicorn app.main:app --reload")
            st.stop()
              
        # Ingestion controls
        col1, col2= st.columns([1, 1])
        
        with col1:
            max_papers = st.number_input(
                "Number of papers:",
                min_value=1,
                max_value=500,
                value=30,
                step=10,
                help="Start with 30 for testing."
            )
        
        with col2:
            estimated_time = max_papers * 12 // 60
            st.metric("Est. Time", f"~{estimated_time} min")
        
        ingest_button = st.button("📥 Start Ingestion", type="primary")
        
        if ingest_button:
            
            # Progress indicators
            progress_container = st.container()
            status_text = st.empty()
            
            with progress_container:
                st.warning(f"⏳ Ingesting {max_papers} papers via API... This may take {estimated_time}+ minutes.")
                st.info("💡 Tip: You can monitor the FastAPI server logs in your terminal to see detailed progress.")
            
            # Make API call
            with st.spinner(f"📡 Calling API to ingest {max_papers} papers..."):
                start_time = time.time()
                result = call_ingest_api(max_papers)
                elapsed_time = time.time() - start_time
            
            # Display results
            if result["success"]:
                data = result["data"]
                
                # Success message
                st.success(f"""
                ✅ **Ingestion Complete!**
                
                - Papers processed: {data['papers_processed']}
                - Chunks created: {data['chunks_created']}
                - Time taken: {elapsed_time:.1f} seconds ({elapsed_time/60:.1f} minutes)
                - Message: {data['message']}
                """)
                
                # Show stats
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Papers", data['papers_processed'])
                with col2:
                    st.metric("Chunks", data['chunks_created'])
                with col3:
                    avg_chunks = data['chunks_created'] / max(data['papers_processed'], 1)
                    st.metric("Avg Chunks/Paper", f"{avg_chunks:.1f}")
                
            else:
                st.error(f"Ingestion failed: {result['error']}")
                st.info("""
                **Troubleshooting:**
                1. Check if API server is running
                2. Check server logs for detailed errors
                3. Verify Ollama is running: `ollama serve`
                4. Verify MongoDB connection in server logs
                """)
# ============================================================================
# RUN APP
# ============================================================================

if __name__ == "__main__":
    main()