"""Representaciones numéricas y tokenización reproducible, sin modelos preentrenados."""
from __future__ import annotations
import hashlib, math, re, unicodedata
from typing import Iterable

TOKEN_RE = re.compile(r"[\wáéíóúüñ]+|[^\w\s]", re.IGNORECASE)

def normalize_text(text: str) -> str:
    return unicodedata.normalize("NFKC", text).casefold().strip()

def tokenize(text: str) -> list[str]:
    """Tokeniza palabras y signos conservando un orden reproducible."""
    return TOKEN_RE.findall(normalize_text(text))

def token_id(token: str, vocabulary_size: int = 100_003) -> int:
    """Identificador estable; nunca usa hash(), que cambia entre procesos."""
    digest = hashlib.blake2b(normalize_text(token).encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(digest, "big") % vocabulary_size

def tokenize_ids(text: str) -> list[int]:
    return [token_id(token) for token in tokenize(text)]

def numeric_spelling(word: str) -> list[int]:
    return [ord(char) for char in normalize_text(word) if not char.isspace()]

def numeric_text(text: str) -> list[list[int]]:
    return [numeric_spelling(token) for token in tokenize(text) if any(char.isalnum() for char in token)]

def vector_for(text: str, dimensions: int = 64) -> list[float]:
    values = [0.0] * dimensions; tokens = tokenize(text) or [normalize_text(text)]
    for token in tokens:
        codes = numeric_spelling(token)
        for i, code in enumerate(codes):
            index=(code+i*31)%dimensions; values[index]+=((code%257)/256.0)*(1.0 if i%2==0 else -1.0)
        digest=hashlib.blake2b(token.encode("utf-8"),digest_size=32).digest()
        for i in range(dimensions):
            byte=digest[i%len(digest)]; sign=-1.0 if digest[(i+7)%len(digest)]&1 else 1.0; values[i]+=sign*(byte/255.0)*.25
    norm=math.sqrt(sum(x*x for x in values)) or 1.0
    return [x/norm for x in values]

def blend_vectors(*vectors: Iterable[float], weights: Iterable[float] | None = None) -> list[float]:
    vectors=[list(v) for v in vectors]
    if not vectors:return []
    weights=list(weights or [1.0]*len(vectors)); result=[sum(v[i]*weights[j] for j,v in enumerate(vectors)) for i in range(len(vectors[0]))]
    norm=math.sqrt(sum(x*x for x in result)) or 1.0; return [x/norm for x in result]

def cosine(a: Iterable[float], b: Iterable[float]) -> float:
    aa,bb=list(a),list(b); denom=math.sqrt(sum(x*x for x in aa))*math.sqrt(sum(x*x for x in bb)); return sum(x*y for x,y in zip(aa,bb))/denom if denom else 0.0
