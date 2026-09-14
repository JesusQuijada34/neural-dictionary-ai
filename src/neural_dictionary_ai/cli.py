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
 {"term":"aprendizaje", "category":"enseñanza", "teaching":"Proceso de adquirir patrones a partir de ejemplos y retroalimentación."},
 {"term":"inteligencia", "category":"ciencia", "teaching":"Capacidad de relacionar información y producir decisiones o respuestas útiles."},
 {"term":"lenguaje", "category":"comunicación", "teaching":"Sistema de símbolos para expresar ideas, estados y relaciones."},
 {"term":"palabra", "category":"lenguaje", "teaching":"Unidad simbólica que puede transformarse en códigos numéricos y vectores."},
 {"term":"respuesta", "category":"comunicación", "teaching":"Salida generada después de comparar una entrada con conocimientos almacenados."},
 {"term":"emoción", "category":"psicología", "teaching":"Estado afectivo estimado mediante señales del texto; no equivale a una experiencia consciente."},
 {"term":"memoria", "category":"computación", "teaching":"Almacenamiento persistente de conceptos, interacciones y vectores."},
 {"term":"vector", "category":"matemáticas", "teaching":"Representación numérica de un objeto; aquí se construye con caracteres y hashing determinista."},
 {"term":"número", "category":"matemáticas", "teaching":"Valor usado para codificar caracteres, medir similitud y formar representaciones."},
 {"term":"neurona", "category":"computación", "teaching":"Unidad de procesamiento configurada en YAML que transforma o transmite datos."},
 {"term":"sqlite", "category":"tecnología", "region":"global", "teaching":"Base de datos embebida en un archivo local."},
 {"term":"python", "category":"tecnología", "region":"global", "teaching":"Lenguaje que coordina la memoria, las transformaciones y el flujo neuronal."},
 {"term":"españa", "category":"región", "region":"Europa", "teaching":"Región usada como ejemplo de contexto geográfico."},
 {"term":"méxico", "category":"región", "region":"América del Norte", "teaching":"Región usada como ejemplo de contexto geográfico."},
 {"term":"colombia", "category":"región", "region":"América del Sur", "teaching":"Región usada como ejemplo de contexto geográfico."},
 {"term":"argentina", "category":"región", "region":"América del Sur", "teaching":"Región usada como ejemplo de contexto geográfico."},
 {"term":"feliz", "category":"emoción", "teaching":"Señal textual asociada heurísticamente con alegría."},
 {"term":"triste", "category":"emoción", "teaching":"Señal textual asociada heurísticamente con tristeza."},
 {"term":"curiosidad", "category":"emoción", "teaching":"Impulso de preguntar, explorar y encontrar explicaciones."},
 {"term":"verdad", "category":"concepto", "teaching":"Proposición que debe contrastarse con evidencia; el sistema no garantiza verdad."},
]

def build_parser():
    p = argparse.ArgumentParser(description="Neural Dictionary AI, prototipo local")
    p.add_argument("--db", default=str(DEFAULT_DB)); p.add_argument("--neurons", default=str(DEFAULT_NEURONS))
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("seed", help="cargar vocabulario inicial")
    chat = sub.add_parser("chat"); chat.add_argument("text", nargs="*")
    add = sub.add_parser("add"); add.add_argument("term"); add.add_argument("--category", default="general"); add.add_argument("--teaching")
    return p

def main():
    args = build_parser().parse_args(); memory = LexicalMemory(args.db)
    try:
        if args.command == "seed": print(f"Conceptos insertados/actualizados: {memory.bulk_add(SEED)}")
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
