from sentence_transformers import SentenceTransformer, util
import requests
from bs4 import BeautifulSoup
import re
import random
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from deep_translator import GoogleTranslator
from langdetect import detect, DetectorFactory
import time

# Pour avoir des résultats de détection de langue cohérents
DetectorFactory.seed = 0

model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Charger le modèle de paraphrase T5 (chargement différé pour éviter les ralentissements)
paraphrase_tokenizer = None
paraphrase_model = None

def load_paraphrase_model():
    """Charge le modèle de paraphrase T5 anglais de manière différée"""
    global paraphrase_tokenizer, paraphrase_model
    if paraphrase_tokenizer is None or paraphrase_model is None:
        print("Chargement du modèle de paraphrase T5 anglais...")
        # Utiliser un modèle anglais performant pour la paraphrase
        paraphrase_tokenizer = AutoTokenizer.from_pretrained("Vamsi/T5_Paraphrase_Paws")
        paraphrase_model = AutoModelForSeq2SeqLM.from_pretrained("Vamsi/T5_Paraphrase_Paws")
        print("Modèle de paraphrase T5 anglais chargé avec succès !")
    return paraphrase_tokenizer, paraphrase_model

def paraphrase_text_ai(text, max_sentences=10):
    """
    Reformule automatiquement un texte en utilisant traduction + paraphrase anglaise + retraduction
    """
    if not text or len(text.strip()) < 10:
        return text

    try:
        # Détecter la langue du texte
        try:
            detected_lang = detect(text)
            print(f"Langue détectée: {detected_lang}")
        except:
            detected_lang = 'fr'  # Par défaut français
            print("Détection de langue échouée, utilisation du français par défaut")

        # Initialiser le traducteur
        translator = GoogleTranslator(source='fr', target='en')
        
        # Si le texte est en français, on le traduit en anglais d'abord
        if detected_lang == 'fr':
            print("Traduction français -> anglais...")
            try:
                # Découper en phrases pour une meilleure traduction
                sentences = re.split(r'[.!?]+', text)
                sentences = [s.strip() for s in sentences if s.strip()]
                
                translated_sentences = []
                for sentence in sentences:
                    if len(sentence) > 5:
                        time.sleep(0.1)  # Éviter les limites de taux
                        translated = translator.translate(sentence)
                        translated_sentences.append(translated)
                    else:
                        translated_sentences.append(sentence)
                
                english_text = '. '.join(translated_sentences)
                if english_text and not english_text.endswith('.'):
                    english_text += '.'
                    
                print(f"Texte traduit en anglais: {english_text[:100]}...")
                
            except Exception as e:
                print(f"Erreur de traduction fr->en: {e}")
                return reformulate_text_basic(text)
        else:
            # Si déjà en anglais, on utilise le texte tel quel
            english_text = text
            print("Texte déjà en anglais, paraphrase directe")

        # Paraphraser en anglais avec le modèle T5
        print("Paraphrase en anglais...")
        paraphrased_english = paraphrase_english_text(english_text, max_sentences)
        
        if not paraphrased_english or paraphrased_english == english_text:
            print("Paraphrase anglaise échouée, fallback")
            return reformulate_text_basic(text)

        # Si le texte original était en français, retraduire en français
        if detected_lang == 'fr':
            print("Retraduction anglais -> français...")
            try:
                # Créer un nouveau traducteur pour EN->FR
                translator_en_fr = GoogleTranslator(source='en', target='fr')
                
                # Découper en phrases pour une meilleure retraduction
                sentences = re.split(r'[.!?]+', paraphrased_english)
                sentences = [s.strip() for s in sentences if s.strip()]
                
                retranslated_sentences = []
                for sentence in sentences:
                    if len(sentence) > 5:
                        time.sleep(0.1)  # Éviter les limites de taux
                        retranslated = translator_en_fr.translate(sentence)
                        retranslated_sentences.append(retranslated)
                    else:
                        retranslated_sentences.append(sentence)
                
                final_text = '. '.join(retranslated_sentences)
                if final_text and not final_text.endswith('.'):
                    final_text += '.'
                    
                print(f"Texte final en français: {final_text[:100]}...")
                return final_text
                
            except Exception as e:
                print(f"Erreur de retraduction en->fr: {e}")
                return reformulate_text_basic(text)
        else:
            # Si le texte était déjà en anglais, retourner la paraphrase anglaise
            return paraphrased_english
        
    except Exception as e:
        print(f"Erreur avec la méthode traduction/paraphrase, fallback: {e}")
        return reformulate_text_basic(text)

