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
KNOWLEDGE += [
    ("energía", "física", "Capacidad de producir cambios o realizar trabajo."), ("materia", "física", "Todo aquello que tiene masa y ocupa un lugar en el espacio."),
    ("fuerza", "física", "Interacción capaz de modificar el movimiento de un cuerpo."), ("velocidad", "física", "Cambio de posición por unidad de tiempo."),
    ("célula", "biología", "Unidad básica estructural y funcional de los seres vivos."), ("organismo", "biología", "Ser vivo formado por una o más células."),
    ("ecosistema", "biología", "Comunidad de seres vivos y su entorno en interacción."), ("agua", "naturaleza", "Sustancia esencial formada por hidrógeno y oxígeno."),
    ("salud", "vida", "Estado de bienestar físico, mental y social; no es diagnóstico médico."), ("tiempo", "concepto", "Magnitud que ordena cambios y permite describir duración."),
    ("espacio", "concepto", "Extensión en la que se encuentran objetos y ocurren eventos."), ("causa", "razonamiento", "Hecho o condición que contribuye a producir un efecto."),
    ("efecto", "razonamiento", "Resultado producido por una causa o conjunto de causas."), ("probabilidad", "matemáticas", "Medida de la posibilidad de que ocurra un evento."),
    ("promedio", "matemáticas", "Valor obtenido al dividir una suma entre el número de elementos."), ("porcentaje", "matemáticas", "Proporción expresada sobre cien unidades."),
    ("internet", "tecnología", "Red global de redes que intercambian datos mediante protocolos."), ("web", "tecnología", "Sistema de documentos y recursos enlazados sobre internet."),
    ("protocolo", "tecnología", "Reglas acordadas para intercambiar o procesar información."), ("servidor", "tecnología", "Sistema que ofrece datos o servicios a otros sistemas."),
    ("cliente", "tecnología", "Sistema que solicita datos o servicios a un servidor."), ("base de datos", "tecnología", "Colección organizada de datos consultable mediante operaciones definidas."),
    ("ética", "sociedad", "Reflexión sobre acciones, valores, responsabilidades y consecuencias."), ("decisión", "razonamiento", "Elección entre alternativas según objetivos e información disponible."),
    ("creatividad", "cognición", "Capacidad de generar combinaciones o ideas nuevas y útiles."), ("atención", "cognición", "Selección de información relevante para procesarla con prioridad."),
    ("explicación", "comunicación", "Descripción que relaciona hechos y razones para facilitar comprensión."), ("traducción", "lenguaje", "Transformación de un mensaje a otra lengua conservando su intención."),
    ("idioma", "lenguaje", "Lengua usada por una comunidad para comunicarse."), ("región", "geografía", "Área delimitada por características físicas, culturales o políticas."),
]
KNOWLEDGE += [
    ("oído", "medicina", "Órgano relacionado con la audición y el equilibrio."), ("dolor de oído", "medicina", "Síntoma de causas diversas que requiere valoración según intensidad y signos asociados."),
    ("dolor punzante", "medicina", "Descripción de un dolor agudo o parecido a pinchazos; no identifica por sí sola una causa."), ("otorrinolaringólogo", "medicina", "Profesional especialista en oído, nariz y garganta."),
    ("infección", "medicina", "Invasión o multiplicación de agentes biológicos que puede causar inflamación y síntomas."), ("oído externo", "anatomía", "Parte del oído que incluye el pabellón y el conducto auditivo."),
    ("oído medio", "anatomía", "Cavidad situada detrás del tímpano que participa en la transmisión del sonido."), ("cerumen", "anatomía", "Sustancia natural del conducto auditivo que ayuda a protegerlo."),
    ("tímpano", "anatomía", "Membrana que separa el oído externo del oído medio y vibra con el sonido."), ("supuración", "medicina", "Salida de líquido, pus o sangre por una abertura; requiere valoración clínica."),
    ("fiebre", "medicina", "Elevación de la temperatura corporal que puede acompañar a algunas enfermedades."), ("vértigo", "medicina", "Sensación de giro o movimiento; puede requerir atención urgente si es intenso."),
    ("mareo", "medicina", "Sensación inespecífica de inestabilidad o aturdimiento."), ("pérdida de audición", "medicina", "Disminución de la capacidad para oír; si es súbita debe valorarse pronto."),
    ("compresa tibia", "autocuidado", "Aplicación externa de calor moderado que puede aliviar molestias, sin introducir objetos."), ("contraindicación", "medicina", "Circunstancia en la que un tratamiento puede ser inadecuado o riesgoso."),
    ("paracetamol", "medicamento", "Analgésico cuyo uso depende de dosis, antecedentes y contraindicaciones personales."), ("ibuprofeno", "medicamento", "Antiinflamatorio y analgésico que no es adecuado para todas las personas."),
    ("diabetes", "medicina", "Condición que puede aumentar el riesgo de complicaciones y modifica la prioridad de consulta."), ("urgencias", "atención médica", "Servicio para situaciones potencialmente graves o que requieren atención inmediata."),
    ("trauma", "medicina", "Lesión causada por un golpe, accidente o fuerza externa."), ("cuerpo extraño", "medicina", "Objeto alojado en una zona del cuerpo donde no debería estar."),
]
RELATIONS = [
    ("palabra", "tiene", "significado"), ("pregunta", "inicia", "conversación"),
    ("usuario", "envía", "pregunta"), ("contexto", "aclara", "significado"),
    ("dato", "forma", "información"), ("información", "apoya", "evidencia"),
    ("entrenamiento", "mejora", "inferencia"), ("vector", "mide", "similitud"),
    ("coseno", "compara", "vector"), ("bucle", "repite", "instrucción"),
    ("prueba", "verifica", "programa"), ("seguridad", "protege", "privacidad"),
    ("dolor de oído", "puede_requerir", "valoración médica"), ("oído", "contiene", "tímpano"),
    ("supuración", "es_signo_de_alarma", "consulta médica"), ("pérdida de audición", "requiere", "valoración pronta"),
    ("trauma", "puede_requerir", "urgencias"), ("diabetes", "aumenta", "prioridad de consulta"),
]
PROBES = [
    "hola cómo estás", "qué significa una palabra", "quiero aprender sobre vectores",
    "qué es una pregunta", "cómo funciona un bucle en Python", "cómo mejorar la seguridad",
    "qué relación hay entre datos e información", "dame una explicación de contexto",
    "qué es la energía", "cómo funciona internet", "qué significa una célula",
    "qué es una probabilidad", "explica causa y efecto",
    "qué significa dolor de oído", "qué señales de alarma tiene el oído",
]
LEXICAL = [
    ("choza", "es", "choza", "sustantivo", "singular", ["casa", "rancho", "cabaña"], ["palacio"], "hut"),
    ("chozas", "es", "choza", "sustantivo", "plural", ["casas", "ranchos"], ["palacios"], "huts"),
    ("casa", "es", "casa", "sustantivo", "singular", ["vivienda", "hogar"], ["calle"], "house"),
    ("house", "en", "house", "noun", "singular", ["home", "dwelling"], ["street"], "casa"),
    ("casa", "pt", "casa", "substantivo", "singular", ["lar", "moradia"], ["rua"], "house"),
    ("rancho", "es", "rancho", "sustantivo", "singular", ["granja", "finca"], ["ciudad"], "ranch"),
    ("y", "es", "y", "conjunción", "invariable", ["e"], ["o"], "and"),
    ("and", "en", "and", "conjunction", "invariable", ["plus"], ["or"], "y"),
    ("ser", "es", "ser", "verbo", "infinitivo", ["existir"], ["dejar de existir"], "to be"),
    ("estar", "es", "estar", "verbo", "infinitivo", ["hallarse"], [], "to be"),
    ("aprender", "es", "aprender", "verbo", "infinitivo", ["estudiar", "asimilar"], ["olvidar"], "learn"),
    ("learn", "en", "learn", "verb", "infinitive", ["study", "acquire"], ["forget"], "aprender"),
    ("hola", "es", "hola", "interjección", "invariable", ["saludos"], ["adiós"], "hello"),
    ("hello", "en", "hello", "interjection", "invariable", ["hi"], ["goodbye"], "hola"),
    ("grande", "es", "grande", "adjetivo", "singular", ["enorme", "amplio"], ["pequeño"], "big"),
    ("pequeño", "es", "pequeño", "adjetivo", "singular", ["chico"], ["grande"], "small"),
]

class Trainer:
    def __init__(self, memory: LexicalMemory, brain: Brain):
        self.memory, self.brain = memory, brain

    def teach_once(self) -> int:
        for term, category, teaching in KNOWLEDGE:
            self.memory.add(term, category=category, teaching=teaching)
        for source, relation, target in RELATIONS:
            self.memory.add_relation(source, relation, target)
        for row in LEXICAL:
            self.memory.add_lexical(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7])
            self.memory.add(row[0], category=row[3], teaching=f"Concepto léxico: {row[0]}.")
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
