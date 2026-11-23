import psycopg

from esg_docs_to_rag.config import settings


def test_pgvector_installed():
    with psycopg.connect(settings.database_url) as conn:
        row = conn.execute(
            "SELECT extversion FROM pg_extension WHERE extname = 'vector'"
        ).fetchone()
    assert row is not None
