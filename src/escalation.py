import re


GENERAL_SUPPORT_EMAIL = (
    "support@novamart.example"
)

COMPLAINTS_EMAIL = (
    "complaints@novamart.example"
)

SECURITY_EMAIL = (
    "security@novamart.example"
)

SUPPORT_PHONE = (
    "+234 700 000 6627"
)


ESCALATION_PATTERNS = {
    "human_request": [
        r"\bspeak (?:to|with) (?:a )?(?:person|human|agent|representative)\b",
        r"\btalk (?:to|with) (?:a )?(?:person|human|agent|representative)\b",
        r"\bhuman support\b",
        r"\bcustomer service agent\b",
        r"\breal person\b",
    ],

    "complaint": [
        r"\bcomplain\b",
        r"\bcomplaint\b",
        r"\bformal complaint\b",
        r"\bunacceptable\b",
        r"\bescalate this\b",
    ],

    "payment_dispute": [
        r"\bcharged twice\b",
        r"\bduplicate charge\b",
        r"\bpayment dispute\b",
        r"\bunknown charge\b",
        r"\bunauthori[sz]ed charge\b",
        r"\bpayment fraud\b",
        r"\bcard charged\b",
    ],

    "account_security": [
        r"\bhacked\b",
        r"\baccount takeover\b",
        r"\bsomeone accessed my account\b",
        r"\bstolen account\b",
        r"\bsecurity issue\b",
        r"\bcompromised account\b",
        r"\bunauthori[sz]ed access\b",
    ],

    "private_order": [
        r"\bwhere is my order\b",
        r"\btrack my order\b",
        r"\bcheck my order\b",
        r"\bmy order status\b",
        r"\bhas my order shipped\b",
        r"\bhas my order been dispatched\b",
    ],

    "action_request": [
        r"\bcancel my order\b",
        r"\bissue (?:me )?a refund\b",
        r"\brefund me\b",
        r"\breset my password\b",
        r"\bchange my password\b",
        r"\bunlock my account\b",
        r"\bchange my email\b",
        r"\bconfirm my payment\b",
        r"\bcheck my payment\b",
    ],
}


def normalize_text(text):
    """
    Normalize customer text before pattern matching.
    """

    if not isinstance(text, str):
        return ""

    return " ".join(
        text.lower().split()
    )


def detect_escalation(question):
    """
    Detect whether a customer question clearly
    requires human support.

    Returns the escalation reason or None.
    """

    text = normalize_text(
        question
    )

    if not text:
        return None

    for reason, patterns in (
        ESCALATION_PATTERNS.items()
    ):
        for pattern in patterns:
            if re.search(
                pattern,
                text,
                flags=re.IGNORECASE,
            ):
                return reason

    return None


def build_escalation_response(reason):
    """
    Create a safe response for an escalation situation.
    """

    if reason == "human_request":
        return (
            "I can help explain NovaMart's published "
            "support information, but I can also direct "
            "you to a human representative. Contact "
            f"{GENERAL_SUPPORT_EMAIL} or call "
            f"{SUPPORT_PHONE} during support hours."
        )

    if reason == "complaint":
        return (
            "I'm sorry you're having an issue. Formal "
            "complaints need to be handled by NovaMart's "
            "human support team. You can email "
            f"{COMPLAINTS_EMAIL}. Please include your "
            "order number if it is relevant."
        )

    if reason == "payment_dispute":
        return (
            "This payment issue requires a human review "
            "because I cannot access transaction records "
            "or verify individual payments. Please contact "
            f"{GENERAL_SUPPORT_EMAIL} or call "
            f"{SUPPORT_PHONE}. Do not send passwords, "
            "PINs, full card numbers, or one-time codes."
        )

    if reason == "account_security":
        return (
            "This appears to involve account security and "
            "should be handled by a human representative. "
            f"Please contact {SECURITY_EMAIL}. If you can "
            "still access your account, change your "
            "password immediately. Do not share passwords "
            "or verification codes in chat."
        )

    if reason == "private_order":
        return (
            "I cannot access live order records or check "
            "the status of a specific customer's order. "
            "Please contact NovaMart support at "
            f"{GENERAL_SUPPORT_EMAIL} or "
            f"{SUPPORT_PHONE} with your order number."
        )

    if reason == "action_request":
        return (
            "I can explain NovaMart's policies, but I "
            "cannot perform actions in NovaMart's private "
            "systems. I cannot cancel orders, issue "
            "refunds, change account details, reset "
            "passwords, or confirm individual payments. "
            "Please contact "
            f"{GENERAL_SUPPORT_EMAIL} or call "
            f"{SUPPORT_PHONE} for assistance."
        )

    return (
        "This request requires assistance from a NovaMart "
        "customer-support representative. Please contact "
        f"{GENERAL_SUPPORT_EMAIL}."
    )


def check_escalation(question):
    """
    Return escalation information for a customer question.
    """

    reason = detect_escalation(
        question
    )

    if reason is None:
        return {
            "required": False,
            "reason": None,
            "response": None,
        }

    return {
        "required": True,
        "reason": reason,
        "response": build_escalation_response(
            reason
        ),
    }


def main():
    test_questions = [
        "Where is my order NM-45882?",
        "Please cancel my order for me.",
        "I was charged twice.",
        "I think someone hacked my account.",
        "I want to speak with a person.",
        "How long does standard delivery take?",
    ]

    for question in test_questions:
        result = check_escalation(
            question
        )

        print(
            f"\nQuestion: {question}"
        )

        print(
            f"Escalation required: "
            f"{result['required']}"
        )

        print(
            f"Reason: {result['reason']}"
        )

        if result["response"]:
            print(
                f"Response: "
                f"{result['response']}"
            )


if __name__ == "__main__":
    main()