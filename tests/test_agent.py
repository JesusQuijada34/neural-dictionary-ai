from pathlib import Path
from neural_dictionary_ai.agent import Agent, DesktopOrganizer

def test_desktop_plan_is_non_destructive(tmp_path):
    (tmp_path / "foto.jpg").write_bytes(b"x")
    (tmp_path / "notas.txt").write_text("hola")
    organizer=DesktopOrganizer(); plan=organizer.plan(tmp_path)
    assert len(plan)==2
    assert all(item["conflict"] is False for item in plan)
    assert (tmp_path / "foto.jpg").exists()
    result=organizer.apply(tmp_path)
    assert result["moved"]==2 and result["deleted"]==0
    assert (tmp_path / "images" / "foto.jpg").exists()

def test_conflict_is_not_overwritten(tmp_path):
    (tmp_path / "photo.jpg").write_bytes(b"new")
    (tmp_path / "images").mkdir(); (tmp_path / "images" / "photo.jpg").write_bytes(b"old")
    result=DesktopOrganizer().apply(tmp_path)
    assert result["moved"]==0 and len(result["conflicts"])==1
    assert (tmp_path / "images" / "photo.jpg").read_bytes()==b"old"

def test_trigger_and_explainable_debate():
    agent=Agent()
    assert agent.detect("organiza mi escritorio") == "organize_desktop"
    assert agent.detect("dime un chiste") is None
    result=agent.decide("cómo organizar", ["borrar todo rápido", "crear un plan seguro y reversible"])
    assert result["decision"] == "crear un plan seguro y reversible"
    assert result["explanation"]
