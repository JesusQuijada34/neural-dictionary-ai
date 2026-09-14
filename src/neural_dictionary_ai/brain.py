from __future__ import annotations
import json
import re
from pathlib import Path
import yaml
from .code_expert import CodeExpert
from .memory import LexicalMemory
from .vectors import cosine, vector_for, tokenize, tokenize_ids, numeric_text

EMOTION_WORDS={"alegria":{"feliz","alegría","gracias","amor","excelente","bien"},"tristeza":{"triste","dolor","pérdida","solo","llorar"},"enojo":{"odio","enojo","rabia","molesto","injusto"},"curiosidad":{"cómo","como","porqué","por","qué","que","aprender","entender"}}
CODE_MARKERS={"python","código","codigo","programa","función","funcion","error","bug","script","clase","variable"}
STOPWORDS={"a","al","con","cómo","como","de","del","el","en","es","esta","está","este","la","las","lo","los","me","mi","para","por","qué","que","se","su","un","una","y","yo","hola","buenas","saludos","estás","estas","hablar","quiero","sobre","gracias","adiós","adios","chao"}

class Brain:
    def __init__(self,memory:LexicalMemory,neuron_file:str|Path):
        self.memory=memory; self.config=yaml.safe_load(Path(neuron_file).read_text(encoding="utf-8")); cfg=self.config["brain"]
        self.dimensions=int(cfg.get("dimensions",64)); self.top_k=int(cfg.get("top_k",5)); self.min_confidence=float(cfg.get("min_confidence",0.28)); self.code=CodeExpert()
        self.history=[]

    def estimate_emotion(self,text):
        tokens=set(tokenize(text)); scores={name:len(tokens&words) for name,words in EMOTION_WORDS.items()}; emotion,score=max(scores.items(),key=lambda x:x[1])
        return (emotion,min(1.0,.25+score*.25)) if score else ("neutralidad",.2)

    def retrieve(self,text):
        user=vector_for(text,self.dimensions); ranked=[]
        for row in self.memory.all():
            try: dictionary=json.loads(row["vector"])
            except (TypeError,json.JSONDecodeError): dictionary=vector_for(row["term"],self.dimensions)
            ranked.append((cosine(user,dictionary),row))
        return sorted(ranked,key=lambda x:x[0],reverse=True)[:self.top_k]

    def _confidence(self,text,memories):
        exact=len(self.memory.search_tokens(text)); best=max((score for score,_ in memories),default=0.0)
        return min(1.0,.55*min(1,exact)+.45*max(0,best))

    def _unknown_terms(self, text):
        known={row["term"] for row in self.memory.all()}
        candidates=[token for token in tokenize(text) if token.isalpha() and token not in STOPWORDS and len(token)>2]
        return [token for token in candidates if token not in known][:2]

    def _learn_from_definition(self, text):
        match=re.search(r"^\s*([\wáéíóúüñ ]{2,40})\s+(?:significa|es)\s+(.{4,})[.!]?\s*$", text, re.IGNORECASE)
        if not match:return None
        term=match.group(1).strip().casefold(); meaning=match.group(2).strip()
        if " " in term: term=term.split()[-1]
        self.memory.add(term, category="enseñanza_usuario", teaching=meaning, examples=[text])
        return term,meaning

    def generate(self,text,emotion,memories,confidence):
        tokens=set(tokenize(text))
        greetings={"hola","buenas","saludos","hey","buenos"}
        if tokens & greetings:
            if {"cómo","como","estás","estas"} & tokens:
                return "Hola. Estoy aquí y listo para conversar contigo. No siento como una persona, pero puedo analizar tu mensaje, recordar el contexto de esta sesión y responder de forma coherente. ¿Cómo te encuentras tú?"
            return "Hola. Me alegra conversar contigo. ¿Qué te gustaría aprender o construir hoy?"
        if tokens & {"adiós","adios","chao","gracias"}:
            return "Ha sido un gusto conversar contigo. Cuando quieras, podemos continuar aprendiendo."
        if tokens & {"claridad","precisión","precision","respeto"}:
            return "Sí. Responderé con claridad, precisión y respeto; si no tengo evidencia suficiente, lo indicaré en lugar de inventar datos."
        code_request = tokens & {"código", "codigo", "revisa", "depura", "debug", "error", "bug"}
        code_syntax = "```" in text or any(marker in text for marker in ("def ", "class ", "import ", "from ", "return ", "():"))
        if "python" in tokens and (code_request or code_syntax) or code_syntax:
            analysis=self.code.analyze(text); status="válido" if analysis["valid"] else "con errores"
            detail="; ".join(analysis["issues"] or analysis["advice"])
            return f"He revisado el código de forma estática: {status}. {detail} No lo ejecuté por seguridad."
        if re.search(r"\bE\s*=\s*m\s*c(?:\^?2|²)\b", text, re.IGNORECASE):
            return "La fórmula E = mc² expresa la equivalencia entre masa y energía: E es energía, m es masa y c es la velocidad de la luz. Como c está al cuadrado, una pequeña masa corresponde a una gran cantidad de energía."
        exact=self.memory.search_tokens(text); candidates=exact+[row for _,row in memories]; seen=set(); candidates=[r for r in candidates if not(r["term"] in seen or seen.add(r["term"]))]
        if confidence<self.min_confidence or not candidates:
            return "No quiero inventar una respuesta. Necesito una definición, un ejemplo o más contexto para responder con rigor."
        terms=", ".join(r["term"] for r in candidates[:3]); teachings=[r["teaching"] for r in candidates if r["teaching"]]
        relations=self.memory.relations_for([r["term"] for r in candidates[:3]])
        relation_text=f" Relación detectada: {relations[0]['source']} {relations[0]['relation']} {relations[0]['target']}." if relations else ""
        tone={"alegria":"Me alegra ayudarte.","tristeza":"Entiendo que puede ser difícil hablar de esto.","enojo":"Veo una señal de molestia; responderé con calma.","curiosidad":"Es una buena pregunta.","neutralidad":"Gracias por explicarlo."}[emotion]
        return f"{tone} Relaciono tu mensaje con {terms}.{relation_text} {teachings[0] if teachings else 'Puedo seguir aprendiendo con ejemplos.'}"

    def process(self,text):
        text=text.strip()
        if not text:
            return {"input":"","response":"Estoy escuchando. Escribe una pregunta, idea o ejemplo.","emotion":"neutralidad","emotion_confidence":1.0,"knowledge_confidence":0.0,"numeric_spelling":[],"user_vector":[],"memories":[]}
        learned=self._learn_from_definition(text)
        if learned:
            term,meaning=learned; response=f"Gracias por enseñarme que «{term}» significa «{meaning}». Lo guardaré en mi memoria para relacionarlo con futuras conversaciones. ¿Qué otra palabra o concepto te gustaría enseñarme?"; emotion,emotion_conf="curiosidad",.8; memories=[]; confidence=1.0
        else:
            emotion,emotion_conf=self.estimate_emotion(text); memories=self.retrieve(text); confidence=self._confidence(text,memories)
            unknown=self._unknown_terms(text)
            response=self.generate(text,emotion,memories,confidence)
            protected = "```" in text or any(marker in text for marker in ("def ", "class ", "import ", "from ", "return ", "E =", "E="))
            if unknown and confidence < self.min_confidence and not protected:
                response=f"Quiero entenderte mejor. ¿Qué significa «{unknown[0]}»? Puedes responder, por ejemplo: «{unknown[0]} significa ...»."
        self.history.append({"user":text,"assistant":response})
        self.history=self.history[-12:]
        self.memory.record_interaction(text,response,emotion,confidence)
        return {"input":text,"response":response,"emotion":emotion,"emotion_confidence":round(emotion_conf,3),"knowledge_confidence":round(confidence,3),"turn":len(self.history),"tokens":tokenize(text),"token_ids":tokenize_ids(text),"numeric_spelling":numeric_text(text),"user_vector":[round(x,5) for x in vector_for(text,self.dimensions)],"memories":[{"term":r["term"],"score":round(s,4),"meaning":r["teaching"]} for s,r in memories]}
