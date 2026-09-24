from io import BytesIO
from pathlib import Path

from pypdf import PdfReader

from config import DOCUMENTS_DIR, SUPPORTED_FILE_TYPES


CATEGORY_MAP = {
    "delivery_policy": "delivery",
    "return_policy": "returns",
    "refund_policy": "refunds",
    "payment_methods": "payments",
    "product_warranty": "warranty",
    "order_cancellation": "cancellations",
    "account_support": "account_support",
    "contact_escalation": "escalation",
    "business_hours": "business_hours",
}


def get_category(filename):
    """
    Determine the category of a document from its filename.
    Unknown filenames are placed in the general category.
    """
    stem = Path(filename).stem.lower()

    return CATEGORY_MAP.get(
        stem,
        "general",
    )


def clean_text(text):
    """
    Remove unnecessary whitespace while preserving paragraphs.
    """
    lines = [
        line.strip()
        for line in text.splitlines()
    ]

    cleaned_lines = []
    previous_blank = False

    for line in lines:
        if line:
            cleaned_lines.append(line)
            previous_blank = False

        elif not previous_blank:
            cleaned_lines.append("")
            previous_blank = True

    return "\n".join(cleaned_lines).strip()


def extract_pdf_text(reader):
    """
    Extract text from all pages of a PDF.
    """
    pages = []

    for page in reader.pages:
        page_text = page.extract_text() or ""

        if page_text.strip():
            pages.append(
                page_text.strip()
            )

    return "\n\n".join(pages)


def extract_text_from_path(file_path):
    """
    Extract text from a TXT, Markdown, or PDF file on disk.
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Document not found: {file_path}"
        )

    if not file_path.is_file():
        raise ValueError(
            f"Path is not a file: {file_path}"
        )

    extension = file_path.suffix.lower()

    if extension not in SUPPORTED_FILE_TYPES:
        raise ValueError(
            f"Unsupported file type: {extension}"
        )

    if extension in {".txt", ".md"}:
        text = file_path.read_text(
            encoding="utf-8"
        )

    elif extension == ".pdf":
        reader = PdfReader(
            str(file_path)
        )

        text = extract_pdf_text(
            reader
        )

    else:
        raise ValueError(
            f"Unsupported file type: {extension}"
        )

    text = clean_text(text)

    if not text:
        raise ValueError(
            f"No readable text found in "
            f"{file_path.name}"
        )

    return text


def extract_text_from_bytes(
    filename,
    file_bytes,
):
    """
    Extract text from an uploaded file held in memory.

    This will later be used by the Streamlit admin uploader.
    """
    extension = Path(
        filename
    ).suffix.lower()

    if extension not in SUPPORTED_FILE_TYPES:
        raise ValueError(
            f"Unsupported file type: {extension}"
        )

    if extension in {".txt", ".md"}:
        try:
            text = file_bytes.decode(
                "utf-8-sig"
            )

        except UnicodeDecodeError as error:
            raise ValueError(
                "The text file could not be "
                "decoded as UTF-8."
            ) from error

    elif extension == ".pdf":
        reader = PdfReader(
            BytesIO(file_bytes)
        )

        text = extract_pdf_text(
            reader
        )

    else:
        raise ValueError(
            f"Unsupported file type: {extension}"
        )

    text = clean_text(text)

    if not text:
        raise ValueError(
            f"No readable text found in "
            f"{filename}"
        )

    return text


def load_document(file_path):
    """
    Load one document and return its text and metadata.
    """
    file_path = Path(file_path)

    text = extract_text_from_path(
        file_path
    )

    return {
        "source": file_path.name,
        "category": get_category(
            file_path.name
        ),
        "text": text,
    }


def load_documents(
    directory=DOCUMENTS_DIR,
):
    """
    Load all supported documents from a directory.
    """
    directory = Path(directory)

    if not directory.exists():
        raise FileNotFoundError(
            f"Document directory not found: "
            f"{directory}"
        )

    documents = []

    for file_path in sorted(
        directory.iterdir()
    ):
        if (
            file_path.is_file()
            and file_path.suffix.lower()
            in SUPPORTED_FILE_TYPES
        ):
            document = load_document(
                file_path
            )

            documents.append(
                document
            )

    return documents


def main():
    documents = load_documents()

    print(
        f"Loaded {len(documents)} "
        f"NovaMart documents.\n"
    )

    for document in documents:
        word_count = len(
            document["text"].split()
        )

        print(
            f"Source: {document['source']}"
        )

        print(
            f"Category: "
            f"{document['category']}"
        )

        print(
            f"Words: {word_count}"
        )

        print("-" * 50)


if __name__ == "__main__":
    main()