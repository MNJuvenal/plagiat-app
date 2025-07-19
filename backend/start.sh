# Script de démarrage pour Render
#!/bin/bash

# Installer les dépendances
pip install -r requirements.txt

# Démarrer l'application
uvicorn main:app --host 0.0.0.0 --port $PORT
