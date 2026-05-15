from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    CORS(app)  # allow React to connect

    db.init_app(app)

    with app.app_context():
        from app.models import db_structure
        db.create_all()
        
    from app.routes.user_routes import user_bp
    from app.routes.tarjeta_routes import tarjeta_bp

    app.register_blueprint(user_bp)
    app.register_blueprint(tarjeta_bp)
    #from app.routes.user_routes import main as main_blueprint
    #app.register_blueprint(main_blueprint)
    #from app.routes import main
    #app.register_blueprint(main)

    return app