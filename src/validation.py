from pathlib import Path

from config import (
    MAX_QUESTION_LENGTH,
    MAX_UPLOAD_SIZE_MB,
    SUPPORTED_FILE_TYPES,
)


def validate_question(question):
    """
    Validate and clean a customer question.

    Returns the cleaned question when valid.
    """

    if not isinstance(question, str):
        raise TypeError(
            "Question must be text."
        )

    cleaned_question = question.strip()

    if not cleaned_question:
        raise ValueError(
            "Please enter a question."
        )

    if len(cleaned_question) > MAX_QUESTION_LENGTH:
        raise ValueError(
            f"Your question is too long. "
            f"Please keep it under "
            f"{MAX_QUESTION_LENGTH} characters."
        )

    return cleaned_question


def get_safe_filename(filename):
    """
    Remove directory information from an uploaded filename.
    """

    if not isinstance(filename, str):
        raise TypeError(
            "Filename must be text."
        )

    safe_name = Path(filename).name.strip()

    if not safe_name:
        raise ValueError(
            "The uploaded file must have a filename."
        )

    return safe_name


def validate_file_type(filename):
    """
    Confirm that the uploaded document type is supported.
    """

    safe_name = get_safe_filename(
        filename
    )

    extension = Path(
        safe_name
    ).suffix.lower()

    if not extension:
        raise ValueError(
            "The uploaded file must have a file extension."
        )

    if extension not in SUPPORTED_FILE_TYPES:
        supported = ", ".join(
            sorted(SUPPORTED_FILE_TYPES)
        )

        raise ValueError(
            f"Unsupported file type. "
            f"Supported types are: {supported}"
        )

    return extension


def validate_file_size(
    file_bytes,
    max_size_mb=MAX_UPLOAD_SIZE_MB,
):
    """
    Confirm that an uploaded file is not empty
    and does not exceed the size limit.
    """

    if not isinstance(
        file_bytes,
        (bytes, bytearray),
    ):
        raise TypeError(
            "Uploaded file content must be bytes."
        )

    file_size = len(
        file_bytes
    )

    if file_size == 0:
        raise ValueError(
            "The uploaded file is empty."
        )

    max_size_bytes = (
        max_size_mb
        * 1024
        * 1024
    )

    if file_size > max_size_bytes:
        raise ValueError(
            f"The uploaded file is too large. "
            f"Maximum size is "
            f"{max_size_mb} MB."
        )

    return file_size


def validate_upload(
    filename,
    file_bytes,
):
    """
    Run all validation checks for an uploaded document.
    """

    safe_name = get_safe_filename(
        filename
    )

    extension = validate_file_type(
        safe_name
    )

    file_size = validate_file_size(
        file_bytes
    )

    return {
        "filename": safe_name,
        "extension": extension,
        "size_bytes": file_size,
    }


def main():
    print(
        "NovaMart Validation Tests"
    )

    print("=" * 50)

    questions = [
        "How long does delivery take?",
        "",
        "   ",
        "A" * (
            MAX_QUESTION_LENGTH + 1
        ),
    ]

    for question in questions:
        try:
            cleaned = validate_question(
                question
            )

            print(
                f"\nValid question: "
                f"{cleaned[:60]}"
            )

        except Exception as error:
            print(
                f"\nRejected question: "
                f"{error}"
            )

    fake_file = (
        b"Example NovaMart policy."
    )

    try:
        result = validate_upload(
            "example_policy.md",
            fake_file,
        )

        print(
            f"\nValid upload: "
            f"{result}"
        )

    except Exception as error:
        print(
            f"\nUpload rejected: "
            f"{error}"
        )


if __name__ == "__main__":
    main()