from pathlib import Path

import chromadb

from config import (
    CHROMA_DIR,
    COLLECTION_NAME,
)


def get_chroma_client():
    """
    Create a persistent local ChromaDB client.
    """

    CHROMA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    return chromadb.PersistentClient(
        path=str(CHROMA_DIR)
    )


def get_collection():
    """
    Get or create the NovaMart knowledge-base collection.
    """

    client = get_chroma_client()

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME
    )

    return collection


def create_chunk_id(chunk):
    """
    Create a stable ID for a document chunk.
    """

    source = Path(
        chunk["source"]
    ).stem.lower()

    chunk_number = chunk[
        "chunk_number"
    ]

    return (
        f"{source}_chunk_{chunk_number}"
    )


def upsert_chunks(
    chunks,
    embeddings,
):
    """
    Store or update chunks and their embeddings
    in ChromaDB.
    """

    if not chunks:
        raise ValueError(
            "No chunks were provided."
        )

    if not embeddings:
        raise ValueError(
            "No embeddings were provided."
        )

    if len(chunks) != len(embeddings):
        raise ValueError(
            "The number of chunks must match "
            "the number of embeddings."
        )

    collection = get_collection()

    ids = []
    documents = []
    metadatas = []

    for chunk in chunks:
        ids.append(
            create_chunk_id(chunk)
        )

        documents.append(
            chunk["text"]
        )

        metadatas.append(
            {
                "source": chunk["source"],
                "category": chunk[
                    "category"
                ],
                "chunk_number": chunk[
                    "chunk_number"
                ],
            }
        )

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )

    return len(ids)


def delete_document(source):
    """
    Delete all chunks belonging to one source document.
    """

    collection = get_collection()

    collection.delete(
        where={
            "source": source
        }
    )


def document_exists(source):
    """
    Check whether a document already has chunks
    stored in the collection.
    """

    collection = get_collection()

    results = collection.get(
        where={
            "source": source
        },
        limit=1,
    )

    return len(
        results["ids"]
    ) > 0


def get_document_sources():
    """
    Return a sorted list of unique source filenames
    currently stored in ChromaDB.
    """

    collection = get_collection()

    results = collection.get(
        include=[
            "metadatas"
        ]
    )

    sources = set()

    for metadata in (
        results["metadatas"] or []
    ):
        if (
            metadata
            and "source" in metadata
        ):
            sources.add(
                metadata["source"]
            )

    return sorted(sources)


def count_chunks():
    """
    Return the number of chunks stored in the collection.
    """

    collection = get_collection()

    return collection.count()


def inspect_chunks(limit=5):
    """
    Return a small sample of stored chunks.
    """

    collection = get_collection()

    return collection.peek(
        limit=limit
    )


def main():
    collection = get_collection()

    print(
        "NovaMart ChromaDB connection successful."
    )

    print(
        f"Collection: {collection.name}"
    )

    print(
        f"Stored chunks: {collection.count()}"
    )

    sources = get_document_sources()

    if sources:
        print("\nStored documents:")

        for source in sources:
            print(
                f"- {source}"
            )

    else:
        print(
            "\nNo documents have been ingested yet."
        )


if __name__ == "__main__":
    main()