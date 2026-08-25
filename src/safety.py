import re


PROMPT_INJECTION_PATTERNS = [
    r"ignore previous instructions",
    r"ignore all previous",
    r"ignore the instructions above",
    r"disregard.*instructions",
    r"reveal.*system prompt",
    r"show.*hidden prompt",
    r"show.*system prompt",
    r"what (are|is) your (system )?instructions",
    r"print your (instructions|prompt)",
    r"developer message",
    r"internal instructions",
    r"act as (if|though) you (have no|had no) rules",
    r"you are now (in )?developer mode",
    r"jailbreak",
]


SENSITIVE_REQUEST_PATTERNS = [
    r"customer.*email",
    r"customer.*address",
    r"customer.*phone",
    r"risk score",
    r"internal note",
    r"warehouse note",
    r"support tags?",
    r"fraud flag",
    r"internal.*(comment|memo|data)",
]


def contains_pattern(text, patterns):

    text = text.lower()

    return any(
        re.search(pattern, text)
        for pattern in patterns
    )


def check_safety(user_message):

    if contains_pattern(
        user_message,
        PROMPT_INJECTION_PATTERNS
    ):
        return {
            "safe": False,
            "reason": "prompt_injection"
        }

    if contains_pattern(
        user_message,
        SENSITIVE_REQUEST_PATTERNS
    ):
        return {
            "safe": False,
            "reason": "sensitive_information"
        }

    return {
        "safe": True,
        "reason": None
    }
