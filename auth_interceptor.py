import grpc
import jwt
from datetime import datetime, timedelta

# Clé secrète pour signer les JWT (en prod, à mettre dans une variable d'environnement !)
SECRET_KEY = "votre_cle_secrete_super_secure_123_ne_jamais_commit_ca"

# Liste des méthodes qui ne nécessitent pas d'authentification
PUBLIC_METHODS = [
    '/UserService/Login'
]


class AuthInterceptor(grpc.ServerInterceptor):
    """
    Interceptor qui vérifie l'authentification pour toutes les requêtes.
    Les méthodes listées dans PUBLIC_METHODS ne sont pas vérifiées.
    """
    
    def intercept_service(self, continuation, handler_call_details):
        """
        Méthode appelée pour CHAQUE requête gRPC.
        
        Args:
            continuation: Fonction pour continuer le traitement
            handler_call_details: Détails de l'appel (méthode, metadata, etc.)
        """
        method_name = handler_call_details.method
        
        print(f"🔍 Interception de la méthode: {method_name}")
        
        # Si la méthode est publique, on laisse passer sans vérification
        if method_name in PUBLIC_METHODS:
            print(f"   ✅ Méthode publique, pas de vérification nécessaire")
            return continuation(handler_call_details)
        
        # Récupérer les metadata (équivalent des headers HTTP)
        metadata = dict(handler_call_details.invocation_metadata)
        authorization = metadata.get('authorization', '')
        
        # Vérifier que le token existe et commence par "Bearer "
        if not authorization:
            print(f"   ❌ Aucun token fourni")
            return self._deny_access("Token d'authentification manquant")
        
        if not authorization.startswith('Bearer '):
            print(f"   ❌ Format de token invalide")
            return self._deny_access("Format de token invalide (doit être 'Bearer <token>')")
        
        # Extraire le token (enlever "Bearer ")
        token = authorization[7:]
        
        # Vérifier et décoder le token JWT
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            print(f"   ✅ Token valide pour l'utilisateur: {payload.get('username')} (ID: {payload.get('user_id')})")
            
            # On pourrait ajouter les infos utilisateur au context ici si besoin
            # context.user_id = payload['user_id']
            
            return continuation(handler_call_details)
            
        except jwt.ExpiredSignatureError:
            print(f"   ❌ Token expiré")
            return self._deny_access("Token expiré, veuillez vous reconnecter")
            
        except jwt.InvalidTokenError as e:
            print(f"   ❌ Token invalide: {e}")
            return self._deny_access("Token invalide")
    
    def _deny_access(self, message="Non autorisé"):
        """
        Refuse l'accès en retournant une erreur PERMISSION_DENIED.
        
        Args:
            message: Message d'erreur à renvoyer au client
        """
        def abort(ignored_request, context):
            context.abort(grpc.StatusCode.PERMISSION_DENIED, message)
        
        return grpc.unary_unary_rpc_method_handler(abort)


def generate_token(user_id, username, expiration_hours=1):
    """
    Génère un JWT token pour un utilisateur.
    
    Args:
        user_id: ID de l'utilisateur
        username: Nom d'utilisateur
        expiration_hours: Durée de validité en heures (défaut: 1h)
    
    Returns:
        str: Token JWT encodé
    """
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=expiration_hours),  # Expiration
        'iat': datetime.utcnow()  # Issued at (date de création)
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    print(f"🔑 Token généré pour {username} (expire dans {expiration_hours}h)")
    
    return token


def verify_token(token):
    """
    Vérifie un token JWT et retourne le payload s'il est valide.
    
    Args:
        token: Token JWT à vérifier
    
    Returns:
        dict: Payload du token si valide, None sinon
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        print("❌ Token expiré")
        return None
    except jwt.InvalidTokenError:
        print("❌ Token invalide")
        return None


def decode_token_info(token):
    """
    Décode un token sans le vérifier (utile pour le debug).
    ATTENTION: Ne pas utiliser pour l'authentification !
    
    Args:
        token: Token JWT
    
    Returns:
        dict: Payload décodé
    """
    try:
        # decode avec verify=False pour voir le contenu sans vérifier la signature
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload
    except Exception as e:
        print(f"Erreur lors du décodage: {e}")
        return None