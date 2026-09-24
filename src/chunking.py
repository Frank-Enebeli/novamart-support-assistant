from config import CHUNK_OVERLAP, CHUNK_SIZE


def chunk_text(
    text,
    chunk_size=CHUNK_SIZE,
    overlap=CHUNK_OVERLAP,
):
    """
    Split text into overlapping word-based chunks.
    """

    if not text or not text.strip():
        return []

    if chunk_size <= 0:
        raise ValueError(
            "chunk_size must be greater than 0."
        )

    if overlap < 0:
        raise ValueError(
            "overlap cannot be negative."
        )

    if overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size."
        )

    words = text.split()

    chunks = []

    step = chunk_size - overlap

    for start in range(
        0,
        len(words),
        step,
    ):
        end = start + chunk_size

        chunk_words = words[
            start:end
        ]

        if not chunk_words:
            break

        chunk = " ".join(
            chunk_words
        )

        chunks.append(chunk)

        if end >= len(words):
            break

    return chunks


def chunk_document(
    document,
    chunk_size=CHUNK_SIZE,
    overlap=CHUNK_OVERLAP,
):
    """
    Split one loaded document into chunks
    while preserving its metadata.
    """

    text_chunks = chunk_text(
        document["text"],
        chunk_size=chunk_size,
        overlap=overlap,
    )

    chunks = []

    for chunk_number, text in enumerate(
        text_chunks
    ):
        chunks.append(
            {
                "source": document["source"],
                "category": document["category"],
                "chunk_number": chunk_number,
                "text": text,
            }
        )

    return chunks


def chunk_documents(
    documents,
    chunk_size=CHUNK_SIZE,
    overlap=CHUNK_OVERLAP,
):
    """
    Chunk a list of loaded documents.
    """

    all_chunks = []

    for document in documents:
        document_chunks = chunk_document(
            document,
            chunk_size=chunk_size,
            overlap=overlap,
        )

        all_chunks.extend(
            document_chunks
        )

    return all_chunks


def main():
    from src.document_loader import (
        load_documents,
    )

    documents = load_documents()

    chunks = chunk_documents(
        documents
    )

    print(
        f"Loaded {len(documents)} documents."
    )

    print(
        f"Created {len(chunks)} chunks."
    )

    print(
        f"Chunk size: {CHUNK_SIZE} words"
    )

    print(
        f"Overlap: {CHUNK_OVERLAP} words\n"
    )

    for chunk in chunks:
        word_count = len(
            chunk["text"].split()
        )

        print(
            f"Source: {chunk['source']}"
        )

        print(
            f"Category: {chunk['category']}"
        )

        print(
            f"Chunk number: "
            f"{chunk['chunk_number']}"
        )

        print(
            f"Words: {word_count}"
        )

        print(
            f"Preview: "
            f"{chunk['text'][:160]}..."
        )

        print("-" * 60)


if __name__ == "__main__":
    main()