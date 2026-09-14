import json
from pathlib import Path
from neural_dictionary_ai.brain import Brain
from neural_dictionary_ai.memory import LexicalMemory
from neural_dictionary_ai.vectors import numeric_spelling, tokenize, tokenize_ids
from neural_dictionary_ai.trainer import Trainer

ROOT = Path(__file__).parents[1]

def test_memory_and_brain(tmp_path):
    memory = LexicalMemory(tmp_path / "test.sqlite3", dimensions=64)
    memory.add("aprendizaje", category="enseñanza", teaching="aprender con ejemplos")
    brain = Brain(memory, ROOT / "neurons" / "default.yml")
    result = brain.process("quiero entender el aprendizaje")
    assert result["response"]
    assert result["emotion"] in {"curiosidad", "neutralidad"}
    assert result["numeric_spelling"][0] == numeric_spelling("quiero")
    assert len(result["user_vector"]) == 64
    assert result["memories"][0]["meaning"]
    assert 0 <= result["knowledge_confidence"] <= 1
    assert json.loads(memory.all()[0]["vector"])
    memory.close()

def test_persistence(tmp_path):
    path = tmp_path / "persistent.sqlite3"
    first = LexicalMemory(path); first.add("memoria"); first.close()
    second = LexicalMemory(path)
    assert second.all()[0]["term"] == "memoria"
    second.close()

def test_code_is_analyzed_without_execution(tmp_path):
    memory = LexicalMemory(tmp_path / "code.sqlite3")
    brain = Brain(memory, ROOT / "neurons" / "default.yml")
    result = brain.process("revisa este código: def suma(a, b): return a + b")
    assert result["response"]
    assert "estática" in result["response"]
    memory.close()

def test_interactive_greeting_and_session_context(tmp_path):
    memory = LexicalMemory(tmp_path / "chat.sqlite3")
    brain = Brain(memory, ROOT / "neurons" / "default.yml")
    first = brain.process("hola cómo estás")
    second = brain.process("gracias")
    assert "¿Cómo te encuentras tú?" in first["response"]
    assert first["turn"] == 1
    assert second["turn"] == 2
    assert len(brain.history) == 2
    memory.close()

def test_trainer_reports_progress(tmp_path):
    memory = LexicalMemory(tmp_path / "train.sqlite3")
    brain = Brain(memory, ROOT / "neurons" / "default.yml")
    report = Trainer(memory, brain).train(rounds=3)
    assert report["rounds_completed"] == 3
    assert report["final"]["concept_count"] >= 30
    memory.close()

def test_tokenization_is_reproducible_and_exportable(tmp_path):
    assert tokenize("¡Hola, MÉXICO!") == ["¡", "hola", ",", "méxico", "!"]
    assert tokenize_ids("hola mundo") == tokenize_ids("hola mundo")
    memory = LexicalMemory(tmp_path / "export.sqlite3")
    memory.add("concepto", teaching="significado")
    memory.add_relation("concepto", "tiene", "significado")
    exported = tmp_path / "knowledge.json"
    payload = memory.export_json(exported)
    assert payload["format"] == "neural-dictionary-ai/1"
    other = LexicalMemory(tmp_path / "import.sqlite3")
    assert other.import_json(exported)["concepts"] == 1
    other.close(); memory.close()

def test_human_teaching_loop_for_unknown_word(tmp_path):
    memory = LexicalMemory(tmp_path / "lesson.sqlite3")
    brain = Brain(memory, ROOT / "neurons" / "default.yml")
    question = brain.process("hola, quiero hablar sobre zumbalú")
    assert "¿Qué significa" in question["response"]
    taught = brain.process("zumbalú significa una idea inventada para probar el aprendizaje")
    assert "Gracias por enseñarme" in taught["response"]
    learned = brain.process("¿qué es zumbalú?")
    assert "idea inventada" in learned["response"]
    memory.close()
