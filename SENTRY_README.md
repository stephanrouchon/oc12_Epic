# Configuration Sentry pour Epic Events

## 1. Configuration

### Variables d'environnement (.env)
```
SENTRY_DSN=https://your-sentry-dsn@sentry.io/your-project-id
ENVIRONMENT=development  # ou production
RELEASE_VERSION=1.0.0
```

### Obtenir votre DSN Sentry
1. Créez un compte sur https://sentry.io
2. Créez un nouveau projet Python
3. Copiez le DSN fourni dans votre fichier .env

## 2. Événements journalisés

### Création d'utilisateur
- **Événement** : Chaque fois qu'un nouvel utilisateur est créé
- **Données** : ID utilisateur, nom d'utilisateur, département, créé par qui
- **Niveau** : INFO

### Modification d'utilisateur
- **Événement** : Chaque fois qu'un utilisateur est modifié
- **Données** : ID utilisateur, champs modifiés, modifié par qui
- **Niveau** : INFO

### Signature de contrat
- **Événement** : Quand un contrat passe à l'état "signé"
- **Données** : ID contrat, nom client, montant, signé par qui
- **Niveau** : INFO

### Exceptions inattendues
- **Événement** : Toutes les exceptions non gérées
- **Données** : Stack trace, contexte, fonction où l'erreur s'est produite
- **Niveau** : ERROR

## 3. Utilisation du décorateur

Pour ajouter la journalisation automatique des exceptions à vos fonctions :

```python
from services.sentry_service import sentry_exception_handler

@sentry_exception_handler("ma_fonction_critique")
def ma_fonction():
    # votre code ici
    pass
```

## 4. Surveillance en production

- Consultez votre dashboard Sentry pour voir les erreurs en temps réel
- Configurez des alertes pour être notifié des erreurs critiques
- Analysez les tendances pour identifier les problèmes récurrents

## 5. Bonnes pratiques

- Utilisez un DSN différent pour development/production
- Configurez des release versions pour suivre les déploiements
- Ne loggez pas d'informations sensibles (mots de passe, tokens)
- Utilisez des tags pour categoriser vos événements
