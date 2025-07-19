"""
Test simple pour vérifier que tout fonctionne
"""
def test_basic():
    """Test basique qui doit toujours passer"""
    assert True

def test_imports():
    """Test des imports principaux"""
    try:
        from main import app
        from plagiat import reformulate_text_basic
        assert app is not None
        assert reformulate_text_basic is not None
        print("✅ Imports successful")
    except Exception as e:
        print(f"❌ Import error: {e}")
        assert False, f"Import failed: {e}"

def test_reformulation_basic():
    """Test basique de reformulation"""
    try:
        from plagiat import reformulate_text_basic
        result = reformulate_text_basic("Ceci est un test simple.")
        assert isinstance(result, str)
        assert len(result) > 0
        print("✅ Basic reformulation works")
    except Exception as e:
        print(f"❌ Reformulation error: {e}")
        assert False, f"Reformulation failed: {e}"
