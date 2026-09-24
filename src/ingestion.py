from src.chunking import chunk_document
from src.document_loader import load_documents
from src.embeddings import create_embeddings
from src.vector_store import (
    count_chunks,
    delete_document,
    document_exists,
    upsert_chunks,
)


def ingest_document(
    document,
    force=False,
):
    """
    Chunk, embed, and store one document.

    If the document already exists:
    - skip it by default
    - replace it when force=True
    """

    source = document["source"]

    already_exists = document_exists(
        source
    )

    if already_exists and not force:
        return {
            "source": source,
            "status": "skipped",
            "chunks": 0,
        }

    chunks = chunk_document(
        document
    )

    if not chunks:
        raise ValueError(
            f"No chunks were created for "
            f"{source}."
        )

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    embeddings = create_embeddings(
        texts
    )

    # Create the new embeddings successfully
    # before deleting an older version.
    if already_exists and force:
        delete_document(
            source
        )

    stored_count = upsert_chunks(
        chunks,
        embeddings,
    )

    return {
        "source": source,
        "status": (
            "reindexed"
            if already_exists
            else "ingested"
        ),
        "chunks": stored_count,
    }


def ingest_all_documents(
    force=False,
):
    """
    Ingest all documents in data/documents.
    """

    documents = load_documents()

    if not documents:
        raise ValueError(
            "No documents were found "
            "for ingestion."
        )

    results = []

    for document in documents:
        print(
            f"\nProcessing: "
            f"{document['source']}"
        )

        result = ingest_document(
            document,
            force=force,
        )

        results.append(result)

        if result["status"] == "skipped":
            print(
                "Skipped — already indexed."
            )

        else:
            print(
                f"{result['status'].capitalize()} "
                f"{result['chunks']} chunks."
            )

    return results


def print_summary(results):
    """
    Display an ingestion summary.
    """

    ingested = sum(
        1
        for result in results
        if result["status"] == "ingested"
    )

    reindexed = sum(
        1
        for result in results
        if result["status"] == "reindexed"
    )

    skipped = sum(
        1
        for result in results
        if result["status"] == "skipped"
    )

    new_chunks = sum(
        result["chunks"]
        for result in results
    )

    print("\n" + "=" * 50)
    print("NovaMart Ingestion Summary")
    print("=" * 50)

    print(
        f"Documents ingested: {ingested}"
    )

    print(
        f"Documents re-indexed: {reindexed}"
    )

    print(
        f"Documents skipped: {skipped}"
    )

    print(
        f"Chunks added this run: {new_chunks}"
    )

    print(
        f"Total chunks in ChromaDB: "
        f"{count_chunks()}"
    )


def main():
    print(
        "NovaMart Knowledge Base Ingestion"
    )

    print("=" * 50)

    results = ingest_all_documents(
        force=False
    )

    print_summary(
        results
    )


if __name__ == "__main__":
    main()