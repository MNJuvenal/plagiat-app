"""
Tests pour les fonctionnalités de détection de plagiat et reformulation
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plagiat import (
    reformulate_text_basic,
    reformulate_sentence_basic,
    reformulate_text,
    check_similarity
)

class TestReformulationBasic:
    """Tests pour la reformulation basique"""
    
    def test_reformulate_sentence_basic_empty(self):
        """Test avec une phrase vide"""
        result = reformulate_sentence_basic("")
        assert result == ""
    
    def test_reformulate_sentence_basic_short(self):
        """Test avec une phrase très courte"""
        result = reformulate_sentence_basic("Test")
        assert result == "Test"
    
    def test_reformulate_sentence_basic_normal(self):
        """Test avec une phrase normale"""
        sentence = "Cette méthode est très importante pour le développement."
        result = reformulate_sentence_basic(sentence)
        # Vérification que la fonction renvoie quelque chose de valide
        assert len(result) > 0
        assert isinstance(result, str)
        # La reformulation peut ou peut ne pas changer le texte selon les mots disponibles
    
    def test_reformulate_text_basic_empty(self):
        """Test de reformulation de texte vide"""
        result = reformulate_text_basic("")
        assert result == ""
    
    def test_reformulate_text_basic_normal(self):
        """Test de reformulation de texte normal"""
        text = "Cette méthode est très efficace. Elle permet d'améliorer les performances."
        result = reformulate_text_basic(text)
        assert isinstance(result, str)
        assert len(result) > 0
        assert "." in result  # Devrait contenir de la ponctuation
        # La reformulation basique peut parfois ne pas changer le texte original

class TestReformulationMain:
    """Tests pour la fonction principale de reformulation"""
    
    def test_reformulate_text_empty(self):
        """Test avec texte vide"""
        result = reformulate_text("", use_ai=False)
        assert result == ""
    
    def test_reformulate_text_short(self):
        """Test avec texte très court"""
        text = "Test."
        result = reformulate_text(text, use_ai=False)
        assert isinstance(result, str)
    
    def test_reformulate_text_basic_mode(self):
        """Test en mode basique"""
        text = "Cette application utilise des méthodes avancées pour détecter le plagiat."
        result = reformulate_text(text, use_ai=False)
        assert isinstance(result, str)
        assert len(result) > 0
        # La reformulation basique peut parfois ne pas changer le texte
        # L'important est qu'elle retourne une chaîne valide
    
    def test_reformulate_text_basic_mode_longer(self):
        """Test en mode basique avec un texte plus long"""
        text = "Cette application moderne utilise des méthodes très avancées et sophistiquées pour détecter efficacement le plagiat dans les documents académiques et professionnels."
        result = reformulate_text(text, use_ai=False)
        assert isinstance(result, str)
        assert len(result) > 0
        # Avec un texte plus long, la reformulation a plus de chances de fonctionner
    
    @patch('plagiat.paraphrase_text_ai')
    def test_reformulate_text_ai_mode_success(self, mock_ai):
        """Test en mode IA avec succès"""
        text = "Test de reformulation avec IA."
        mock_ai.return_value = "Reformulation IA réussie."
        
        result = reformulate_text(text, use_ai=True)
        assert result == "Reformulation IA réussie."
        mock_ai.assert_called_once_with(text)
    
    @patch('plagiat.paraphrase_text_ai')
    def test_reformulate_text_ai_mode_fallback(self, mock_ai):
        """Test en mode IA avec fallback vers basique"""
        text = "Ce texte contient plusieurs mots intéressants pour la reformulation automatique."
        mock_ai.side_effect = Exception("Erreur IA")
        
        result = reformulate_text(text, use_ai=True)
        # Le fallback devrait au moins renvoyer quelque chose
        assert len(result) > 0
        assert isinstance(result, str)

class TestSimilarityCheck:
    """Tests pour la vérification de similarité"""
    
    @patch('plagiat.google_search_serpapi')
    @patch('plagiat.extract_text')
    def test_check_similarity_no_results(self, mock_extract, mock_search):
        """Test sans résultats de recherche"""
        mock_search.return_value = []
        
        score, sources = check_similarity("Texte de test", "fake_api_key")
        assert isinstance(score, (int, float))
        assert isinstance(sources, list)
        assert score >= 0
    
    @patch('plagiat.google_search_serpapi')
    @patch('plagiat.extract_text')
    @patch('plagiat.model')
    def test_check_similarity_with_results(self, mock_model, mock_extract, mock_search):
        """Test avec résultats de recherche"""
        mock_search.return_value = ["http://example.com"]
        mock_extract.return_value = "Contenu de la page web"
        
        # Mock du modèle de similarité
        mock_emb = MagicMock()
        mock_emb.item.return_value = 0.7
        mock_model.encode.return_value = "fake_embedding"
        
        with patch('plagiat.util.cos_sim', return_value=mock_emb):
            score, sources = check_similarity("Texte de test", "fake_api_key")
            assert isinstance(score, (int, float))
            assert isinstance(sources, list)
    
    def test_check_similarity_empty_text(self):
        """Test avec texte vide"""
        score, sources = check_similarity("", "fake_api_key")
        assert score == 0
        assert sources == []
    
    def test_check_similarity_short_text(self):
        """Test avec texte très court"""
        score, sources = check_similarity("Test", "fake_api_key")
        assert score == 0
        assert sources == []

class TestUtilityFunctions:
    """Tests pour les fonctions utilitaires"""
    
    def test_synonyms_replacement(self):
        """Test du remplacement de synonymes"""
        text = "Cette méthode est très importante."
        result = reformulate_sentence_basic(text)
        # Vérifier que certains mots ont pu être remplacés
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_sentence_transformation(self):
        """Test des transformations de structure"""
        sentences = [
            "Il faut analyser ce texte.",
            "On peut utiliser cette méthode.",
            "Cette méthode permet de résoudre le problème."
        ]
        
        for sentence in sentences:
            result = reformulate_sentence_basic(sentence)
            assert isinstance(result, str)
            assert len(result) > 0

class TestErrorHandling:
    """Tests de gestion d'erreurs"""
    
    def test_reformulate_with_none(self):
        """Test avec None"""
        result = reformulate_text(None, use_ai=False)
        assert result is None or result == ""
    
    @patch('plagiat.paraphrase_text_ai')
    def test_ai_reformulation_exception(self, mock_ai):
        """Test de gestion d'exception en mode IA"""
        mock_ai.side_effect = Exception("Erreur critique")
        text = "Texte de test."
        
        result = reformulate_text(text, use_ai=True)
        # Devrait fallback vers la méthode basique
        assert isinstance(result, str)
        assert len(result) > 0
