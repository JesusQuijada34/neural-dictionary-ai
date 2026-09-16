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

## Cómo convierte texto en números y vectores

Cada palabra pasa por tres niveles reproducibles:

1. `numeric_spelling("hola")` devuelve los códigos Unicode de sus caracteres, por ejemplo `[104, 111, 108, 97]`.
2. `vector_for(...)` distribuye esos números en un vector de 64 dimensiones y mezcla una pequeña señal hash para reducir colisiones.
3. El cerebro calcula la similitud coseno entre el **vector del usuario** y cada **vector del diccionario**. Los conceptos con mayor puntuación alimentan la respuesta.

La salida JSON de `chat` muestra `numeric_spelling`, `user_vector`, los conceptos recuperados y el vector de cada concepto. Esto permite inspeccionar cómo se forma la respuesta en lugar de ocultar el proceso.

Esta es una arquitectura de IA experimental basada en símbolos, memoria y vectores. Para convertirse en un sistema lingüístico más capaz necesitará aprendizaje con grandes corpus legalmente disponibles, objetivos de entrenamiento, evaluación y mecanismos de corrección; agregar palabras por sí solo no crea comprensión general.

## Conversación interactiva

El comando `chat` sin texto abre una sesión continua. Reconoce saludos como `hola`, `hola cómo estás`, despedidas y turnos sucesivos. El objeto `Brain` conserva hasta 12 turnos en memoria de sesión y registra las interacciones en SQLite, por lo que puede mantener continuidad básica durante la conversación.

```bash
PYTHONPATH=src python -m neural_dictionary_ai.cli --db data/dictionary.sqlite3 seed
PYTHONPATH=src python -m neural_dictionary_ai.cli --db data/dictionary.sqlite3 chat
```

Ejemplo:

```text
tú> hola cómo estás
ia> Hola. Estoy aquí y listo para conversar contigo. No siento como una persona, pero puedo analizar tu mensaje, recordar el contexto de esta sesión y responder de forma coherente. ¿Cómo te encuentras tú?
tú> quiero aprender Python
ia> ...
```

El texto se transforma internamente a códigos numéricos y vectores antes de buscar significado. Eso no significa que se convierta directamente a lenguaje máquina: Python es interpretado o compilado por el entorno y el procesador ejecuta instrucciones de bajo nivel. El proyecto busca el comportamiento de un sistema conversacional local, no pretende afirmar consciencia, sentimientos reales ni equivalencia con un modelo grande de Hugging Face.

## Entrenamiento local verificable

El comando `train` enseña al sistema un conjunto estructurado de conceptos y relaciones, ejecuta preguntas de evaluación y escribe un reporte JSON. No usa un bucle infinito: cada ejecución tiene un máximo de rondas y se detiene antes si la cobertura y la confianza se estabilizan. La estabilidad significa que las métricas del conjunto de pruebas dejan de cambiar; no significa que el sistema conozca todo.

```bash
PYTHONPATH=src python -m neural_dictionary_ai.cli \
  --db data/dictionary.sqlite3 train --rounds 8 \
  --report data/training_report.json
```

El entrenamiento actual añade conceptos de comunicación, lenguaje, computación, programación, matemáticas, ciencia, seguridad e inteligencia artificial, además de relaciones como `palabra tiene significado`, `contexto aclara significado` y `entrenamiento mejora inferencia`. El reporte contiene rondas, conceptos, cobertura y confianza media para poder inspeccionar el progreso.

## Enseñanza durante la conversación

Cuando aparece un término relevante que no está en SQLite, el sistema pregunta de forma conversacional:

```text
ia> Quiero entenderte mejor. ¿Qué significa «zumbalú»? Puedes responder, por ejemplo: «zumbalú significa ...».
```

Si el usuario responde con una definición, el sistema la guarda como conocimiento aprendido:

```text
tú> zumbalú significa una idea inventada para probar el aprendizaje
ia> Gracias por enseñarme que «zumbalú» significa «una idea inventada para probar el aprendizaje». Lo guardaré en mi memoria para relacionarlo con futuras conversaciones. ¿Qué otra palabra o concepto te gustaría enseñarme?
```

Las expresiones comunes como `hola`, `gracias`, `adiós` y `cómo estás` se tratan como lenguaje conversacional básico, no como términos desconocidos que deban definirse. Este aprendizaje es explícito y verificable: no inventa el significado y solo lo incorpora después de recibir una explicación.

## Léxico multilingüe y rutas semánticas

El entrenador incorpora formas en español, inglés y portugués. Cada forma puede registrar idioma, lema, categoría gramatical, número, sinónimos, antónimos y traducción. Por ejemplo, `choza` se conecta con `casa`, `rancho` y `cabaña`, mientras que `y` se clasifica como un conector de adición o anexo entre palabras.

