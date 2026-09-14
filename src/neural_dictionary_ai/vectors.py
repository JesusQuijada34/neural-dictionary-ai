"""Representaciones numéricas deterministas, sin modelos preentrenados."""
from __future__ import annotations
import hashlib
import math
import re
from typing import Iterable

TOKEN_RE = re.compile(r"[\wáéíóúüñ]+", re.IGNORECASE)

def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())

def numeric_spelling(word: str) -> list[int]:
    """Deletrea una palabra como números Unicode normalizados a enteros.

    Se conserva el código Unicode de cada carácter para que Python transforme
    explícitamente el texto en una secuencia numérica reproducible.
    """
    return [ord(char) for char in word.lower() if not char.isspace()]

def numeric_text(text: str) -> list[list[int]]:
    return [numeric_spelling(token) for token in tokenize(text)]

def vector_for(text: str, dimensions: int = 64) -> list[float]:
    """Construye un vector propio mezclando códigos de caracteres y hashing."""
    values = [0.0] * dimensions
    tokens = tokenize(text) or [text.lower()]
    for token in tokens:
        codes = numeric_spelling(token)
        for i, code in enumerate(codes):
            index = (code + i * 31) % dimensions
            values[index] += ((code % 257) / 256.0) * (1.0 if i % 2 == 0 else -1.0)
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=32).digest()
        for i in range(dimensions):
            byte = digest[i % len(digest)]
            sign = -1.0 if digest[(i + 7) % len(digest)] & 1 else 1.0
            values[i] += sign * (byte / 255.0) * 0.25
    norm = math.sqrt(sum(x * x for x in values)) or 1.0
    return [x / norm for x in values]

def blend_vectors(*vectors: Iterable[float], weights: Iterable[float] | None = None) -> list[float]:
    vectors = [list(v) for v in vectors]
    if not vectors: return []
    weights = list(weights or [1.0] * len(vectors))
    result = [sum(vector[i] * weights[j] for j, vector in enumerate(vectors)) for i in range(len(vectors[0]))]
    norm = math.sqrt(sum(x*x for x in result)) or 1.0
    return [x / norm for x in result]

def cosine(a: Iterable[float], b: Iterable[float]) -> float:
    aa, bb = list(a), list(b)
    denom = math.sqrt(sum(x*x for x in aa)) * math.sqrt(sum(x*x for x in bb))
    return sum(x*y for x, y in zip(aa, bb)) / denom if denom else 0.0
