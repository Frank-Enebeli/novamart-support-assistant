import os

from dotenv import load_dotenv
from openai import OpenAI

from config import EMBEDDING_MODEL


load_dotenv()


def get_openai_client():
    """
    Create an OpenAI client using the API key
    stored in the .env file.
    """

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY was not found. "
            "Add it to your .env file."
        )

    return OpenAI(
        api_key=api_key
    )


def create_embeddings(
    texts,
    client=None,
):
    """
    Create embeddings for multiple text strings.
    """

    if not texts:
        raise ValueError(
            "At least one text is required."
        )

    cleaned_texts = []

    for text in texts:
        if not isinstance(text, str):
            raise TypeError(
                "Each embedding input must be text."
            )

        cleaned_text = text.strip()

        if not cleaned_text:
            raise ValueError(
                "Embedding input cannot be empty."
            )

        cleaned_texts.append(
            cleaned_text
        )

    api_client = (
        client
        if client is not None
        else get_openai_client()
    )

    response = api_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=cleaned_texts,
    )

    embeddings = [
        item.embedding
        for item in response.data
    ]

    return embeddings


def create_embedding(
    text,
    client=None,
):
    """
    Create one embedding for one text string.
    """

    embeddings = create_embeddings(
        [text],
        client=client,
    )

    return embeddings[0]


def main():
    from src.chunking import (
        chunk_documents,
    )

    from src.document_loader import (
        load_documents,
    )

    documents = load_documents()

    chunks = chunk_documents(
        documents
    )

    sample_chunks = chunks[:3]

    sample_texts = [
        chunk["text"]
        for chunk in sample_chunks
    ]

    print(
        f"Creating embeddings for "
        f"{len(sample_texts)} sample chunks..."
    )

    embeddings = create_embeddings(
        sample_texts
    )

    print(
        f"Created {len(embeddings)} embeddings."
    )

    print(
        f"Embedding dimensions: "
        f"{len(embeddings[0])}"
    )

    print(
        "\nFirst five values "
        "from the first embedding:"
    )

    print(
        embeddings[0][:5]
    )


if __name__ == "__main__":
    main()