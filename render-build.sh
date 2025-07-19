#!/bin/bash

# Script de build pour Render (sans Docker)
set -e

echo "🔧 Début du build Render..."

# Backend
echo "📦 Installation des dépendances backend..."
cd backend
pip install --upgrade pip
pip install -r requirements.txt
cd ..

# Frontend
echo "🎨 Build du frontend..."
cd frontend
npm install
npm run build
cd ..

echo "✅ Build terminé avec succès !"