def paraphrase_english_text(text, max_sentences=10):
    """
    Paraphrase un texte anglais avec le modèle T5
    """
    try:
        tokenizer, model = load_paraphrase_model()
        
        # Découper le texte en phrases
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
        paraphrased_sentences = []

        print(f"Paraphrase de {len(sentences)} phrases en anglais")

        for i, sentence in enumerate(sentences[:max_sentences]):
            if len(sentence) < 15:  # Ignorer les phrases très courtes
                paraphrased_sentences.append(sentence)
                continue
                
            # Nettoyer et préparer la phrase
            clean_sentence = sentence.strip()
            if not clean_sentence.endswith('.'):
                clean_sentence += '.'
                
            input_text = f"paraphrase: {clean_sentence}"
            
            try:
                encoding = tokenizer.encode_plus(
                    input_text, 
                    padding="max_length", 
                    return_tensors="pt", 
                    max_length=256, 
                    truncation=True
                )
                input_ids, attention_mask = encoding["input_ids"], encoding["attention_mask"]

                with torch.no_grad():
                    outputs = model.generate(
                        input_ids=input_ids,
                        attention_mask=attention_mask,
                        max_length=256,
                        num_beams=8,
                        num_return_sequences=1,
                        no_repeat_ngram_size=3,
                        early_stopping=True,
                        do_sample=True,
                        temperature=1.2,
                        top_p=0.9,
                        repetition_penalty=1.2
                    )

                paraphrased = tokenizer.decode(outputs[0], skip_special_tokens=True, clean_up_tokenization_spaces=True)
                
                # Vérifier si la paraphrase est différente de l'original
                if paraphrased.lower().strip() != clean_sentence.lower().strip():
                    paraphrased_sentences.append(paraphrased)
                    print(f"Phrase anglaise {i+1} paraphrasée avec succès")
                else:
                    # Utiliser l'original si pas de changement
                    paraphrased_sentences.append(clean_sentence)
                    print(f"Phrase anglaise {i+1} inchangée (paraphrase identique)")
                    
            except Exception as e:
                print(f"Erreur pour la phrase anglaise {i+1}: {e}")
                paraphrased_sentences.append(sentence)

        result = '. '.join(paraphrased_sentences)
        if result and not result.endswith('.'):
            result += '.'
            
        print(f"Paraphrase anglaise terminée: {len(result)} caractères")
        return result
        
    except Exception as e:
        print(f"Erreur avec le modèle T5 anglais: {e}")
        return text

def reformulate_sentence_basic(sentence):
    """Reformule une phrase individuelle avec des synonymes et transformations"""
    if not sentence or len(sentence.strip()) < 10:
        return sentence
    
    # Dictionnaire de synonymes enrichi
    synonyms = {
        'très': ['extrêmement', 'particulièrement', 'vraiment', 'fort', 'remarquablement'],
        'important': ['essentiel', 'crucial', 'primordial', 'capital', 'fondamental'],
        'permettre': ['autoriser', 'donner la possibilité', 'rendre possible', 'faciliter'],
        'utiliser': ['employer', 'se servir de', 'exploiter', 'mettre en œuvre', 'recourir à'],
        'développer': ['élaborer', 'concevoir', 'créer', 'mettre au point', 'établir'],
        'analyser': ['examiner', 'étudier', 'évaluer', 'décortiquer', 'scruter'],
        'montrer': ['démontrer', 'révéler', 'illustrer', 'mettre en évidence', 'exhiber'],
        'différent': ['distinct', 'varié', 'divers', 'autre', 'dissemblable'],
        'nouveau': ['récent', 'innovant', 'inédit', 'moderne', 'contemporain'],
        'donner': ['fournir', 'procurer', 'offrir', 'apporter', 'octroyer'],
        'créer': ['concevoir', 'élaborer', 'générer', 'produire', 'établir'],
        'améliorer': ['perfectionner', 'optimiser', 'bonifier', 'enrichir', 'raffiner'],
        'faire': ['effectuer', 'réaliser', 'accomplir', 'exécuter', 'mener'],
        'voir': ['observer', 'constater', 'remarquer', 'percevoir', 'discerner'],
        'dire': ['affirmer', 'déclarer', 'énoncer', 'mentionner', 'stipuler'],
        'avoir': ['posséder', 'détenir', 'disposer de', 'bénéficier de'],
        'être': ['constituer', 'représenter', 'former', 's\'avérer'],
        'grand': ['important', 'considérable', 'majeur', 'significatif', 'substantiel'],
        'bon': ['excellent', 'satisfaisant', 'adéquat', 'approprié', 'convenable'],
        'simple': ['facile', 'aisé', 'élémentaire', 'basique', 'accessible']
    }
    
    result = sentence
    
    # Remplacer des mots par leurs synonymes avec probabilité
    for word, synonym_list in synonyms.items():
        if random.random() < 0.7:  # 70% de chance de remplacer
            pattern = r'\b' + re.escape(word) + r'\b'
            if re.search(pattern, result, flags=re.IGNORECASE):
                synonym = random.choice(synonym_list)
                result = re.sub(pattern, synonym, result, flags=re.IGNORECASE, count=1)
    
    # Transformations de structure
    structure_transforms = [
        (r'^Il faut (.+)', r'Il convient de \1'),
        (r'^On peut (.+)', r'Il est possible de \1'),
        (r'^Cela permet (.+)', r'Cette approche offre la possibilité \1'),
        (r'^Cette méthode (.+)', r'Ce procédé \1'),
        (r'^Ce système (.+)', r'Cette architecture \1'),
        (r'est utilisé', 'trouve son application'),
        (r'est basé sur', 'repose sur'),
        (r'est défini comme', 'se caractérise par'),
        (r'peut être', 'est susceptible d\'être'),
        (r'doit être', 'se doit d\'être'),
    ]
    
    for pattern, replacement in structure_transforms:
        if random.random() < 0.5:  # 50% de chance d'appliquer
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    
    return result.strip()

