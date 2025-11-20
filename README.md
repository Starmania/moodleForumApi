# Moodle Forums API

Petit utilitaire Python pour récupérer et sauvegarder les discussions d'un forum Moodle (export en Markdown).

## Fonctionnalités

- Connexion à un Moodle avec identifiants.
- Récupération des discussions d'un forum (titre, auteur, date, messages).
- Export de chaque discussion dans un dossier en Markdown.
- Possibilité d'utiliser et de sauvegarder des cookies pour éviter les connexions répétées.

## Prérequis

- Python 3.12+
- uv

## Installation

1. Cloner le dépôt ou copier les fichiers dans un dossier local.
2. Installer les dépendances :

```bash
uv sync
```

## Configuration

Créer un fichier `config.json` à la racine du projet (même dossier que `main.py`) avec le contenu suivant :

```json
{
  "username": "VOTRE_LOGIN",
  "password": "VOTRE_MOT_DE_PASSE",
  "forum_id": 12345,
  "output_directory": "exported_forum",
  "save_cookies": true
}
```

- `forum_id` : identifiant du forum Moodle (paramètre `id` dans l'URL du forum).
- `output_directory` : dossier où seront écrites les discussions.
- `save_cookies` : si `true`, les cookies seront chargés/sauvegardés dans `cookies.json`.

## Utilisation

1. Placer `config.json` correctement renseigné.
2. Lancer :

```bash
python main.py
```

- Si `cookies.json` existe et `save_cookies` est à `true`, il sera utilisé pour la session.
- Après connexion, les discussions du forum configuré seront exportées dans le dossier `output_directory`.

## Sortie

- Chaque discussion est sauvegardée dans un sous-dossier nommé par son `discussion_id`.
- Les messages sont convertis en Markdown (via `html-to-markdown`).

## Remarques

- Ce script est spécifique à une instance Moodle (ex. `moodle.umontpellier.fr`) et parse le HTML ; des modifications côté Moodle (structure HTML) peuvent nécessiter une adaptation du parser.
- Gérer vos identifiants et cookies avec prudence (ne pas committer `config.json` contenant des mots de passe).

## Développement

- Code principal : `main.py`
- Logique forum : `forums.py`
- Client HTTP : `http_client.py`
- Modèles d'objet : `post.py`
- Exceptions dédiées : `exceptions.py`

## Licence

Apache License 2.0
