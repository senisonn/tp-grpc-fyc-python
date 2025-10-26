@echo off
echo Compilation du fichier user.proto en cours...

cd ..

REM On compile dans le dossier courant
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. user.proto

IF %ERRORLEVEL% EQU 0 (
    echo    Compilation terminée avec succès !
    echo    Fichiers générés : user_pb2.py et user_pb2_grpc.py dans le dossier courant.
) ELSE (
    echo    Erreur lors de la compilation du fichier .proto
)

pause
