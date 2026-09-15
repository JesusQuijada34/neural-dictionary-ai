from __future__ import annotations
from pathlib import Path
import yaml

class SkillRegistry:
    def __init__(self,path: str|Path):
        self.path=Path(path); data=yaml.safe_load(self.path.read_text(encoding="utf-8")) if self.path.exists() else {"skills":[]}; self.skills=data.get("skills",[])
    def list(self): return self.skills
    def match(self,text: str):
        low=text.casefold(); return [skill for skill in self.skills if skill.get("trigger","").casefold() in low]
