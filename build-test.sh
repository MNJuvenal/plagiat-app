#!/bin/bash

echo "🚀 Test de build pour le déploiement Render"
echo "============================================"

echo "📦 Test du backend..."
cd backend
echo "Installation des dépendances backend..."
pip install -r requirements.txt

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

cd ../frontend
echo "📦 Test du frontend..."
echo "Installation des dépendances frontend..."
npm install

echo "Test de build frontend..."
npm run build

if [ -d "dist" ]; then
    echo "✅ Build frontend réussi - dossier dist créé"
    ls -la dist/
else
    echo "❌ Échec du build frontend"
    exit 1
fi

echo ""
echo "🎉 Tests de build terminés avec succès!"
echo "📋 Prêt pour le déploiement sur Render:"
echo ""
echo "1. Backend API:"
echo "   - Build Command: pip install -r requirements.txt"
echo "   - Start Command: uvicorn main:app --host 0.0.0.0 --port \$PORT"
echo "   - Environment: Python 3.11"
echo ""
echo "2. Frontend:"
echo "   - Build Command: npm install && npm run build" 
echo "   - Publish Directory: dist"
echo ""
echo "3. Variables d'environnement à configurer:"
echo "   - SERPAPI_KEY: votre_cle_serpapi"
echo "   - ENVIRONMENT: production"
echo ""
echo "📝 N'oubliez pas de mettre à jour l'URL backend dans src/config.js"
