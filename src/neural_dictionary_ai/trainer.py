from __future__ import annotations
import json
from pathlib import Path
from .brain import Brain
from .memory import LexicalMemory

KNOWLEDGE = [
    ("sistema", "arquitectura", "Conjunto de partes coordinadas para lograr una función."),
    ("dato", "computación", "Representación de un hecho que puede almacenarse y procesarse."),
    ("información", "conocimiento", "Datos interpretados dentro de un contexto."),
    ("significado", "lenguaje", "Contenido o concepto asociado a una palabra o expresión."),
    ("contexto", "lenguaje", "Circunstancias que ayudan a interpretar una expresión."),
    ("pregunta", "comunicación", "Expresión que solicita información o una explicación."),
    ("conversación", "comunicación", "Intercambio de mensajes entre participantes."),
    ("saludo", "comunicación", "Expresión usada para iniciar o reconocer una conversación."),
    ("usuario", "personas", "Persona que interactúa con el sistema."),
    ("objetivo", "razonamiento", "Resultado que se pretende conseguir."),
    ("evidencia", "razonamiento", "Información que sirve para respaldar o evaluar una afirmación."),
    ("confianza", "razonamiento", "Medida de seguridad sobre una respuesta, no una garantía de verdad."),
    ("hipótesis", "ciencia", "Explicación provisional que debe contrastarse."),
    ("experimento", "ciencia", "Procedimiento para observar o evaluar una hipótesis."),
    ("seguridad", "computación", "Protección frente a usos, datos o acciones dañinas."),
    ("privacidad", "computación", "Control sobre información personal y su uso."),
    ("archivo", "computación", "Conjunto persistente de datos identificado por un nombre."),
    ("base", "computación", "Estructura que sirve como fundamento de otra operación."),
    ("entrenamiento", "inteligencia artificial", "Proceso de ajustar o ampliar un sistema usando ejemplos."),
    ("inferencia", "inteligencia artificial", "Obtención de una salida a partir de datos y reglas aprendidas."),
    ("clasificación", "inteligencia artificial", "Asignación de una entrada a una o más categorías."),
    ("similitud", "matemáticas", "Medida de cercanía entre dos representaciones."),
    ("coseno", "matemáticas", "Medida angular usada para comparar vectores."),
    ("matriz", "matemáticas", "Organización rectangular de valores numéricos."),
    ("bucle", "programación", "Estructura que repite instrucciones bajo una condición."),
    ("condición", "programación", "Expresión que decide qué camino seguir en un programa."),
    ("clase", "programación", "Definición de datos y comportamientos para crear objetos."),
    ("objeto", "programación", "Entidad que combina datos y operaciones relacionadas."),
    ("excepción", "programación", "Situación anómala que puede gestionarse durante la ejecución."),
    ("prueba", "ingeniería", "Comprobación automatizada o manual de un comportamiento esperado."),
]
RELATIONS = [
    ("palabra", "tiene", "significado"), ("pregunta", "inicia", "conversación"),
    ("usuario", "envía", "pregunta"), ("contexto", "aclara", "significado"),
    ("dato", "forma", "información"), ("información", "apoya", "evidencia"),
    ("entrenamiento", "mejora", "inferencia"), ("vector", "mide", "similitud"),
    ("coseno", "compara", "vector"), ("bucle", "repite", "instrucción"),
    ("prueba", "verifica", "programa"), ("seguridad", "protege", "privacidad"),
]
PROBES = [
    "hola cómo estás", "qué significa una palabra", "quiero aprender sobre vectores",
    "qué es una pregunta", "cómo funciona un bucle en Python", "cómo mejorar la seguridad",
    "qué relación hay entre datos e información", "dame una explicación de contexto",
]

class Trainer:
    def __init__(self, memory: LexicalMemory, brain: Brain):
        self.memory, self.brain = memory, brain

    def teach_once(self) -> int:
        for term, category, teaching in KNOWLEDGE:
            self.memory.add(term, category=category, teaching=teaching)
        for source, relation, target in RELATIONS:
            self.memory.add_relation(source, relation, target)
        return len(KNOWLEDGE)

    def evaluate(self) -> dict:
        results = [self.brain.process(query) for query in PROBES]
        known = sum(r["knowledge_confidence"] >= self.brain.min_confidence for r in results)
        return {"probes": len(results), "known": known, "coverage": round(known / len(results), 3),
                "average_confidence": round(sum(r["knowledge_confidence"] for r in results) / len(results), 3)}

    def train(self, rounds=8, patience=2, report_path: str | Path | None = None) -> dict:
        history=[]; stable=0; previous=None
        for epoch in range(1, rounds + 1):
            added=self.teach_once(); metrics=self.evaluate(); metrics.update({"round":epoch,"concepts_added":added,"concept_count":len(self.memory.all())}); history.append(metrics)
            score=(metrics["coverage"], metrics["average_confidence"])
            stable = stable + 1 if score == previous else 0; previous=score
            if stable >= patience: break
        report={"rounds_completed":len(history),"stable":stable>=patience,"final":history[-1],"history":history}
        if report_path: Path(report_path).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
        return report
