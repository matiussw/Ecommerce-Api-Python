from flask import Blueprint, request, jsonify
from app import db
from app.models import Users, RoleS, Sales
import jwt
import os

user_bp = Blueprint('users', __name__)

def get_user_from_token():
    """Obtener usuario del token JWT"""
    token = request.headers.get('Authorization')
    if not token:
        return None
    
    if token.startswith('Bearer '):
        token = token[7:]
    
    try:
        payload = jwt.decode(token, os.getenv('SECRET_KEY', 'HolaMundo'), algorithms=['HS256'])
        return Users.query.get(payload['user_id'])
    except:
        return None

@user_bp.route('/profile', methods=['GET'])
def get_profile():
    """Obtener perfil del usuario actual"""
    try:
        user = get_user_from_token()
        if not user:
            return jsonify({'error': 'Token inválido'}), 401
        
        return jsonify({
            'user': user.to_dict(include_roles=True)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/profile', methods=['PUT'])
def update_profile():
    """Actualizar perfil del usuario actual"""
    try:
        user = get_user_from_token()
        if not user:
            return jsonify({'error': 'Token inválido'}), 401
        
        data = request.get_json()
        
        # Campos que se pueden actualizar
        if 'UserName' in data:
            user.UserName = data['UserName']
        
        if 'iD_City' in data:
            user.iD_City = data['iD_City']
        
        # Verificar si el email cambió y no está en uso
        if 'Email' in data and data['Email'] != user.Email:
            existing_user = Users.query.filter_by(Email=data['Email']).first()
            if existing_user:
                return jsonify({'error': 'El email ya está en uso'}), 409
            user.Email = data['Email']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Perfil actualizado exitosamente',
            'user': user.to_dict(include_roles=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/', methods=['GET'])
def get_users():
    """Obtener todos los usuarios (solo admin)"""
    try:
        user = get_user_from_token()
        if not user:
            return jsonify({'error': 'Token inválido'}), 401
        
        # Verificar si es admin
        is_admin = any(role.TypeRole == 'Administrador' for role in user.roles)
        if not is_admin:
            return jsonify({'error': 'No tienes permisos de administrador'}), 403
        
        # Parámetros de consulta
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        
        # Construir query
        query = Users.query
        
        if search:
            query = query.filter(
                (Users.UserName.contains(search)) |
                (Users.Email.contains(search))
            )
        
        # Paginación
        users = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'users': [u.to_dict(include_roles=True) for u in users.items],
            'pagination': {
                'page': page,
                'pages': users.pages,
                'per_page': per_page,
                'total': users.total
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Obtener un usuario específico (solo admin o el mismo usuario)"""
    try:
        current_user = get_user_from_token()
        if not current_user:
            return jsonify({'error': 'Token inválido'}), 401
        
        # Verificar permisos
        is_admin = any(role.TypeRole == 'Administrador' for role in current_user.roles)
        if not is_admin and current_user.iD_User != user_id:
            return jsonify({'error': 'No tienes permiso para ver este usuario'}), 403
        
        target_user = Users.query.get_or_404(user_id)
        
        return jsonify({
            'user': target_user.to_dict(include_roles=True)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/<int:user_id>/roles', methods=['PUT'])
def update_user_roles(user_id):
    """Actualizar roles de un usuario (solo admin)"""
    try:
        current_user = get_user_from_token()
        if not current_user:
            return jsonify({'error': 'Token inválido'}), 401
        
        # Verificar si es admin
        is_admin = any(role.TypeRole == 'Administrador' for role in current_user.roles)
        if not is_admin:
            return jsonify({'error': 'No tienes permisos de administrador'}), 403
        
        target_user = Users.query.get_or_404(user_id)
        data = request.get_json()
        
        if 'role_ids' not in data:
            return jsonify({'error': 'role_ids es requerido'}), 400
        
        # Limpiar roles actuales
        target_user.roles.clear()
        
        # Agregar nuevos roles
        for role_id in data['role_ids']:
            role = RoleS.query.get(role_id)
            if role:
                target_user.roles.append(role)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Roles actualizados exitosamente',
            'user': target_user.to_dict(include_roles=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Eliminar un usuario (solo admin)"""
    try:
        current_user = get_user_from_token()
        if not current_user:
            return jsonify({'error': 'Token inválido'}), 401
        
        # Verificar si es admin
        is_admin = any(role.TypeRole == 'Administrador' for role in current_user.roles)
        if not is_admin:
            return jsonify({'error': 'No tienes permisos de administrador'}), 403
        
        # No permitir auto-eliminación
        if current_user.iD_User == user_id:
            return jsonify({'error': 'No puedes eliminar tu propia cuenta'}), 400
        
        target_user = Users.query.get_or_404(user_id)
        
        # Verificar si tiene ventas asociadas
        if target_user.sales:
            return jsonify({
                'error': 'No se puede eliminar un usuario con ventas asociadas'
            }), 400
        
        db.session.delete(target_user)
        db.session.commit()
        
        return jsonify({'message': 'Usuario eliminado exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/<int:user_id>/sales', methods=['GET'])
def get_user_sales(user_id):
    """Obtener ventas de un usuario específico"""
    try:
        current_user = get_user_from_token()
        if not current_user:
            return jsonify({'error': 'Token inválido'}), 401
        
        # Verificar permisos
        is_admin = any(role.TypeRole == 'Administrador' for role in current_user.roles)
        if not is_admin and current_user.iD_User != user_id:
            return jsonify({'error': 'No tienes permiso para ver las ventas de este usuario'}), 403
        
        target_user = Users.query.get_or_404(user_id)
        
        # Parámetros de consulta
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        sales = Sales.query.filter_by(iD_User=user_id).order_by(
            Sales.DateCreated.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'user': target_user.to_dict(),
            'sales': [sale.to_dict(include_details=True) for sale in sales.items],
            'pagination': {
                'page': page,
                'pages': sales.pages,
                'per_page': per_page,
                'total': sales.total
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/stats', methods=['GET'])
def get_users_stats():
    """Obtener estadísticas de usuarios (solo admin)"""
    try:
        current_user = get_user_from_token()
        if not current_user:
            return jsonify({'error': 'Token inválido'}), 401
        
        # Verificar si es admin
        is_admin = any(role.TypeRole == 'Administrador' for role in current_user.roles)
        if not is_admin:
            return jsonify({'error': 'No tienes permisos de administrador'}), 403
        
        # Estadísticas generales
        total_users = Users.query.count()
        
        # Usuarios por rol
        roles_stats = []
        roles = RoleS.query.all()
        for role in roles:
            user_count = len(role.users)
            roles_stats.append({
                'role': role.to_dict(),
                'user_count': user_count
            })
        
        # Usuarios con más ventas
        from sqlalchemy import func
        top_buyers = db.session.query(
            Users,
            func.count(Sales.id_Sale).label('sales_count')
        ).join(Sales).group_by(Users.iD_User).order_by(
            func.count(Sales.id_Sale).desc()
        ).limit(5).all()
        
        top_buyers_data = []
        for user, sales_count in top_buyers:
            user_data = user.to_dict()
            user_data['sales_count'] = sales_count
            top_buyers_data.append(user_data)
        
        return jsonify({
            'total_users': total_users,
            'roles_distribution': roles_stats,
            'top_buyers': top_buyers_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/search', methods=['GET'])
def search_users():
    """Buscar usuarios (solo admin)"""
    try:
        current_user = get_user_from_token()
        if not current_user:
            return jsonify({'error': 'Token inválido'}), 401
        
        # Verificar si es admin
        is_admin = any(role.TypeRole == 'Administrador' for role in current_user.roles)
        if not is_admin:
            return jsonify({'error': 'No tienes permisos de administrador'}), 403
        
        query_text = request.args.get('q', '')
        if not query_text:
            return jsonify({'users': []}), 200
        
        users = Users.query.filter(
            (Users.UserName.contains(query_text)) |
            (Users.Email.contains(query_text))
        ).limit(20).all()
        
        return jsonify({
            'users': [user.to_dict(include_roles=True) for user in users],
            'count': len(users)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500