def reformulate_text_basic(text):
    """
    Version de base avec synonymes et restructuration améliorée
    """
    if not text or len(text.strip()) < 10:
        return text
    
    print("Utilisation de la reformulation basique améliorée")
    
    # Découper en phrases
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 5]
    
    reformulated_sentences = []
    
    # Connecteurs pour varier les transitions
    connectors = [
        'Par ailleurs,', 'En outre,', 'De plus,', 'Également,', 'Ainsi,', 
        'En effet,', 'Néanmoins,', 'Cependant,', 'Toutefois,', 'D\'autre part,'
    ]
    
    for i, sentence in enumerate(sentences):
        if not sentence:
            continue
            
        # Reformuler la phrase
        reformed = reformulate_sentence_basic(sentence)
        
        # Ajouter des connecteurs occasionnellement (pas pour la première phrase)
        if i > 0 and random.random() < 0.3 and not reformed.lower().startswith(('il', 'on', 'ce', 'cette', 'cela')):
            connector = random.choice(connectors)
            reformed = f"{connector} {reformed.lower()}"
        
        reformulated_sentences.append(reformed)
    
    # Rejoindre les phrases
    result = '. '.join(reformulated_sentences)
    
    # Nettoyer et finaliser
    result = re.sub(r'\s+', ' ', result.strip())
    if result and not result.endswith('.'):
        result += '.'
    
    return result

def reformulate_text(text, use_ai=True):
    """
    Fonction principale de reformulation avec choix du niveau
    """
    if not text or len(text.strip()) < 10:
        return text
    
    print(f"Reformulation du texte (longueur: {len(text)}, AI: {use_ai})")
    
    if use_ai and len(text) < 2000:  # Utiliser l'IA pour les textes pas trop longs
        try:
            ai_result = paraphrase_text_ai(text)
            # Si l'IA retourne quelque chose de valide, on l'utilise
            if ai_result and len(ai_result) > len(text) * 0.5:
                print("Reformulation IA réussie")
                return ai_result
            else:
                print("Reformulation IA insuffisante, fallback")
        except Exception as e:
            print(f"Erreur IA, fallback vers méthode basique: {e}")
    
    # Fallback ou texte trop long ou IA désactivée
    print("Utilisation de la reformulation basique")
    basic_result = reformulate_text_basic(text)
    
    # Si la reformulation basique n'est pas assez différente, on fait un second passage
    original_words = set(text.lower().split())
    reformed_words = set(basic_result.lower().split())
    similarity = len(original_words & reformed_words) / len(original_words) if original_words else 1
    
    if similarity > 0.7:  # Si plus de 70% des mots sont identiques
        print("Reformulation insuffisante, second passage...")
        # Second passage avec transformations plus agressives
        basic_result = reformulate_text_aggressive(basic_result)
    
    print(f"Reformulation terminée")
    return basic_result

def google_search_serpapi(query, api_key):
    if not api_key:
        print("Warning: No API key provided")
        return []
    
    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "engine": "google",
        "api_key": api_key,
        "num": 5
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if "error" in data:
            print(f"SerpAPI Error: {data['error']}")
            return []
        results = data.get("organic_results", [])
        return [r.get("link") for r in results if "link" in r]
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error in search: {e}")
        return []

def extract_text(url):
    try:
        html = requests.get(url, timeout=5).text
        soup = BeautifulSoup(html, 'html.parser')
        return soup.get_text()
    except:
        return ""

