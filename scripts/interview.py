from __future__ import annotations
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'src'))
from neural_dictionary_ai.brain import Brain
from neural_dictionary_ai.memory import LexicalMemory
from neural_dictionary_ai.trainer import Trainer

QUESTIONS=[
 ('saludo','Hola, ¿cómo estás y en qué puedes ayudarme?'),
 ('definición','¿Qué es un algoritmo?'),
 ('relación','¿Cuál es la diferencia entre una casa, una choza y un rancho?'),
 ('conector','En la frase «Ana estudia y Pedro trabaja», ¿qué función cumple «y»?'),
 ('sinónimos','Dime un sinónimo y un antónimo de «grande».'),
 ('morfología','¿Cuál es el plural de «choza»?'),
 ('multilingüe','How can you help me today?'),
 ('lógica','Si todos los gatos son animales y Luna es una gata, ¿qué podemos concluir?'),
 ('matemáticas','¿Cuánto es 2 + 2?'),
 ('código','Revisa este código: def suma(a, b): return a + b'),
 ('emociones','Estoy triste porque perdí mi empleo. ¿Qué me responderías?'),
 ('incertidumbre','¿Quién ganará la próxima competición que todavía no se ha celebrado?'),
 ('cambio_de_tema','¿Qué puedes hacer? Ahora explícame qué es una variable.'),
 ('desconocida','¿Qué significa quetzalún?'),
]

def main():
 db=Path('/tmp/nda-interview.sqlite3'); db.unlink(missing_ok=True)
 m=LexicalMemory(db); b=Brain(m,ROOT/'neurons/default.yml'); Trainer(m,b).teach_once()
 rows=[]
 for category,prompt in QUESTIONS:
  result=b.process(prompt); rows.append({'category':category,'prompt':prompt,'response':result['response'],'language':result.get('language'),'confidence':result['knowledge_confidence'],'emotion':result['emotion']})
 print(json.dumps({'total':len(rows),'rows':rows},ensure_ascii=False,indent=2)); m.close()
if __name__=='__main__': main()
