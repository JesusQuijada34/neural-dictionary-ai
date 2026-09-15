import os
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))

def test_hf_backend_has_safe_fallback():
    from neural_dictionary_ai.hf_backend import HFTextBackend
    backend=HFTextBackend("model-that-does-not-exist", "/tmp/nda-no-model-cache")
    assert backend.encode(["hola"]) == []
    assert backend.status()["enabled"] is False

def test_flask_health_and_chat(tmp_path, monkeypatch):
    monkeypatch.setenv("NDA_DB", str(tmp_path/'web.sqlite3'))
    monkeypatch.setenv("NDA_SEED_ON_START", "1")
    import importlib, webapp
    importlib.reload(webapp)
    client=webapp.app.test_client()
    assert client.get('/healthz').status_code == 200
    result=client.post('/chat',json={'text':'hola cómo estás'})
    assert result.status_code == 200 and result.get_json()['response']
    webapp.memory.close()
