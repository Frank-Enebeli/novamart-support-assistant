import pytest

from config import MAX_QUESTION_LENGTH

from src.validation import (
    validate_question,
    validate_upload,
)


def test_empty_question_is_rejected():
    with pytest.raises(
        ValueError,
        match="Please enter a question",
    ):
        validate_question("")


def test_whitespace_question_is_rejected():
    with pytest.raises(
        ValueError,
        match="Please enter a question",
    ):
        validate_question("     ")


def test_oversized_question_is_rejected():
    question = "A" * (
        MAX_QUESTION_LENGTH + 1
    )

    with pytest.raises(
        ValueError,
        match="too long",
    ):
        validate_question(
            question
        )


def test_valid_question_is_cleaned():
    result = validate_question(
        "   How long does delivery take?   "
    )

    assert result == (
        "How long does delivery take?"
    )


def test_unsupported_document_type_is_rejected():
    with pytest.raises(
        ValueError,
        match="Unsupported file type",
    ):
        validate_upload(
            "malware.exe",
            b"fake content",
        )


def test_empty_upload_is_rejected():
    with pytest.raises(
        ValueError,
        match="empty",
    ):
        validate_upload(
            "policy.md",
            b"",
        )


def test_valid_markdown_upload_is_accepted():
    result = validate_upload(
        "refund_policy.md",
        b"# Refund Policy",
    )

    assert (
        result["filename"]
        == "refund_policy.md"
    )

    assert (
        result["extension"]
        == ".md"
    ) 