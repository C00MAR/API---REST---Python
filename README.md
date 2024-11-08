# Projet de Gestion Utilisateurs avec Threading

Ce projet permet de créer et gérer des utilisateurs en parallèle via une API REST, en utilisant le threading natif de Python.

## 🌐 API Endpoints

Base URL: `https://2sqsobpu3f.execute-api.eu-west-1.amazonaws.com/dev`

### Endpoints disponibles:

- `POST /insertEmail` : Crée ou récupère un utilisateur
- `GET /userManager` : Récupère les informations d'un utilisateur via son token

## 🚀 Installation

1. Cloner le projet
```bash
git clone [votre-repo]
cd [votre-dossier]
```

2. Créer un environnement virtuel
```bash
python -m venv venv
```

3. Activer l'environnement virtuel
```bash
# Windows
venv\Scripts\activate

# Linux/MacOS
source venv/bin/activate
```

4. Installer les dépendances
```bash
pip install requests
```

## 📝 Configuration

Le projet utilise une API key par défaut, mais vous pouvez la modifier dans le code :
```python
api_key = "15e97ca6-037e-4527-9bc5-a0479fbe0f9e"
```

## 🏃‍♂️ Utilisation

Pour lancer les tests :
```bash
python test.py
```

### Paramètres configurables :
- Nombre de workers (threads) : `max_workers=3`
- Nombre d'emails de test : modifier la ligne `range(2)` dans `test_emails`

## 📊 Structure du projet

```
├── test.py            # Script principal avec threading
├── README.md          # Documentation
└── requirements.txt   # Dépendances
```

## 🔍 Fonctionnalités

- Création d'utilisateurs en parallèle
- Génération de tokens uniques
- Vérification des emails
- Gestion des erreurs
- Traitement asynchrone via threading

## 📋 Format des données

### Requête insertEmail
```json
{
    "email": "test@example.com"
}
```

### Réponse insertEmail
```json
{
    "token": "votre_token",
    "id": "user_id"
}
```

### Requête userManager
```
GET /userManager?token=votre_token
```

### Réponse userManager
```json
{
    "email": "test@example.com"
}
```

## ⚠️ Notes importantes

1. L'API nécessite une clé d'API valide
2. Les tokens sont générés automatiquement
3. Le nombre maximum de workers recommandé est de 3
4. Les emails doivent être uniques dans la base de données

## 🐛 Gestion des erreurs

Le script gère plusieurs types d'erreurs :
- Emails invalides
- Tokens invalides
- Erreurs de réseau
- Timeouts
- Erreurs de validation

## 🤝 Contribution

Pour contribuer :
1. Forker le projet
2. Créer une branche (`git checkout -b feature/ma-feature`)
3. Commiter vos changements (`git commit -m 'Ajout de ma feature'`)
4. Pusher sur la branche (`git push origin feature/ma-feature`)
5. Ouvrir une Pull Request

## 📄 License

MIT License