from flask import Blueprint, request, jsonify
from app import db
from app.models import Category, Product, product_categories

category_bp = Blueprint('categories', __name__)

@category_bp.route('/', methods=['GET'])
def get_categories():
    """Obtener todas las categorías"""
    try:
        include_products = request.args.get('include_products', False, type=bool)
        
        categories = Category.query.all()
        
        result = []
        for category in categories:
            cat_data = category.to_dict()
            
            if include_products:
                # Contar productos en la categoría
                product_count = db.session.query(product_categories).filter(
                    product_categories.c.id_Category == category.id_Category
                ).count()
                cat_data['product_count'] = product_count
                
                # Incluir algunos productos de ejemplo si se requiere
                sample_products = category.products[:5] if hasattr(category, 'products') else []
                cat_data['sample_products'] = [p.to_dict() for p in sample_products]
            
            result.append(cat_data)
        
        return jsonify({
            'categories': result,
            'count': len(result)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@category_bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """Obtener una categoría específica"""
    try:
        category = Category.query.get_or_404(category_id)
        
        # Obtener productos de esta categoría
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        products = Product.query.join(product_categories).filter(
            product_categories.c.id_Category == category_id
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'category': category.to_dict(),
            'products': [product.to_dict(include_images=True) for product in products.items],
            'pagination': {
                'page': page,
                'pages': products.pages,
                'per_page': per_page,
                'total': products.total
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@category_bp.route('/', methods=['POST'])
def create_category():
    """Crear una nueva categoría"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        if not data.get('CategoryName'):
            return jsonify({'error': 'CategoryName es requerido'}), 400
        
        # Verificar si ya existe
        existing_category = Category.query.filter_by(
            CategoryName=data['CategoryName']
        ).first()
        
        if existing_category:
            return jsonify({'error': 'La categoría ya existe'}), 409
        
        # Crear categoría
        new_category = Category(
            CategoryName=data['CategoryName']
        )
        
        db.session.add(new_category)
        db.session.commit()
        
        return jsonify({
            'message': 'Categoría creada exitosamente',
            'category': new_category.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@category_bp.route('/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    """Actualizar una categoría"""
    try:
        category = Category.query.get_or_404(category_id)
        data = request.get_json()
        
        if 'CategoryName' in data:
            # Verificar si el nuevo nombre ya existe
            existing_category = Category.query.filter(
                Category.CategoryName == data['CategoryName'],
                Category.id_Category != category_id
            ).first()
            
            if existing_category:
                return jsonify({'error': 'El nombre de categoría ya existe'}), 409
            
            category.CategoryName = data['CategoryName']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Categoría actualizada exitosamente',
            'category': category.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@category_bp.route('/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    """Eliminar una categoría"""
    try:
        category = Category.query.get_or_404(category_id)
        
        # Verificar si tiene productos asociados
        product_count = db.session.query(product_categories).filter(
            product_categories.c.id_Category == category_id
        ).count()
        
        if product_count > 0:
            return jsonify({
                'error': 'No se puede eliminar una categoría con productos asociados'
            }), 400
        
        db.session.delete(category)
        db.session.commit()
        
        return jsonify({'message': 'Categoría eliminada exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@category_bp.route('/<int:category_id>/products', methods=['GET'])
def get_category_products(category_id):
    """Obtener todos los productos de una categoría"""
    try:
        category = Category.query.get_or_404(category_id)
        
        # Parámetros de consulta
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        in_stock = request.args.get('in_stock', type=bool)
        
        # Construir query
        query = Product.query.join(product_categories).filter(
            product_categories.c.id_Category == category_id
        )
        
        # Aplicar filtros
        if min_price is not None:
            query = query.filter(Product.Price >= min_price)
        if max_price is not None:
            query = query.filter(Product.Price <= max_price)
        if in_stock:
            query = query.filter(Product.Stock > 0)
        
        # Paginación
        products = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'category': category.to_dict(),
            'products': [product.to_dict(include_images=True) 
                        for product in products.items],
            'pagination': {
                'page': page,
                'pages': products.pages,
                'per_page': per_page,
                'total': products.total
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@category_bp.route('/stats', methods=['GET'])
def get_category_stats():
    """Obtener estadísticas de categorías"""
    try:
        # Estadísticas por categoría
        stats = []
        categories = Category.query.all()
        
        for category in categories:
            product_count = db.session.query(product_categories).filter(
                product_categories.c.id_Category == category.id_Category
            ).count()
            
            # Calcular stock total de la categoría
            total_stock = db.session.query(db.func.sum(Product.Stock)).join(
                product_categories
            ).filter(
                product_categories.c.id_Category == category.id_Category
            ).scalar() or 0
            
            # Precio promedio de productos en la categoría
            avg_price = db.session.query(db.func.avg(Product.Price)).join(
                product_categories
            ).filter(
                product_categories.c.id_Category == category.id_Category
            ).scalar() or 0
            
            stats.append({
                'category': category.to_dict(),
                'product_count': product_count,
                'total_stock': int(total_stock),
                'average_price': float(avg_price)
            })
        
        return jsonify({
            'category_stats': stats,
            'total_categories': len(categories)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500