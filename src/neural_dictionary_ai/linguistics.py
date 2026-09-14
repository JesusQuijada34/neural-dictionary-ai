from __future__ import annotations
import re
from .vectors import tokenize

LANGUAGE_HINTS={
    "es": {"el","la","los","las","qué","que","cómo","y","una","hola","casa"},
    "en": {"the","a","an","what","how","and","hello","house"},
    "pt": {"o","a","os","as","que","como","e","olá","casa"},
}
CONNECTORS={"y":"anexo/adición","e":"anexo/adición","o":"alternativa","u":"alternativa","pero":"contraste","porque":"causa","si":"condición","then":"consecuencia","and":"anexo/adición"}
VERBS={"ser":"ser/estado","estar":"estar/estado","tener":"posesión","hacer":"acción","aprender":"adquisición","ayudar":"asistencia","saber":"conocimiento","to be":"ser/estado","have":"posesión","learn":"adquisición","help":"asistencia"}

def detect_language(text: str) -> tuple[str,float]:
    tokens=set(tokenize(text)); scores={lang:len(tokens&hints) for lang,hints in LANGUAGE_HINTS.items()}; lang,score=max(scores.items(),key=lambda item:item[1])
    return (lang, round(min(1.0,.35+score*.15),3)) if score else ("es",.2)

def analyze_tokens(text: str) -> list[dict]:
    output=[]
    for token in tokenize(text):
        clean=token.casefold()
        role="puntuación" if not clean.isalnum() else "palabra"
        if clean in CONNECTORS: role="conector"
        elif clean in VERBS or clean.endswith(("ar","er","ir","ando","iendo")): role="verbo"
        elif clean.endswith(("s","es")) and len(clean)>3: role="posible_plural"
        output.append({"token":token,"role":role,"path":CONNECTORS.get(clean,VERBS.get(clean,"concepto"))})
    return output

def singular_plural(word: str) -> dict:
    w=word.casefold()
    if w.endswith("ces"): singular=w[:-3]+"z"
    elif w.endswith("es") and len(w)>4: singular=w[:-2]
    elif w.endswith("s") and len(w)>3: singular=w[:-1]
    else: singular=w
    plural=w if singular!=w else (w+"es" if w.endswith(("r","l","d","n","z")) else w+"s")
    return {"input":word,"singular":singular,"plural":plural}

def sentence_template(intent: str, language="es") -> str:
    templates={
        "es":{"greeting":"Hola, ¿cómo estás? ¿En qué puedo ayudarte hoy?","unknown":"¿Qué significa «{term}»?","teach":"Gracias por enseñarme que «{term}» significa «{meaning}»."},
        "en":{"greeting":"Hello, how are you? How can I help you today?","unknown":"What does «{term}» mean?","teach":"Thank you for teaching me that «{term}» means «{meaning}»."},
        "pt":{"greeting":"Olá, como você está? Como posso ajudar hoje?","unknown":"O que significa «{term}»?","teach":"Obrigado por me ensinar que «{term}» significa «{meaning}»."},
    }
    return templates.get(language,templates["es"])[intent]
