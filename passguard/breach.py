"""Check passwords against the Have I Been Pwned database using k-anonymity.

Only the first 5 characters of the password's SHA-1 hash leave this machine.
The API returns every hash suffix sharing that prefix, and the match is done locally.
See: https://haveibeenpwned.com/API/v3#PwnedPasswords
"""

import hashlib
import urllib.request

API_URL = "https://api.pwnedpasswords.com/range/"


def sha1_hex(password: str) -> str:
    return hashlib.sha1(password.encode("utf-8")).hexdigest().upper()


def split_hash(full_hash: str) -> tuple[str, str]:
    return full_hash[:5], full_hash[5:]


def parse_range_response(body: str, suffix: str) -> int:
    """Find how many times `suffix` appears in a HIBP range response."""
    for line in body.splitlines():
        candidate, _, count = line.partition(":")
        if candidate.strip().upper() == suffix:
            return int(count.strip())
    return 0


def pwned_count(password: str, timeout: float = 10) -> int:
    """Return how many times the password appeared in known data breaches."""
    prefix, suffix = split_hash(sha1_hex(password))
    request = urllib.request.Request(
        API_URL + prefix,
        headers={
            "User-Agent": "PassGuard-password-checker",
            # Padding hides the real response size from network observers.
            "Add-Padding": "true",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read().decode("utf-8")
    return parse_range_response(body, suffix)
