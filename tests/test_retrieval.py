import uuid

import chromadb

from src import retrieval
from src import ingestion

def test_retrieval_does_not_run_document_ingestion(
    monkeypatch,
):
    collection = (
        create_test_collection()
    )

    def fake_get_collection():
        return collection

    def fake_query_embedding(
        question,
        client=None,
    ):
        return [1.0, 0.0]

    def forbidden_document_embedding(
        *args,
        **kwargs,
    ):
        raise AssertionError(
            "Document embeddings should not "
            "be regenerated during retrieval."
        )

    monkeypatch.setattr(
        retrieval,
        "get_collection",
        fake_get_collection,
    )

    monkeypatch.setattr(
        retrieval,
        "create_embedding",
        fake_query_embedding,
    )

    monkeypatch.setattr(
        ingestion,
        "create_embeddings",
        forbidden_document_embedding,
    )

    results = retrieval.retrieve_chunks(
        "Do you deliver to Canada?",
        top_k=1,
    )

    assert (
        results[0]["source"]
        == "delivery_policy.md"
    )
def create_test_collection():
    client = chromadb.Client()

    collection = (
        client.create_collection(
            name=(
                "test_collection_"
                + uuid.uuid4().hex
            ),
            embedding_function=None,
        )
    )

    collection.add(
        ids=[
            "delivery_chunk",
            "refund_chunk",
        ],
        embeddings=[
            [1.0, 0.0],
            [0.0, 1.0],
        ],
        documents=[
            (
                "NovaMart delivers orders "
                "to Canada."
            ),
            (
                "Approved refunds take "
                "5 to 10 business days."
            ),
        ],
        metadatas=[
            {
                "source": "delivery_policy.md",
                "category": "delivery",
                "chunk_number": 0,
            },
            {
                "source": "refund_policy.md",
                "category": "refunds",
                "chunk_number": 0,
            },
        ],
    )

    return collection


def test_retrieval_returns_expected_document(
    monkeypatch,
):
    collection = (
        create_test_collection()
    )

    def fake_get_collection():
        return collection

    def fake_create_embedding(
        question,
        client=None,
    ):
        # This vector is intentionally
        # closest to the delivery vector.
        return [1.0, 0.0]

    monkeypatch.setattr(
        retrieval,
        "get_collection",
        fake_get_collection,
    )

    monkeypatch.setattr(
        retrieval,
        "create_embedding",
        fake_create_embedding,
    )

    results = retrieval.retrieve_chunks(
        "Do you deliver to Canada?",
        top_k=1,
    )

    assert len(results) == 1

    assert (
        results[0]["source"]
        == "delivery_policy.md"
    )

    assert (
        results[0]["category"]
        == "delivery"
    )


def test_customer_question_only_creates_query_embedding(
    monkeypatch,
):
    collection = (
        create_test_collection()
    )

    embedding_calls = []

    def fake_get_collection():
        return collection

    def fake_create_embedding(
        question,
        client=None,
    ):
        embedding_calls.append(
            question
        )

        return [1.0, 0.0]

    monkeypatch.setattr(
        retrieval,
        "get_collection",
        fake_get_collection,
    )

    monkeypatch.setattr(
        retrieval,
        "create_embedding",
        fake_create_embedding,
    )

    retrieval.retrieve_chunks(
        "Do you deliver to Canada?",
        top_k=1,
    )

    assert len(
        embedding_calls
    ) == 1

    assert (
        embedding_calls[0]
        == "Do you deliver to Canada?"
    )