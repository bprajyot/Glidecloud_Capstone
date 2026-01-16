# Medical Case Assistant

A simple, Retrieval Augmented Generation (RAG) system for medical research assistance using arXiv papers.

---

## 📚 What This Does

This system helps researchers explore medical and biomedical literature by:

1. **Fetching** papers from arXiv
2. **Chunking** abstracts into smaller pieces
3. **Embedding** chunks using semantic vectors
4. **Storing** everything in MongoDB with vector search
5. **Retrieving** relevant research for your questions
6. **Generating** grounded answers with proper citations

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────┐
│                    USER QUERY                        │
│   "What mechanisms drive autophagy in cancer?"       │
└────────────────────┬─────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────┐
│              RETRIEVAL (Vector Search)                 │
│  • Convert query to embedding                          │
│  • Search MongoDB for similar chunks                   │
│  • Return top-K most relevant papers                   │
└────────────────────┬───────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────┐
│              GENERATION (LLM)                          │
│  • Take retrieved research                             │
│  • Generate grounded answer                            │
│  • Include arXiv citations                             │
└────────────────────┬───────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────┐
│         ANSWER WITH CITATIONS                          │
│  "Based on research literature, autophagy..."          │
│  References: [arXiv:2301.12345, ...]                   │
└────────────────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```
medical-rag/
│
├── app/
│   ├── main.py                    
│   │
│   ├── core/
│   │   ├── config.py              
│   │   └── logger.py              
│   │
│   ├── models/
│   │   └── schemas.py             
│   │
│   ├── db/
│   │   └── database.py            
│   │
│   ├── services/                  
│   │   ├── paper.py       
│   │   ├── embedding_service.py   
│   │   ├── retrieval_service.py   
│   │   └── generation_service.py  
│   │
│   ├── api/routes/
│   │   ├── ingest.py              
│   │   └── query.py               
│   │
│   └── utils/
│       └── text_utils.py                       
│
├── requirements.txt
├── .env
├── README.md
└── sample_xml.xml              # contains sample response from arXiv
```

**Why this structure?**
- **`core/`**: Configuration and logging
- **`services/`**: Each service does ONE thing
- **`api/routes/`**: API endpoints separated by function
- **`utils/`**: Helper functions used across the app

---

## 🚀 Setup Instructions

### 1. Prerequisites

- **Python 3.10+**
- **Ollama** installed ([https://ollama.ai](https://ollama.ai))
- **MongoDB Atlas** account (free tier works!)

### 2. Install Ollama Models

```bash
# Install Ollama first, then pull models
ollama pull llama3.2
ollama pull mxbai-embed-large
```

### 3. Setup MongoDB Atlas Vector Search

1. Create a MongoDB Atlas account
2. Create a new cluster (free M0 tier is fine)
3. Create database: `medical_rag`
4. Create collection: `papers`
5. **IMPORTANT**: Create a Vector Search Index

Go to "Atlas Search" → "Create Search Index" → "JSON Editor" and paste:

```json
{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 1024,
      "similarity": "cosine"
    }
  ]
}
```

Name it: `vector_index`

### 4. Clone and Setup Project

```bash
# Clone repository
git clone https://github.com/bprajyot/Glidecloud_Capstone.git
cd medical-rag

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env
# Edit .env with your MongoDB URI
```

### 5. Ingest Data
- hit the ingest/paper end point on swagger ui

This will take several minutes! The script:
- Fetches 50 papers from arXiv
- Cleans and chunks each abstract
- Generates embeddings for each chunk
- Stores everything in MongoDB

### 6. Run the API

```bash
uvicorn app.main:app --reload
```

Visit: http://localhost:8000/docs for interactive API documentation