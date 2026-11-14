# guardrails.py - safety checks around the assistant (no LLM needed, so they are fast to test)

import re

MAX_QUESTION_LENGTH = 300

# Input guardrail: phrases that try to rewrite or steal our instructions
BLOCK_PHRASES = [
    "ignore all", "ignore your", "ignore previous", "disregard",
    "system prompt", "your instructions", "reveal your",
]

# Output guardrail: private data that must never leave the company
PRIVATE_PATTERNS = {
    "CNIC number": r"(?<!\d)\d{5}-\d{7}-\d(?!\d)",
    "phone number": r"(?<!\d)(?:\+92|0)3\d{2}[- ]?\d{7}(?!\d)",
}


def check_input(question):
    """Return a reason if the question must be blocked, otherwise None."""
    if len(question) > MAX_QUESTION_LENGTH:
        return "question too long"
    lowered = question.lower()
    for phrase in BLOCK_PHRASES:
        if phrase in lowered:
            return f"blocked phrase: {phrase}"
    return None


def check_output(answer):
    """Return a reason if the answer contains private data, otherwise None."""
    for name, pattern in PRIVATE_PATTERNS.items():
        if re.search(pattern, answer):
            return f"answer contains a {name}"
    return None