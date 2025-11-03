import grpc
from concurrent import futures
import user_pb2
import user_pb2_grpc
from auth_interceptor import AuthInterceptor, generate_token

# Base de données simulée (en prod, utiliser une vraie DB)
# ATTENTION: Les mots de passe ne doivent JAMAIS être stockés en clair en production !
# Utilisez bcrypt ou argon2 pour hasher les mots de passe
USERS_DB = {
    "alice": {
        "id": 1,
        "password": "password123",  # En prod: hash bcrypt
        "email": "alice@example.com",
        "full_name": "Alice Dupont"
    },
    "bob": {
        "id": 2,
        "password": "secret456",
        "email": "bob@example.com",
        "full_name": "Bob Martin"
    },
    "charlie": {
        "id": 3,
        "password": "charlie789",
        "email": "charlie@example.com",
        "full_name": "Charlie Dubois"
    }
}


class UserServiceServicer(user_pb2_grpc.UserServiceServicer):
    """
    Implémentation du service utilisateur avec authentification.
    """
    
    def Login(self, request, context):
        """
        Authentifie un utilisateur et génère un token JWT.
        Cette méthode est publique (pas de vérification de token).
        
        Args:
            request: LoginRequest contenant username et password
            context: Contexte gRPC
        
        Returns:
            LoginResponse avec token si succès, ou message d'erreur
        """
        print(f"\n🔐 Tentative de connexion: {request.username}")
        
        # Vérifier si l'utilisateur existe
        user = USERS_DB.get(request.username)
        
        if not user:
            print(f"   ❌ Utilisateur '{request.username}' non trouvé")
            return user_pb2.LoginResponse(
                token="",
                user_id=0,
                message="Identifiants incorrects"
            )
        
        # Vérifier le mot de passe
        # En prod: utiliser bcrypt.checkpw(request.password, user['password_hash'])
        if user['password'] != request.password:
            print(f"   ❌ Mot de passe incorrect pour '{request.username}'")
            return user_pb2.LoginResponse(
                token="",
                user_id=0,
                message="Identifiants incorrects"
            )
        
        # Générer le token JWT
        token = generate_token(user['id'], request.username)
        
        print(f"   ✅ Connexion réussie pour '{request.username}'")
        
        return user_pb2.LoginResponse(
            token=token,
            user_id=user['id'],
            message="Connexion réussie"
        )
    
    def GetProfile(self, request, context):
        """
        Récupère le profil d'un utilisateur.
        Cette méthode est PROTÉGÉE (token vérifié par l'interceptor).
        
        Args:
            request: GetProfileRequest avec user_id
            context: Contexte gRPC
        
        Returns:
            GetProfileResponse avec les infos utilisateur
        """
        print(f"\n👤 Récupération du profil pour user_id: {request.user_id}")
        
        # L'interceptor a déjà vérifié le token, on peut traiter la requête
        
        # Trouver l'utilisateur par ID
        user = None
        username_found = None
        
        for username, data in USERS_DB.items():
            if data['id'] == request.user_id:
                user = data
                username_found = username
                break
        
        if not user:
            print(f"   ❌ Utilisateur avec ID {request.user_id} non trouvé")
            return user_pb2.GetProfileResponse(
                error="Utilisateur non trouvé"
            )
        
        # Créer l'objet User
        user_obj = user_pb2.User(
            id=user['id'],
            username=username_found,
            email=user['email'],
            full_name=user['full_name']
        )
        
        print(f"   ✅ Profil récupéré pour '{username_found}'")
        
        return user_pb2.GetProfileResponse(
            user=user_obj,
            error=""
        )
    
    def UpdateProfile(self, request, context):
        """
        Met à jour le profil d'un utilisateur.
        Cette méthode est PROTÉGÉE (token vérifié par l'interceptor).
        
        Args:
            request: UpdateProfileRequest avec user_id, email, full_name
            context: Contexte gRPC
        
        Returns:
            UpdateProfileResponse avec succès ou erreur
        """
        print(f"\n✏️  Mise à jour du profil pour user_id: {request.user_id}")
        print(f"   Nouvel email: {request.email}")
        print(f"   Nouveau nom: {request.full_name}")
        
        # L'interceptor a déjà vérifié le token
        
        # Trouver et mettre à jour l'utilisateur
        for username, data in USERS_DB.items():
            if data['id'] == request.user_id:
                # Mettre à jour les données
                data['email'] = request.email
                data['full_name'] = request.full_name
                
                print(f"   ✅ Profil mis à jour pour '{username}'")
                
                return user_pb2.UpdateProfileResponse(
                    success=True,
                    message="Profil mis à jour avec succès"
                )
        
        print(f"   ❌ Utilisateur avec ID {request.user_id} non trouvé")
        
        return user_pb2.UpdateProfileResponse(
            success=False,
            message="Utilisateur non trouvé"
        )


def serve():
    """
    Démarre le serveur gRPC avec l'interceptor d'authentification.
    """
    # Créer l'interceptor d'authentification
    interceptors = [AuthInterceptor()]
    
    # Créer le serveur avec l'interceptor
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        interceptors=interceptors  # ← CRUCIAL: Ajouter l'interceptor ici !
    )
    
    # Enregistrer le service
    user_pb2_grpc.add_UserServiceServicer_to_server(UserServiceServicer(), server)
    
    # Écouter sur le port 50053
    server.add_insecure_port('[::]:50053')
    
    # Démarrer le serveur
    server.start()
    
    print("=" * 70)
    print("🔒 SERVEUR UTILISATEUR SÉCURISÉ DÉMARRÉ")
    print("=" * 70)
    print("📡 Port: 50053")
    print("🔐 Authentification: JWT")
    print("👥 Utilisateurs disponibles:")
    for username, data in USERS_DB.items():
        print(f"   - {username} (ID: {data['id']}, password: {data['password']})")
    print("\n📝 Méthodes disponibles:")
    print("   🔓 Login - Publique")
    print("   🔒 GetProfile - Protégée (token requis)")
    print("   🔒 UpdateProfile - Protégée (token requis)")
    print("\n⌛ En attente de connexions...\n")
    print("=" * 70)
    
    # Attendre l'arrêt
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt du serveur...")
        server.stop(0)


if __name__ == '__main__':
    serve()