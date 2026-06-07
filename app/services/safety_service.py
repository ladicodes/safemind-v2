import re


CRISIS_PATTERNS = (
    r"\bkill myself\b",
    r"\bend my life\b",
    r"\bsuicid(?:e|al)\b",
    r"\bself[- ]?harm\b",
    r"\bhurt myself\b",
    r"\bdon't want to live\b",
    r"\bdo not want to live\b",
    r"\bimmediate danger\b",
)

CRISIS_MESSAGE = (
    "Your safety matters. If you may act on these thoughts or are in immediate "
    "danger, contact local emergency services now. Please also reach out to a "
    "trusted person or qualified mental health professional and avoid being alone. "
    "SafeSpace is not a replacement for therapy or emergency care."
)

DISCLAIMER = (
    "SafeSpace offers supportive reflection, not diagnosis or treatment, and is "
    "not a replacement for therapy or emergency care."
)


def contains_crisis_language(text: str) -> bool:
    lowered = text.lower()
    return any(re.search(pattern, lowered) for pattern in CRISIS_PATTERNS)
