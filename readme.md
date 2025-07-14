# 🏢 Epic Events CRM

Un système de gestion de la relation client (CRM) développé pour Epic Events, une entreprise d'organisation d'événements. Ce système permet de gérer les clients, contrats, événements et utilisateurs avec un système d'authentification basé sur les rôles.

## 📋 Table des matières

- [Fonctionnalités](#-fonctionnalités)
- [Installation](#-installation)
- [Configuration](#-configuration)

## ✨ Fonctionnalités

### 🔐 Gestion des utilisateurs et authentification
- Système d'authentification sécurisé avec JWT
- Gestion des rôles (Commercial, Gestion, Support)
- Hachage des mots de passe avec Argon2
- Sessions utilisateur persistantes

### 👥 Gestion des clients
- Création et modification des profils clients
- Assignation des clients aux commerciaux
- Historique des interactions

### 📄 Gestion des contrats
- Création de contrats liés aux clients
- Signature électronique des contrats
- Suivi des paiements et statuts
- Contrôle d'accès basé sur les rôles

### 🎉 Gestion des événements
- Planification d'événements liés aux contrats
- Assignation du personnel support
- Gestion des lieux et participants
- Suivi en temps réel

### 📊 Monitoring et journalisation
- Intégration Sentry pour le monitoring d'erreurs
- Journalisation des actions utilisateur
- Tableaux de bord et rapports

## 🏗️ Architecture

### Stack technique
- **Backend**: Python 3.9+
- **Base de données**: PostgreSQL
- **ORM**: SQLAlchemy Core
- **CLI**: Click
- **Tests**: Pytest
- **Monitoring**: Sentry
- **Sécurité**: Argon2, JWT


## 🚀 Installation

### Prérequis
- Python 3.9 ou supérieur
- PostgreSQL 12+
- Git

### Installation locale

1. **Cloner le repository**
```bash
git clone https://github.com/votre-repo/epic-events-crm.git
cd epic-events-crm
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer les variables d'environnement**
```bash
cp .env.example .env
# Éditer .env avec vos paramètres
```

5. **Initialiser la base de données**
```bash
python -m database.init_db
```

## ⚙️ Configuration

### Variables d'environnement

Créez un fichier `.env` à la racine du projet :

```env
# Base de données
DATABASE_URL=postgresql://username:password@localhost:5432/epic_events

# Sentry (optionnel)
SENTRY_DSN=https://your-sentry-dsn

# JWT
JWT_SECRET_KEY=your-super-secret-key
JWT_ALGORITHM=HS256

# Mode debug
DEBUG=False
```

### Configuration Sentry

Pour activer le monitoring avec Sentry :

1. Créer un compte sur [Sentry.io](https://sentry.io)
2. Créer un nouveau projet Python
3. Copier le DSN dans votre fichier `.env`
4. Redémarrer l'application