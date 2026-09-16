

def test_basic_social_phrases(tmp_path):
    m,b=make(tmp_path)
    assert '¿Cómo te encuentras tú?' in b.process('cómo estás')['response']
    assert 'me alegra' in b.process('me encuentro bien como siempre')['response'].casefold()
    assert 'procesando' in b.process('qué haces')['response']
    assert 'no voy a responder con insultos' in b.process('vete a la vrg')['response']
    m.close()
