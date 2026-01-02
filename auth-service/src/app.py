from flask import Flask, request, jsonify
from flask_cors import CORS
from src.config import config
from src.models.user import UserStore
from src.utils.jwt_helper import JWTHelper
from src.clients.logging_client import LoggingClient

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = config.SECRET_KEY

# Store utilisateurs (en mémoire)
user_store = UserStore()

# Client de logging
logger = LoggingClient()

@app.route('/health', methods=['GET'])
def health():
    """Health check du service"""
    return jsonify({
        'status': 'healthy',
        'service': 'auth-service',
        'version': '1.0.0'
    })

@app.route('/auth/register', methods=['POST'])
def register():
    """Inscription d'un nouvel utilisateur"""
    try:
        data = request.get_json()
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        # Validation
        if not username or not email or not password:
            logger.warning("Tentative d'inscription avec champs manquants", username=username or "N/A")
            return jsonify({
                'success': False,
                'error': 'Champs manquants (username, email, password requis)'
            }), 400
        
        if len(password) < 6:
            logger.warning(f"Mot de passe trop court pour {username}")
            return jsonify({
                'success': False,
                'error': 'Le mot de passe doit faire au moins 6 caractères'
            }), 400
        
        # Créer l'utilisateur
        user = user_store.create_user(username, email, password)
        
        if not user:
            logger.warning(f"Tentative de création d'utilisateur existant: {username}")
            return jsonify({
                'success': False,
                'error': 'Utilisateur déjà existant'
            }), 409
        
        # LOG SUCCESS
        logger.info(
            f"Nouvel utilisateur créé: {username}",
            user_id=user.user_id,
            email=email,
            action="register"
        )
        
        return jsonify({
            'success': True,
            'message': 'Utilisateur créé avec succès',
            'user': user.to_dict()
        }), 201
    
    except Exception as e:
        logger.error(f"Erreur lors de l'inscription: {str(e)}", action="register")
        return jsonify({
            'success': False,
            'error': f'Erreur serveur: {str(e)}'
        }), 500

@app.route('/auth/login', methods=['POST'])
def login():
    """Connexion utilisateur"""
    try:
        data = request.get_json()
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            logger.warning("Tentative de login avec champs manquants")
            return jsonify({
                'success': False,
                'error': 'Champs manquants (username et password requis)'
            }), 400
        
        # Récupérer l'utilisateur
        user = user_store.get_user_by_username(username)
        
        if not user or not user.check_password(password):
            logger.warning(f"Tentative de login échouée pour: {username}", action="login_failed")
            return jsonify({
                'success': False,
                'error': 'Identifiants invalides'
            }), 401
        
        # Générer le token JWT
        token = JWTHelper.generate_token(user.user_id, user.username)
        
        # LOG SUCCESS
        logger.info(
            f"Login réussi pour: {username}",
            user_id=user.user_id,
            action="login"
        )
        
        return jsonify({
            'success': True,
            'token': token,
            'user': user.to_dict()
        })
    
    except Exception as e:
        logger.error(f"Erreur lors du login: {str(e)}", action="login")
        return jsonify({
            'success': False,
            'error': f'Erreur serveur: {str(e)}'
        }), 500

@app.route('/auth/validate', methods=['POST'])
def validate():
    """Valider un token JWT"""
    try:
        data = request.get_json() or {}
        token = data.get('token')
        
        # Si pas dans le body, chercher dans le header
        if not token:
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({
                'valid': False,
                'error': 'Token manquant'
            }), 400
        
        # Décoder et valider le token
        payload = JWTHelper.decode_token(token)
        user = user_store.get_user_by_id(payload['user_id'])
        
        logger.info(
            f"Token validé pour: {payload.get('username')}",
            user_id=payload.get('user_id'),
            action="validate_token"
        )
        
        return jsonify({
            'valid': True,
            'user': user.to_dict() if user else None,
            'payload': {
                'user_id': payload['user_id'],
                'username': payload['username'],
                'exp': payload['exp']
            }
        })
    
    except ValueError as e:
        logger.warning(f"Token invalide: {str(e)}", action="validate_token_failed")
        return jsonify({
            'valid': False,
            'error': str(e)
        }), 401
    except Exception as e:
        logger.error(f"Erreur validation token: {str(e)}", action="validate_token")
        return jsonify({
            'valid': False,
            'error': f'Erreur serveur: {str(e)}'
        }), 500

@app.route('/auth/me', methods=['GET'])
def me():
    """Obtenir les informations de l'utilisateur connecté"""
    try:
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'error': 'Token manquant'
            }), 401
        
        token = auth_header.split(' ')[1]
        
        # Décoder le token
        payload = JWTHelper.decode_token(token)
        user = user_store.get_user_by_id(payload['user_id'])
        
        if not user:
            return jsonify({
                'error': 'Utilisateur non trouvé'
            }), 404
        
        return jsonify(user.to_dict())
    
    except ValueError as e:
        return jsonify({
            'error': str(e)
        }), 401
    except Exception as e:
        return jsonify({
            'error': f'Erreur serveur: {str(e)}'
        }), 500

@app.route('/auth/users', methods=['GET'])
def list_users():
    """Lister tous les utilisateurs (pour debug)"""
    users = [user.to_dict() for user in user_store.users.values()]
    return jsonify({
        'total': len(users),
        'users': users
    })

def run():
    """Démarrer le serveur Flask"""
    print("="*60)
    print(f"🚀 Auth Service (Flask) démarré sur le port {config.FLASK_PORT}")
    print("="*60)
    print(f"📝 Utilisateurs de test créés:")
    print(f"   - Username: admin  | Password: admin123")
    print(f"   - Username: alice  | Password: alice123")
    print()
    print(f"🔗 Endpoints disponibles:")
    print(f"   POST /auth/register  - Créer un compte")
    print(f"   POST /auth/login     - Se connecter")
    print(f"   POST /auth/validate  - Valider un token")
    print(f"   GET  /auth/me        - Infos utilisateur")
    print(f"   GET  /health         - Health check")
    print("="*60)
    
    # Log du démarrage
    logger.info("Auth Service démarré", port=config.FLASK_PORT)
    
    app.run(host='0.0.0.0', port=config.FLASK_PORT, debug=True)

if __name__ == '__main__':
    run()