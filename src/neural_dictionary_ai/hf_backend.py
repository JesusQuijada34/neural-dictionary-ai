from __future__ import annotations
import os
from pathlib import Path

DEFAULT_MODEL="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
class HFTextBackend:
    """Embeddings opcionales; no genera personalidad ni copia marcas/personas."""
    def __init__(self, model_name: str | None = None, cache_dir: str | Path | None = None):
        self.model_name=model_name or os.getenv("NDA_HF_MODEL", DEFAULT_MODEL)
        self.cache_dir=Path(cache_dir or os.getenv("NDA_MODEL_CACHE", "models/cache")); self.cache_dir.mkdir(parents=True,exist_ok=True)
        self.model=None; self.error=None
    def load(self):
        if self.model is not None:return self.model
        try:
            from sentence_transformers import SentenceTransformer
            self.model=SentenceTransformer(self.model_name, cache_folder=str(self.cache_dir))
            return self.model
        except Exception as exc:
            self.error=f"HF opcional no disponible: {exc}"; return None
    @property
    def available(self): return self.load() is not None
    def encode(self, texts):
        model=self.load()
        if model is None:return []
        return model.encode(list(texts),normalize_embeddings=True,show_progress_bar=False).tolist()
    def similarity(self, text: str, candidates: list[str]) -> list[float]:
        vectors=self.encode([text,*candidates])
        if not vectors:return []
        query=vectors[0]
        return [sum(a*b for a,b in zip(query,vector)) for vector in vectors[1:]]
    def status(self): return {"enabled":self.available,"model":self.model_name,"cache":str(self.cache_dir),"error":self.error}
