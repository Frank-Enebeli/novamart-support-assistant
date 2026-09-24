import pytest
import json

from src import feedback


def test_feedback_is_stored_correctly(
    tmp_path,
    monkeypatch,
):
    test_file = (
        tmp_path
        / "feedback.jsonl"
    )

    monkeypatch.setattr(
        feedback,
        "FEEDBACK_DIR",
        tmp_path,
    )

    monkeypatch.setattr(
        feedback,
        "FEEDBACK_FILE",
        test_file,
    )

    record = feedback.save_feedback(
        question=(
            "How long does a refund take?"
        ),
        answer=(
            "Approved refunds normally take "
            "5 to 10 business days."
        ),
        sources=[
            {
                "source": "refund_policy.md",
                "category": "refunds",
            }
        ],
        feedback_value="helpful",
    )

    assert test_file.exists()

    assert (
        record["feedback"]
        == "helpful"
    )

    assert (
        record["question"]
        == "How long does a refund take?"
    )

    assert (
        record["sources"][0]["source"]
        == "refund_policy.md"
    )

    stored_lines = (
        test_file.read_text(
            encoding="utf-8"
        )
        .strip()
        .splitlines()
    )

    assert len(
        stored_lines
    ) == 1

    stored_record = json.loads(
        stored_lines[0]
    )

    assert (
        stored_record["feedback"]
        == "helpful"
    )

    assert (
        stored_record["sources"][0][
            "category"
        ]
        == "refunds"
    )


def test_invalid_feedback_value_is_rejected(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        feedback,
        "FEEDBACK_DIR",
        tmp_path,
    )

    monkeypatch.setattr(
        feedback,
        "FEEDBACK_FILE",
        (
            tmp_path
            / "feedback.jsonl"
        ),
    )

    with pytest.raises(
        ValueError
    ):
        feedback.save_feedback(
            question="Question",
            answer="Answer",
            sources=[],
            feedback_value="maybe",
        )