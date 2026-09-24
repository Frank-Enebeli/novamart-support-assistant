import uuid
from pathlib import Path

import streamlit as st

from config import (
    DOCUMENTS_DIR,
    MAX_QUESTION_LENGTH,
    MAX_UPLOAD_SIZE_MB,
)

from src.assistant import (
    MISSING_INFORMATION_RESPONSE,
    answer_customer_question,
)

from src.document_loader import (
    extract_text_from_bytes,
    get_category,
)

from src.feedback import (
    count_feedback,
    save_feedback,
)

from src.ingestion import ingest_document

from src.validation import (
    validate_question,
    validate_upload,
)

from src.vector_store import (
    count_chunks,
    delete_document,
    document_exists,
    get_document_sources,
)


st.set_page_config(
    page_title="NovaMart Support Assistant",
    page_icon="🛍️",
    layout="centered",
)


def initialize_session_state():
    """
    Create session-specific application state.
    """

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = str(
            uuid.uuid4()
        )


def clear_conversation():
    """
    Clear only the current visitor's conversation.
    """

    st.session_state.messages = []

    st.session_state.conversation_id = str(
        uuid.uuid4()
    )


def history_for_model():
    """
    Convert UI message state into the role/content
    format expected by the assistant module.
    """

    history = []

    for message in st.session_state.messages:
        if message["role"] not in {
            "user",
            "assistant",
        }:
            continue

        history.append(
            {
                "role": message["role"],
                "content": message["content"],
            }
        )

    return history


def render_sources(sources):
    """
    Display retrieved source filenames and categories.
    """

    if not sources:
        return

    st.markdown("**Sources / retrieved context:**")

    for source in sources:
        st.markdown(
            f"- `{source['source']}` "
            f"— {source['category']}"
        )


def render_retrieval_details(chunks):
    """
    Display retrieval diagnostics for transparency.
    """

    if not chunks:
        return

    with st.expander(
        "View retrieval details"
    ):
        for index, chunk in enumerate(
            chunks,
            start=1,
        ):
            st.markdown(
                f"**Result {index}**"
            )

            st.write(
                f"Source: {chunk['source']}"
            )

            st.write(
                f"Category: {chunk['category']}"
            )

            st.write(
                f"Chunk: {chunk['chunk_number']}"
            )

            st.write(
                f"Distance: "
                f"{chunk['distance']:.4f}"
            )

            st.write(
                chunk["text"]
            )

            st.divider()


def record_feedback(
    message_index,
    feedback_value,
):
    """
    Save feedback for one assistant response.
    """

    message = (
        st.session_state.messages[
            message_index
        ]
    )

    save_feedback(
        question=message["question"],
        answer=message["content"],
        sources=message.get(
            "sources",
            [],
        ),
        feedback_value=feedback_value,
    )

    st.session_state.messages[
        message_index
    ]["feedback"] = feedback_value


def render_feedback_buttons(
    message,
    message_index,
):
    """
    Display feedback controls beneath an answer.
    """

    existing_feedback = message.get(
        "feedback"
    )

    if existing_feedback:
        display_value = (
            "Helpful"
            if existing_feedback == "helpful"
            else "Not helpful"
        )

        st.caption(
            f"Feedback recorded: "
            f"{display_value}"
        )

        return

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "👍 Helpful",
            key=(
                f"helpful_"
                f"{st.session_state.conversation_id}_"
                f"{message_index}"
            ),
            use_container_width=True,
        ):
            record_feedback(
                message_index,
                "helpful",
            )

            st.rerun()

    with col2:
        if st.button(
            "👎 Not helpful",
            key=(
                f"not_helpful_"
                f"{st.session_state.conversation_id}_"
                f"{message_index}"
            ),
            use_container_width=True,
        ):
            record_feedback(
                message_index,
                "not_helpful",
            )

            st.rerun()


def render_existing_messages():
    """
    Re-render the current conversation after each
    Streamlit rerun.
    """

    for index, message in enumerate(
        st.session_state.messages
    ):
        with st.chat_message(
            message["role"]
        ):
            st.markdown(
                message["content"]
            )

            if (
                message["role"]
                == "assistant"
            ):
                if message.get(
                    "show_sources",
                    False,
                ):
                    render_sources(
                        message.get(
                            "sources",
                            [],
                        )
                    )

                render_retrieval_details(
                    message.get(
                        "retrieved_chunks",
                        [],
                    )
                )

                render_feedback_buttons(
                    message,
                    index,
                )


def customer_support_page():
    """
    Main customer-facing chat page.
    """

    st.title(
        "🛍️ NovaMart Support Assistant"
    )

    st.write(
        "Ask about NovaMart delivery, returns, "
        "refunds, payments, warranties, orders, "
        "accounts, or customer support."
    )

    st.info(
        "This assistant can explain NovaMart policies, "
        "but it cannot access private accounts, track "
        "individual orders, issue refunds, or perform "
        "account actions."
    )

    if st.button(
        "🗑️ Clear Conversation"
    ):
        clear_conversation()
        st.rerun()

    render_existing_messages()

    question = st.chat_input(
        "Ask NovaMart a question...",
        max_chars=MAX_QUESTION_LENGTH,
    )

    if question is None:
        return

    try:
        cleaned_question = (
            validate_question(
                question
            )
        )

    except (
        ValueError,
        TypeError,
    ) as error:
        st.error(
            str(error)
        )
        return

    # Capture history BEFORE adding the
    # current customer message.
    recent_history = history_for_model()

    st.session_state.messages.append(
        {
            "role": "user",
            "content": cleaned_question,
        }
    )

    with st.chat_message("user"):
        st.markdown(
            cleaned_question
        )

    with st.chat_message("assistant"):
        with st.spinner(
            "Searching NovaMart support documents..."
        ):
            result = (
                answer_customer_question(
                    cleaned_question,
                    history=recent_history,
                )
            )

        answer = result["answer"]

        st.markdown(
            answer
        )

        show_sources = (
            result["status"] == "success"
            and answer
            != MISSING_INFORMATION_RESPONSE
        )

        if show_sources:
            render_sources(
                result["sources"]
            )

        render_retrieval_details(
            result["retrieved_chunks"]
        )

        if (
            result["status"]
            == "escalated"
        ):
            st.caption(
                "This request was routed to "
                "human-support guidance."
            )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "question": cleaned_question,
            "sources": result["sources"],
            "retrieved_chunks": result[
                "retrieved_chunks"
            ],
            "status": result["status"],
            "show_sources": show_sources,
            "feedback": None,
        }
    )

    st.rerun()


