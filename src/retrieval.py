from config import TOP_K

from src.embeddings import create_embedding
from src.vector_store import get_collection


def retrieve_chunks(
    question,
    top_k=TOP_K,
    embedding_client=None,
):
    """
    Retrieve the most relevant knowledge-base chunks
    for a customer question.
    """

    if not isinstance(question, str):
        raise TypeError(
            "Question must be a string."
        )

    question = question.strip()

    if not question:
        raise ValueError(
            "Question cannot be empty."
        )

    if top_k <= 0:
        raise ValueError(
            "top_k must be greater than 0."
        )

    query_embedding = create_embedding(
        question,
        client=embedding_client,
    )

    collection = get_collection()

    if collection.count() == 0:
        return []

    result_count = min(
        top_k,
        collection.count(),
    )

    results = collection.query(
        query_embeddings=[
            query_embedding
        ],
        n_results=result_count,
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )

    documents = results.get(
        "documents",
        [[]],
    )[0]

    metadatas = results.get(
        "metadatas",
        [[]],
    )[0]

    distances = results.get(
        "distances",
        [[]],
    )[0]

    retrieved_chunks = []

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances,
    ):
        retrieved_chunks.append(
            {
                "text": document,
                "source": metadata.get(
                    "source",
                    "unknown",
                ),
                "category": metadata.get(
                    "category",
                    "unknown",
                ),
                "chunk_number": metadata.get(
                    "chunk_number",
                    -1,
                ),
                "distance": distance,
            }
        )

    return retrieved_chunks


def format_retrieved_context(
    retrieved_chunks,
):
    """
    Convert retrieved chunks into text that can later
    be supplied to the language model.
    """

    if not retrieved_chunks:
        return ""

    context_parts = []

    for index, chunk in enumerate(
        retrieved_chunks,
        start=1,
    ):
        context_parts.append(
            (
                f"[Retrieved chunk {index}]\n"
                f"Source: {chunk['source']}\n"
                f"Category: {chunk['category']}\n"
                f"Chunk number: "
                f"{chunk['chunk_number']}\n"
                f"Content:\n{chunk['text']}"
            )
        )

    return "\n\n---\n\n".join(
        context_parts
    )


def main():
    print(
        "NovaMart Semantic Search"
    )

    print("=" * 50)

    question = input(
        "\nEnter a customer question: "
    ).strip()

    if not question:
        print(
            "Please enter a question."
        )
        return

    try:
        chunks = retrieve_chunks(
            question
        )

        if not chunks:
            print(
                "\nNo knowledge-base "
                "chunks were found."
            )
            return

        print(
            f"\nTop {len(chunks)} "
            f"retrieved chunks:\n"
        )

        for rank, chunk in enumerate(
            chunks,
            start=1,
        ):
            print(
                f"Result {rank}"
            )

            print(
                f"Distance: "
                f"{chunk['distance']:.4f}"
            )

            print(
                f"Source: "
                f"{chunk['source']}"
            )

            print(
                f"Category: "
                f"{chunk['category']}"
            )

            print(
                f"Chunk: "
                f"{chunk['chunk_number']}"
            )

            print(
                f"Text: "
                f"{chunk['text']}"
            )

            print(
                "-" * 60
            )

    except Exception as error:
        print(
            f"\nSearch failed: {error}"
        )


if __name__ == "__main__":
    main()