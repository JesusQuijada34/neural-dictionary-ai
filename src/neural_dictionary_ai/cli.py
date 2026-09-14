from __future__ import annotations
import argparse
import json
from pathlib import Path
from .brain import Brain
from .memory import LexicalMemory

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB = ROOT / "data" / "dictionary.sqlite3"
DEFAULT_NEURONS = ROOT / "neurons" / "default.yml"
SEED = [
 {"term":"aprendizaje", "category":"enseñanza", "teaching":"Proceso de adquirir patrones a partir de ejemplos y retroalimentación.", "examples":["aprender con práctica"]},
 {"term":"emoción", "category":"psicología", "teaching":"Estado afectivo estimado mediante señales del texto; no equivale a una experiencia consciente."},
 {"term":"memoria", "category":"computación", "teaching":"Almacenamiento persistente de conceptos, interacciones y vectores."},
 {"term":"vector", "category":"matemáticas", "teaching":"Representación numérica de un objeto; aquí se construye con hashing determinista."},
 {"term":"sqlite", "category":"tecnología", "region":"global", "teaching":"Base de datos embebida en un archivo local."},
 {"term":"españa", "category":"región", "region":"Europa", "teaching":"Región usada como ejemplo de contexto geográfico."},
 {"term":"méxico", "category":"región", "region":"América del Norte", "teaching":"Región usada como ejemplo de contexto geográfico."},
]

def build_parser():
    p = argparse.ArgumentParser(description="Neural Dictionary AI, prototipo local")
    p.add_argument("--db", default=str(DEFAULT_DB)); p.add_argument("--neurons", default=str(DEFAULT_NEURONS))
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("seed")
    chat = sub.add_parser("chat"); chat.add_argument("text", nargs="*")
    add = sub.add_parser("add"); add.add_argument("term"); add.add_argument("--category", default="general"); add.add_argument("--teaching")
    return p

def main():
    args = build_parser().parse_args(); memory = LexicalMemory(args.db)
    try:
        if args.command == "seed": print(f"Conceptos insertados: {memory.bulk_add(SEED)}")
        elif args.command == "add": memory.add(args.term, args.category, teaching=args.teaching); print(f"Aprendido: {args.term}")
        else:
            brain = Brain(memory, args.neurons); text = " ".join(args.text)
            if text: print(json.dumps(brain.process(text), ensure_ascii=False, indent=2))
            else:
                print("Escribe 'salir' para terminar.")
                while True:
                    text = input("tú> ").strip()
                    if text.lower() in {"salir", "exit", "quit"}: break
                    print("ia>", brain.process(text)["response"])
    finally: memory.close()

if __name__ == "__main__": main()
