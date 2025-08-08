from flask import Blueprint, request, jsonify
from app import db
from app.models import Product, Category, PRODUC_Image, product_categories
from sqlalchemy import or_, and_

product_bp = Blueprint('products', __name__)

@product_bp.route('/', methods=['GET'])
def get_products():
    """Obtener todos los productos con filtros opcionales"""
    try:
        # Parámetros de consulta
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        category_id = request.args.get('category_id', type=int)
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        in_stock = request.args.get('in_stock', type=bool)
        
        # Construir query base
        query = Product.query
        
        # Filtro por búsqueda en nombre
        if search:
            query = query.filter(Product.ProductName.contains(search))
        
        # Filtro por categoría
        if category_id:
            query = query.join(product_categories).filter(
                product_categories.c.id_Category == category_id
            )
        
        # Filtro por rango de precios
        if min_price is not None:
            query = query.filter(Product.Price >= min_price)
        if max_price is not None:
            query = query.filter(Product.Price <= max_price)
        
        # Filtro por stock
        if in_stock:
            query = query.filter(Product.Stock > 0)
        
        # Paginación
        products = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'products': [product.to_dict(include_categories=True, include_images=True) 
                        for product in products.items],
            'pagination': {
                'page': page,
                'pages': products.pages,
                'per_page': per_page,
                'total': products.total,
                'has_next': products.has_next,
                'has_prev': products.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@product_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Obtener un producto específico"""
    try:
        product = Product.query.get_or_404(product_id)
        return jsonify({
            'product': product.to_dict(include_categories=True, include_images=True)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@product_bp.route('/', methods=['POST'])
def create_product():
    """Crear un nuevo producto"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['ProductName', 'Price']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} es requerido'}), 400
        
        # Crear producto
        new_product = Product(
            ProductName=data['ProductName'],
            Price=data['Price'],
            Stock=data.get('Stock', 0)
        )
        
        # Agregar categorías si se proporcionan
        if 'categories' in data:
            for cat_id in data['categories']:
                category = Category.query.get(cat_id)
                if category:
                    new_product.categories.append(category)
        
        db.session.add(new_product)
        db.session.commit()
        
        return jsonify({
            'message': 'Producto creado exitosamente',
            'product': new_product.to_dict(include_categories=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@product_bp.route('/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Actualizar un producto"""
    try:
        product = Product.query.get_or_404(product_id)
        data = request.get_json()
        
        # Actualizar campos
        if 'ProductName' in data:
            product.ProductName = data['ProductName']
        if 'Price' in data:
            product.Price = data['Price']
        if 'Stock' in data:
            product.Stock = data['Stock']
        
        # Actualizar categorías
        if 'categories' in data:
            product.categories.clear()
            for cat_id in data['categories']:
                category = Category.query.get(cat_id)
                if category:
                    product.categories.append(category)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Producto actualizado exitosamente',
            'product': product.to_dict(include_categories=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@product_bp.route('/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Eliminar un producto"""
    try:
        product = Product.query.get_or_404(product_id)
        
        # Verificar si tiene ventas asociadas
        if product.sales_details:
            return jsonify({
                'error': 'No se puede eliminar un producto con ventas asociadas'
            }), 400
        
        db.session.delete(product)
        db.session.commit()
        
        return jsonify({'message': 'Producto eliminado exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@product_bp.route('/<int:product_id>/images', methods=['POST'])
def add_product_image(product_id):
    """Agregar imagen a un producto"""
    try:
        product = Product.query.get_or_404(product_id)
        data = request.get_json()
        
        # Validar datos requeridos
        if not data.get('pathimage'):
            return jsonify({'error': 'pathimage es requerido'}), 400
        
        # Si es imagen principal, desmarcar las demás
        if data.get('is_main_image'):
            PRODUC_Image.query.filter_by(id_Product=product_id).update(
                {'is_main_image': 0}
            )
        
        # Crear imagen
        new_image = PRODUC_Image(
            id_Product=product_id,
            id_Category=data.get('id_Category'),
            pathimage=data['pathimage'],
            alt_text=data.get('alt_text'),
            is_main_image=1 if data.get('is_main_image') else 0
        )
        
        db.session.add(new_image)
        db.session.commit()
        
        return jsonify({
            'message': 'Imagen agregada exitosamente',
            'image': new_image.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@product_bp.route('/<int:product_id>/images/<int:image_id>', methods=['DELETE'])
def delete_product_image(product_id, image_id):
    """Eliminar imagen de un producto"""
    try:
        image = PRODUC_Image.query.filter_by(
            id_image=image_id, 
            id_Product=product_id
        ).first_or_404()
        
        db.session.delete(image)
        db.session.commit()
        
        return jsonify({'message': 'Imagen eliminada exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@product_bp.route('/<int:product_id>/stock', methods=['PUT'])
def update_stock(product_id):
    """Actualizar stock de un producto"""
    try:
        product = Product.query.get_or_404(product_id)
        data = request.get_json()
        
        if 'Stock' not in data:
            return jsonify({'error': 'Stock es requerido'}), 400
        
        if data['Stock'] < 0:
            return jsonify({'error': 'Stock no puede ser negativo'}), 400
        
        product.Stock = data['Stock']
        db.session.commit()
        
        return jsonify({
            'message': 'Stock actualizado exitosamente',
            'product': product.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@product_bp.route('/search', methods=['GET'])
def search_products():
    """Búsqueda avanzada de productos"""
    try:
        query_text = request.args.get('q', '')
        
        if not query_text:
            return jsonify({'products': []}), 200
        
        # Búsqueda en nombre y descripción
        products = Product.query.filter(
            or_(
                Product.ProductName.contains(query_text),
                # Aquí podrías agregar más campos si tienes descripción
            )
        ).limit(20).all()
        
        return jsonify({
            'products': [product.to_dict(include_categories=True) 
                        for product in products],
            'count': len(products)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@product_bp.route('/featured', methods=['GET'])
def get_featured_products():
    """Obtener productos destacados (ejemplo: más vendidos o con más stock)"""
    try:
        # Por ejemplo, productos con más stock o random
        products = Product.query.filter(Product.Stock > 0).order_by(
            Product.Stock.desc()
        ).limit(8).all()
        
        return jsonify({
            'featured_products': [product.to_dict(include_categories=True, include_images=True) 
                                for product in products]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500