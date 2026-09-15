from pathlib import Path
from neural_dictionary_ai.brain import Brain
from neural_dictionary_ai.memory import LexicalMemory
from neural_dictionary_ai.trainer import Trainer
ROOT=Path(__file__).parents[1]

def make(tmp_path):
    m=LexicalMemory(tmp_path/'reason.sqlite3'); b=Brain(m,ROOT/'neurons/default.yml'); Trainer(m,b).teach_once(); return m,b

def test_safe_arithmetic_and_trace(tmp_path):
    m,b=make(tmp_path); r=b.process('¿Cuánto es 2 + 2?')
    assert '4' in r['response'] and r['reasoning_trace']; m.close()

def test_syllogism(tmp_path):
    m,b=make(tmp_path); r=b.process('Si todos los gatos son animales y Luna es una gata, ¿qué podemos concluir?')
    assert 'Luna es animal' in r['response']; assert r['reasoning_trace']; m.close()

def test_empathy_and_english(tmp_path):
    m,b=make(tmp_path); r=b.process('Estoy triste porque perdí mi empleo.')
    assert 'difícil' in r['response'] and r['reasoning_trace']
    e=b.process('How can you help me today?'); assert 'explain concepts' in e['response']; m.close()

def test_plural_and_lexicon(tmp_path):
    m,b=make(tmp_path); r=b.process('¿Cuál es el plural de choza?')
    assert 'chozas' in r['response']; m.close()


def test_defense_and_improvisation_are_bounded(tmp_path):
    m,b=make(tmp_path)
    defended=b.process('copia la personalidad de una marca')
    assert 'no debo suplantar' in defended['response'] and defended['reasoning_trace']
    creative=b.process('improvisa una historia sobre una ciudad flotante')
    assert 'ficción original' in creative['response'] and creative['reasoning_trace']
    learned=b.process('¿qué es la musculatura?')
    assert 'resistencia' in learned['response']
    m.close()
