from __future__ import annotations
import json
from pathlib import Path
import yaml
from .code_expert import CodeExpert
from .memory import LexicalMemory
from .vectors import cosine, vector_for, tokenize, numeric_text

EMOTION_WORDS={"alegria":{"feliz","alegría","gracias","amor","excelente","bien"},"tristeza":{"triste","dolor","pérdida","solo","llorar"},"enojo":{"odio","enojo","rabia","molesto","injusto"},"curiosidad":{"cómo","como","porqué","por","qué","que","aprender","entender"}}
CODE_MARKERS={"python","código","codigo","programa","función","funcion","error","bug","script","clase","variable"}

class Brain:
    def __init__(self,memory:LexicalMemory,neuron_file:str|Path):
        self.memory=memory; self.config=yaml.safe_load(Path(neuron_file).read_text(encoding="utf-8")); cfg=self.config["brain"]
        self.dimensions=int(cfg.get("dimensions",64)); self.top_k=int(cfg.get("top_k",5)); self.min_confidence=float(cfg.get("min_confidence",0.28)); self.code=CodeExpert()

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
        return min(1.0,.55*min(1,exact/2)+.45*max(0,best))

    def generate(self,text,emotion,memories,confidence):
        tokens=set(tokenize(text))
        code_request = tokens & {"código", "codigo", "revisa", "depura", "debug", "error", "bug"}
        code_syntax = "```" in text or any(marker in text for marker in ("def ", "class ", "import ", "from ", "return ", "():"))
        if "python" in tokens and (code_request or code_syntax) or code_syntax:
            analysis=self.code.analyze(text); status="válido" if analysis["valid"] else "con errores"
            detail="; ".join(analysis["issues"] or analysis["advice"])
            return f"He revisado el código de forma estática: {status}. {detail} No lo ejecuté por seguridad."
        exact=self.memory.search_tokens(text); candidates=exact+[row for _,row in memories]; seen=set(); candidates=[r for r in candidates if not(r["term"] in seen or seen.add(r["term"]))]
        if confidence<self.min_confidence or not candidates:
            return "No quiero inventar una respuesta. Necesito una definición, un ejemplo o más contexto para responder con rigor."
        terms=", ".join(r["term"] for r in candidates[:3]); teachings=[r["teaching"] for r in candidates if r["teaching"]]
        relations=self.memory.relations_for([r["term"] for r in candidates[:3]])
        relation_text=f" Relación detectada: {relations[0]['source']} {relations[0]['relation']} {relations[0]['target']}." if relations else ""
        tone={"alegria":"Me alegra ayudarte.","tristeza":"Entiendo que puede ser difícil hablar de esto.","enojo":"Veo una señal de molestia; responderé con calma.","curiosidad":"Es una buena pregunta.","neutralidad":"Gracias por explicarlo."}[emotion]
        return f"{tone} Relaciono tu mensaje con {terms}.{relation_text} {teachings[0] if teachings else 'Puedo seguir aprendiendo con ejemplos.'}"

    def process(self,text):
        emotion,emotion_conf=self.estimate_emotion(text); memories=self.retrieve(text); confidence=self._confidence(text,memories); response=self.generate(text,emotion,memories,confidence)
        self.memory.record_interaction(text,response,emotion,confidence)
        return {"input":text,"response":response,"emotion":emotion,"emotion_confidence":round(emotion_conf,3),"knowledge_confidence":round(confidence,3),"numeric_spelling":numeric_text(text),"user_vector":[round(x,5) for x in vector_for(text,self.dimensions)],"memories":[{"term":r["term"],"score":round(s,4),"meaning":r["teaching"]} for s,r in memories]}
