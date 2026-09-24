import json
from datetime import datetime, timezone
from pathlib import Path

from src.assistant import (
    answer_customer_question,
)


EVALUATION_DIR = Path(__file__).parent

QUESTIONS_FILE = (
    EVALUATION_DIR
    / "questions.json"
)

RESULTS_JSON_FILE = (
    EVALUATION_DIR
    / "results.json"
)

RESULTS_MD_FILE = (
    EVALUATION_DIR
    / "results.md"
)


def load_questions():
    with QUESTIONS_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def extract_actual_sources(result):
    """
    Return unique retrieved source names.
    """

    sources = []

    for source in result.get(
        "sources",
        [],
    ):
        filename = source.get(
            "source"
        )

        if (
            filename
            and filename not in sources
        ):
            sources.append(
                filename
            )

    return sources


def ask_for_correctness():
    while True:
        value = input(
            "\nWas this result correct? "
            "[y/n/s = skip]: "
        ).strip().lower()

        if value == "y":
            return True

        if value == "n":
            return False

        if value == "s":
            return None

        print(
            "Please enter y, n, or s."
        )


def ask_for_notes():
    return input(
        "Optional notes: "
    ).strip()


def run_evaluation():
    questions = load_questions()

    results = []

    print(
        "NovaMart 20-Question Evaluation"
    )

    print("=" * 70)

    for item in questions:
        print(
            "\n"
            + "=" * 70
        )

        print(
            f"Question {item['id']} "
            f"({item['type']})"
        )

        print("=" * 70)

        print(
            f"\nQuestion:\n"
            f"{item['question']}"
        )

        print(
            f"\nExpected behaviour:\n"
            f"{item['expected_behavior']}"
        )

        print(
            "\nExpected sources:"
        )

        if item[
            "expected_sources"
        ]:
            for source in item[
                "expected_sources"
            ]:
                print(
                    f"- {source}"
                )

        else:
            print(
                "- No specific supporting source"
            )

        # Each evaluation question is isolated.
        # Conversation history is deliberately empty.
        result = (
            answer_customer_question(
                item["question"],
                history=[],
            )
        )

        actual_sources = (
            extract_actual_sources(
                result
            )
        )

        print(
            f"\nStatus: "
            f"{result['status']}"
        )

        print(
            f"\nAssistant answer:\n"
            f"{result['answer']}"
        )

        print(
            "\nActual retrieved sources:"
        )

        if actual_sources:
            for source in actual_sources:
                print(
                    f"- {source}"
                )

        else:
            print(
                "- None"
            )

        retrieved_chunks = []

        for chunk in result.get(
            "retrieved_chunks",
            [],
        ):
            retrieved_chunks.append(
                {
                    "source": chunk[
                        "source"
                    ],
                    "category": chunk[
                        "category"
                    ],
                    "chunk_number": chunk[
                        "chunk_number"
                    ],
                    "distance": chunk[
                        "distance"
                    ],
                }
            )

        correct = (
            ask_for_correctness()
        )

        notes = ask_for_notes()

        results.append(
            {
                "id": item["id"],
                "type": item["type"],
                "question": item[
                    "question"
                ],
                "expected_behavior": item[
                    "expected_behavior"
                ],
                "expected_sources": item[
                    "expected_sources"
                ],
                "actual_answer": result[
                    "answer"
                ],
                "actual_sources": (
                    actual_sources
                ),
                "retrieved_chunks": (
                    retrieved_chunks
                ),
                "status": result[
                    "status"
                ],
                "correct": correct,
                "notes": notes,
            }
        )

    return results


def save_json_results(results):
    payload = {
        "evaluated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "results": results,
    }

    with RESULTS_JSON_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            payload,
            file,
            indent=2,
            ensure_ascii=False,
        )


def yes_no(value):
    if value is True:
        return "Yes"

    if value is False:
        return "No"

    return "Not scored"


def markdown_escape(text):
    return str(text).replace(
        "|",
        "\\|",
    ).replace(
        "\n",
        " ",
    )


def save_markdown_results(
    results,
):
    scored = [
        result
        for result in results
        if result["correct"]
        is not None
    ]

    correct_count = sum(
        1
        for result in scored
        if result["correct"]
        is True
    )

    lines = [
        "# NovaMart Evaluation Results",
        "",
        (
            f"Questions evaluated: "
            f"{len(results)}"
        ),
        (
            f"Questions scored: "
            f"{len(scored)}"
        ),
        (
            f"Correct: "
            f"{correct_count}"
        ),
        "",
    ]

    if scored:
        accuracy = (
            correct_count
            / len(scored)
            * 100
        )

        lines.append(
            f"Accuracy: {accuracy:.1f}%"
        )

        lines.append("")

    lines.extend(
        [
            "| # | Type | Question | Expected source | Actual source | Correct? |",
            "|---|---|---|---|---|---|",
        ]
    )

    for result in results:
        expected = (
            ", ".join(
                result[
                    "expected_sources"
                ]
            )
            or "None / clarification"
        )

        actual = (
            ", ".join(
                result[
                    "actual_sources"
                ]
            )
            or "None"
        )

        lines.append(
            "| "
            f"{result['id']} | "
            f"{markdown_escape(result['type'])} | "
            f"{markdown_escape(result['question'])} | "
            f"{markdown_escape(expected)} | "
            f"{markdown_escape(actual)} | "
            f"{yes_no(result['correct'])} |"
        )

    lines.append(
        "\n## Detailed Results\n"
    )

    for result in results:
        lines.extend(
            [
                (
                    f"### Question "
                    f"{result['id']}"
                ),
                "",
                (
                    f"**Type:** "
                    f"{result['type']}"
                ),
                "",
                (
                    f"**Question:** "
                    f"{result['question']}"
                ),
                "",
                (
                    "**Expected behaviour:** "
                    + result[
                        "expected_behavior"
                    ]
                ),
                "",
                (
                    "**Expected sources:** "
                    + (
                        ", ".join(
                            result[
                                "expected_sources"
                            ]
                        )
                        or "None"
                    )
                ),
                "",
                (
                    "**Actual sources:** "
                    + (
                        ", ".join(
                            result[
                                "actual_sources"
                            ]
                        )
                        or "None"
                    )
                ),
                "",
                (
                    f"**Status:** "
                    f"{result['status']}"
                ),
                "",
                "**Actual answer:**",
                "",
                result[
                    "actual_answer"
                ],
                "",
                (
                    f"**Correct:** "
                    f"{yes_no(result['correct'])}"
                ),
                "",
                (
                    f"**Notes:** "
                    f"{result['notes'] or '-'}"
                ),
                "",
            ]
        )

    RESULTS_MD_FILE.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def main():
    results = run_evaluation()

    save_json_results(
        results
    )

    save_markdown_results(
        results
    )

    print(
        "\n"
        + "=" * 70
    )

    print(
        "Evaluation complete."
    )

    print(
        f"JSON results: "
        f"{RESULTS_JSON_FILE}"
    )

    print(
        f"Markdown results: "
        f"{RESULTS_MD_FILE}"
    )


if __name__ == "__main__":
    main()