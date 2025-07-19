# 🚀 CI/CD Configuration pour PlagiatDetect Pro

Ce document explique la configuration CI/CD mise en place pour automatiser les tests, la qualité du code et le déploiement.

## 📁 Structure des Fichiers CI/CD

```
.github/
└── workflows/
    └── ci-cd.yml          # Pipeline principal GitHub Actions

backend/
├── tests/
│   ├── __init__.py
│   ├── test_main.py       # Tests API FastAPI
│   └── test_plagiat.py    # Tests logique métier
├── pytest.ini            # Configuration pytest
└── .coveragerc           # Configuration coverage

frontend/
├── tests/
│   ├── App.test.jsx      # Tests composants React
│   └── setup.js          # Configuration tests
└── vite.config.test.js   # Configuration Vitest

build-test.sh             # Script de test local
```

## ⚙️ GitHub Actions Workflow

### Déclencheurs
- **Push** sur `main` et `develop`
- **Pull Request** vers `main`

### Jobs Configurés

#### 1. 🐍 Tests Backend
```yaml
- Installation Python 3.11
- Installation dépendances
- Linting avec flake8
- Tests avec pytest
- Coverage report
- Vérification imports
```

#### 2. ⚛️ Tests Frontend
```yaml
- Installation Node.js 18
- Installation dépendances npm
- Linting ESLint
- Tests Vitest
- Build de production
- Vérification taille bundle
```

#### 3. 🔒 Security Checks
```yaml
- Scan sécurité avec Bandit
- Détection de secrets avec TruffleHog
- Vérification vulnérabilités avec Safety
```

#### 4. 🚀 Déploiement
```yaml
- Déclenchement automatique sur main
- Health checks post-déploiement
- Notifications de statut
```

## 🧪 Tests Automatisés

### Backend Tests
- **API Tests**: Endpoints FastAPI avec TestClient
- **Unit Tests**: Fonctions de reformulation et détection
- **Integration Tests**: Tests avec mocks des services externes
- **Coverage**: Rapport de couverture automatique

### Frontend Tests
- **Component Tests**: Tests React avec Testing Library
- **API Integration**: Tests des appels API mockés
- **Build Tests**: Vérification du build de production
- **UI Tests**: Tests d'interface utilisateur

## 🔒 Sécurité et Qualité

### Outils Intégrés
- **Bandit**: Scan sécurité Python
- **TruffleHog**: Détection de secrets
- **Safety**: Vulnérabilités des dépendances
- **ESLint**: Qualité code JavaScript
- **Flake8**: Standards Python PEP8

### Vérifications
- ✅ Pas de credentials hardcodés
- ✅ Dépendances à jour
- ✅ Code conforme aux standards
- ✅ Tests de sécurité réussis

## 📊 Métriques et Rapports

### Coverage Reports
- **Backend**: Coverage XML/HTML générés
- **Frontend**: Coverage Vitest intégré
- **Upload**: Codecov pour tracking

### Quality Gates
- **Tests**: Tous les tests doivent passer
- **Security**: Pas de vulnérabilités critiques
- **Build**: Build de production réussi
- **Linting**: Pas d'erreurs bloquantes

## 🚀 Déploiement Automatique

### Conditions de Déploiement
```yaml
if: github.ref == 'refs/heads/main' && github.event_name == 'push'
```

### Processus
1. **Tests Réussis** → Déclenchement déploiement
2. **Render Webhook** → Build automatique
3. **Health Checks** → Vérification post-déploiement
4. **Notifications** → Statut de déploiement

## 🔧 Configuration Locale

### Prérequis
```bash
# Backend
python 3.11+
pip install -r requirements.txt

# Frontend  
node 18+
npm install
```

### Exécution des Tests
```bash
# Test complet
./build-test.sh

# Backend uniquement
cd backend && python -m pytest

# Frontend uniquement
cd frontend && npm test
```

## 📝 Variables d'Environnement

### GitHub Secrets Requis
```env
SERPAPI_KEY_TEST=your_test_api_key
RENDER_DEPLOY_HOOK=your_render_webhook_url
```

### Variables de Production
```env
SERPAPI_KEY=your_production_api_key
ENVIRONMENT=production
```

## 🔍 Monitoring et Debugging

### Logs GitHub Actions
- Accès via l'onglet "Actions" du repository
- Logs détaillés par job
- Artifacts téléchargeables (coverage, builds)

### Health Checks
```bash
# Backend
curl https://your-backend.onrender.com/health

# Frontend
curl https://your-frontend.onrender.com
```

## 🎯 Bonnes Pratiques

### Commits
- **Convention**: type(scope): description
- **Exemples**: 
  - `feat(api): add reformulation endpoint`
  - `fix(ui): resolve button alignment issue`
  - `test(backend): add coverage for similarity check`

### Pull Requests
- Tests doivent passer avant merge
- Review requise pour `main`
- Check automatique des security scans

### Déploiement
- Déploiement automatique depuis `main`
- Rollback possible via Render dashboard
- Monitoring des performances post-déploiement

---

**💡 Tip**: Utilisez `./build-test.sh` avant chaque push pour vérifier localement que tout fonctionne !
