"""Password strength analysis based on entropy and common weak patterns."""

import math
import string
from dataclasses import dataclass, field

# A small sample of the most used passwords. Real tools use lists with millions of entries.
COMMON_PASSWORDS = {
    "123456", "password", "123456789", "12345678", "12345", "qwerty", "abc123",
    "football", "1234567", "monkey", "111111", "letmein", "1234", "1234567890",
    "dragon", "baseball", "sunshine", "iloveyou", "trustno1", "princess",
    "admin", "welcome", "master", "login", "passw0rd", "starwars", "shadow",
    "superman", "qwerty123", "hello", "freedom", "whatever", "123123", "654321",
    "michael", "football1", "charlie", "aa123456", "donald", "qwertyuiop",
}

KEYBOARD_ROWS = ("qwertyuiop", "asdfghjkl", "zxcvbnm", "1234567890")

# Leetspeak substitutions, used to catch variants like "p@ssw0rd".
LEET_MAP = str.maketrans({"@": "a", "4": "a", "3": "e", "1": "i", "!": "i",
                          "0": "o", "$": "s", "5": "s", "7": "t"})

# Assumed attacker speed: 10 billion guesses/sec (a GPU rig against a fast hash like MD5).
GUESSES_PER_SECOND = 1e10

LABELS = ("Very weak", "Weak", "Fair", "Strong", "Very strong")


@dataclass
class StrengthResult:
    length: int
    charset_size: int
    entropy_bits: float
    score: int  # 0 (very weak) .. 4 (very strong)
    label: str
    crack_time: str
    warnings: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)


def charset_size(password: str) -> int:
    """Size of the character pool an attacker would have to search."""
    size = 0
    if any(c in string.ascii_lowercase for c in password):
        size += 26
    if any(c in string.ascii_uppercase for c in password):
        size += 26
    if any(c in string.digits for c in password):
        size += 10
    if any(c in string.punctuation or c == " " for c in password):
        size += 33
    if any(ord(c) > 127 for c in password):
        size += 100
    return size


def is_common(password: str) -> bool:
    lowered = password.lower()
    stripped = lowered.rstrip(string.digits + string.punctuation)
    return (lowered in COMMON_PASSWORDS
            or lowered.translate(LEET_MAP) in COMMON_PASSWORDS
            or (len(stripped) >= 4 and stripped in COMMON_PASSWORDS))


def has_keyboard_pattern(password: str, min_len: int = 4) -> bool:
    lowered = password.lower()
    for row in KEYBOARD_ROWS:
        for seq in (row, row[::-1]):
            for i in range(len(seq) - min_len + 1):
                if seq[i:i + min_len] in lowered:
                    return True
    return False


def effective_length(password: str) -> float:
    """Length where repeated or sequential characters (aaa, abc, 321) count less."""
    if not password:
        return 0.0
    length = 1.0
    for prev, cur in zip(password, password[1:]):
        if abs(ord(cur) - ord(prev)) <= 1:
            length += 0.25
        else:
            length += 1
    return length


def format_duration(seconds: float) -> str:
    if seconds < 1:
        return "instantly"
    units = [("century", 3.15576e9), ("year", 3.15576e7), ("month", 2.6298e6),
             ("day", 86400), ("hour", 3600), ("minute", 60), ("second", 1)]
    for name, size in units:
        if seconds >= size:
            value = seconds / size
            if name == "century" and value >= 1e6:
                return "millions of centuries"
            value = int(value)
            plural = "centuries" if name == "century" else name + "s"
            return f"{value} {name if value == 1 else plural}"
    return "instantly"


def analyze(password: str) -> StrengthResult:
    warnings: list[str] = []
    suggestions: list[str] = []

    pool = charset_size(password)
    entropy = effective_length(password) * math.log2(pool) if pool else 0.0

    if is_common(password):
        warnings.append("This is one of the most common passwords.")
        entropy = min(entropy, 10.0)
    if has_keyboard_pattern(password):
        warnings.append("Contains a keyboard pattern (e.g. 'qwerty', '1234').")
        entropy *= 0.7
    if effective_length(password) < len(password) * 0.75:
        warnings.append("Contains repeated or sequential characters (e.g. 'aaa', 'abc').")

    if len(password) < 12:
        suggestions.append("Use at least 12 characters - length matters most.")
    if not any(c.isupper() for c in password) or not any(c.islower() for c in password):
        suggestions.append("Mix uppercase and lowercase letters.")
    if not any(c.isdigit() for c in password):
        suggestions.append("Add some numbers.")
    if not any(c in string.punctuation for c in password):
        suggestions.append("Add symbols like ! ? # %.")
    if warnings:
        suggestions.append("Try a passphrase of 4+ random words, e.g. 'violet-tractor-lamp-river'.")

    if entropy < 28:
        score = 0
    elif entropy < 36:
        score = 1
    elif entropy < 60:
        score = 2
    elif entropy < 80:
        score = 3
    else:
        score = 4

    # On average an attacker finds the password after searching half the space.
    seconds = (2 ** entropy) / 2 / GUESSES_PER_SECOND

    return StrengthResult(
        length=len(password),
        charset_size=pool,
        entropy_bits=round(entropy, 1),
        score=score,
        label=LABELS[score],
        crack_time=format_duration(seconds),
        warnings=warnings,
        suggestions=suggestions,
    )