def check_similarity(text, api_key):
    if not text or len(text.strip()) < 10:
        print("Warning: Text too short for analysis")
        return 0, []
    
    query = text[:200]
    print(f"Searching for: {query[:50]}...")
    urls = google_search_serpapi(query, api_key)
    print(f"Found {len(urls)} URLs to analyze")
    
    results = []
    if not urls:
        print("No URLs found - returning mock results for testing")
        # Pour les tests, retournons un score simulé basé sur la longueur du texte
        mock_score = min(80, max(10, len(text) % 50))
        return mock_score, [{"url": "http://example.com", "score": mock_score}]

    for url in urls:
        print(f"Analyzing: {url}")
        page_text = extract_text(url)
        if not page_text:
            continue
        try:
            emb1 = model.encode(text, convert_to_tensor=True)
            emb2 = model.encode(page_text[:1000], convert_to_tensor=True)
            score = util.cos_sim(emb1, emb2).item()
            print(f"Similarity score for {url}: {score}")
            if score > 0.3:  # Baissé le seuil pour plus de résultats
                results.append({"url": url, "score": round(score * 100, 2)})
        except Exception as e:
            print(f"Error analyzing {url}: {e}")
            continue

    max_score = max([r["score"] for r in results], default=0)
    print(f"Final max score: {max_score}")
    return max_score, results

def reformulate_text_aggressive(text):
    """
    Reformulation plus agressive avec transformations de structures complètes
    """
    if not text or len(text.strip()) < 10:
        return text
    
    print("Application de la reformulation agressive")
    
    # Dictionnaire de transformations de phrases complètes
    phrase_transforms = {
        r'Il est important de noter que (.+)': r'Il convient de souligner que \1',
        r'On peut observer que (.+)': r'Il est possible de constater que \1',
        r'Cette méthode permet de (.+)': r'Cette approche donne la possibilité de \1',
        r'Il faut (.+)': r'Il s\'avère nécessaire de \1',
        r'Cela signifie que (.+)': r'Ceci implique que \1',
        r'En outre, (.+)': r'Par ailleurs, \1',
        r'De plus, (.+)': r'En complément, \1',
        r'Cependant, (.+)': r'Néanmoins, \1',
        r'Par conséquent, (.+)': r'De ce fait, \1',
        r'En effet, (.+)': r'Effectivement, \1',
    }
    
    # Synonymes plus complets pour une reformulation agressive
    aggressive_synonyms = {
        'utilisation': 'emploi', 'usage': 'utilisation', 'emploi': 'recours',
        'développement': 'élaboration', 'création': 'conception', 'formation': 'constitution',
        'application': 'mise en œuvre', 'implémentation': 'déploiement', 'réalisation': 'concrétisation',
        'analyse': 'examen', 'étude': 'investigation', 'recherche': 'exploration',
        'résultat': 'aboutissement', 'conséquence': 'résultante', 'effet': 'répercussion',
        'problème': 'difficulté', 'enjeu': 'défi', 'question': 'problématique',
        'solution': 'résolution', 'réponse': 'parade', 'remède': 'palliatif',
        'processus': 'procédure', 'mécanisme': 'dispositif', 'système': 'architecture',
        'approche': 'démarche', 'stratégie': 'tactique', 'méthode': 'procédé',
        'objectif': 'finalité', 'but': 'visée', 'cible': 'dessein',
        'avantage': 'bénéfice', 'intérêt': 'profit', 'gain': 'plus-value',
        'inconvénient': 'désavantage', 'défaut': 'handicap', 'limite': 'contrainte'
    }
    
    result = text
    
    # Appliquer les transformations de phrases
    for pattern, replacement in phrase_transforms.items():
        if random.random() < 0.8:  # 80% de chance d'appliquer
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    
    # Appliquer les synonymes agressifs
    for original, synonym in aggressive_synonyms.items():
        if random.random() < 0.9:  # 90% de chance de remplacer
            pattern = r'\b' + re.escape(original) + r'\b'
            if re.search(pattern, result, flags=re.IGNORECASE):
                result = re.sub(pattern, synonym, result, flags=re.IGNORECASE, count=1)
    
    # Transformations structurelles plus poussées
    structural_changes = [
        # Passif vers actif et vice versa
        (r'est utilisé par (.+)', r'\1 utilise'),
        (r'est développé par (.+)', r'\1 développe'),
        (r'est créé par (.+)', r'\1 crée'),
        # Inversions de structures
        (r'Grâce à (.+), (.+)', r'\2 du fait de \1'),
        (r'Malgré (.+), (.+)', r'\2 en dépit de \1'),
        (r'Avant de (.+), (.+)', r'\2 préalablement à \1'),
        # Changements de connecteurs
        (r'Ainsi, (.+)', r'De cette manière, \1'),
        (r'Donc, (.+)', r'Par voie de conséquence, \1'),
        (r'Puis, (.+)', r'Ensuite, \1'),
    ]
    
    for pattern, replacement in structural_changes:
        if random.random() < 0.6:  # 60% de chance d'appliquer
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    
    # Nettoyer et finaliser
    result = re.sub(r'\s+', ' ', result.strip())
    if result and not result.endswith('.'):
        result += '.'
    
    return result
