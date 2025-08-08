from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv ()

db= SQLAlchemy()

def create_app():
    app = Flask (__name__)

    app.config ['SECRET_KEY'] = os.getenv ('SECRET_KEY','HolaMundo')
    app.config ['SQLALCHEMY_DATABASE_URI'] = os.getenv ('DATABASE_URL','sqlite:///C:/Users/T30/Documents/Ecommerce-Api/database/ecommerce.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
   
    
    db.init_app(app)
    CORS(app)

     # Registrar blueprints
    from app.routes.auth_route import auth_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
   
    # Ruta de prueba
    @app.route('/')
    def home():
        return {
            'message': 'API E-commerce funcionando',
            'version': '1.0',
            'endpoints': {
                'auth': '/api/auth'
            }
        }
    
    # Crear tablas si no existen
    with app.app_context():
        db.create_all()
    
    return app