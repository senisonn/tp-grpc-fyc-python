try:
    from user_pb2 import User, UserIdRequest
    print("✅ Import réussi")
except ImportError as e:
    print(f"❌ Erreur d'import : {e}")
    exit(1)

    
# Création d'un utilisateur
user = User(id=1, name="Alice", email="alice@example.com")

# Sérialisation
data = user.SerializeToString()
print("✅ Données sérialisées :", data)

# Désérialisation
user2 = User()
user2.ParseFromString(data)
print("✅ Données désérialisées :")
print(user2)
