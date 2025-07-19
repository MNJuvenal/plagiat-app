"""
Tests pour l'API principale de PlagiatDetect Pro
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestMainAPI:
    """Tests pour les endpoints principaux de l'API"""
    
    def test_root_endpoint(self):
        """Test de l'endpoint racine"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "status" in data
        assert data["status"] == "running"
        assert "Plagiat Detection API" in data["message"]
    
    def test_health_endpoint(self):
        """Test de l'endpoint de santé"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "plagiat-api"
    
    def test_docs_endpoint(self):
        """Test de l'endpoint de documentation"""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

class TestPlagiarismCheck:
    """Tests pour la détection de plagiat"""
    
    def test_check_endpoint_valid_text(self):
        """Test de l'endpoint /check avec du texte valide"""
        test_data = {
            "text": "Ceci est un texte de test pour la détection de plagiat. Il devrait être analysé correctement."
        }
        response = client.post("/check", json=test_data)
        assert response.status_code == 200
        data = response.json()
        assert "plagiarism_score" in data
        assert "sources" in data
        assert isinstance(data["plagiarism_score"], (int, float))
        assert isinstance(data["sources"], list)
    
    def test_check_endpoint_empty_text(self):
        """Test avec du texte vide"""
        test_data = {"text": ""}
        response = client.post("/check", json=test_data)
        # L'API devrait gérer les textes vides gracieusement
        assert response.status_code in [200, 400]
    
    def test_check_endpoint_short_text(self):
        """Test avec du texte très court"""
        test_data = {"text": "Test"}
        response = client.post("/check", json=test_data)
        assert response.status_code == 200
        data = response.json()
        # Un texte court devrait avoir un score faible
        assert data["plagiarism_score"] >= 0

class TestReformulation:
    """Tests pour la reformulation de texte"""
    
    def test_reformulate_endpoint_basic(self):
        """Test de reformulation basique"""
        test_data = {
            "text": "Cette méthode est très efficace pour améliorer les performances du système.",
            "use_ai": False
        }
        response = client.post("/reformulate", json=test_data)
        assert response.status_code == 200
        data = response.json()
        assert "original" in data
        assert "reformulated" in data
        assert "method" in data
        assert data["method"] == "Basic"
        assert data["original"] == test_data["text"]
        # Le texte reformulé devrait être différent de l'original
        assert data["reformulated"] != data["original"]
    
    def test_reformulate_endpoint_ai(self):
        """Test de reformulation avec IA"""
        test_data = {
            "text": "L'intelligence artificielle permet d'automatiser de nombreuses tâches complexes.",
            "use_ai": True
        }
        response = client.post("/reformulate", json=test_data)
        assert response.status_code == 200
        data = response.json()
        assert "original" in data
        assert "reformulated" in data
        assert "method" in data
        assert data["original"] == test_data["text"]
    
    def test_reformulate_endpoint_empty_text(self):
        """Test avec du texte vide pour la reformulation"""
        test_data = {"text": "", "use_ai": False}
        response = client.post("/reformulate", json=test_data)
        # Devrait retourner le texte vide ou une erreur appropriée
        assert response.status_code in [200, 400]

class TestFileUpload:
    """Tests pour l'upload de fichiers"""
    
    def test_upload_endpoint_no_file(self):
        """Test sans fichier"""
        response = client.post("/upload")
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_upload_endpoint_unsupported_format(self):
        """Test avec un format de fichier non supporté"""
        files = {"file": ("test.txt", b"Contenu de test", "text/plain")}
        response = client.post("/upload", files=files)
        assert response.status_code == 400
        assert "Format non supporté" in response.json()["detail"]

class TestValidation:
    """Tests de validation des données"""
    
    def test_check_invalid_json(self):
        """Test avec JSON invalide"""
        response = client.post("/check", json={"invalid": "data"})
        assert response.status_code == 422
    
    def test_reformulate_missing_text(self):
        """Test de reformulation sans texte"""
        response = client.post("/reformulate", json={"use_ai": True})
        assert response.status_code == 422

class TestErrorHandling:
    """Tests de gestion d'erreurs"""
    
    def test_check_with_very_long_text(self):
        """Test avec un texte très long"""
        long_text = "A" * 50000  # 50k caractères
        test_data = {"text": long_text}
        response = client.post("/check", json=test_data)
        # L'API devrait gérer les textes longs ou retourner une erreur appropriée
        assert response.status_code in [200, 400, 413]
    
    def test_reformulate_with_special_characters(self):
        """Test avec des caractères spéciaux"""
        test_data = {
            "text": "Texte avec émojis 🚀 et caractères spéciaux àáâãäåæçèéêë",
            "use_ai": False
        }
        response = client.post("/reformulate", json=test_data)
        assert response.status_code == 200
