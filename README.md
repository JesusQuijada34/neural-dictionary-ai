# Neural Dictionary AI

Prototipo local de inteligencia artificial **simbólico-vectorial**, diseñado sin modelos binarios de Hugging Face ni pesos preentrenados. El sistema representa palabras y frases como vectores numéricos deterministas, conserva conceptos en SQLite y coordina neuronas declaradas en YAML.

## Qué incluye

- **Memoria léxica SQLite**: términos, categorías, regiones, enseñanzas, ejemplos, frecuencia e interacciones.
- **Vectores propios**: hashing BLAKE2b reproducible y normalización; no es un embedding semántico entrenado.
- **Neurona YAML**: encoder, recuperador contextual, estimador emocional y generador de respuesta.
- **Aprendizaje incremental básico**: `add` añade conceptos y vuelve a calcular su representación.
- **Procesamiento local**: CPU y RAM mediante Python; no traduce a lenguaje máquina manualmente, aunque Python y SQLite se ejecutan mediante el intérprete y el sistema operativo.

## Instalación

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
```

## Uso

```bash
python -m neural_dictionary_ai.cli --db data/dictionary.sqlite3 seed
python -m neural_dictionary_ai.cli --db data/dictionary.sqlite3 chat "quiero entender el aprendizaje"
python -m neural_dictionary_ai.cli --db data/dictionary.sqlite3 add "perseverancia" --category enseñanza --teaching "Continuar ante la dificultad."
python -m neural_dictionary_ai.cli --db data/dictionary.sqlite3 chat
```

También queda disponible el comando `nda` después de `pip install -e .`.

## Arquitectura

```text
texto del usuario
      |
      v
lexical_encoder --> context_retriever --> emotion_estimator
                                      \\--> response_generator
      |
      v
SQLite: conceptos, vectores, interacciones
```

## Límites importantes

Este repositorio es un núcleo experimental, no una inteligencia general. El hashing produce representaciones reproducibles, pero no comprende el mundo por sí solo. Las emociones son etiquetas heurísticas sobre palabras y no sentimientos conscientes. Para escalar a millones de registros habrá que incorporar ingesta por lotes, índices ANN, control de calidad y fuentes con licencias adecuadas; no se deben descargar millones de palabras indiscriminadamente.

## Pruebas

```bash
pytest -q
```

## Próximas fases

1. Ingesta con licencia y metadatos de idioma/región.
2. Entrenamiento propio de una matriz de coocurrencias o subword vectors.
3. Memoria episódica y evaluación de respuestas.
4. Aprendizaje supervisado con correcciones del usuario.
5. Optimización por lotes y, solo si hace falta, módulos nativos controlados.
