"""Deterministic numeric representations; no pretrained or binary HF model is used."""
from __future__ import annotations
import hashlib
import math
import re
from typing import Iterable

TOKEN_RE = re.compile(r"[\wáéíóúüñ]+", re.IGNORECASE)

def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())

def vector_for(text: str, dimensions: int = 64) -> list[float]:
    """Map text to a reproducible signed hash vector, then normalize it."""
    values = [0.0] * dimensions
    tokens = tokenize(text) or [text.lower()]
    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=32).digest()
        for i in range(dimensions):
            byte = digest[i % len(digest)]
            sign = -1.0 if digest[(i + 7) % len(digest)] & 1 else 1.0
            values[i] += sign * (byte / 255.0)
    norm = math.sqrt(sum(x * x for x in values)) or 1.0
    return [x / norm for x in values]

def cosine(a: Iterable[float], b: Iterable[float]) -> float:
    aa, bb = list(a), list(b)
    denom = math.sqrt(sum(x*x for x in aa)) * math.sqrt(sum(x*x for x in bb))
    return sum(x*y for x, y in zip(aa, bb)) / denom if denom else 0.0
