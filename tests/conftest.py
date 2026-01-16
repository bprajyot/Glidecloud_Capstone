import pytest
from datetime import datetime
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

@pytest.fixture
def sample_paper_data():
    return {
        "arxiv_id": "2301.12345",
        "title": "Understanding Autophagy in Neurodegenerative Diseases",
        "authors": ["John Doe", "Jane Smith"],
        "published": datetime(2023, 1, 15),
        "categories": ["q-bio.CB", "q-bio.NC"],
        "abstract": (
            "Autophagy is a lysosomal degradation pathway essential for "
            "cellular homeostasis. This study investigates the role of "
            "autophagy in neurodegenerative diseases including Alzheimer's "
            "and Parkinson's disease."
        )
    }


@pytest.fixture
def sample_chunks():
    return [
        {
            "arxiv_id": "2301.12345",
            "title": "Autophagy in Cancer",
            "chunk_text": "Autophagy is a cellular degradation process that plays a complex role in cancer development.",
            "chunk_index": 0,
            "score": 0.92
        },
        {
            "arxiv_id": "2302.67890",
            "title": "Cell Death Mechanisms",
            "chunk_text": "Programmed cell death involves multiple pathways including apoptosis and autophagy.",
            "chunk_index": 0,
            "score": 0.85
        }
    ]


@pytest.fixture
def sample_embedding():
    return [0.1, 0.2, -0.3, 0.5, -0.1] * 153 + [0.1, 0.2, -0.3]


@pytest.fixture
def scientific_abstract():
    return (
        "Autophagy is an evolutionarily conserved catabolic process involving "
        "the degradation of cellular components through the lysosomal machinery. "
        "It plays a crucial role in maintaining cellular homeostasis by removing "
        "damaged organelles and misfolded proteins. Recent studies have demonstrated "
        "that autophagy dysfunction is associated with various pathological conditions, "
        "including neurodegenerative diseases, cancer, and metabolic disorders. "
        "Understanding the molecular mechanisms regulating autophagy may provide "
        "therapeutic targets for these conditions."
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers", 
        "integration: marks tests requiring external services (Ollama, MongoDB)"
    )
    config.addinivalue_line(
        "markers", 
        "slow: marks tests that take significant time to run"
    )