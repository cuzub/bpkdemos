# Demo Showcase

Application Vue 3 + Vuetify + FastAPI pour afficher un catalogue de démos sous forme de cards, avec administration sécurisée, tags, image d'illustration et description rich text simplifiée.

## Fonctionnalités

- Catalogue public avec recherche et filtres par tags
- Administration protégée par authentification
- Création, modification et suppression de démos
- Description riche avec toolbar minimale : gras, italique, souligné, listes, lien, image
- Upload d'images pour la carte et dans l'éditeur rich text
- Mode clair / sombre avec mémorisation locale
- Backend FastAPI + SQLite persistée dans un volume Docker
- Images stockées dans `/data/uploads`

## Lancement

```bash
docker compose up --build
```

Applications disponibles :

- Frontend : `http://localhost:8080`
- API : `http://localhost:8000`
- Uploads : `http://localhost:8000/uploads/...`

## Identifiants admin par défaut

- utilisateur : `admin`
- mot de passe : `admin123!`

Ces valeurs sont configurables dans `docker-compose.yml` via :

- `ADMIN_USERNAME`
- `ADMIN_PASSWORD`
- `ADMIN_JWT_SECRET`
- `ADMIN_TOKEN_EXPIRE_HOURS`

## Persistance

Le volume Docker `demo_data` conserve :

- la base SQLite
- les images uploadées

## Notes

- si vous aviez déjà une base créée avec l'ancienne version, les colonnes manquantes sont ajoutées automatiquement au démarrage
- les routes d'administration sont sécurisées côté backend ; le catalogue reste public
