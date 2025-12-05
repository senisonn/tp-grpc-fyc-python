# Lab Starter Code - Backend gRPC Python

## Installation
```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
./generate_proto.sh
```

## Structure
- proto/ - Fichier user.proto fourni
- generated/ - Stubs générés (après generate_proto.sh)
- services/ - Implémentez UserService ici
- interceptors/ - Logging et auth interceptors
- tests/ - Tests pytest

## Objectifs (30 points)
1. Service CRUD (12 pts)
2. Gestion erreurs (8 pts)
3. Intercepteurs (6 pts)
4. Tests (4 pts)

Voir instructions complètes dans le lab assignment.
