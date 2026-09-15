# Modelos opcionales

El repositorio no incluye pesos binarios grandes. Se descargan con versión desde Hugging Face y se guardan en la caché local, lo que evita inflar Git y permite reproducibilidad.

Modelo recomendado:

- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- Licencia declarada en su model card: Apache-2.0
- Embeddings multilingües de 384 dimensiones; aproximadamente 0.1B parámetros según la ficha del modelo.
- Uso: similitud semántica y agrupación, no personalidad, imitación de marca ni generación de identidad.

Modelo alternativo en inglés:

- `sentence-transformers/all-MiniLM-L6-v2`
- Licencia declarada: Apache-2.0
- 22.7M parámetros según la ficha del modelo.

Para activar el backend opcional:

```bash
pip install -e '.[hf]'
NDA_ENABLE_HF=1 python -m neural_dictionary_ai.cli --db data/dictionary.sqlite3 chat
```

El primer arranque descarga el modelo en `models/cache` o en `NDA_MODEL_CACHE`. Los pesos no se versionan en Git; el manifiesto y la referencia exacta sí. Revisa siempre la licencia y el hash del artefacto antes de redistribuirlo.
