import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_mail import Mail

db = SQLAlchemy()
mail = Mail()

def create_app():
    app = Flask(__name__)
   
    app.config.from_object('app.config.Config')
    app.secret_key = os.environ.get('SECRET_KEY', 'club-360-secret-key')

    CORS(app, supports_credentials=True)

    db.init_app(app)
    mail = Mail(app)
    with app.app_context():
        from app.models import db_structure
        db.create_all()
        
    from app.routes.central_routing import all_routes
    from app.routes.user_routes import user_bp
    from app.routes.tarjeta_routes import tarjeta_bp

    #app.register_blueprint(user_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(tarjeta_bp)
    #from app.routes.user_routes import main as main_blueprint
    #app.register_blueprint(main_blueprint)
    #from app.routes import main
    #app.register_blueprint(main)

    return app

