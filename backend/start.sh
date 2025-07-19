#!/bin/bash
# Script de démarrage pour Render - PlagiatDetect Pro

set -e  # Arrêter en cas d'erreur

echo "🚀 Starting PlagiatDetect Pro Backend..."
echo "📦 Installing dependencies..."

# Mettre à jour pip
python -m pip install --upgrade pip

# Installer les dépendances
pip install -r requirements.txt

echo "✅ Dependencies installed successfully"
echo "🌐 Starting server on port $PORT..."

# Démarrer l'application
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1
