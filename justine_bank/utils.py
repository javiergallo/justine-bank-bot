import re

from justine_bank.constants import USERNAME_REGEX


def clean_username(username: str) -> str:
    return (username[1:] if username and username[0] == "@" else username).lower()
