from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from neural_dictionary_ai.brain import Brain
from neural_dictionary_ai.memory import LexicalMemory
from neural_dictionary_ai.trainer import Trainer
from neural_dictionary_ai.cli import SEED, RELATIONS

CASES = [
    ("saludo", "Hola, ¿cómo estás?", ["Hola", "¿Cómo"]),
    ("acentos", "¿Qué significa la energía y cómo se relaciona con la materia?", ["energía", "materia"]),
    ("gramática", "Explícame qué es una función en Python, por favor.", ["función", "Bloque"]),
    ("puntuación", "¿Puedes responder con claridad, precisión y respeto?", ["claridad", "respeto"]),
    ("fórmula", "¿Qué representa E = mc² en física?", ["energía", "masa"]),
    ("incertidumbre", "¿Quién ganará una competición futura que todavía no existe?", ["No quiero inventar", "contexto"]),
    ("código", "Revisa este código: def suma(a, b): return a + b", ["estática", "válido"]),
]

def punctuation_ok(text: str) -> bool:
    return not bool(re.search(r"\s+[,.!?;:]", text))

def main():
    db = Path("/tmp/nda-language-challenge.sqlite3")
    if db.exists(): db.unlink()
    memory = LexicalMemory(db)
    brain = Brain(memory, ROOT / "neurons" / "default.yml")
    memory.bulk_add(SEED)
    for relation in RELATIONS:
        memory.add_relation(*relation)
    Trainer(memory, brain).teach_once()
    results=[]
    for name, prompt, expected in CASES:
        result=brain.process(prompt); response=result["response"]
        found=sum(1 for item in expected if item.casefold() in response.casefold())
        checks={"has_response":bool(response.strip()),"expected_terms":found==len(expected),"tokens_present":bool(result["tokens"]),"punctuation_clean":punctuation_ok(response)}
        results.append({"name":name,"prompt":prompt,"response":response,"checks":checks,"knowledge_confidence":result["knowledge_confidence"]})
    passed=sum(all(item["checks"].values()) for item in results)
    report={"passed":passed,"total":len(results),"score":round(passed/len(results),3),"results":results}
    print(json.dumps(report,ensure_ascii=False,indent=2))
    memory.close()
    raise SystemExit(0 if passed >= 5 else 1)

if __name__ == "__main__": main()
