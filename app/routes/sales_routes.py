from flask import Blueprint, request, jsonify
from app import db
from app.models import Sales, SalesDetail, TemporalSales, Product, Users
from datetime import datetime
import jwt
import os

sales_bp = Blueprint('sales', __name__)

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

# ===============================
# RUTAS DEL CARRITO (TemporalSales)
# ===============================

@sales_bp.route('/cart', methods=['GET'])
def get_cart():
    """Obtener carrito del usuario actual"""
    try:
        user = get_user_from_token()
        if not user:
            return jsonify({'error': 'Token inválido'}), 401
        
        # Obtener items del carrito (sin id_Sale)
        cart_items = TemporalSales.query.filter_by(
            iD_User=user.iD_User,
            id_Sale=None
        ).all()
        
        total = sum(item.product.Price * item.quantity for item in cart_items if item.product)
        
        return jsonify({
            'cart_items': [item.to_dict() for item in cart_items],
            'total': total,
            'count': len(cart_items)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sales_bp.route('/cart/add', methods=['POST'])
def add_to_cart():
    """Agregar producto al carrito"""
    try:
        user = get_user_from_token()
        if not user:
            return jsonify({'error': 'Token inválido'}), 401
        
        data = request.get_json()
        
        # Validar datos
        if not data.get('id_Product'):
            return jsonify({'error': 'id_Product es requerido'}), 400
        
        quantity = data.get('quantity', 1)
        if quantity <= 0:
            return jsonify({'error': 'Cantidad debe ser mayor a 0'}), 400
        
        # Verificar que el producto existe y tiene stock
        product = Product.query.get(data['id_Product'])
        if not product:
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        if product.Stock < quantity:
            return jsonify({'error': 'Stock insuficiente'}), 400
        
        # Verificar si ya existe en el carrito
        existing_item = TemporalSales.query.filter_by(
            iD_User=user.iD_User,
            id_Product=data['id_Product'],
            id_Sale=None
        ).first()
        
        if existing_item:
            # Actualizar cantidad
            new_quantity = existing_item.quantity + quantity
            if product.Stock < new_quantity:
                return jsonify({'error': 'Stock insuficiente para la cantidad total'}), 400
            
            existing_item.quantity = new_quantity
            existing_item.DateAdded = datetime.utcnow()
        else:
            # Crear nuevo item
            new_item = TemporalSales(
                iD_User=user.iD_User,
                id_Product=data['id_Product'],
                quantity=quantity
            )
            db.session.add(new_item)
        
        db.session.commit()
        
        return jsonify({'message': 'Producto agregado al carrito'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@sales_bp.route('/cart/update/<int:item_id>', methods=['PUT'])
def update_cart_item(item_id):
    """Actualizar cantidad de un item del carrito"""
    try:
        user = get_user_from_token()
        if not user:
            return jsonify({'error': 'Token inválido'}), 401
        
        data = request.get_json()
        quantity = data.get('quantity', 1)
        
        if quantity <= 0:
            return jsonify({'error': 'Cantidad debe ser mayor a 0'}), 400
        
        # Buscar item del carrito
        cart_item = TemporalSales.query.filter_by(
            id_TemporalSales=item_id,
            iD_User=user.iD_User,
            id_Sale=None
        ).first_or_404()
        
        # Verificar stock
        if cart_item.product.Stock < quantity:
            return jsonify({'error': 'Stock insuficiente'}), 400
        
        cart_item.quantity = quantity
        cart_item.DateAdded = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Cantidad actualizada',
            'item': cart_item.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@sales_bp.route('/cart/remove/<int:item_id>', methods=['DELETE'])
def remove_from_cart(item_id):
    """Eliminar item del carrito"""
    try:
        user = get_user_from_token()
        if not user:
            return jsonify({'error': 'Token inválido'}), 401
        
        cart_item = TemporalSales.query.filter_by(
            id_TemporalSales=item_id,
            iD_User=user.iD_User,
            id_Sale=None
        ).first_or_404()
        
        db.session.delete(cart_item)
        db.session.commit()
        
        return jsonify({'message': 'Producto eliminado del carrito'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@sales_bp.route('/cart/clear', methods=['DELETE'])
def clear_cart():
    """Vaciar carrito completo"""
    try:
        user = get_user_from_token()
        if not user:
            return jsonify({'error': 'Token inválido'}), 401
        
        TemporalSales.query.filter_by(
            iD_User=user.iD_User,
            id_Sale=None
        ).delete()
        
        db.session.commit()
        
        return jsonify({'message': 'Carrito vaciado'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ===============================
# RUTAS DE VENTAS
# ===============================

@sales_bp.route('/checkout', methods=['POST'])
def checkout():
    """Procesar compra del carrito"""
    try:
        user = get_user_from_token()
        if not user:
            return jsonify({'error': 'Token inválido'}), 401
        
        # Obtener items del carrito
        cart_items = TemporalSales.query.filter_by(
            iD_User=user.iD_User,
            id_Sale=None
        ).all()
        
        if not cart_items:
            return jsonify({'error': 'Carrito vacío'}), 400
        
        # Verificar stock de todos los productos
        for item in cart_items:
            if item.product.Stock < item.quantity:
                return jsonify({
                    'error': f'Stock insuficiente para {item.product.ProductName}'
                }), 400
        
        # Crear venta
        data = request.get_json() or {}
        new_sale = Sales(
            iD_User=user.iD_User,
            DescripcionSale=data.get('DescripcionSale', 'Compra online'),
            DateCreated=datetime.utcnow()
        )
        
        db.session.add(new_sale)
        db.session.flush()  # Para obtener el ID
        
        total_sale = 0
        
        # Crear detalles de venta y actualizar stock
        for item in cart_items:
            # Crear detalle de venta
            detail = SalesDetail(
                id_Product=item.id_Product,
                id_Sale=new_sale.id_Sale,
                id_TemporalSales=item.id_TemporalSales,
                DateSales=datetime.utcnow(),
                amount=item.quantity,
                ValueSale=item.product.Price * item.quantity
            )
            
            # Actualizar stock
            item.product.Stock -= item.quantity
            
            # Vincular item temporal con la venta
            item.id_Sale = new_sale.id_Sale
            
            total_sale += detail.ValueSale
            db.session.add(detail)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Compra procesada exitosamente',
            'sale': new_sale.to_dict(include_details=True),
            'total': total_sale
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@sales_bp.route('/', methods=['GET'])
def get_sales():
    """Obtener ventas del usuario o todas (admin)"""
    try:
        user = get_user_from_token()
        if not user:
            return jsonify({'error': 'Token inválido'}), 401
        
        # Verificar si es admin
        is_admin = any(role.TypeRole == 'Administrador' for role in user.roles)
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        if is_admin:
            # Admin ve todas las ventas
            sales = Sales.query.order_by(Sales.DateCreated.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
        else:
            # Usuario ve solo sus ventas
            sales = Sales.query.filter_by(iD_User=user.iD_User).order_by(
                Sales.DateCreated.desc()
            ).paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
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

@sales_bp.route('/<int:sale_id>', methods=['GET'])
def get_sale(sale_id):
    """Obtener detalle de una venta específica"""
    try:
        user = get_user_from_token()
        if not user:
            return jsonify({'error': 'Token inválido'}), 401
        
        sale = Sales.query.get_or_404(sale_id)
        
        # Verificar permisos
        is_admin = any(role.TypeRole == 'Administrador' for role in user.roles)
        if not is_admin and sale.iD_User != user.iD_User:
            return jsonify({'error': 'No tienes permiso para ver esta venta'}), 403
        
        return jsonify({
            'sale': sale.to_dict(include_details=True)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sales_bp.route('/stats', methods=['GET'])
def get_sales_stats():
    """Obtener estadísticas de ventas (solo admin)"""
    try:
        user = get_user_from_token()
        if not user:
            return jsonify({'error': 'Token inválido'}), 401
        
        # Verificar si es admin
        is_admin = any(role.TypeRole == 'Administrador' for role in user.roles)
        if not is_admin:
            return jsonify({'error': 'No tienes permisos de administrador'}), 403
        
        # Estadísticas básicas
        total_sales = Sales.query.count()
        total_revenue = db.session.query(db.func.sum(SalesDetail.ValueSale)).scalar() or 0
        
        # Ventas del último mes
        from datetime import datetime, timedelta
        last_month = datetime.utcnow() - timedelta(days=30)
        recent_sales = Sales.query.filter(Sales.DateCreated >= last_month).count()
        
        return jsonify({
            'total_sales': total_sales,
            'total_revenue': float(total_revenue),
            'recent_sales': recent_sales,
            'average_sale': float(total_revenue / total_sales) if total_sales > 0 else 0
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500