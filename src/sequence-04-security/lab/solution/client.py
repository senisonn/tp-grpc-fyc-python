import grpc
import user_pb2
import user_pb2_grpc


def login(stub, username, password):
    """
    Se connecter et obtenir un token JWT.
    
    Args:
        stub: Stub du service UserService
        username: Nom d'utilisateur
        password: Mot de passe
    
    Returns:
        str: Token JWT si succès, None sinon
    """
    print(f"\n🔐 Connexion avec l'utilisateur: {username}")
    
    request = user_pb2.LoginRequest(
        username=username,
        password=password
    )
    
    try:
        response = stub.Login(request)
        
        if response.token:
            print(f"✅ {response.message}")
            print(f"   User ID: {response.user_id}")
            print(f"   Token: {response.token[:50]}...{response.token[-10:]}")
            return response.token
        else:
            print(f"❌ {response.message}")
            return None
    
    except grpc.RpcError as e:
        print(f"❌ Erreur gRPC: {e.code()} - {e.details()}")
        return None


def get_profile(stub, user_id, token):
    """
    Récupérer le profil d'un utilisateur (nécessite authentification).
    
    Args:
        stub: Stub du service UserService
        user_id: ID de l'utilisateur
        token: Token JWT
    """
    print(f"\n👤 Récupération du profil (user_id: {user_id})")
    
    request = user_pb2.GetProfileRequest(user_id=user_id)
    
    # CRUCIAL: Passer le token dans les metadata
    metadata = [('authorization', f'Bearer {token}')]
    
    try:
        response = stub.GetProfile(request, metadata=metadata)
        
        if response.error:
            print(f"❌ Erreur: {response.error}")
        else:
            print(f"✅ Profil récupéré:")
            print(f"   ID: {response.user.id}")
            print(f"   Username: {response.user.username}")
            print(f"   Email: {response.user.email}")
            print(f"   Nom complet: {response.user.full_name}")
    
    except grpc.RpcError as e:
        print(f"❌ Erreur gRPC: {e.code()} - {e.details()}")


def update_profile(stub, user_id, email, full_name, token):
    """
    Mettre à jour le profil d'un utilisateur (nécessite authentification).
    
    Args:
        stub: Stub du service UserService
        user_id: ID de l'utilisateur
        email: Nouvel email
        full_name: Nouveau nom complet
        token: Token JWT
    """
    print(f"\n✏️  Mise à jour du profil (user_id: {user_id})")
    print(f"   Nouvel email: {email}")
    print(f"   Nouveau nom: {full_name}")
    
    request = user_pb2.UpdateProfileRequest(
        user_id=user_id,
        email=email,
        full_name=full_name
    )
    
    # CRUCIAL: Passer le token dans les metadata
    metadata = [('authorization', f'Bearer {token}')]
    
    try:
        response = stub.UpdateProfile(request, metadata=metadata)
        
        if response.success:
            print(f"✅ {response.message}")
        else:
            print(f"❌ {response.message}")
    
    except grpc.RpcError as e:
        print(f"❌ Erreur gRPC: {e.code()} - {e.details()}")