La salida de una consulta incluye `language`, `token_paths`, `morphology` y los datos léxicos disponibles. Las plantillas reconocen saludos y respuestas en varios idiomas, aunque el soporte actual es lingüístico y estructurado, no una traducción general perfecta.

## Agente, triggers y decisiones

El proyecto incluye un agente local con acciones declarativas. `organiza mi escritorio` activa un plan de organización por extensiones, pero el modo de planificación no mueve nada. El comando `organize --apply` es la única ruta que aplica movimientos, nunca borra archivos, no sale de la carpeta raíz indicada y conserva conflictos sin sobrescribir.

```bash
# Solo plan; no modifica archivos
PYTHONPATH=src python -m neural_dictionary_ai.cli organize /ruta/al/escritorio

# Aplicar movimientos explícitamente; no elimina ni sobrescribe conflictos
PYTHONPATH=src python -m neural_dictionary_ai.cli organize /ruta/al/escritorio --apply

# Detectar un trigger sin ejecutar acciones
PYTHONPATH=src python -m neural_dictionary_ai.cli agent organiza mi escritorio --root /ruta/al/escritorio

# Comparar alternativas con criterios explícitos
PYTHONPATH=src python -m neural_dictionary_ai.cli debate \
  "cómo organizar archivos" \
  "borrar todo rápido" \
  "crear un plan seguro y reversible"
```

El agente también puede crear planes de decisión explicables. No tiene autonomía ilimitada: una acción destructiva, una ruta ambigua o una operación fuera de la raíz permitida se rechaza o queda como propuesta. Las pruebas adversariales cubren conflictos, borrado, triggers, planes sin movimiento y conversaciones contradictorias.

## Contexto médico prudente

El corpus incluye conceptos sobre oído, dolor punzante, oído externo y medio, cerumen, tímpano, infección, supuración, fiebre, vértigo, mareo, pérdida de audición, trauma, cuerpo extraño, diabetes, urgencias, otorrinolaringología, contraindicaciones y autocuidado. Ante una entrada que combina dolor y oído, el cerebro produce una orientación general con señales de alarma y evita diagnosticar o indicar gotas y medicamentos de forma personalizada. Este módulo es educativo y no sustituye atención médica.

## Hugging Face ligero y vectorización avanzada

El backend opcional `HFTextBackend` usa `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, cuya ficha declara licencia Apache-2.0 y embeddings multilingües de 384 dimensiones. Los pesos no se suben al repositorio: se descargan de forma explícita, versionable y con caché local para evitar un binario grande y opaco dentro de Git. El vectorizador determinista propio sigue siendo el fallback.

```bash
pip install -e '.[hf]'
python scripts/download_model.py
NDA_ENABLE_HF=1 python -m neural_dictionary_ai.cli --db data/dictionary.sqlite3 chat "¿qué significa choza?"
```

Hugging Face se usa aquí para similitud semántica y recuperación de contexto, no para copiar personalidades, marcas, estilos de terceros o identidades. El aprendizaje automático del proyecto sigue siendo explícito y auditable: `AutoTrainer` solo registra definiciones o correcciones confirmadas por el usuario; no realiza autoentrenamiento infinito ni incorpora texto desconocido como verdad.

## Skills

Las capacidades están registradas en [skills/registry.yml](/home/ubuntu/neural-dictionary-ai/skills/registry.yml) y pueden consultarse con:

```bash
PYTHONPATH=src python -m neural_dictionary_ai.cli skills
```

## App web y Telegram

La app Flask está en [webapp.py](/home/ubuntu/neural-dictionary-ai/webapp.py). Render puede desplegarla con [render.yaml](/home/ubuntu/neural-dictionary-ai/render.yaml) y `requirements-render.txt`. Endpoints:

```text
GET  /healthz
POST /chat                 {"text":"hola"}
POST /telegram/webhook     actualización de Telegram
```

Variables para Telegram: `TELEGRAM_BOT_TOKEN` y opcionalmente `TELEGRAM_WEBHOOK_SECRET`. El webhook valida el secreto si está configurado y solo responde al mensaje recibido; no ejecuta acciones de escritorio ni operaciones destructivas desde Telegram. Para producción, configura la URL HTTPS del servicio como webhook mediante la API oficial de Telegram y conserva el token únicamente en variables secretas.

## Despliegue en Render paso a paso

1. En Render selecciona **New > Web Service**, conecta el repositorio `JesusQuijada34/neural-dictionary-ai` y usa Python.
2. Configura el build command como `pip install -r requirements-render.txt` y el start command como `gunicorn webapp:app`. El archivo `render.yaml` ya contiene estos valores para un despliegue Blueprint.
3. Configura el health check path `/healthz`.
4. Añade las variables `NDA_SEED_ON_START=1`, `NDA_ENABLE_HF=0` y `NDA_DB=data/web.sqlite3`. Para usar embeddings locales, instala el extra HF del requirements y cambia `NDA_ENABLE_HF=1`; el primer arranque puede tardar y consumir más memoria.
5. Despliega y abre `https://TU-SERVICIO.onrender.com/`. La raíz muestra una interfaz web de chat; `/chat` es la API JSON.

