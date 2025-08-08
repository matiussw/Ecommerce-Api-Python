from flask import Blueprint, request, jsonify
from app import db
from app.models import Users, RoleS
from werkzeug.security import generate_password_hash
import jwt
import datetime
import os

auth_bp = Blueprint('auth', __name__)

def generate_token(user):
    """Generar token JWT para el usuario"""
    payload = {
        'user_id': user.iD_User,
        'email': user.Email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    return jwt.encode(payload, os.getenv('SECRET_KEY', 'HolaMundo'), algorithm='HS256')

@auth_bp.route('/register', methods=['POST'])
def register():
    """Registrar nuevo usuario"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['UserName', 'Email', 'PasswoRDkey']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} es requerido'}), 400
        
        # Verificar si el email ya existe
        existing_user = Users.query.filter_by(Email=data['Email']).first()
        if existing_user:
            return jsonify({'error': 'El email ya está registrado'}), 409
        
        # Crear nuevo usuario
        new_user = Users(
            UserName=data['UserName'],
            Email=data['Email']
        )
        new_user.set_password(data['PasswoRDkey'])
        
        # Asignar rol de Cliente por defecto (ID 4 según tus datos)
        client_role = RoleS.query.filter_by(TypeRole='Cliente').first()
        if client_role:
            new_user.roles.append(client_role)
        
        db.session.add(new_user)
        db.session.commit()
        
        # Generar token
        token = generate_token(new_user)
        
        return jsonify({
            'message': 'Usuario registrado exitosamente',
            'user': new_user.to_dict(include_roles=True),
            'token': token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Iniciar sesión"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        if not data.get('Email') or not data.get('PasswoRDkey'):
            return jsonify({'error': 'Email y password son requeridos'}), 400
        
        # Buscar usuario
        user = Users.query.filter_by(Email=data['Email']).first()
        
        if not user or not user.check_password(data['PasswoRDkey']):
            return jsonify({'error': 'Credenciales inválidas'}), 401
        
        # Generar token
        token = generate_token(user)
        
        return jsonify({
            'message': 'Login exitoso',
            'user': user.to_dict(include_roles=True),
            'token': token
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/verify-token', methods=['POST'])
def verify_token():
    """Verificar si un token es válido"""
    try:
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token no proporcionado'}), 401
        
        # Remover 'Bearer ' si está presente
        if token.startswith('Bearer '):
            token = token[7:]
        
        # Decodificar token
        payload = jwt.decode(token, os.getenv('SECRET_KEY', 'HolaMundo'), algorithms=['HS256'])
        
        # Buscar usuario
        user = Users.query.get(payload['user_id'])
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        return jsonify({
            'valid': True,
            'user': user.to_dict(include_roles=True)
        }), 200
        
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expirado'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Token inválido'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/roles', methods=['GET'])
def get_roles():
    """Obtener todos los roles disponibles"""
    try:
        roles = RoleS.query.all()
        return jsonify({
            'roles': [role.to_dict() for role in roles]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/change-password', methods=['PUT'])
def change_password():
    """Cambiar password del usuario"""
    try:
        # Verificar token
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token no proporcionado'}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        payload = jwt.decode(token, os.getenv('SECRET_KEY', 'HolaMundo'), algorithms=['HS256'])
        user = Users.query.get(payload['user_id'])
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        data = request.get_json()
        
        # Validar password actual
        if not user.check_password(data.get('current_password', '')):
            return jsonify({'error': 'Password actual incorrecto'}), 400
        
        # Cambiar password
        user.set_password(data['new_password'])
        db.session.commit()
        
        return jsonify({'message': 'Password cambiado exitosamente'}), 200
        
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expirado'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Token inválido'}), 401
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
