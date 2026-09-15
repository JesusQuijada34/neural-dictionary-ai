from __future__ import annotations
import argparse
from neural_dictionary_ai.hf_backend import HFTextBackend

p=argparse.ArgumentParser(description="Descarga opcional y explícita de un modelo Hugging Face con caché local")
p.add_argument("--model",default=None); p.add_argument("--cache",default="models/cache")
args=p.parse_args(); backend=HFTextBackend(args.model,args.cache)
if not backend.available: raise SystemExit(f"No se pudo descargar/cargar el modelo: {backend.error}")
print(backend.status())
