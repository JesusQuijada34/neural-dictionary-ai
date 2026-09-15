from __future__ import annotations
import json
from pathlib import Path
from .memory import LexicalMemory

class AutoTrainer:
    """Aprendizaje explícito y auditable: solo incorpora datos que el usuario confirma."""
    def __init__(self,memory:LexicalMemory,log_path:str|Path="data/learning_log.jsonl"):
        self.memory=memory; self.log_path=Path(log_path); self.log_path.parent.mkdir(parents=True,exist_ok=True)
    def teach(self, term:str, meaning:str, category="usuario", examples=None, language="es"):
        self.memory.add(term,category=category,teaching=meaning,examples=examples or [])
        self.memory.add_lexical(term,language=language,lemma=term,part_of_speech="concepto",grammatical_number="singular")
        event={"term":term,"meaning":meaning,"category":category,"language":language,"source":"explicit_user_teaching"}
        with self.log_path.open("a",encoding="utf-8") as file:file.write(json.dumps(event,ensure_ascii=False)+"\n")
        return event
    def feedback(self, prompt:str, old_response:str, corrected_response:str):
        event={"prompt":prompt,"old_response":old_response,"corrected_response":corrected_response,"source":"explicit_user_feedback"}
        with self.log_path.open("a",encoding="utf-8") as file:file.write(json.dumps(event,ensure_ascii=False)+"\n")
        return event
