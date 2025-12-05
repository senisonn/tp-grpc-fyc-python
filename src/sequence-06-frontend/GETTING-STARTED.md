# 🚀 Guide de Démarrage - Séquence 6

## Bienvenue dans la Séquence 6!

Ce guide vous aidera à démarrer rapidement avec l'intégration Front-End gRPC-Web.

## ✅ Prérequis

### Connaissances
- [ ] JavaScript ES6+ ou TypeScript
- [ ] React (hooks, composants fonctionnels)
- [ ] Promesses et async/await
- [ ] Concepts HTTP de base
- [ ] Séquences 1-5 du cours complétées

### Environnement technique

#### 1. Node.js et npm
```bash
# Vérifier l'installation
node --version  # Doit être v18+ ou v20+
npm --version   # Doit être v9+

# Si non installé, télécharger depuis:
# https://nodejs.org/
```

#### 2. Protocol Buffers Compiler (protoc)
```bash
# macOS
brew install protobuf

# Ubuntu/Debian
sudo apt-get install -y protobuf-compiler

# Windows
# Télécharger depuis https://github.com/protocolbuffers/protobuf/releases
```

#### 3. Plugin gRPC-Web pour protoc
```bash
# Installer le plugin gRPC-Web
npm install -g grpc-web protoc-gen-grpc-web

# OU télécharger le binaire depuis:
# https://github.com/grpc/grpc-web/releases
```

#### 4. Docker et Docker Compose
```bash
# Vérifier l'installation
docker --version         # v20+
docker-compose --version # v2+

# Pour installer Docker Desktop:
# https://www.docker.com/products/docker-desktop
```

## 📥 Téléchargement des ressources

### Sur Moodle

1. **Guides PDF**
   - Téléchargez "Guide Envoy Proxy" (25 pages)
   - Téléchargez "Guide React gRPC-Web" (28 pages)
   - Conservez-les pour référence offline

2. **Dossiers de code**
   - Téléchargez le dossier "Configurations Envoy"
   - Téléchargez le dossier "Exemples React"
   - Téléchargez le "Template React"
   - Décompressez dans votre répertoire de travail

3. **Code du Lab**
   - Téléchargez le starter code
   - Lisez les instructions du lab

### Structure recommandée

```
~/grpc-course/
├── sequence-06/
│   ├── guides/              # PDFs téléchargés
│   ├── envoy-configs/       # Configurations Envoy
│   ├── react-examples/      # Exemples React
│   ├── react-template/      # Template pour démarrer
│   └── lab/                 # Votre code pour le lab
```

## 🛠️ Configuration initiale

### Étape 1: Créer le répertoire de travail

```bash
# Créer la structure
mkdir -p ~/grpc-course/sequence-06/{guides,envoy-configs,react-examples,lab}
cd ~/grpc-course/sequence-06
```

### Étape 2: Vérifier les outils

Créez un script de vérification:

```bash
# check-setup.sh
#!/bin/bash

echo "🔍 Vérification de l'environnement..."

# Node.js
if command -v node &> /dev/null; then
    echo "✅ Node.js: $(node --version)"
else
    echo "❌ Node.js non installé"
fi

# npm
if command -v npm &> /dev/null; then
    echo "✅ npm: $(npm --version)"
else
    echo "❌ npm non installé"
fi

# protoc
if command -v protoc &> /dev/null; then
    echo "✅ protoc: $(protoc --version)"
else
    echo "❌ protoc non installé"
fi

# Docker
if command -v docker &> /dev/null; then
    echo "✅ Docker: $(docker --version)"
else
    echo "❌ Docker non installé"
fi

# Docker Compose
if command -v docker-compose &> /dev/null; then
    echo "✅ Docker Compose: $(docker-compose --version)"
else
    echo "❌ Docker Compose non installé"
fi

echo ""
echo "📋 Résumé:"
echo "Si tous les outils affichent ✅, vous êtes prêt!"
echo "Sinon, installez les outils manquants avant de continuer."
```

Exécutez-le:
```bash
chmod +x check-setup.sh
./check-setup.sh
```

### Étape 3: Installer les dépendances globales

```bash
# Installer les outils npm nécessaires
npm install -g grpc-web google-protobuf

# Vérifier l'installation
npm list -g --depth=0 | grep grpc
```

## 📚 Parcours d'apprentissage recommandé

### Jour 1 (1h30)
1. Lire "Introduction à gRPC-Web" (15 min)
2. Regarder la vidéo H5P "Setup gRPC-Web" (15 min)
3. Lire le "Guide Envoy Proxy" PDF - Chapitres 1-3 (40 min)
4. Tester la configuration Envoy basique (20 min)

