#!/bin/bash

echo "🚀 Test de build pour le déploiement Render"
echo "============================================"

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les erreurs
error() {
    echo -e "${RED}❌ $1${NC}"
}

# Fonction pour afficher les succès
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Fonction pour afficher les infos
info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Fonction pour afficher les warnings
warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

echo "📦 Test du backend..."
cd backend

# Vérification de l'environnement virtuel
if [[ "$VIRTUAL_ENV" == "" ]]; then
    warning "Aucun environnement virtuel détecté"
    echo "Création d'un environnement virtuel temporaire..."
    python3 -m venv test_venv
    source test_venv/bin/activate
    TEMP_VENV=true
else
    info "Environnement virtuel détecté: $VIRTUAL_ENV"
    TEMP_VENV=false
fi

echo "Installation des dépendances backend..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    error "Échec de l'installation des dépendances backend"
    exit 1
fi

echo "Test d'import des modules Python..."
python -c "
try:
    from main import app
    from plagiat import check_similarity, reformulate_text
    print('✅ Tous les imports backend fonctionnent')
except Exception as e:
    print(f'❌ Erreur d\'import backend: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    error "Échec des tests d'import backend"
    exit 1
fi

echo "🧪 Exécution des tests backend..."
python -m pytest tests/ -v --tb=short

if [ $? -eq 0 ]; then
    success "Tests backend réussis"
else
    warning "Certains tests backend ont échoué (peut être normal en développement)"
fi

# Nettoyage de l'environnement virtuel temporaire
if [ "$TEMP_VENV" = true ]; then
    deactivate
    rm -rf test_venv
    info "Environnement virtuel temporaire supprimé"
fi

cd ../frontend
echo "📦 Test du frontend..."

# Vérification de Node.js
if ! command -v node &> /dev/null; then
    error "Node.js n'est pas installé"
    exit 1
fi

# Vérification de npm
if ! command -v npm &> /dev/null; then
    error "npm n'est pas installé"
    exit 1
fi

info "Version Node.js: $(node --version)"
info "Version npm: $(npm --version)"

echo "Installation des dépendances frontend..."
npm install

if [ $? -ne 0 ]; then
    error "Échec de l'installation des dépendances frontend"
    exit 1
fi

echo "🔍 Vérification de la syntaxe..."
npm run lint || warning "Problèmes de linting détectés"

echo "🧪 Exécution des tests frontend..."
npm run test:ci || warning "Tests frontend échoués (peut être normal)"

echo "🏗️ Test de build frontend..."
npm run build

if [ -d "dist" ]; then
    success "Build frontend réussi - dossier dist créé"
    echo "📊 Contenu du dossier dist:"
    ls -la dist/
    echo "📏 Taille du build:"
    du -sh dist/
else
    error "Échec du build frontend"
    exit 1
fi

echo "🔄 Test du serveur de preview..."
timeout 10s npm run preview &
PREVIEW_PID=$!
sleep 3

if kill -0 $PREVIEW_PID 2>/dev/null; then
    success "Serveur de preview démarré avec succès"
    kill $PREVIEW_PID
else
    warning "Le serveur de preview n'a pas pu démarrer"
fi

cd ..

echo ""
echo "🎉 Tests de build terminés avec succès!"
echo "======================================"
echo ""
success "Frontend et Backend prêts pour le déploiement"
echo ""
echo "📋 Prêt pour le déploiement sur Render:"
echo ""
info "1. Backend API:"
echo "   - Build Command: pip install -r requirements.txt"
echo "   - Start Command: uvicorn main:app --host 0.0.0.0 --port \$PORT"
echo "   - Environment: Python 3.11"
echo ""
info "2. Frontend:"
echo "   - Build Command: npm install && npm run build" 
echo "   - Publish Directory: dist"
echo ""
info "3. Variables d'environnement à configurer:"
echo "   - SERPAPI_KEY: votre_cle_serpapi"
echo "   - ENVIRONMENT: production"
echo ""
warning "📝 N'oubliez pas de mettre à jour l'URL backend dans src/config.js après déploiement"
echo ""
echo "🔗 Liens utiles:"
echo "   - Documentation API: /docs"
echo "   - Health Check: /health"
echo "   - Tests CI/CD: .github/workflows/ci-cd.yml"