def test_authentication():
    """
    Lance une batterie de tests pour vérifier l'authentification.
    """
    with grpc.insecure_channel('localhost:50053') as channel:
        stub = user_pb2_grpc.UserServiceStub(channel)
        
        print("=" * 70)
        print("🔒 CLIENT SÉCURISÉ - TESTS D'AUTHENTIFICATION")
        print("=" * 70)
        
        # ========== TEST 1: Login réussi ==========
        print("\n" + "─" * 70)
        print("TEST 1: Connexion avec identifiants valides")
        print("─" * 70)
        token = login(stub, "alice", "password123")
        
        if not token:
            print("\n❌ Tests arrêtés: impossible de se connecter")
            return
        
        # ========== TEST 2: Récupérer le profil avec token valide ==========
        print("\n" + "─" * 70)
        print("TEST 2: Récupération du profil (avec token valide)")
        print("─" * 70)
        get_profile(stub, 1, token)
        
        # ========== TEST 3: Mettre à jour le profil ==========
        print("\n" + "─" * 70)
        print("TEST 3: Mise à jour du profil")
        print("─" * 70)
        update_profile(stub, 1, "alice.dupont@example.com", "Alice DUPONT", token)
        
        # ========== TEST 4: Vérifier la mise à jour ==========
        print("\n" + "─" * 70)
        print("TEST 4: Vérification de la mise à jour")
        print("─" * 70)
        get_profile(stub, 1, token)
        
        # ========== TEST 5: Tentative sans token ==========
        print("\n" + "─" * 70)
        print("TEST 5: Tentative d'accès SANS token (doit échouer)")
        print("─" * 70)
        get_profile(stub, 1, "")
        
        # ========== TEST 6: Token invalide ==========
        print("\n" + "─" * 70)
        print("TEST 6: Token invalide (doit échouer)")
        print("─" * 70)
        get_profile(stub, 1, "fake_token_123_invalid")
        
        # ========== TEST 7: Token malformé ==========
        print("\n" + "─" * 70)
        print("TEST 7: Token sans 'Bearer' (doit échouer)")
        print("─" * 70)
        try:
            request = user_pb2.GetProfileRequest(user_id=1)
            metadata = [('authorization', token)]  # Sans "Bearer "
            stub.GetProfile(request, metadata=metadata)
        except grpc.RpcError as e:
            print(f"❌ Erreur gRPC (attendue): {e.code()} - {e.details()}")
        
        # ========== TEST 8: Mauvais identifiants ==========
        print("\n" + "─" * 70)
        print("TEST 8: Connexion avec mauvais mot de passe")
        print("─" * 70)
        login(stub, "alice", "wrong_password")
        
        # ========== TEST 9: Utilisateur inexistant ==========
        print("\n" + "─" * 70)
        print("TEST 9: Connexion avec utilisateur inexistant")
        print("─" * 70)
        login(stub, "hacker", "password")
        
        # ========== TEST 10: Accéder au profil d'un autre utilisateur ==========
        print("\n" + "─" * 70)
        print("TEST 10: Bob se connecte et accède à son profil")
        print("─" * 70)
        bob_token = login(stub, "bob", "secret456")
        if bob_token:
            get_profile(stub, 2, bob_token)
        
        print("\n" + "=" * 70)
        print("✅ TOUS LES TESTS TERMINÉS")
        print("=" * 70)


def interactive_mode():
    """
    Mode interactif pour tester manuellement.
    """
    with grpc.insecure_channel('localhost:50053') as channel:
        stub = user_pb2_grpc.UserServiceStub(channel)
        token = None
        user_id = None
        
        print("=" * 70)
        print("🔒 CLIENT INTERACTIF - SERVICE UTILISATEUR SÉCURISÉ")
        print("=" * 70)
        
        while True:
            print("\n📋 Menu:")
            print("1. Se connecter")
            print("2. Voir mon profil")
            print("3. Modifier mon profil")
            print("4. Se déconnecter")
            print("0. Quitter")
            
            choice = input("\nVotre choix: ").strip()
            
            if choice == "0":
                print("👋 Au revoir !")
                break
            
            elif choice == "1":
                username = input("Username: ")
                password = input("Password: ")
                token = login(stub, username, password)
                if token:
                    # Récupérer l'ID utilisateur (simplifié pour cet exemple)
                    if username == "alice":
                        user_id = 1
                    elif username == "bob":
                        user_id = 2
                    elif username == "charlie":
                        user_id = 3
            
            elif choice == "2":
                if not token:
                    print("❌ Vous devez d'abord vous connecter (option 1)")
                else:
                    get_profile(stub, user_id, token)
            
            elif choice == "3":
                if not token:
                    print("❌ Vous devez d'abord vous connecter (option 1)")
                else:
                    email = input("Nouvel email: ")
                    full_name = input("Nouveau nom complet: ")
                    update_profile(stub, user_id, email, full_name, token)
            
            elif choice == "4":
                token = None
                user_id = None
                print("✅ Déconnecté")
            
            else:
                print("❌ Choix invalide")


if __name__ == '__main__':
    import sys
    
    # Si argument "--test", lancer les tests automatiques
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_authentication()
    else:
        # Sinon, mode interactif
        print("\n💡 Lancez avec --test pour les tests automatiques")
        print("   Ou utilisez le mode interactif ci-dessous\n")
        interactive_mode()