Render puede reiniciar servicios y el disco del plan gratuito no debe tratarse como almacenamiento permanente. Para conservar SQLite entre despliegues usa un disco persistente de Render compatible con tu plan o cambia `NDA_DB` a una base de datos administrada. No guardes tokens en el repositorio.

## Conectar Telegram

En Render añade `TELEGRAM_BOT_TOKEN` con el token de BotFather y genera un secreto aleatorio para `TELEGRAM_WEBHOOK_SECRET`. Después de desplegar, registra el webhook con la URL HTTPS de Render:

```bash
curl -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook" \
  -d "url=https://TU-SERVICIO.onrender.com/telegram/webhook" \
  -d "secret_token=$TELEGRAM_WEBHOOK_SECRET"
```

Comprueba la configuración:

```bash
curl "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getWebhookInfo"
```

Escribe al bot en Telegram. Telegram enviará el mensaje al webhook y Flask responderá usando el mismo cerebro SQLite. Telegram requiere una URL HTTPS pública para webhooks; el endpoint valida `X-Telegram-Bot-Api-Secret-Token` cuando se configuró el secreto.

## Neuronas cognitivas y datos de esta conversación

La configuración YAML ahora declara 15 neuronas, incluyendo `improviser`, `character_profile`, `defense_guard`, `resilience_muscle`, `mathematician`, `logician`, `reflective_thinker` y `decision_maker`. La “musculatura” es una metáfora de validación, memoria, recuperación y tolerancia limitada a errores; no representa un cuerpo físico.

El personaje está definido en [neurons/persona.yml](/home/ubuntu/neural-dictionary-ai/neurons/persona.yml) como un perfil original y configurable. Puede tener tono y rasgos generales, pero no copia una persona, una marca, un personaje protegido ni una voz identificable. La improvisación solo se activa como ficción declarada y separa imaginación de hechos.

Se añadió un resumen estructurado de esta conversación en [conversation_training.yml](/home/ubuntu/neural-dictionary-ai/docs/conversation_training.yml). Contiene lecciones sobre IA simbólico-vectorial, enseñanza de palabras, semántica multilingüe, agentes seguros, razonamiento explicable, identidad, Flask/Telegram y contexto médico. Se conserva como resumen de objetivos y no como copia literal de una identidad.

La defensa devuelve una explicación cuando se solicita suplantar una identidad. El razonamiento continúa exponiendo una traza breve de reglas aplicadas, sin afirmar que el sistema tenga pensamientos privados, consciencia o sentimientos reales.

## Dos servicios Render: web y Telegram

`render.yaml` define dos servicios independientes que ejecutan la misma aplicación:

- `neural-dictionary-web`: interfaz `/` y API `/chat`.
- `neural-dictionary-telegram`: webhook `/telegram/webhook`, con `TELEGRAM_BOT_TOKEN` y `TELEGRAM_WEBHOOK_SECRET` propios.

Después del despliegue, configura el webhook usando la URL del segundo servicio, no la del servicio web:

```bash
curl -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook" \
  -d "url=https://NEURAL-DICTIONARY-TELEGRAM.onrender.com/telegram/webhook" \
  -d "secret_token=$TELEGRAM_WEBHOOK_SECRET"
```

Comprueba `https://NEURAL-DICTIONARY-TELEGRAM.onrender.com/healthz`: debe mostrar `service: telegram` y `telegram_configured: true`. Si Telegram sigue sin responder, consulta:

```bash
curl "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getWebhookInfo"
```

y los logs del servicio Telegram en Render. Un error al enviar `sendMessage` ahora devuelve HTTP 502 y queda registrado en los logs en vez de fallar silenciosamente.

El vocabulario social incluye `cómo estás`, `cómo te va`, `me encuentro bien como siempre`, `qué haces` y expresiones hostiles como `vete a la vrg`. Las respuestas no pretenden sentimientos reales, pero sí mantienen una conversación cordial y explican las capacidades del sistema.
