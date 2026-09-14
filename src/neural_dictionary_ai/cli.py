from __future__ import annotations
import argparse,json
from pathlib import Path
from .brain import Brain
from .memory import LexicalMemory
from .trainer import Trainer
ROOT=Path(__file__).resolve().parents[2]; DEFAULT_DB=ROOT/"data/dictionary.sqlite3"; DEFAULT_NEURONS=ROOT/"neurons/default.yml"
SEED=[
 {"term":"aprendizaje","category":"enseñanza","teaching":"Proceso de adquirir patrones a partir de ejemplos y retroalimentación."},{"term":"inteligencia","category":"ciencia","teaching":"Capacidad de relacionar información y producir respuestas útiles."},{"term":"lenguaje","category":"comunicación","teaching":"Sistema de símbolos para expresar ideas, estados y relaciones."},{"term":"palabra","category":"lenguaje","teaching":"Unidad simbólica que puede transformarse en códigos numéricos y vectores."},{"term":"respuesta","category":"comunicación","teaching":"Salida generada después de comparar una entrada con conocimientos almacenados."},{"term":"emoción","category":"psicología","teaching":"Estado afectivo estimado mediante señales del texto; no es una experiencia consciente."},{"term":"memoria","category":"computación","teaching":"Almacenamiento persistente de conceptos, interacciones y vectores."},{"term":"vector","category":"matemáticas","teaching":"Representación numérica de un objeto mediante caracteres y hashing determinista."},{"term":"número","category":"matemáticas","teaching":"Valor usado para codificar caracteres y medir similitud."},{"term":"neurona","category":"computación","teaching":"Unidad de procesamiento configurada en YAML que transforma o transmite datos."},{"term":"python","category":"tecnología","region":"global","teaching":"Lenguaje que coordina memoria, transformaciones y flujo neuronal."},{"term":"algoritmo","category":"programación","teaching":"Procedimiento finito y ordenado para resolver un problema."},{"term":"variable","category":"programación","teaching":"Nombre asociado a un valor que puede cambiar durante un programa."},{"term":"función","category":"programación","teaching":"Bloque reutilizable que recibe datos y produce un resultado."},{"term":"error","category":"programación","teaching":"Condición que impide o altera el resultado esperado de un programa."},{"term":"españa","category":"región","region":"Europa","teaching":"Región geográfica."},{"term":"méxico","category":"región","region":"América del Norte","teaching":"Región geográfica."},{"term":"colombia","category":"región","region":"América del Sur","teaching":"Región geográfica."},{"term":"feliz","category":"emoción","teaching":"Señal textual asociada heurísticamente con alegría."},{"term":"triste","category":"emoción","teaching":"Señal textual asociada heurísticamente con tristeza."}]
RELATIONS=[("python","es_un","lenguaje"),("función","parte_de","algoritmo"),("variable","parte_de","programa"),("neurona","usa","vector"),("memoria","guarda","palabra"),("aprendizaje","mejora","inteligencia")]
def parser():
 p=argparse.ArgumentParser();p.add_argument("--db",default=str(DEFAULT_DB));p.add_argument("--neurons",default=str(DEFAULT_NEURONS));s=p.add_subparsers(dest="command",required=True);s.add_parser("seed");t=s.add_parser("train");t.add_argument("--rounds",type=int,default=8);t.add_argument("--report",default="data/training_report.json");e=s.add_parser("export");e.add_argument("path");i=s.add_parser("import");i.add_argument("path");c=s.add_parser("chat");c.add_argument("text",nargs="*");a=s.add_parser("add");a.add_argument("term");a.add_argument("--category",default="general");a.add_argument("--teaching");r=s.add_parser("relate");r.add_argument("source");r.add_argument("relation");r.add_argument("target");u=s.add_parser("remember");u.add_argument("key");u.add_argument("value");return p
def main():
 args=parser().parse_args();m=LexicalMemory(args.db)
 try:
  if args.command=="seed": m.bulk_add(SEED);[m.add_relation(*x) for x in RELATIONS];print(f"Conceptos: {len(SEED)}; relaciones: {len(RELATIONS)}")
  elif args.command=="train":
   b=Brain(m,args.neurons);report=Trainer(m,b).train(rounds=max(1,min(args.rounds,100)),report_path=args.report);print(json.dumps(report,ensure_ascii=False,indent=2))
  elif args.command=="export": print(json.dumps(m.export_json(args.path),ensure_ascii=False,indent=2))
  elif args.command=="import": print(json.dumps(m.import_json(args.path),ensure_ascii=False,indent=2))
  elif args.command=="add": m.add(args.term,args.category,teaching=args.teaching);print(f"Aprendido: {args.term}")
  elif args.command=="relate": m.add_relation(args.source,args.relation,args.target);print("Relación aprendida")
  elif args.command=="remember": m.remember_user(args.key,args.value);print("Memoria de usuario guardada")
  else:
   b=Brain(m,args.neurons);text=" ".join(args.text)
   if text: print(json.dumps(b.process(text),ensure_ascii=False,indent=2))
   else:
    print("Escribe 'salir' para terminar.")
    while True:
     text=input("tú> ").strip()
     if text.lower() in {"salir","exit","quit"}:break
     print("ia>",b.process(text)["response"])
 finally:m.close()
if __name__=="__main__":main()
