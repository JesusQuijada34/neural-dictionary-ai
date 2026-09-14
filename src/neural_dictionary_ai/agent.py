from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import shutil

@dataclass
class Action:
    trigger: str
    kind: str
    description: str
    safe: bool = True

class DesktopOrganizer:
    CATEGORIES={"images":{'.png','.jpg','.jpeg','.gif','.webp','.svg'},"documents":{'.pdf','.doc','.docx','.txt','.md','.odt'},"spreadsheets":{'.csv','.xls','.xlsx'},"audio":{'.mp3','.wav','.flac'},"video":{'.mp4','.mov','.mkv'},"archives":{'.zip','.tar','.gz','.7z'}}
    def plan(self, root: str | Path) -> list[dict]:
        root=Path(root).expanduser().resolve(); actions=[]
        if not root.exists() or not root.is_dir(): raise ValueError("La carpeta raíz no existe o no es un directorio")
        for item in sorted(root.iterdir()):
            if item.is_dir() or item.name.startswith('.') or item.suffix.lower() not in {x for s in self.CATEGORIES.values() for x in s}: continue
            category=next(name for name,suffixes in self.CATEGORIES.items() if item.suffix.lower() in suffixes)
            destination=root/category/item.name
            actions.append({"source":str(item),"destination":str(destination),"category":category,"conflict":destination.exists()})
        return actions

    def apply(self, root: str | Path) -> dict:
        plan=self.plan(root); moved=[]; conflicts=[]
        for action in plan:
            source=Path(action["source"]); destination=Path(action["destination"])
            if action["conflict"]: conflicts.append(action); continue
            destination.parent.mkdir(exist_ok=True); shutil.move(str(source),str(destination)); moved.append(action)
        return {"planned":len(plan),"moved":len(moved),"conflicts":conflicts,"deleted":0}

class Agent:
    TRIGGERS={"organize_desktop":"organize_desktop","organiza mi escritorio":"organize_desktop","organiza el escritorio":"organize_desktop","crea una carpeta":"create_folder","mueve los archivos":"organize_desktop"}
    def detect(self, text: str) -> str | None:
        lowered=text.casefold()
        for trigger,kind in self.TRIGGERS.items():
            if trigger in lowered:return kind
        return None

    def plan(self, text: str, root: str | Path) -> dict:
        kind=self.detect(text)
        if kind=="organize_desktop": return {"trigger":kind,"mode":"plan","actions":DesktopOrganizer().plan(root),"requires_confirmation":True}
        if kind=="create_folder": return {"trigger":kind,"mode":"proposal","message":"Puedo crearla, pero necesito el nombre exacto y una carpeta raíz permitida.","requires_confirmation":True}
        return {"trigger":None,"mode":"conversation","message":"No detecté una acción autorizada. Puedo conversar o preparar un plan sin ejecutarlo."}

    def debate(self, topic: str, options: list[str], criteria: dict[str,float] | None=None) -> dict:
        criteria=criteria or {"claridad":1.0,"seguridad":1.0,"reversibilidad":1.0}; rows=[]
        for option in options:
            low=option.casefold(); score=0.0; reasons=[]
            if any(x in low for x in ("seguro","copia","plan","reversible")): score+=criteria.get("seguridad",1)+criteria.get("reversibilidad",1); reasons.append("reduce riesgo")
            if any(x in low for x in ("rápido","rapido","simple","directo")): score+=criteria.get("claridad",1); reasons.append("es simple")
            rows.append({"option":option,"score":round(score,3),"reasons":reasons})
        rows.sort(key=lambda row:row["score"],reverse=True)
        return {"topic":topic,"decision":rows[0]["option"] if rows else None,"alternatives":rows}

    def decide(self, question: str, options: list[str]) -> dict:
        result=self.debate(question,options)
        result["explanation"]="Elegí la alternativa con mayor puntuación explícita; la decisión es una recomendación, no una certeza."
        return result
