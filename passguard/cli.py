"""Command line interface for PassGuard."""

import argparse
import getpass
import sys
import urllib.error

from .breach import pwned_count
from .strength import analyze

COLORS = ["\033[91m", "\033[91m", "\033[93m", "\033[92m", "\033[92m"]
RESET = "\033[0m"
BOLD = "\033[1m"


def strength_bar(score: int) -> str:
    filled = score + 1
    return COLORS[score] + "#" * (filled * 4) + RESET + "-" * ((5 - filled) * 4)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="passguard",
        description="Check password strength and whether it appeared in known data breaches.",
    )
    parser.add_argument("--offline", action="store_true",
                        help="skip the Have I Been Pwned breach check")
    args = parser.parse_args(argv)

    # getpass hides input so the password never shows on screen or in shell history.
    password = getpass.getpass("Enter password to check (input hidden): ")
    if not password:
        print("No password entered.")
        return 1

    result = analyze(password)
    print()
    print(f"{BOLD}Strength:{RESET}   [{strength_bar(result.score)}] {result.label}")
    print(f"{BOLD}Length:{RESET}     {result.length} characters")
    print(f"{BOLD}Entropy:{RESET}    ~{result.entropy_bits} bits (charset size {result.charset_size})")
    print(f"{BOLD}Crack time:{RESET} {result.crack_time} (offline attack, 10B guesses/sec)")

    exit_code = 0
    if not args.offline:
        try:
            count = pwned_count(password)
        except (urllib.error.URLError, TimeoutError) as exc:
            print(f"{BOLD}Breaches:{RESET}   could not reach Have I Been Pwned ({exc})")
        else:
            if count:
                print(f"{BOLD}Breaches:{RESET}   {COLORS[0]}FOUND {count:,} times in data breaches - do not use it!{RESET}")
                exit_code = 2
            else:
                print(f"{BOLD}Breaches:{RESET}   {COLORS[4]}not found in known breaches{RESET}")

    if result.warnings:
        print(f"\n{BOLD}Warnings:{RESET}")
        for warning in result.warnings:
            print(f"  ! {warning}")
    if result.suggestions:
        print(f"\n{BOLD}Suggestions:{RESET}")
        for suggestion in result.suggestions:
            print(f"  - {suggestion}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
