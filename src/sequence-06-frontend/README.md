# Séquence 6 - Intégration Front-End avec gRPC-Web

## 📋 Vue d'ensemble

**Durée totale**: 2 heures  
**Niveau**: Intermédiaire  
**Prérequis**: 
- Séquences 1-5 complétées
- Connaissance de JavaScript/TypeScript
- Bases de React
- Compréhension de HTTP et des proxies

## 🎯 Objectifs d'apprentissage

À la fin de cette séquence, vous serez capable de:

1. ✅ Comprendre les limitations des navigateurs avec gRPC et la solution gRPC-Web
2. ✅ Configurer et déployer Envoy comme proxy gRPC-Web
3. ✅ Générer des stubs JavaScript/TypeScript à partir de fichiers .proto
4. ✅ Implémenter un client React utilisant gRPC-Web
5. ✅ Gérer les appels unaires et le streaming côté client
6. ✅ Déboguer les problèmes courants gRPC-Web
7. ✅ Appliquer les bonnes pratiques de sécurité (CORS, TLS)

## 📚 Structure de la séquence

### 1. Introduction à gRPC-Web (15 min)
- Pourquoi gRPC-Web?
- Limitations des navigateurs
- Architecture avec proxy
- Comparaison gRPC vs gRPC-Web

### 2. Envoy Proxy (40 min)
- **Guide PDF complet** (25 pages)
- Installation et configuration de base
- Filtres gRPC-Web
- Configuration CORS
- Routage et load balancing
- Déploiement en production
- **Dossier de configurations** prêtes à l'emploi

### 3. Génération de stubs JavaScript (15 min)
- Installation des outils
- Génération pour JavaScript
- Génération pour TypeScript
- Scripts automatisés

### 4. Intégration React (40 min)
- **Guide PDF complet** (28 pages)
- Setup du projet React
- Import des stubs générés
- Création de clients gRPC
- Hooks React personnalisés
- Gestion des états (loading, error, success)
- Streaming dans React
- **8 exemples de code** complets

### 5. Debugging (10 min)
- Outils de développement
- Logs et tracing
- Problèmes courants et solutions

### 6. Lab pratique (30 min)
- **Projet noté** (30 points)
- Créer un client React complet
- Code starter fourni

### 7. Évaluation (10 min)
- QCM de 15 questions

## 🛠️ Environnement technique

### Outils requis
```bash
# Node.js et npm
node --version  # v18+
npm --version   # v9+

# Protoc avec plugin gRPC-Web
# Installation détaillée dans le guide

# Docker (pour Envoy)
docker --version
docker-compose --version
```

### Dépendances principales
```json
{
  "grpc-web": "^1.5.0",
  "google-protobuf": "^3.21.0",
  "react": "^18.2.0",
  "react-dom": "^18.2.0"
}
```

## 📦 Contenu fourni

### Guides PDF
1. **Guide Envoy Proxy** (25 pages)
   - Installation et configuration
   - Exemples de configs pour différents cas d'usage
   - Troubleshooting

2. **Guide React avec gRPC-Web** (28 pages)
   - Setup complet
   - 8 patterns d'implémentation
   - Bonnes pratiques

### Code et configurations
- Configurations Envoy prêtes à l'emploi
- Template React complet
- 8 exemples React commentés
- Scripts de génération automatisés
- Starter code pour le lab

## 🎓 Évaluation

### Lab pratique (30 points)
- Mise en place d'Envoy (5 pts)
- Génération des stubs (5 pts)
- Implémentation du client (15 pts)
- Gestion des erreurs (5 pts)

### QCM (15 questions)
- Concepts gRPC-Web
- Configuration Envoy
- Intégration React
- Debugging

## 📖 Ressources complémentaires

### Documentation officielle
- [gRPC-Web GitHub](https://github.com/grpc/grpc-web)
- [Envoy Proxy](https://www.envoyproxy.io/)
- [Protocol Buffers](https://developers.google.com/protocol-buffers)

### Tutoriels
- Exemples gRPC-Web officiels
- React avec gRPC-Web (blog posts)
- Envoy configuration patterns

## 🗂️ Organisation des fichiers

```
sequence-06-frontend/
├── 01-introduction/           # Pages d'introduction
├── 02-envoy-proxy/           # Guide et configs Envoy
├── 03-proto-generation/      # Scripts de génération
├── 04-h5p-video/             # Script vidéo H5P
├── 05-react-integration/     # Guide React et exemples
├── 06-debugging/             # Guide de debugging
├── 07-lab-assignment/        # Instructions et code du lab
└── 08-evaluation/            # QCM et corrigé
```

## ⏱️ Planning recommandé

| Activité | Durée | Type |
|----------|-------|------|
| Introduction gRPC-Web | 15 min | Lecture + Vidéo |
| Guide Envoy (lecture) | 40 min | PDF |
| Configuration Envoy (pratique) | 20 min | Hands-on |
| Génération stubs | 15 min | Pratique |
| Guide React (lecture) | 40 min | PDF |
| Exemples React (étude) | 30 min | Code |
| Lab pratique | 60 min | Projet |
| Debugging | 10 min | Lecture |
| QCM | 15 min | Évaluation |
| **Total** | **~4h** | **Mix théorie/pratique** |

> 💡 **Conseil**: Prenez le temps d'expérimenter avec les exemples de code fournis avant de démarrer le lab.

## 🚀 Pour commencer

1. Lisez le guide **GETTING-STARTED.md**
2. Vérifiez votre environnement technique
3. Téléchargez tous les fichiers de la séquence
4. Suivez l'ordre des activités
5. N'hésitez pas à poser des questions sur le forum

## ✅ Critères de réussite

Vous avez réussi cette séquence si vous pouvez:
- [ ] Expliquer le rôle d'Envoy dans l'architecture gRPC-Web
- [ ] Configurer Envoy pour exposer un service gRPC au web
- [ ] Générer des stubs JavaScript/TypeScript
- [ ] Créer un client React fonctionnel
- [ ] Gérer les erreurs et les états de chargement
- [ ] Déboguer les problèmes de connexion
- [ ] Obtenir au moins 70% au QCM
- [ ] Réaliser le lab avec succès

---

**Prochaine étape**: Section 7 - Projet fil rouge (Application de chat complète)

**Support**: Forum de la séquence 6 pour toute question
