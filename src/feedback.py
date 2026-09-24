import json
from datetime import datetime, timezone
from pathlib import Path

from config import FEEDBACK_DIR


FEEDBACK_FILE = (
    FEEDBACK_DIR
    / "feedback.jsonl"
)

ALLOWED_FEEDBACK = {
    "helpful",
    "not_helpful",
}


def validate_feedback_value(value):
    """
    Validate the feedback rating.
    """

    if not isinstance(value, str):
        raise TypeError(
            "Feedback value must be text."
        )

    cleaned_value = (
        value.strip().lower()
    )

    if cleaned_value not in ALLOWED_FEEDBACK:
        raise ValueError(
            "Feedback must be either "
            "'helpful' or 'not_helpful'."
        )

    return cleaned_value


def normalize_sources(sources):
    """
    Convert retrieved source information into
    a safe JSON-serializable list.
    """

    if not sources:
        return []

    normalized = []

    for source in sources:
        if isinstance(source, dict):
            normalized.append(
                {
                    "source": source.get(
                        "source",
                        "unknown",
                    ),
                    "category": source.get(
                        "category",
                        "unknown",
                    ),
                }
            )

        elif isinstance(source, str):
            normalized.append(
                {
                    "source": source,
                    "category": "unknown",
                }
            )

    return normalized


def save_feedback(
    question,
    answer,
    sources,
    feedback_value,
):
    """
    Store one feedback record locally.
    """

    if not isinstance(question, str):
        raise TypeError(
            "Question must be text."
        )

    if not isinstance(answer, str):
        raise TypeError(
            "Answer must be text."
        )

    question = question.strip()
    answer = answer.strip()

    if not question:
        raise ValueError(
            "Question cannot be empty."
        )

    if not answer:
        raise ValueError(
            "Answer cannot be empty."
        )

    feedback_value = (
        validate_feedback_value(
            feedback_value
        )
    )

    safe_sources = normalize_sources(
        sources
    )

    FEEDBACK_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    record = {
        "question": question,
        "answer": answer,
        "sources": safe_sources,
        "feedback": feedback_value,
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
    }

    with FEEDBACK_FILE.open(
        "a",
        encoding="utf-8",
    ) as file:
        file.write(
            json.dumps(
                record,
                ensure_ascii=False,
            )
            + "\n"
        )

    return record


def load_feedback():
    """
    Load all stored feedback records.
    """

    if not FEEDBACK_FILE.exists():
        return []

    records = []

    with FEEDBACK_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        for line in file:
            line = line.strip()

            if not line:
                continue

            try:
                records.append(
                    json.loads(line)
                )

            except json.JSONDecodeError:
                continue

    return records


def count_feedback():
    """
    Return feedback totals.
    """

    records = load_feedback()

    helpful = sum(
        1
        for record in records
        if record.get("feedback")
        == "helpful"
    )

    not_helpful = sum(
        1
        for record in records
        if record.get("feedback")
        == "not_helpful"
    )

    return {
        "total": len(records),
        "helpful": helpful,
        "not_helpful": not_helpful,
    }


def main():
    print(
        "NovaMart Feedback Test"
    )

    print("=" * 50)

    test_record = save_feedback(
        question=(
            "How long does a refund take?"
        ),
        answer=(
            "Approved refunds are normally "
            "processed within 5 to 10 "
            "business days."
        ),
        sources=[
            {
                "source": "refund_policy.md",
                "category": "refunds",
            }
        ],
        feedback_value="helpful",
    )

    print(
        "\nSaved feedback:"
    )

    print(
        json.dumps(
            test_record,
            indent=2,
        )
    )

    print(
        "\nFeedback totals:"
    )

    print(
        count_feedback()
    )


if __name__ == "__main__":
    main()