### Jour 2 (1h30)
1. Lire le "Guide Envoy Proxy" PDF - Chapitres 4-7 (40 min)
2. Expérimenter avec les configurations CORS et TLS (30 min)
3. Lire "Génération de stubs JavaScript" (20 min)
4. Générer vos premiers stubs (20 min - pratique)

### Jour 3 (2h)
1. Lire le "Guide React gRPC-Web" PDF - Partie 1 (40 min)
2. Étudier les exemples 01-04 (30 min)
3. Lire le "Guide React gRPC-Web" PDF - Partie 2 (40 min)
4. Étudier les exemples 05-08 (40 min)

### Jour 4 (1h)
1. Lire "Debugging gRPC-Web" (15 min)
2. Commencer le Lab pratique (45 min)
3. Continuer/terminer le Lab

### Jour 5 (30 min)
1. Finaliser le Lab
2. Passer le QCM (15 questions)

> **Total**: ~6h30 pour une compréhension approfondie

## 🎯 Mode accéléré (2h)

Si vous manquez de temps:

1. **Lecture rapide** (45 min)
   - Survol Guide Envoy (focus chapitres 1, 2, 5)
   - Survol Guide React (focus chapitres 1, 3, 5, 7)

2. **Pratique** (1h)
   - Tester 1 config Envoy
   - Étudier exemples 01, 03, 05, 06
   - Commencer le Lab

3. **Évaluation** (15 min)
   - QCM

> ⚠️ Mode accéléré = compréhension de surface. Recommandé uniquement si très à l'aise avec React.

## 💡 Conseils pour réussir

### 1. Apprentissage actif
- ✅ N'hésitez pas à modifier les exemples
- ✅ Testez chaque configuration Envoy
- ✅ Expérimentez avec les stubs générés
- ❌ Ne vous contentez pas de lire passivement

### 2. Documentation
- Gardez les guides PDF ouverts pendant le lab
- Bookmarkez les pages importantes
- Prenez des notes sur ce qui n'est pas clair

### 3. Debugging
- Utilisez les DevTools Chrome/Firefox
- Activez les logs détaillés Envoy
- Consultez la section "Debugging" avant de bloquer

### 4. Communauté
- Posez vos questions sur le forum
- Partagez vos découvertes
- Aidez les autres apprenants

## 🔧 Troubleshooting commun

### Problème: protoc ne trouve pas le plugin gRPC-Web

**Solution**:
```bash
# Télécharger le plugin manuellement
# https://github.com/grpc/grpc-web/releases
# Exemple pour Linux:
wget https://github.com/grpc/grpc-web/releases/download/1.5.0/protoc-gen-grpc-web-1.5.0-linux-x86_64
chmod +x protoc-gen-grpc-web-1.5.0-linux-x86_64
sudo mv protoc-gen-grpc-web-1.5.0-linux-x86_64 /usr/local/bin/protoc-gen-grpc-web
```

### Problème: Erreurs CORS avec Envoy

**Solution**:
- Vérifiez la configuration CORS dans `envoy.yaml`
- Utilisez la config `envoy-with-cors.yaml` fournie
- Consultez le chapitre 5 du Guide Envoy

### Problème: React ne trouve pas les stubs générés

**Solution**:
```bash
# Vérifier que les stubs sont bien générés
ls -la src/proto/

# Vérifier les imports dans votre code
# Doit être: import { UserServiceClient } from './proto/user_grpc_web_pb';
```

### Problème: Docker Envoy ne démarre pas

**Solution**:
```bash
# Voir les logs
docker-compose logs envoy

# Vérifier la syntaxe du fichier envoy.yaml
# Utiliser un validateur YAML en ligne
```

## 📞 Support

### Ressources
1. **Forum de la séquence** - Questions générales
2. **Forum technique** - Problèmes d'installation/config
3. **Documentation officielle** - Liens dans README.md

### Horaires de support
- Forum: Réponse sous 24h max
- Sessions live: Consultez le calendrier Moodle

## ✅ Checklist avant de commencer

Avant de passer à la première activité, vérifiez:

- [ ] Tous les outils sont installés (node, npm, protoc, docker)
- [ ] Les guides PDF sont téléchargés
- [ ] Les dossiers de code sont décompressés
- [ ] Le répertoire de travail est créé
- [ ] Le script `check-setup.sh` affiche tous les ✅
- [ ] Vous avez lu ce guide en entier

## 🎉 Vous êtes prêt!

Si tous les points de la checklist sont cochés, vous pouvez commencer l'activité 1:

**👉 Rendez-vous dans `01-introduction/grpc-web-introduction.md`**

Bon apprentissage! 🚀

---

*Dernière mise à jour: 2024*  
*Questions? Postez sur le forum de la Séquence 6*
