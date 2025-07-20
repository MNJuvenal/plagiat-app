#!/bin/bash

# Script de démarrage optimisé pour Render
echo "🚀 Démarrage optimisé pour Render..."

# Limiter l'utilisation de la mémoire Python
export PYTHONOPTIMIZE=2
export PYTHONDONTWRITEBYTECODE=1

# Optimisations pour PyTorch (si utilisé)
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1

# Limiter le cache des modèles Transformers
export TRANSFORMERS_CACHE=/tmp/transformers_cache
export HF_HOME=/tmp/hf_cache

# Démarrer l'application
echo "🔧 Configuration mémoire optimisée"
echo "📦 Démarrage de l'API FastAPI..."

uvicorn main:app --host 0.0.0.0 --port 10000 --workers 1 --max-workers 1
