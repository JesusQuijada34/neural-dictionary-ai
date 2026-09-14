import json
from pathlib import Path
from neural_dictionary_ai.brain import Brain
from neural_dictionary_ai.memory import LexicalMemory
from neural_dictionary_ai.vectors import numeric_spelling

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
    assert result["memories"][0]["dictionary_vector"]
    assert json.loads(memory.all()[0]["vector"])
    memory.close()

def test_persistence(tmp_path):
    path = tmp_path / "persistent.sqlite3"
    first = LexicalMemory(path); first.add("memoria"); first.close()
    second = LexicalMemory(path)
    assert second.all()[0]["term"] == "memoria"
    second.close()
