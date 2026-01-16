VECTOR_INDEX_DEFINITION = {
    "fields": [
        {
            "type": "vector",
            "path": "embedding",
            "numDimensions": 1024,
            "similarity": "cosine"
        },
        {
            "type": "filter",
            "path": "categories"
        },
        {
            "type": "filter",
            "path": "arxiv_id"
        }
    ]
}