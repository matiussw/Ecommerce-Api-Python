from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Inicializar extensiones
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Configuración
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'HolaMundo')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///database/ecommerce.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JSON_AS_ASCII'] = False  # Para caracteres especiales en JSON
    
    # Inicializar extensiones con la app
    db.init_app(app)
    CORS(app)  # Permitir CORS para frontend
    
    # Registrar blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.product_routes import product_bp
    from app.routes.user_routes import user_bp
    from app.routes.sales_routes import sales_bp
    from app.routes.category_routes import category_bp
    from app.routes.location_routes import location_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(product_bp, url_prefix='/api/products')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(sales_bp, url_prefix='/api/sales')
    app.register_blueprint(category_bp, url_prefix='/api/categories')
    app.register_blueprint(location_bp, url_prefix='/api/locations')
    
    # Ruta de prueba
    @app.route('/')
    def home():
        return {
            'message': 'API E-commerce funcionando',
            'version': '1.0',
            'endpoints': {
                'auth': '/api/auth',
                'products': '/api/products', 
                'users': '/api/users',
                'sales': '/api/sales',
                'categories': '/api/categories',
                'locations': '/api/locations'
            }
        }
    
    # Crear tablas si no existen
    with app.app_context():
        db.create_all()
    
    return app