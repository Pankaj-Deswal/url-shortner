"""Base62 encoding (0-9, a-z, A-Z) for short codes."""

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
BASE = len(ALPHABET)


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
