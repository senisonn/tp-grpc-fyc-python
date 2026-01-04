import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps

from src.config import config
from src.clients.auth_client import AuthClient
from src.clients.chat_client import ChatClient
from src.websocket_handler import init_socketio

sys.stdout = sys.stderr
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = config.SECRET_KEY

# Clients
auth_client = AuthClient()
chat_client = ChatClient()

# Initialiser WebSocket
socketio = init_socketio(app)

def require_auth(f):
    """Décorateur pour vérifier le JWT"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token manquant'}), 401
        
        token = auth_header.split(' ')[1]
        result = auth_client.validate_token(token)
        
        if not result.get('valid'):
            return jsonify({'error': 'Token invalide'}), 401
        
        request.user = result.get('user')
        return f(*args, **kwargs)
    
    return decorated

# ===================================
# HEALTH
# ===================================

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'gateway',
        'version': '1.0.0',
        'features': ['REST', 'WebSocket', 'gRPC Streaming']
    })

# ===================================
# ROOMS
# ===================================

@app.route('/api/rooms', methods=['POST'])
@require_auth
def create_room():
    """Créer une room"""
    data = request.get_json()
    try:
        room = chat_client.create_room(
            name=data.get('name'),
            description=data.get('description', ''),
            created_by=request.user['user_id']
        )
        return jsonify(room), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/rooms', methods=['GET'])
@require_auth
def list_rooms():
    """Lister les rooms"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    try:
        result = chat_client.list_rooms(page, limit)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/rooms/<room_id>/join', methods=['POST'])
@require_auth
def join_room_rest(room_id):
    """Rejoindre une room (REST uniquement - pour compatibilité)"""
    try:
        result = chat_client.join_room(
            room_id=room_id,
            user_id=request.user['user_id'],
            username=request.user['username']
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/rooms/<room_id>/history', methods=['GET'])
@require_auth
def get_history(room_id):
    """Récupérer l'historique des messages"""
    limit = request.args.get('limit', 50, type=int)
    try:
        messages = chat_client.get_room_history(room_id, limit)
        return jsonify({
            'room_id': room_id,
            'messages': messages,
            'count': len(messages)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===================================
# RUN
# ===================================

def run():
    print("="*60)
    print(f"🚀 Gateway sur le port {config.FLASK_PORT}")
    print("="*60)
    print(f"📡 Auth Service: {config.AUTH_SERVICE_URL}")
    print(f"📡 Chat Service: {config.CHAT_SERVICE_HOST}:{config.CHAT_SERVICE_PORT}")
    print()
    print("🔗 Architecture:")
    print("  • REST API: Authentification, Rooms, Historique")
    print("  • WebSocket: Messages temps réel (bidirectionnel)")
    print("  • gRPC: Streaming bidirectionnel vers Chat Service")
    print("="*60)
    
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=config.FLASK_PORT, 
        debug=False, 
        use_reloader=False,
        allow_unsafe_werkzeug=True  
    )

if __name__ == '__main__':
    run()