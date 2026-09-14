from __future__ import annotations
import json
import math
from pathlib import Path
import yaml
from .memory import LexicalMemory
from .vectors import cosine, vector_for, tokenize

EMOTION_WORDS = {
    "alegria": {"feliz", "alegría", "gracias", "amor", "excelente", "bien"},
    "tristeza": {"triste", "dolor", "pérdida", "solo", "llorar"},
    "enojo": {"odio", "enojo", "rabia", "molesto", "injusto"},
    "curiosidad": {"cómo", "como", "porqué", "por", "qué", "que", "aprender", "entender"},
}

class Brain:
    def __init__(self, memory: LexicalMemory, neuron_file: str | Path):
        self.memory = memory
        self.config = yaml.safe_load(Path(neuron_file).read_text(encoding="utf-8"))
        self.dimensions = int(self.config["brain"].get("dimensions", 64))
        self.top_k = int(self.config["brain"].get("top_k", 5))
        self.learning_rate = float(self.config["brain"].get("learning_rate", 0.08))

    def estimate_emotion(self, text: str) -> tuple[str, float]:
        tokens = set(tokenize(text))
        scores = {name: len(tokens & words) for name, words in EMOTION_WORDS.items()}
        emotion, score = max(scores.items(), key=lambda item: item[1])
        return (emotion, min(1.0, 0.25 + score * 0.25)) if score else ("neutralidad", 0.2)

    def retrieve(self, text: str):
        query = vector_for(text, self.dimensions)
        ranked = []
        for row in self.memory.all():
            try:
                score = cosine(query, json.loads(row["vector"]))
            except (TypeError, json.JSONDecodeError):
                score = 0.0
            ranked.append((score, row))
        return sorted(ranked, key=lambda x: x[0], reverse=True)[:self.top_k]

    def generate(self, text: str, emotion: str, memories) -> str:
        exact = self.memory.search_tokens(text)
        candidates = [row for row in exact] + [row for _, row in memories]
        seen = set()
        candidates = [r for r in candidates if not (r["term"] in seen or seen.add(r["term"]))]
        if not candidates:
            return "Todavía no tengo conceptos suficientes; puedo aprender si me das una definición o ejemplo."
        terms = ", ".join(r["term"] for r in candidates[:3])
        teachings = [r["teaching"] for r in candidates if r["teaching"]]
        if teachings:
            return f"Relaciono tu mensaje con: {terms}. Idea aprendida: {teachings[0]}"
        return f"Relaciono tu mensaje con: {terms}. Mi estado estimado es {emotion}."

    def process(self, text: str) -> dict:
        emotion, confidence = self.estimate_emotion(text)
        memories = self.retrieve(text)
        response = self.generate(text, emotion, memories)
        self.memory.record_interaction(text, response, emotion)
        return {"input": text, "response": response, "emotion": emotion,
                "confidence": round(confidence, 3),
                "memories": [{"term": row["term"], "score": round(score, 4)} for score, row in memories]}
