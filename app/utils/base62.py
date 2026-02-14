"""Base62 encoding (0-9, a-z, A-Z) and random short code generation."""

import secrets

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
BASE = len(ALPHABET)


def generate_random_base62(length: int) -> str:
    """Generate a random Base62 string of given length (cryptographically strong)."""
    return "".join(secrets.choice(ALPHABET) for _ in range(length))


def encode(num: int) -> str:
    """Encode a non-negative integer to a Base62 string."""
    if num == 0:
        return ALPHABET[0]
    chars: list[str] = []
    while num:
        num, rem = divmod(num, BASE)
        chars.append(ALPHABET[rem])
    return "".join(reversed(chars))


def decode(s: str) -> int:
    """Decode a Base62 string to a non-negative integer."""
    num = 0
    for char in s:
        idx = ALPHABET.index(char)
        num = num * BASE + idx
    return num
