#!/bin/bash

echo "Compilation du fichier user.proto en cours..."
cd ..

# On compile dans le dossier courant
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. user.proto

if [ $? -eq 0 ]; then
    echo "   Compilation terminée avec succès !"
    echo "   Fichiers générés : user_pb2.py et user_pb2_grpc.py dans le dossier courant."
else
    echo "   Erreur lors de la compilation du fichier .proto"
fi

read -p "Appuyez sur Entrée pour continuer..."