def process_uploaded_document(
    uploaded_file,
    replace_existing=False,
):
    """
    Validate, extract, ingest, and save an uploaded
    NovaMart document.
    """

    file_bytes = (
        uploaded_file.getvalue()
    )

    validation = validate_upload(
        uploaded_file.name,
        file_bytes,
    )

    filename = validation[
        "filename"
    ]

    text = extract_text_from_bytes(
        filename,
        file_bytes,
    )

    document = {
        "source": filename,
        "category": get_category(
            filename
        ),
        "text": text,
    }

    file_path = (
        DOCUMENTS_DIR
        / filename
    )

    already_exists = (
        document_exists(filename)
        or file_path.exists()
    )

    if (
        already_exists
        and not replace_existing
    ):
        raise ValueError(
            "A document with this filename "
            "already exists. Enable the "
            "replace/re-index option if you "
            "intend to update it."
        )

    result = ingest_document(
        document,
        force=replace_existing,
    )

    DOCUMENTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_path.write_bytes(
        file_bytes
    )

    return result


def admin_page():
    """
    Simple administrator knowledge-base page.
    """

    st.title(
        "⚙️ NovaMart Knowledge Base Admin"
    )

    st.warning(
        "This project admin area is separated from "
        "the customer interface but does not include "
        "production-grade authentication."
    )

    st.subheader(
        "Knowledge-base status"
    )

    sources = (
        get_document_sources()
    )

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Indexed documents",
            len(sources),
        )

    with col2:
        st.metric(
            "Stored chunks",
            count_chunks(),
        )

    if sources:
        st.markdown(
            "**Existing documents:**"
        )

        for source in sources:
            st.markdown(
                f"- `{source}`"
            )

    else:
        st.info(
            "No documents are currently indexed."
        )

    st.divider()

    st.subheader(
        "Upload a knowledge-base document"
    )

    uploaded_file = st.file_uploader(
        "Upload Markdown, TXT, or PDF",
        type=[
            "md",
            "txt",
            "pdf",
        ],
        max_upload_size=(
            MAX_UPLOAD_SIZE_MB
        ),
        help=(
            f"Maximum file size: "
            f"{MAX_UPLOAD_SIZE_MB} MB."
        ),
    )

    replace_existing = st.checkbox(
        "Replace and re-index the document "
        "if the filename already exists"
    )

    if st.button(
        "Add document",
        type="primary",
        disabled=(
            uploaded_file is None
        ),
    ):
        try:
            with st.spinner(
                "Validating and indexing document..."
            ):
                result = (
                    process_uploaded_document(
                        uploaded_file,
                        replace_existing=(
                            replace_existing
                        ),
                    )
                )

            st.success(
                f"{result['source']} was "
                f"{result['status']} successfully "
                f"with {result['chunks']} chunks."
            )

        except (
            ValueError,
            TypeError,
        ) as error:
            st.error(
                str(error)
            )

        except Exception:
            st.error(
                "The document could not be processed. "
                "Please verify the file and try again."
            )

    st.divider()

    st.subheader(
        "Remove a document"
    )

    current_sources = (
        get_document_sources()
    )

    if not current_sources:
        st.info(
            "There are no indexed documents to remove."
        )

    else:
        selected_source = st.selectbox(
            "Choose a document",
            current_sources,
        )

        confirm_delete = st.checkbox(
            "I understand this will remove "
            "the document from the knowledge base."
        )

        if st.button(
            "Delete selected document",
            disabled=not confirm_delete,
        ):
            try:
                delete_document(
                    selected_source
                )

                file_path = (
                    DOCUMENTS_DIR
                    / Path(
                        selected_source
                    ).name
                )

                if file_path.exists():
                    file_path.unlink()

                st.success(
                    f"{selected_source} "
                    "was removed."
                )

                st.rerun()

            except Exception:
                st.error(
                    "The document could not be removed."
                )

    st.divider()

    st.subheader(
        "Feedback summary"
    )

    feedback_totals = (
        count_feedback()
    )

    feedback_col1, feedback_col2, feedback_col3 = (
        st.columns(3)
    )

    with feedback_col1:
        st.metric(
            "Total",
            feedback_totals["total"],
        )

    with feedback_col2:
        st.metric(
            "Helpful",
            feedback_totals["helpful"],
        )

    with feedback_col3:
        st.metric(
            "Not helpful",
            feedback_totals[
                "not_helpful"
            ],
        )


def main():
    initialize_session_state()

    st.sidebar.title(
        "NovaMart"
    )

    page = st.sidebar.radio(
        "Choose area",
        [
            "Customer Support",
            "Admin",
        ],
    )

    if page == "Customer Support":
        customer_support_page()

    else:
        admin_page()


if __name__ == "__main__":
    main()